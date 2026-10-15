import asyncio

from src.Core import Settings

from src.Operations import ThreadOperations as TO
from src.Operations import URLOperations as UO

from src.Core.DataAcquisition.ProcessingAndExtracting import DataProcessing as DP

from src.Core.DataAcquisition.Scraping import FindRegion
from src.Core.DataAcquisition.ProcessingAndExtracting.Fetcher import Fetcher
from src.Core.DataAcquisition.ProcessingAndExtracting import ProductPage
from src.Core.DataAcquisition.ProcessingAndExtracting import ProductReviewExtractor as PE

from src.Core.DataAnalysis import RelevanceAnalysis as RA


async def ScrapeOneStore(fetcher, url, store, progress):
    """Orchestrates the scraping workflow for a single store URL, handling raw HTTP fetches,
    automatic browser escalation for JavaScript-heavy pages, listing extraction,
    direct product page fallbacks, and concurrent task dispatching.

    Args:
        fetcher: The network/browser fetching utility instance.
        url (str): The target URL to scrape (listing or product page).
        store (dict): Metadata dictionary containing store configuration (e.g., 'domain').
        progress (dict): Shared dictionary tracking overall scraping metrics and totals.
    """

    if Settings.VERBOSE:
        print(f"[*] Navigating to listing page: {url}")

    # Scroll enabled to force loading of lazy-loaded elements before extraction
    listing = await fetcher.get(url, renderOptions={"navigate": True})

    if not listing["html"] or listing["blocked"] or listing["status"] >= 400:
        print(f"[!] Error fetching listing page {url}: {listing.get('error') or 'HTTP ' + str(listing['status'])}")
        return

    pdpLinks = await TO.ParallelDispatch(DP.ExtractListingLinks, listing["html"], listing["url"], listing["json"])

    # If the fetched page is itself a product page (not a search listing),
    # include it as a candidate too - the discovery often lands directly on
    # the product page, and its own product data is the most relevant offer.
    single = None
    if not UO.LooksLikeSearchURL(listing["url"]):
        single = await TO.ParallelDispatch(ProductPage.ExtractProductPage, listing["html"], listing["url"], listing["json"])
        if (single["productName"] or single["pageTitle"]) and single["price"]:
            knownLinks = {UO.CleanSortURL(link) for link in pdpLinks}
            if UO.CleanSortURL(listing["url"]) not in knownLinks:
                pdpLinks.insert(0, listing["url"])

    # Fallback: If no catalog links are found, the target URL might be a standalone product page
    if not pdpLinks and single is not None and (single["productName"] or single["pageTitle"]) and single["price"]:
        pdpLinks = [listing["url"]]

    # Fallback: If raw HTTP missed content due to client-side JS rendering, escalate to a headless browser
    if not pdpLinks and listing["via"] == "http" and not fetcher.browserFailed:
        if Settings.VERBOSE:
            print(f"[*] No products in the raw HTML of {store['domain']} (rendered via JS) -> switching to browser...")

        rendered = await fetcher.FetchDataThroughBrowser(url, navigate=True)
        if rendered["html"] and not rendered["blocked"]:
            listing = rendered
            pdpLinks = await TO.ParallelDispatch(DP.ExtractListingLinks, listing["html"], listing["url"], listing["json"])
            if not pdpLinks:
                single = await TO.ParallelDispatch(ProductPage.ExtractProductPage, listing["html"], listing["url"], listing["json"])
                if (single["productName"] or single["pageTitle"]) and single["price"]:
                    pdpLinks = [listing["url"]]

    if Settings.MAX_PRODUCTS:
        pdpLinks = pdpLinks[:Settings.MAX_PRODUCTS]

    if Settings.VERBOSE:
        print(f"[+] {store['domain']}: detected {len(pdpLinks)} product pages. Scraping...")

    if not pdpLinks:
        print(f"[!] No product links found on {url}")
        return

    progress["total"] += len(pdpLinks)

    # Process all extracted product pages concurrently in parallel tasks
    await asyncio.gather(*(DP.ProcessProduct(fetcher, store, i, link, listing["url"], progress)
                           for i, link in enumerate(pdpLinks, start=1)))


async def ScrapeStore(fetcher, url, store, progress):
    """Safely executes the scraping routine for a single store, catching unhandled
    exceptions to ensure that a failure in one store does not halt the execution
    of other stores in a multi-store pipeline.

    Args:
        fetcher: The network/browser fetching utility instance.
        url (str): The target store URL to scrape.
        store (dict): Metadata dictionary containing store configuration (e.g., 'domain').
        progress (dict): Shared dictionary tracking overall scraping metrics and totals.

    Examples:
        # If ScrapeOneStore raises a timeout or parsing error, it is caught gracefully:
        # output -> [!] example.com: stopped by an error: TimeoutError: ...
    """
    try:
        await ScrapeOneStore(fetcher, url, store, progress)
    except Exception as e:
        # Isolate store failures to prevent a single broken site from crashing the entire batch
        print(f"[!] {store['domain']}: stopped by an error: {type(e).__name__}: {e}")



def GetResultsOfStores(stores):
    """Takes in the stores, and returns a list of dictionaries for all products of all stores combined"""
    products = []
    for store in stores:
        for _, product in store["results"]:
            product["storeName"] = UO.GetDomainFromURL(product["productURL"])
            products.append(product)

    return products


async def StartScraping(query):
    """Scrapes all regional stores for the query. Returns (products, stats)."""
    if not query or query.strip() == "":
        print("[-] Please Enter the product you wish to buy")
        return


    urls = FindRegion.GetRegionalStoreUrls(query)

    TO.StartHelpers()
    stores = [{"url": u, "domain": UO.GetDomainFromURL(u), "results": [], "reviewApi": PE.ProductReviewExtractor()} for u in urls]
    progress = {"done": 0, "total": 0}
    stats = {"http": 0, "browser": 0}
    products = []

    print("[*] Scraping the network, hold on this might take a few minutes...")

    try:
        async with Fetcher() as fetcher:
            try:
                await asyncio.gather(*(ScrapeStore(fetcher, store["url"], store, progress) for store in stores))
            finally:
                stats = fetcher.stats
    except (asyncio.CancelledError, KeyboardInterrupt):
        print("[!] Stopped by user (results collected so far were saved).")
    finally:
        TO.StopHelpers()
        products = GetResultsOfStores(stores)

    # Drop products that clearly do not match the searched query (other
    # models, unrelated listings). Accessories are still kept when the user
    # actually searches for one - they only lose against the real product
    # later, in the price-cluster logic of StatisticalAnalysis.
    products = RA.FilterProducts(products, query)

    return products, stats
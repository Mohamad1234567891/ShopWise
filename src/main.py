import asyncio
import json
import multiprocessing
import sys
import time

from src.Core.DataAcquisition.ProcessingAndExtracting.Fetcher import Fetcher
from src.Core.DataAcquisition.ProcessingAndExtracting import ProductReviewExtractor as PE
from src.Core.DataAcquisition.Scraping import Scraper
from src.Core.DataAcquisition import AsyncSession as AM

from src.Core import Settings

from src.Operations import URLOperations as UO
from src.Operations import ThreadOperations as TO


def SaveResults(stores):
    """Flattens, sorts, and serializes scraped product data from multiple stores into
    a single JSON output file, preserving sequential order.

    Args:
        stores (list): A list of store dictionaries, each containing a 'results' key
                       with an iterable of (index, product_data) pairs.

    Returns:
        list: The consolidated, sorted list of all product data dictionaries.

    Examples:
        stores = [
            {"results": [(2, {"name": "Phone B"}), (1, {"name": "Phone A"})]}
        ]

        # The nested comprehension sorts each store's results by index (r[0]) and flattens them
        output -> [{"name": "Phone A"}, {"name": "Phone B"}]
    """
    # Flatten results across all stores while sorting each store's items by their index (r[0])
    products = [data for store in stores for _, data in sorted(store["results"], key=lambda r: r[0])]

    with open(Settings.OUTPUT_FILE, "w", encoding="utf-8") as fh:
        json.dump(products, fh, ensure_ascii=False, indent=4)

    return products


# ================================================================ MAIN
async def main():
    #url = "https://www.hepsiburada.com/iphone-17-iphone-ios-telefonlar-xc-60005202-t6721"
    url = "https://www.mediamarkt.com.tr/tr/category/iphone-17-90434.html"
    url = "https://www.teknosa.com/iphone-17-c-100001001034"
    #url = "https://www.amazon.com.tr/s?k=iphone+17&i=electronics&__mk_tr_TR=%C3%85M%C3%85%C5%BD%C3%95%C3%91"
    #url = "https://www.ebay.com/sch/i.html?_nkw=iphone+17&_sacat=0&_from=R40&_trksid=p4624852.m570.l1313"
    #url = "https://www.n11.com/arama?q=iphone+17"
    #url = "https://www.ciceksepeti.com/arama?query=iphone%2017&qt=iphone%2017&choice=1"

    urls = sys.argv[1:] or [url]  # python scraper.py "<store 1 URL>" "<store 2 URL>" ...  (all stores at once)

    startTime = time.perf_counter()
    print("[*] Initializing fast session (HTTP first, browser only for pages that need it)...")
    if AM.GetAsyncSession() is None:
        print("[!] curl_cffi is not installed -> every page goes through the browser (slower). pip install curl_cffi")
    TO.SartHelpers()
    stores = [{"url": u, "domain": UO.GetDomainFromURL(u), "results": [], "reviewApi": PE.ProductReviewExtractor()} for u in urls]
    progress = {"done": 0, "total": 0}
    stats = {"http": 0, "browser": 0}

    try:
        async with Fetcher() as fetcher:
            try:
                await asyncio.gather(*(Scraper.ScrapeStore(fetcher, store["url"], store, progress) for store in stores))
            finally:
                stats = fetcher.stats
    finally:  # also runs on Ctrl+C: everything collected so far is saved

        TO.StopHelpers()
        products = SaveResults(stores)
        print(f"\n[*] Crawling session complete: {len(products)} products in {time.perf_counter() - startTime:.1f}s "
              f"({stats['http']} fast requests, {stats['browser']} browser pages). Saved to {Settings.OUTPUT_FILE}")


if __name__ == "__main__":
    multiprocessing.freeze_support()  # needed only if this script is packaged as an .exe
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[!] Stopped by user (results collected so far were saved).")
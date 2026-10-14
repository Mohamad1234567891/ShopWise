import asyncio
import multiprocessing
import time

from src.Core.DataAcquisition.ProcessingAndExtracting.Fetcher import Fetcher
from src.Core.DataAcquisition.ProcessingAndExtracting import ProductReviewExtractor as PE
from src.Core.DataAcquisition.Scraping import Scraper
from src.Core.DataAcquisition.Scraping import Search
from src.Core.DataAcquisition import AsyncSession as AM

from src.Core import Settings, CLIRenderer

from src.Operations import URLOperations as UO
from src.Operations import ThreadOperations as TO

from src.Core.DataAnalysis import StatisticalAnalysis as SA
from src.Core import ArgumentsParser as AP


def GetResultsOfStores(stores):
    """Takes in the stores, and returns a list of dictionaries for all products of all stores combined"""
    products = []
    for store in stores:
        for _, product in store["results"]:
            product["storeName"] = UO.GetDomainFromURL(product["productURL"])
            products.append(product)

    return products


# ================================================================ MAIN
async def main():
    args = AP.parseArguments()
    urls = Search.GetRegionalStoreUrls(args.productName)

    Settings.UpdateSettings(args.maxProducts, args.maxSearch, args.getReviews, args.maxPages, args.HTTPPerStore, args.browserTabs, args.requestTimeout, args.productTimeLimit, args.verbose)

    startTime = time.perf_counter()

    if Settings.VERBOSE:
        print("[*] Initializing session")

    if AM.GetAsyncSession() is None:
        print("[!] curl_cffi is not installed -> every page goes through the browser (slower). pip install curl_cffi")

    TO.SartHelpers()
    stores = [{"url": u, "domain": UO.GetDomainFromURL(u), "results": [], "reviewApi": PE.ProductReviewExtractor()} for u in urls]
    progress = {"done": 0, "total": 0}
    stats = {"http": 0, "browser": 0}

    print("[*] Scraping the network, hold on this might take a few minutes...")

    try:
        async with Fetcher() as fetcher:
            try:
                await asyncio.gather(*(Scraper.ScrapeStore(fetcher, store["url"], store, progress) for store in stores))
            finally:
                stats = fetcher.stats
    finally:  # also runs on Ctrl+C: everything collected so far is saved

        TO.StopHelpers()

        print("Our top products are listed first, with the best options usually found in the top five. We recommend checking prices and reviews, as the fifth item can sometimes outmatch the first. However, the top five will almost always give you the best value.")

        products = GetResultsOfStores(stores)

        givenPointsProducts = SA.AssignPoints(products)

        CLIRenderer.DisplayStoreCli(givenPointsProducts)

        print(givenPointsProducts[0]["productURL"])

        if Settings.VERBOSE:
            print(f"\n[*] Crawling session complete: {len(products)} products in {time.perf_counter() - startTime:.1f}s "
                  f"({stats['http']} fast requests, {stats['browser']} browser pages). Saved to {Settings.OUTPUT_FILE}")


if __name__ == "__main__":
    multiprocessing.freeze_support()  # needed only if this script is packaged as an .exe
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[!] Stopped by user (results collected so far were saved).")
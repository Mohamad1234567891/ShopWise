import asyncio
import multiprocessing
import time

from src.Core.DataAcquisition.Scraping import Scraper
from src.Core.DataAcquisition import AsyncSession as AM

from src.Core import Settings, CLIRenderer

from src.Core.DataAnalysis import StatisticalAnalysis as SA
from src.Core import ArgumentsParser as AP

from src.GUI.Core import Window


# ================================================================ MAIN
async def main():
    args = AP.parseArguments()

    Settings.UpdateSettings(args.maxProducts, args.maxSearch, args.getReviews, args.maxPages, args.HTTPPerStore, args.browserTabs, args.requestTimeout, args.productTimeLimit, args.verbose, args.cluster, args.minFactor, args.maxFactor)

    if args.productName.lower() == "gui":
        Window.StartGUI()
        return

    newSearch = True # after doing our first run if this remained true then the user have searched for a new product
    firstRun = True # this will decide from where the query is taken(from the arguments or from the new input) if first run then from arguments.
    while newSearch:
        startTime = time.perf_counter()
        if Settings.VERBOSE:
            print("[*] Initializing session")

        if AM.GetAsyncSession() is None:
            print("[!] curl_cffi is not installed -> every page goes through the browser (slower). pip install curl_cffi")

        products, stats = await Scraper.StartScraping(args.productName if firstRun else input("Enter a product name: "))
        firstRun = False

        givenPointsProducts = SA.SortAndColorStores(SA.AssignPoints(products))

        if not givenPointsProducts:
            print("[!] No products with a valid price were found.")
            return

        newSearch = CLIRenderer.DisplayOnCli(givenPointsProducts)

        if Settings.VERBOSE:
            print(f"\n[*] Crawling session complete: {len(givenPointsProducts)} products in {time.perf_counter() - startTime:.1f}s "
                  f"({stats['http']} fast requests, {stats['browser']} browser pages).")




if __name__ == "__main__":
    multiprocessing.freeze_support()  # needed only if this script is packaged as an .exe
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[!] Stopped by user (results collected so far were saved).")
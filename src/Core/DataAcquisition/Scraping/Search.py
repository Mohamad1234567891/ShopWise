import requests

from concurrent.futures import ThreadPoolExecutor, as_completed

from src.Operations import URLOperations as UO

from src.Constants import Constants as C

from src.Core import Settings

from ddgs import DDGS



def AutoDetectCountry():
    """Automatically detects the user's country code via IP geolocation."""
    try:
        requestHeaders = {"User-Agent": "Mozilla/5.0"}
        apiResponse = requests.get("https://ipapi.co/json/", headers=requestHeaders, timeout=5)
        if apiResponse.status_code == 200:
            responseData = apiResponse.json()
            return responseData.get("country_code", "US").upper()
    except Exception:
        pass
    return "TR"  # Fallback


def FetchSingleStore(storeDomain, searchQuery, ddgRegion, maxResults):
    """Helper function to query a single store dynamically via the thread queue."""
    try:
        currentQuery = f"{searchQuery} {storeDomain}"

        with DDGS() as ddgClient:
            searchResults = ddgClient.text(currentQuery, region=ddgRegion, max_results=maxResults)

            for resultItem in searchResults:
                targetUrl = resultItem.get("href")
                if not targetUrl:
                    continue

                extractedDomain = UO.GetDomainFromURL(targetUrl)

                if extractedDomain in storeDomain or storeDomain in extractedDomain:
                    return targetUrl
    except Exception:
        pass

    return None


def GetRegionalStoreUrls(searchQuery, maxResults = Settings.MAX_SEARCH_RESULTS):
    """Auto-detects region and uses a dynamic thread pool queue to process

    stores concurrently as fast as possible.
    """
    regionCode = AutoDetectCountry()
    print(f"[*] Auto-detected Region: {regionCode}")

    storeList = C.STORES_BY_REGION.get(regionCode, C.STORES_BY_REGION["TR"])
    finalUrls = []

    ddgRegion = f"{regionCode.lower()}-{regionCode.lower()}"

    # max_workers=4 creates 4 worker threads that pull from the queue dynamically
    with ThreadPoolExecutor(max_workers=12) as executor:
        # Submitting all stores populates the internal task queue immediately
        futureToStore = {
            executor.submit(FetchSingleStore, storeDomain, searchQuery, ddgRegion, maxResults): storeDomain
            for storeDomain in storeList
        }

        # As threads finish items, as_completed yields them immediately
        for futureItem in as_completed(futureToStore):
            resultUrl = futureItem.result()
            if resultUrl:
                finalUrls.append(resultUrl)

    return finalUrls


# --- Example Usage ---
#if __name__ == "__main__":
#    queryStr = "iphone 17"
#
#    print(f"[*] Searching for '{queryStr}' across local stores...")
#    storeUrls = GetRegionalStoreUrls(queryStr)
#
#    print("\n[+] Final Matched Store URLs:")
#    for urlItem in storeUrls:
#        print(f'    url = "{urlItem}"')
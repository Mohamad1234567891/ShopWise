import requests

from urllib.parse import quote

from src.Constants import Constants as C

from src.Core import Settings


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


def DirectStoreUrl(storeDomain, searchQuery):
    """Builds the store's search-results URL directly from its template.

    Returns None when no template is known for the store (the store is then
    skipped for this search)."""
    template = C.SEARCH_URL_TEMPLATES.get(storeDomain)
    if not template:
        return None
    return template.format(query=quote(searchQuery))


def GetRegionalStoreUrls(searchQuery):
    """Detects the user's region and returns a search URL for every store in
    that region, built directly from the templates in Constants - no search
    engine is involved, so all stores are resolved instantly."""
    regionCode = AutoDetectCountry()

    if Settings.VERBOSE:
        print(f"[*] Auto-detected Region: {regionCode}")

    storeList = C.STORES_BY_REGION.get(regionCode, C.STORES_BY_REGION["TR"])

    urls = []
    for storeDomain in storeList:
        storeUrl = DirectStoreUrl(storeDomain, searchQuery)
        if storeUrl:
            urls.append(storeUrl)

    return urls

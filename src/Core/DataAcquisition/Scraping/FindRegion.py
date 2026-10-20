"""
This file is part of ShopWise, an open-source multi-region, multi-store
price-comparison and product-search engine.

Copyright (c) 2026 Muhammed Bekiroğlu and the ShopWise contributors.

Original ShopWise repository: https://github.com/Mohamad1234567891/ShopWise

Muhammed Bekiroğlu (ShopWise team leader and top contributor) YouTube channel:
    https://www.youtube.com/@ALShajaraComputerScienceInstit

Licensed under the Mozilla Public License 2.0 with Additional Attribution
Terms — see the LICENSE file.
-------------------------------------------------------------------------------------------------------------------------------

Region and store discovery. Auto-detects the user's country, translates the query into the region's language only when the translation keeps every original token (so brand names survive) and returns the regional store search URLs together with the effective query.
"""

import requests

from urllib.parse import quote

from src.Constants import Constants as C

from src.Core import Settings
from src.Core.DataAnalysis import RelevanceAnalysis as RA


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


# Caches for the translation step, so the models are loaded only once.
InstalledLanguages = None
Translators = {}


def PreservesTokens(original, translated):
    """True when the translation kept every token of the original query.

    Argos can mangle brand/model words ('matepad' -> 'eşipad'), and searching
    stores with such a query would give WORSE results. A translation is only
    trusted when every original token survives it."""
    originalRuns = RA.NormalizeRuns(original)
    translatedRuns = RA.NormalizeRuns(translated)
    return all(run in translatedRuns for run in originalRuns)


def TranslateQuery(searchQuery, regionCode):
    """Translates the query into the region's local language (best effort).

    Local stores name their products in their own language (Turkish "kılıf"
    for "cover"), so an English query often matches nothing. When the Argos
    model for the region is installed AND the translation keeps every token
    of the original query intact, the translated query is used. Returns the
    original query unchanged otherwise."""
    global InstalledLanguages, Translators

    targetLang = C.REGION_LANGUAGES.get(regionCode)
    if not targetLang or targetLang == "en":
        return searchQuery

    try:
        import argostranslate.translate as ArgosTranslate

        if InstalledLanguages is None:
            InstalledLanguages = {lang.code: lang for lang in ArgosTranslate.get_installed_languages()}
        if "en" not in InstalledLanguages or targetLang not in InstalledLanguages:
            return searchQuery

        # never translate a query that is already in the region's language
        try:
            from langdetect import detect
            if detect(searchQuery) == targetLang:
                return searchQuery
        except Exception:
            pass

        key = (targetLang,)
        if key not in Translators:
            Translators[key] = InstalledLanguages["en"].get_translation(InstalledLanguages[targetLang])

        translated = Translators[key].translate(searchQuery)
        if translated and translated.strip() and PreservesTokens(searchQuery, translated):
            return translated.strip()
    except Exception:
        pass

    return searchQuery


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
    engine is involved, so all stores are resolved instantly.

    The query is first translated into the region's language (when possible),
    because local stores respond far better to local queries. Returns
    (urls, effectiveQuery), where effectiveQuery is the query actually used -
    it is also the one the relevance filter should compare product names
    against."""
    regionCode = AutoDetectCountry()

    if Settings.VERBOSE:
        print(f"[*] Auto-detected Region: {regionCode}")

    effectiveQuery = TranslateQuery(searchQuery, regionCode)

    if Settings.VERBOSE and effectiveQuery != searchQuery:
        print(f"[*] Translated the query to the region's language: {effectiveQuery}")

    storeList = C.STORES_BY_REGION.get(regionCode, C.STORES_BY_REGION["TR"])

    urls = []
    for storeDomain in storeList:
        storeUrl = DirectStoreUrl(storeDomain, effectiveQuery)
        if storeUrl:
            urls.append(storeUrl)

    return urls, effectiveQuery

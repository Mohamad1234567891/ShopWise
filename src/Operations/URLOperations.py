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

URL cleaning and link intelligence. Strips tracking parameters, builds canonical comparable URLs (sorted query order), detects search-result URLs, extracts product IDs (url/sku/gtin), resolves the real store domain (including .com.tr-style domains) and picks the best product link from a set of anchors.
"""

import re

from urllib.parse import urlparse, urlunparse, urlencode, parse_qsl, urljoin

from src.Operations import StringOperations as SO
from src.Operations import HTMLOperations as HO

from src.Constants import RegexConstants as RE
from src.Constants import URLConstants as URLC

def CleanURL(url):
    """Cleans the URL from any junk, like Trackers(Google Analytics, Google Ads, Microsoft Ads, etc.).

    url: A string value containing the url we intend to clean

    Examples:
        url = https://www.market.com/electronics/item-987?utm_source=facebook&product_id=456&ref=tracker_xyz&color=black#specs-section

        #utm_source gets rejected because this is a tracker
        #ref get rejected this is a tracker

        output -> https://www.market.com/electronics/item-987?product_id=456&color=black
    """

    """dividing the url into its components, if url is https://electronics.store.com/something/otherthing parsed would hold 
       ParseResult(scheme='https', netloc='electronics.store.com', path='/something/otherthing')."""
    parsed = urlparse(url)

    query = [(k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=True) if not RE.TRACKING_PARAM_RE.match(k)]

    return urlunparse((parsed.scheme, parsed.netloc, parsed.path or "/", parsed.params, urlencode(query), ""))


def CleanSortURL(url):
    """ignores http/https, 'www.', trailing slash, and tracking parameters. It also orders the URL queries aphabetically.

    url: A string value that contains the url

    Examples:
        url = https://www.example.com/product/item-123/?utm_source=google&size=large&color=red

        output -> example.com/product/item-123?color=red&size=large
    """

    parsed = urlparse(CleanURL(url))

    host = parsed.netloc.lower()

    host = host[4:] if host.startswith("www.") else host

    """sorting the query alphabetically and then encoding them again, we do that because websites often returns URL that contains queries in random orders, if we were to compare
       the same URL but having their queries ordered differently using python, this would result in a conclusion that those are not the same URL, so by always ordering the queries
       alphabetically we ensure that the same URL with different query order is always viewed as the same URL."""
    query = urlencode(sorted(parse_qsl(parsed.query, keep_blank_values=True)))

    return f"{host}{parsed.path.rstrip('/')}" + (f"?{query}" if query else "")#stitching back everything together


def LooksLikeSearchURL(url):
    """Returns True when the URL points to a site's search-results page.

    Examples:
        https://www.hepsiburada.com/ara?q=huawei  -> True
        https://www.trendyol.com/sr?q=huawei     -> True
        https://www.amazon.com/s?k=huawei        -> True
        https://www.store.com/item/123           -> False
    """
    parsed = urlparse(url)
    queryKeys = {key.lower() for key, _ in parse_qsl(parsed.query, keep_blank_values=True)}
    if queryKeys & {"q", "s", "k", "text", "query", "keywords", "search", "search_query", "nkw", "_nkw"}:
        return True
    return bool(re.search(
        r"/(?:search|sr|ara|arama|arar|sch|suche|recherche|busqueda|busca|ricerca)(?:/|$|\.html)",
        parsed.path.lower()))


def ExtractIDs(url, extra=()):
    """Detects and extracts IDs from a URL or from the extra parameter if provided in sku, gtin, etc. formats. returns a dictionary containing the format as the key and the
       value as the ID.

    Args:
        url: A string that contains a url that we want to extract the id from
        extra: contains any extra metadata


    Examples:
        url = "https://www.store.com/phones/product-125079812"
        extra = ()

        output -> {'urlFirst': '125079812', 'urlLast': '125079812'}
        --------------------------------------------------------
        url = "https://www.store.com/phones/product-125079812"
        extra = [
            ("sku", "SKU-99482-X"),
            ("gtin", "12345"),
            ("short_id", 98),]

        output -> {'urlFirst': '', 'urlLast': '125079812', 'sku': 'SKU-99482-X', 'gtin': '12345'}
    """


    ids = {}
    parts = [p for p in re.split(r"[^A-Za-z0-9]+", urlparse(url).path) if len(p) >= 5 and re.search(r"\d", p)]
    if parts:
        ids["urlLast"] = parts[-1]
        ids["urlFirst"] = parts[0]

    for key, value in extra:
        if isinstance(value, (str, int)) and not isinstance(value, bool) and len(str(value).strip()) >= 5:
            ids[key] = str(value).strip()
    return ids


def GetDomainFromURL(url):
    """this function extracts a domain from a url
    Examples:
        https://www.store.example.com.tr/something -> example.com.tr
        https://www.hepsiburada.com -> hepsiburada.com"""


    host = (urlparse(url).hostname or "").lower()

    if host.startswith("www."):
        host = host[4:]

    parts = host.split(".")
    if len(parts) >= 3 and parts[-2] in URLC.SECOND_LEVEL and len(parts[-1]) == 2: #checking if there was a second level country code within the url
        return ".".join(parts[-3:]) # joins the domain with the second level country code and leaves between them the '.' character(example.com.tr)(the last three elements)

    return ".".join(parts[-2:]) #if there was no second country code it joins the domain only and puts a '.' character between them (hepsiburada.com)(the last two elements)


def FirstURL(value, baseURL):
    """Extracts and resolves the first valid URL or image link from various data
    types (strings, lists, or dictionary objects containing URL keys) relative
    to a base URL.

    Args:
        value: The input data source containing a URL (str, list, dict).
        baseURL (str): The base URL used for resolving relative links.

    Returns:
        str | None: The absolute resolved URL string, or None if no valid URL is found.

    Examples:
        # Extracts an image URL from a dictionary object:
        FirstURL({"contentUrl": "/images/item.jpg"}, "https://store.com")
        # Returns: "https://store.com/images/item.jpg"
    """
    for _ in range(3):
        if isinstance(value, list):
            value = value[0] if value else None
        elif isinstance(value, dict):
            value = value.get("url") or value.get("contentUrl") or value.get("src") or value.get("@id")

    if isinstance(value, str) and value.strip() and not value.strip().startswith("data:"):
        return urljoin(baseURL, value.strip())

    return None


def PrimaryLink(links):
    """Calculates scores for candidate product links based on the presence of images,
    link text length, and title attributes, returning the absolute URL with the highest score.

    Args:
        links (list[tuple[etree.Element, str]]): A list of tuples containing anchor elements and their resolved URLs.

    Returns:
        str | None: The primary URL with the highest score, or None if the input list is empty.

    Examples:
        # Selects the best primary product link from a set of candidate anchor links:
        best_url = PrimaryLink(site_links)
    """
    scores, urls = {}, {}
    for a, url in links:
        key = CleanSortURL(url)
        urls.setdefault(key, url)
        scores[key] = (
            scores.get(key, 0) + 1 +
            2 * bool(a.xpath(".//img")) +
            2 * (len(SO.TextOf(a)) >= 10) +
            bool(a.get("title"))
        )
    return urls[max(scores, key=lambda k: scores[k])] if scores else None


def PatternLinks(doc, pageURL):
    """Fallback link extraction method identifying rich anchor links that repeat the same URL
    structural pattern multiple times across the page (representing a product grid), excluding menus.

    Args:
        doc: The parsed HTML document tree (e.g., lxml element).
        pageURL (str): The absolute URL of the listing page.

    Returns:
        list[str]: A list of primary product URLs grouped by common URL path shapes.

    Examples:
        # Extracts recurring product grid pattern links as a last resort:
        grid_links = PatternLinks(parsed_doc, "https://store.com/category")
    """
    groups = {}
    for a, url in HO.SiteLinks(doc, pageURL, GetDomainFromURL(pageURL)):
        if not HO.IsRich(a) or any(
                x.tag in ("header", "footer", "nav") or HO.ExtractSemantic(x) & {"menu", "nav", "navigation",
                                                                                 "megamenu", "breadcrumb", "footer"}
                for x in a.iterancestors()):
            continue

        parts = [p for p in urlparse(url).path.split("/") if p]
        shape = "/".join(parts[:-1]) + ("/*" if parts else "/")
        group = groups.setdefault(shape, {})
        group.setdefault(CleanSortURL(url), (url, len(SO.TextOf(a) or a.get("title") or "")))

    scored = [(len(g) * (sum(t for _, t in g.values()) / len(g)), g) for g in groups.values() if len(g) >= 3]
    return [url for url, _ in max(scored, key=lambda x: x[0])[1].values()] if scored else []
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

HTML parsing and semantics. Wraps lxml parsing and encoding detection, extracts microdata and Schema.org structures, judges element visibility, collects internal site links, identifies rich product-card anchors and discovers product cards by price position and card repetition.
"""

import re

from lxml import etree
from lxml import html as lxmlHtml
from urllib.parse import urljoin, urlparse

from src.Operations import StringOperations as SO
from src.Operations import URLOperations as UO
from src.Core.DataAcquisition.ProcessingAndExtracting import DataProcessing as DP

from src.Constants import StringConstants as SC
from src.Constants import RegexConstants as RE

def ExtractSemantic(el):
    """Extracts semantic keywords from HTML attributes (such as class, id, data, etc.)


    Examples:
        # Given this HTML element:
        # <div id="product-price-box" class="discount current">...</div>

        # The function filters hint attributes, merges them, and tokenizes the text:
        output -> {'product', 'price', 'box', 'discount', 'current'}
    """

    return SO.WordsOfText(" ".join(v for k, v in el.attrib.items() if k in SC.HINT_ATTRIBUTES))

def ParseHTML(html):
    try:
        return lxmlHtml.document_fromstring(html.encode("utf-8", "replace"), parser=lxmlHtml.HTMLParser(encoding="utf-8", remove_comments=True))

    except (etree.ParserError, ValueError):
        return lxmlHtml.document_fromstring(b"<html><body></body></html>")


def DecodeBody(content, contentType):
    """Decodes raw HTTP response bytes into a unicode string by detecting the character
    encoding from the Content-Type header, HTML meta tags, or common fallback encodings.

    Args:
        content (bytes): The raw byte string of the response body.
        contentType (str): The HTTP Content-Type header value containing potential charset information.

    Returns:
        str: The decoded string representation of the response body.

    Examples:
        # Decodes raw bytes using charset specified in Content-Type:
        html_text = DecodeBody(response_bytes, "text/html; charset=ISO-8859-1")
    """
    match = re.search(r"charset=([\w\-]+)", contentType or "", re.I)
    charset = match.group(1) if match else None

    # Fallback: Inspect the beginning of the binary content for an HTML meta charset tag
    if not charset:
        meta = re.search(rb"<meta[^>]+charset=[\"']?\s*([A-Za-z0-9_\-]+)", content[:4096], re.I)
        charset = meta.group(1).decode("ascii", "ignore") if meta else None

    # Attempt decoding with detected charset or utf-8 fallback
    for encoding in (charset, "utf-8"):
        if encoding:
            try:
                return content.decode(encoding)
            except (LookupError, UnicodeDecodeError):
                pass

    # Ultimate fallback: decode as utf-8 and replace unparseable bytes
    return content.decode("utf-8", errors="replace")


def MicrodataValue(el):
    """Extracts the underlying value from an HTML element based on HTML5 microdata
        attributes (`content`) or standard element semantics (e.g., extracting `href`
        from links, `src`/`data-src` from media elements, `datetime` from time tags,
        or text content as a fallback).

        Args:
            el: The HTML element node (e.g., lxml element) from which to extract the value.

        Returns:
            str | None: The extracted value string, or None if no valid value is found.

        Examples:
            # Extracts the datetime attribute or text content from a time element:
            time_element = parsed_doc.xpath('//time')[0]
            value = MicrodataValue(time_element)
        """
    tag = el.tag.lower() if isinstance(el.tag, str) else ""
    if el.get("content") is not None:
        return el.get("content")
    if tag in ("a", "link", "area"):
        return el.get("href")
    if tag in ("img", "source", "video", "audio", "iframe", "embed"):
        src = el.get("src") or ""
        return el.get("data-src") if (not src or src.startswith("data:")) and el.get("data-src") else src
    if tag in ("data", "meter"):
        return el.get("value")
    if tag == "time":
        return el.get("datetime") or el.text_content()
    return el.text_content()


def MicrodataItem(scope, depth=0):
    """Parses an HTML element tree marked with HTML5 Microdata (`itemscope`, `itemtype`,
    and `itemprop`) and converts it into a structured dictionary resembling JSON-LD objects.

    Args:
        scope: The HTML element node (lxml element) representing the item scope.
        depth (int, optional): The current recursion depth used to limit nested item parsing. Defaults to 0.

    Returns:
        dict: A structured dictionary representing the extracted microdata attributes and nested items.

    Examples:
        # Parses a product itemscope container into a schema-like dictionary:
        scope_el = parsed_doc.xpath('//*[@itemscope]')[0]
        item_data = MicrodataItem(scope_el)
    """
    node = {"@type": (scope.get("itemtype") or "").split()[0] if scope.get("itemtype") else ""}
    stack = [child for child in reversed(scope) if isinstance(child.tag, str)]

    # Traverse the element stack iteratively to extract item properties
    while stack:
        el = stack.pop()
        nested = el.get("itemscope") is not None  # A nested item owns its own independent properties
        if el.get("itemprop"):
            value = MicrodataItem(el, depth + 1) if nested and depth < 5 else MicrodataValue(el)
            if value not in (None, ""):
                for name in el.get("itemprop").split():
                    if name in node:
                        node[name] = (node[name] if isinstance(node[name], list) else [node[name]]) + [value]
                    else:
                        node[name] = value

        if not nested:
            stack.extend(child for child in reversed(el) if isinstance(child.tag, str))

    return node


def IsHidden(el):
    """Determines whether an HTML element is hidden from view on the page (via explicit
    'hidden' attributes, CSS `display:none` or `visibility:hidden`, or semantic hidden classes
    while excluding responsive breakpoint classes like `hidden-xs`).

    Args:
        el: The HTML element node (e.g., lxml element) to inspect.

    Returns:
        bool: True if the element is hidden, False otherwise.

    Examples:
        # Checks if a review container or button is hidden on the page:
        if IsHidden(element):
            print("Element is hidden from users.")
    """
    style = (el.get("style") or "").replace(" ", "").lower()
    if el.get("hidden") is not None or el.get("aria-hidden") == "true" or "display:none" in style or \
            "visibility:hidden" in style:
        return True

    return any(({"hidden", "hide", "invisible"} & w and not w & {"xs", "sm", "md", "lg", "xl", "mobile", "desktop", "tablet", "print"}) or {"sr", "only"} <= w for w in SO.NameWords(el))


def SiteLinks(root, pageURL, site):
    """Extracts all internal site links from an HTML element tree, resolving relative
    URLs, filtering out non-http protocols, anchors, javascript, mailtos, and junk path patterns.

    Args:
        root: The root HTML element tree (e.g., lxml element).
        pageURL (str): The absolute URL of the current page for resolving relative links.
        site (str): The target domain name to ensure links remain internal.

    Returns:
        list[tuple[etree.Element, str]]: A list of tuples containing anchor elements and their absolute resolved URLs.

    Examples:
        # Extracts all valid internal product and category links:
        internal_links = SiteLinks(parsed_doc, "https://store.com/category", "store.com")
    """
    links = []
    for a in root.xpath("descendant-or-self::a[@href]"):
        href = (a.get("href") or "").strip()
        if href and not href.startswith(("#", "javascript:", "mailto:", "tel:")):
            url = UO.CleanURL(urljoin(pageURL, href))
            if url.startswith("http") and UO.GetDomainFromURL(url) == site and not RE.JUNK_PATH_RE.search(urlparse(url).path):
                links.append((a, url))
    return links


def IsRich(a):
    """Determines whether an anchor element is 'rich' (i.e., likely representing a product card
    or detailed listing item by containing an embedded image, substantial link text, or a title attribute).

    Args:
        a: An lxml anchor element (`<a>`).

    Returns:
        bool: True if the link is rich, False otherwise.

    Examples:
        # Checks if a product grid link contains rich visual/textual data:
        if IsRich(anchor_element):
            print("Link represents a rich product card.")
    """
    return bool(a.xpath(".//img") or len(SO.TextOf(a)) >= 15 or len(a.get("title") or "") >= 10)


def CardLinks(doc, pageURL):
    """Extracts and identifies product card listing links from a catalog or search page
    by analyzing price element positions, DOM hierarchy, link distribution, and card recurrence patterns.

    Args:
        doc: The parsed HTML document tree (e.g., lxml element).
        pageURL (str): The absolute URL of the listing page.

    Returns:
        list[str]: A list of primary product URLs extracted from identified product cards.

    Examples:
        # Extracts product links from all product cards on a search results page:
        product_urls = CardLinks(parsed_doc, "https://store.com/search?q=laptop")
    """
    body = doc.find("body") if doc.find("body") is not None else doc
    site, cache = UO.GetDomainFromURL(pageURL), {}

    def linksOf(el):
        if el not in cache:
            cache[el] = SiteLinks(el, pageURL, site)
        return cache[el]

    def richKeys(links):
        return {UO.CleanSortURL(u) for a, u in links if IsRich(a)}

    bases = []
    for el, _ in DP.PriceCandidates(body):
        node = el
        for _ in range(12):
            node = node.getparent()
            if node is None or node.tag in ("body", "html"):
                break
            links = linksOf(node)
            if links:
                if len(richKeys(links)) <= 1 and not node.xpath(".//h1"):
                    bases.append((node, UO.CleanSortURL(UO.PrimaryLink(links))))
                break

    keysUnder = {}
    for base, key in bases:
        node = base
        for _ in range(8):
            if node is None:
                break
            keysUnder.setdefault(node, set()).add(key)
            node = node.getparent()

    cards = []
    for base, key in bases:
        card = base
        for _ in range(6):
            parent = card.getparent()
            if parent is None or parent.tag in ("body", "html") or len(keysUnder.get(parent, ())) > 1 or \
                    len(richKeys(linksOf(parent))) > 1 or len(parent.text_content()) > 2500:
                break
            card = parent
        if card not in cards:
            cards.append(card)

    shapes = {}
    for card in cards:
        shape = (card.tag, frozenset(c for c in (card.get("class") or "").split() if not re.search(r"\d", c)))
        shapes[shape] = shapes.get(shape, 0) + 1

    repeated = any(n >= 2 for n in shapes.values())
    return [UO.PrimaryLink(linksOf(card)) for card in cards
            if not repeated or shapes[(card.tag, frozenset(c for c in (card.get("class") or "").split()
                                                           if not re.search(r"\d", c)))] >= 2]
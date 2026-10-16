import json
import asyncio
import re

from lxml import etree
from urllib.parse import urlparse, urljoin

from src.Core import Settings
from src.Core.DataAcquisition.ProcessingAndExtracting import ProductPage
from src.Core.DataAnalysis import RelevanceAnalysis as RA

from src.Constants import Constants
from src.Constants import StringConstants as SC
from src.Constants import RegexConstants as RE

from src.Operations import StringOperations as SO
from src.Operations import ThreadOperations as TO
from src.Operations import HTMLOperations as HO
from src.Operations import URLOperations as UO
from src.Operations import JsonOperations as JO


async def MoreReviews(fetcher, store, pdpURL, page, data, reviews):
    """Asynchronously fetches additional product reviews beyond those present on the
       initial product detail page, handling multi-page review pagination or fallback
       JavaScript/API review fetching.

    Args:
        fetcher: The network/browser fetching utility instance.
        store (dict): Metadata dictionary containing store configuration (e.g., 'reviewApi').
        pdpURL (str): The target product detail page URL.
        page (dict): The current page dictionary containing metadata like URL and transport method.
        data (dict): Parsed product dictionary containing review links and identification attributes.
        reviews (list): Mutable list where newly collected reviews are appended in-place.

    Fetches secondary review pages or triggers JS/API review requests if initial reviews are empty:
    await MoreReviews(fetcher, store, pdpURL, page, data, reviews)
    """
    if data["reviewLinks"]:
        await ProductPage.CollectReviewPages(fetcher, data["reviewLinks"][0], page["url"], reviews)

    httpMode = fetcher.httpRequestor is not None and UO.GetDomainFromURL(pdpURL) not in fetcher.browserOnly

    if not reviews and httpMode:
        # Fallback: If raw collection yielded no reviews, attempt fetching via store review API or browser target
        target = data["reviewLinks"][0] if data["reviewLinks"] else (pdpURL if page["via"] == "http" else None)
        if target:
            await ProductPage.JsReviews(fetcher, store["reviewApi"], target, data["ids"], reviews)


async def ProcessProduct(fetcher, store, index, pdpURL, listingURL, progress):
    """Asynchronously processes an individual product detail page (PDP), handling
    initial fetching, client-side JavaScript rendering fallback, deep review pagination
    with timeout safety, and structuring the final product record.

    Args:
        fetcher: The network/browser fetching utility instance.
        store (dict): Metadata dictionary containing store configuration and results list.
        index (int): Sequential index of the product for ordering.
        pdpURL (str): The target product detail page URL.
        listingURL (str): The originating listing page URL used as a referer.
        progress (dict): Shared dictionary tracking overall scraping metrics and totals.

    Examples:
        # After successful extraction and processing, the product data is
        # appended to store["results"] along with its index:

        # store["results"] layout:
        # [
        #     (1, {
        #         "storeName": "TechStore",
        #         "productName": "Wireless Gaming Mouse",
        #         "price": "$49.99",
        #         "rating": 4.6,
        #         "imageURL": "https://store.com/images/mouse.jpg",
        #         "productURL": "https://store.com/item/123",
        #         "ratingAmount": 128,
        #         "reviews": ["Great battery life!", "Very responsive."]
        #     })
        # ]
    """
    try:
        # Prioritize new product requests behind active review loads to manage queue flow
        page = await fetcher.get(pdpURL, referer=listingURL, renderOptions={"navigate": True, "openReviews": True}, priority=Constants.NEXT)

        if not page["html"] or page["blocked"] or page["status"] >= 400:
            reason = page.get("error") or ("blocked by the store" if page["blocked"] else f"HTTP {page['status']}")
            print(f"  -> Error processing product page {pdpURL}: {reason}")
            return
        data = await TO.ParallelDispatch(ProductPage.ExtractProductPage, page["html"], page["url"], page["json"])

        # Fallback: If raw HTTP missed key attributes due to dynamic JS rendering, escalate to a browser fetch
        if page["via"] == "http" and not (data["price"] and (data["productName"] or data["pageTitle"])) and \
                not fetcher.browserFailed:
            rendered = await fetcher.FetchDataThroughBrowser(pdpURL, navigate=True, openReviews=True)
            if rendered["html"] and not rendered["blocked"]:
                more = await TO.ParallelDispatch(ProductPage.ExtractProductPage, rendered["html"], rendered["url"], rendered["json"])
                for key in ("productName", "price", "rating", "ratingAmount", "imageURL", "pageTitle"):
                    if data[key] in (None, ""):
                        data[key] = more[key]
                SO.MergeReviews(data["reviews"], more["reviews"])
                data["reviewLinks"] = data["reviewLinks"] or more["reviewLinks"]
                page = rendered

        # Products whose name clearly does not match the query will be
        # filtered out later anyway, so their (expensive) review crawling is
        # skipped here - this is what keeps flooded searches fast. The check
        # runs only AFTER the browser fallback above, so the names it reads
        # are the best ones we have.
        query = store.get("query", "")
        relevant = RA.ProductRelevance(query, data["productName"] or data["pageTitle"] or "") if query else 1.0

        reviews = data["reviews"] if Settings.GET_REVIEWS else []
        if relevant > 0 and Settings.GET_REVIEWS and Settings.MAX_REVIEW_PAGES != 0 and data["ratingAmount"] != 0:
            try:
                # Impose a strict time limit on review pagination; timeout is caught to preserve partial results
                await asyncio.wait_for(MoreReviews(fetcher, store, pdpURL, page, data, reviews), Settings.PRODUCT_TIME_LIMIT)
            except asyncio.TimeoutError:
                pass

        productData = {
            "storeName": data["storeName"],
            "productName": data["productName"] or data["pageTitle"] or "N/A",
            "price": data["price"] or "N/A",
            "rating": data["rating"] if data["rating"] is not None else "N/A",
            "imageURL": data["imageURL"] or "N/A",
            "productURL": UO.CleanURL(page["url"]),
            "ratingAmount": data["ratingAmount"] if data["ratingAmount"] is not None else "N/A",
            "reviews": list(reviews),
        }
        store["results"].append((index, productData))
        progress["done"] += 1

        if Settings.VERBOSE:
            print(f"=== Processed Product {progress['done']}/{progress['total']} ({store['domain']}) ===")
            print(json.dumps(productData, indent=4, ensure_ascii=False))
            print("-" * 50)
        #else:
            #print(f"[{progress['done']}/{progress['total']}] {store['domain']}: {productData['price']} | "
                  #f"{len(reviews)} reviews | {productData['productName'][:70]}")

    except Exception as e:
        print(f"  -> Error processing product page {pdpURL}: {type(e).__name__}: {e}")


def ExtractMetaTags(doc):
    """Extracts and maps all HTML meta tags from a parsed document tree into a dictionary,
    using property, name, or itemprop attributes as normalized lowercase keys and their
    corresponding content as values.

    Args:
        doc: The parsed HTML document tree (lxml element).

    Returns:
        dict[str, str]: A dictionary mapping normalized meta property/name/itemprop keys to their content values.

    Examples:
        # Extracts OpenGraph and standard meta tags into a lookup dictionary:
        metas = metaTags(parsed_doc)
        description = metas.get("og:description") or metas.get("description")
    """
    metas = {}
    for meta in doc.xpath("//meta[@content]"):
        key = (meta.get("property") or meta.get("name") or meta.get("itemprop") or "").strip().lower()
        if key and key not in metas:
            metas[key] = meta.get("content")
    return metas

def IsPriceWord(el):
    """Determines whether an HTML element exhibits semantic traits, classes, or attributes
        associated with pricing (supporting both English 'price' and Turkish 'fiyat' terminology,
        as well as predefined price keyword sets).

        Args:
            el: The HTML element node (e.g., lxml element) to inspect.

        Returns:
            bool: True if the element matches price-related semantic keywords, False otherwise.

        Examples:
            # Checks if a price label span contains pricing semantics:
            span_el = parsed_doc.xpath('//span[@class="product-price"]')[0]
            if isPriceWord(span_el):
                print("Element is price-related!")
        """
    if el is None:
        return False

    semantic_tokens = HO.ExtractSemantic(el)
    return any(
        t in SC.PRICE_WORDS or "price" in t or "fiyat" in t
        for t in semantic_tokens
    )


def PriceWords(el):
    """Extracts semantic words and class-name tokens from an HTML element, automatically
    splitting joined compound forms containing 'price' (e.g., 'oldprice' yields both 'oldprice'
    and 'old', 'pricesale' yields 'sale') for robust semantic classification.

    Args:
        el: The HTML element node (e.g., lxml element) to inspect.

    Returns:
        set[str]: A set of semantic words and split token variations.

    Examples:
        # Extracts split price-related semantic tokens from an element class:
        tokens = PriceWords(price_element)
    """
    words = HO.ExtractSemantic(el)
    return words | {t[:-5] for t in words if t.endswith("price")} | {t[5:] for t in words if t.startswith("price")}


def IsOldPrice(el):
    """Determines whether an element or any of its ancestor nodes (up to 2 levels up)
    represent an old, discounted, or crossed-out price by evaluating HTML strike tags,
    CSS text-decoration styles, and semantic old-price vocabulary sets.

    Args:
        el: The HTML element node (e.g., lxml element) to inspect.

    Returns:
        bool: True if the element or its parent represents an old/slashed price, False otherwise.

    Examples:
        # Checks if a price span is wrapped in a deletion tag or has old-price styling:
        if IsOldPrice(span_element):
            print("This is the previous/original price.")
    """
    node = el
    for _ in range(3):
        if node is None:
            break
        words = PriceWords(node)
        if node.tag in ("del", "s", "strike") or "line-through" in (node.get("style") or "") or \
                {"line", "through"} <= words or words & SC.STRONG_OLD_WORDS or (words & SC.WEAK_OLD_WORDS and IsPriceWord(node)):
            return True
        node = node.getparent()
    return False


def PriceCandidates(root, start=None, accept=None, stopAfter=None):
    """Scans and extracts price candidates from an HTML document tree in page order,
    identifying short text nodes matching currency patterns or pricing semantics while
    filtering out long text blocks, non-price numbers, and crossed-out old prices.

    Args:
        root: The root HTML element tree (e.g., lxml element).
        start (optional): An element node to begin scanning from. Defaults to None.
        accept (callable, optional): A filter function taking an element and returning a boolean for acceptance. Defaults to None.
        stopAfter (int, optional): Number of valid current prices to process after the first non-crossed-out price before halting. Defaults to None.

    Returns:
        list[tuple[etree.Element, str]]: A list of tuples containing the price element and its formatted price string.

    Examples:
        # Extracts price candidates from an HTML document starting from a product container:
        prices = PriceCandidates(parsed_doc, start=product_element, stopAfter=3)
        for el, price_text in prices:
            print(price_text)
    """
    found, checked, ownTexts, since = {}, {}, {}, None
    for text, el in ProductPage.PageTexts(root, start):
        if not any(ch.isdigit() for ch in text) or (len(text) > 120 and len(text.strip()) > 60):
            continue  # A long text is never (part of) a price

        for _ in range(3):  # Inspect the text's element and up to 2 parents (handling prices split across <span>s)
            if el is None or not isinstance(el.tag, str) or el.tag in SC.SKIP_TAGS or el.tag in SC.BIG_TAGS or len(
                    el) > 8:
                break
            if el not in checked:
                value = SO.TextOf(el)
                checked[el] = len(value) > 60
                parent = el.getparent()

                if not checked[el] and "%" not in value and \
                        (RE.CURRENCY_RE.search(value) or IsPriceWord(el) or IsPriceWord(parent)):
                    numbers = SO.ExtractNumbersFromText(value)
                    if len(numbers) == 1 and numbers[0] > 0:
                        if parent is not None and parent not in ownTexts:  # Cache texts written directly in the parent
                            ownTexts[parent] = " ".join(t for t in [parent.text] + [c.tail for c in parent] if t)
                        if not RE.NOT_PRICE_RE.search(value + " " + (ownTexts[parent] if parent is not None else "")):
                            ok = accept is None or bool(accept(el))
                            found[el] = (value, numbers[0], ok)
                            if since is not None:
                                since += 1
                            elif ok and not IsOldPrice(el):
                                since = 0  # First current price: from here on, count subsequent prices

            if checked[el]:
                break
            el = el.getparent()

        if stopAfter and since is not None and since > stopAfter:
            break

    # Resolve duplicate or nested price elements (e.g., handling split currency symbols or side-by-side prices)
    drop = set()
    for el in found:
        for ancestor in list(el.iterancestors())[:3]:
            if ancestor not in found:
                continue
            (outer, outerNumber, _), (inner, innerNumber, _) = found[ancestor], found[el]
            if inner in outer:
                extra = RE.CURRENCY_RE.sub("", outer.replace(inner, " ", 1))
                if any(ch.isalpha() for ch in extra) and (RE.CURRENCY_RE.search(inner) or HOLDS_NAME(ancestor)):
                    drop.add(ancestor)
                elif any(ch.isdigit() for ch in extra) and RE.CURRENCY_RE.search(inner) and \
                        int(outerNumber) != int(innerNumber):  # A whole price next to other digits
                    drop.add(ancestor)
                else:
                    drop.add(el)
            elif outerNumber == innerNumber:
                drop.add(el)

    return [(el, value) for el, (value, number, ok) in found.items() if ok and el not in drop]


HOLDS_NAME = etree.XPath("boolean(.//a[normalize-space()] | .//h1 | .//h2 | .//h3 | .//h4 | .//h5 | .//h6)")




def VisibleText(el):
    """Extracts and cleans all visible text visible to a visitor within an HTML
    element, automatically stripping out hidden elements and invisible tags like
    scripts and stylesheets.

    Args:
        el: The HTML element node (e.g., lxml element).

    Returns:
        str: The cleaned visible text string.

    Examples:
        # Extracts visible text from a product description container:
        text = visibleText(description_element)
    """
    out = []

    def walk(node):
        if node.text:
            out.append(node.text)
        for child in node:
            if isinstance(child.tag, str) and child.tag not in SC.INVISIBLE_TAGS and not HO.IsHidden(child):
                walk(child)
            if child.tail:
                out.append(child.tail)

    walk(el)
    return SO.Clean(" ".join(out)) or ""





def ReviewBody(item):
    """Extracts the primary review body opinion text from an individual review card container,
    preferring explicitly labeled review body elements or falling back to the longest valid opinion text.

    Args:
        item: The HTML review card element node (e.g., lxml element).

    Returns:
        str | None: The extracted review body text, or None if no valid review opinion is found.

    Examples:
        # Extracts review body text from a single review card:
        review_text = reviewBody(review_card_element)
    """
    candidates = []
    for el in item.iterdescendants():
        if not isinstance(el.tag, str) or el.tag in SC.REVIEW_SKIP_TAGS:
            continue
        names = SO.NameWords(el)
        itemprop = (el.get("itemprop") or "").lower()
        isBody = any(w & SC.REVIEW_BODY_WORDS and not w & SC.REVIEW_PART_WORDS for w in names)
        if not (isBody or itemprop in ("reviewbody", "description")) or \
                any(w & SC.REVIEW_PART_WORDS and not w & SC.REVIEW_BODY_WORDS for w in names):
            continue
        if HO.IsHidden(el) or any(HO.IsHidden(a) or a.tag in SC.REVIEW_SKIP_TAGS or
                                  any(w & SC.REVIEW_PART_WORDS and not w & SC.REVIEW_BODY_WORDS for w in
                                      SO.NameWords(a))
                                  for a in el.iterancestors() if a is not item and item in a.iterancestors()):
            continue
        text = VisibleText(el)
        if SO.IsOpinionText(text):
            score = (
                    6 * (itemprop in ("reviewbody", "description")) +
                    3 * isBody +
                    2 * any(w & SC.REVIEW_WORDS and w & SC.REVIEW_BODY_WORDS for w in names)
            )
            candidates.append((score, el, text))

    inner = {el for _, el, _ in candidates}
    # A wrapper around another text element is not the text itself (e.g., body + its "Read more" button)
    leaves = [c for c in candidates if not any(d in inner for d in c[1].iterdescendants())]
    if leaves:
        return max(leaves, key=lambda c: (c[0], len(c[2])))[2]

    # Fallback when nothing is explicitly labeled: find the longest text in the card that is not a title, name, date, or button
    best = ""
    for el in item.iter():
        if not isinstance(el.tag, str) or el.tag in SC.REVIEW_SKIP_TAGS or el.tag in SC.INVISIBLE_TAGS:
            continue
        own = SO.Clean(" ".join(t for t in [el.text] + [c.tail for c in el] if t)) or ""
        if len(own) > len(best) and SO.IsOpinionText(own) and not any(
                HO.IsHidden(a) or a.tag in SC.REVIEW_SKIP_TAGS or any(w & SC.REVIEW_PART_WORDS for w in SO.NameWords(a))
                for a in [el] + [x for x in el.iterancestors() if item in x.iterancestors()]):
            best = own

    return best or None


def DOMReviews(doc):
    """Extracts all product reviews and user opinions from an HTML document tree using
    DOM review card heuristics, microdata annotations, and semantic attribute analysis,
    while filtering out ads, boilerplate sections, and non-opinion text.

    Args:
        doc: The parsed HTML document tree (e.g., lxml element).

    Returns:
        list[str]: A deduplicated, merged list of clean review opinion text strings.

    Examples:
        # Extracts all product reviews from an HTML review page:
        reviews = DOMReviews(parsed_doc)
        for review in reviews:
            print("-", review)
    """
    body = doc.find("body") if doc.find("body") is not None else doc

    def isReviewCard(el):
        """Checks whether an element qualifies as a distinct review card container."""
        itemtype = (el.get("itemtype") or "").lower()
        if (el.get("itemprop") or "").lower() == "review" or itemtype.endswith("/review"):
            return True
        names = SO.ElementNames(el)
        return bool(names) and bool(RE.REVIEW_HINT_RE.search(" ".join(names))) and \
            any(SO.NameKind(SO.SplitName(n)) == "card" for n in names)

    def badPlace(el):
        """Determines if an element is located within a form, header, footer, nav, or ad block."""
        return any(a.tag in ("form", "header", "footer", "nav") or any(w & SC.AD_WORDS for w in SO.NameWords(a))
                   for a in [el] + list(el.iterancestors()))

    def signature(el):
        """Returns a signature (tag and class set) for identifying repeated review cards in lists."""
        return el.tag, frozenset((el.get("class") or "").split())

    # Single efficient pass over the page to locate elements referencing reviews
    hinted = []
    for el in body.iter():
        if isinstance(el.tag, str) and el.tag not in SC.REVIEW_SKIP_TAGS and (
                (el.get("itemprop") or "").lower() in ("review", "reviewbody") or
                (el.get("itemtype") or "").lower().endswith("/review") or
                RE.REVIEW_HINT_RE.search(" ".join(SO.ElementNames(el)))):
            hinted.append(el)

    cards = [el for el in hinted if isReviewCard(el)]
    cardSet = set(cards)
    parentCard = {el: next((a for a in el.iterancestors() if a in cardSet), None) for el in cards}
    subCards = {}
    for el, parent in parentCard.items():
        if parent is not None:
            subCards.setdefault(parent, []).append(el)

    def reviewsIn(card):
        """Recursively extracts individual review items or containers holding multiple review cards."""
        repeated = [c for c in subCards.get(card, [])
                    if sum(signature(x) == signature(c) for x in subCards.get(card, [])) >= 2]
        return [r for c in repeated for r in reviewsIn(c)] if repeated else [card]

    items = [r for el in cards if parentCard[el] is None for r in reviewsIn(el) if not badPlace(r)]
    texts = [ReviewBody(item) for item in items]

    # Fallback: capture loose review texts not enclosed in a recognized card (e.g., itemprop="reviewBody")
    itemSet = set(items)
    loose = []
    for el in hinted:
        strong = (el.get("itemprop") or "").lower() == "reviewbody" or \
                 any(SO.NameKind(words) == "body" and set(words) & SC.REVIEW_WORDS and set(words) & SC.STRONG_BODY_WORDS
                     for words in SO.NameTokens(el))
        if strong and not any(a in itemSet for a in el.iterancestors()) and el not in itemSet and \
                not badPlace(el) and not any(HO.IsHidden(a) for a in [el] + list(el.iterancestors())[:6]):
            loose.append(el)

    looseSet = set(loose)
    for el in loose:
        if not any(d in looseSet for d in el.iterdescendants()):
            texts.append(VisibleText(el))

    return SO.MergeReviews([], [t for t in texts if SO.IsOpinionText(t)])


def IsCounterText(text):
    """Determines whether a text string represents a rating/review widget count or
    summary (e.g., '2.345 değerlendirme', '(87)', '4,6 out of 5') rather than an actual review opinion.

    Args:
        text (str): The text string to evaluate.

    Returns:
        bool: True if the text is a counter or rating widget, False otherwise.

    Examples:
        # Filters out rating counts from review candidates:
        if IsCounterText("(87)"):
            `print(`"Skipping count widget.")
    """
    return len(text) <= 40 and bool(
        RE.COUNT_TEXT_RE.fullmatch(text) or
        (re.search(r"\d", text) and RE.RATING_TEXT_RE.search(text) and len(text.split()) <= 6)
    )


def ReviewPageLinks(doc, pageURL):
    """Extracts and returns a list of absolute URLs pointing to dedicated product review
    sub-pages by scanning anchor tags for review keywords, matching product IDs or slugs,
    and filtering out external domains or irrelevant links.

    Args:
        doc: The parsed HTML document tree (e.g., lxml element).
        pageURL (str): The absolute URL of the current product page.

    Returns:
        list[str]: A list of cleaned, verified review page URLs.

    Examples:
        # Discovers dedicated review pages for pagination crawling:
        review_links = ReviewPageLinks(parsed_doc, "https://store.com/item/123")
    """
    ids = list(UO.ExtractIDs(pageURL).values())
    slug = [s for s in urlparse(pageURL).path.split("/") if s][-1:] if urlparse(pageURL).path.strip("/") else []
    site, pageKey, links = UO.GetDomainFromURL(pageURL), UO.CleanSortURL(pageURL), []
    pageHasWord = bool(RE.REVIEW_LINK_RE.search(urlparse(pageURL).path))

    for href in doc.xpath("//a/@href"):
        href = href.strip()
        if not href or href.startswith(("#", "javascript:", "mailto:")) or \
                not (pageHasWord or RE.REVIEW_LINK_RE.search(href)):  # Quick skip: no review keywords present
            continue

        url = UO.CleanURL(urljoin(pageURL, href))
        tail = urlparse(url).path + "?" + urlparse(url).query

        if UO.GetDomainFromURL(url) != site or UO.CleanSortURL(url) == pageKey or not RE.REVIEW_LINK_RE.search(tail) \
                or RE.NOT_REVIEW_LINK_RE.search(tail):
            continue

        if (ids and any(i in url for i in ids)) or (not ids and slug and len(slug[0]) >= 5 and slug[0] in url):
            if url not in links:
                links.append(url)

    return links

def ExtractListingLinks(html, pageURL, captured=()):
    """Extracts all product listing detail links from a category, search, or catalog page.

    Args:
        html (str): The raw HTML content of the listing page.
        pageURL (str): The absolute URL of the listing page.
        captured (tuple, optional): Captured network payloads or embedded data items. Defaults to ().

    Returns:
        list[str]: A list of absolute product URLs discovered on the listing page.

    Examples:
        # Extracts product links from a search results page:
        links = ExtractListingLinks(html_content, "https://store.com/search?q=laptop")
    """
    doc = HO.ParseHTML(html)
    return ProductPage.ProductLinksFromListing(doc, pageURL, JO.EmbeddedJson(doc) + [item["data"] for item in captured])


def StoreNameOf(doc, metas, pageURL):
    """Extracts the primary store or brand name from OpenGraph/application meta tags,
    schema.org structured data (WebSite/Organization types), or falls back to capitalizing the domain name.

    Args:
        doc: The parsed HTML document tree (e.g., lxml element).
        metas (dict): A dictionary of extracted page meta tags.
        pageURL (str): The absolute URL of the page.

    Returns:
        str: The identified store name.

    Examples:
        # Determines the store name for a product page:
        store_name = StoreNameOf(doc, metas, "https://www.store.com/item/123")
    """
    name = SO.Clean(metas.get("og:site_name")) or SO.Clean(metas.get("application-name"))
    if not name:
        for block in JO.JsonLdBlocks(doc):
            for node in (block.get("@graph") or [block]) if isinstance(block, dict) else \
                    (block if isinstance(block, list) else []):
                if isinstance(node, dict) and ProductPage.SchemaTypes(node) & SC.STORE_TYPES and SO.Clean(
                        node.get("name")):
                    return SO.Clean(node.get("name"))

    if name:
        return name

    label = UO.GetDomainFromURL(pageURL).split(".")[0]
    return label.capitalize() if label else "E-Commerce Store"
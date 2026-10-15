import re
import asyncio

from urllib.parse import urlparse, parse_qsl, urlunparse, urlencode, urljoin
from lxml import etree

from src.Core.DataAcquisition.ProcessingAndExtracting import DataProcessing as DP

from src.Constants import StringConstants as SC
from src.Constants import RegexConstants as RE


from src.Operations import ThreadOperations as TO
from src.Operations import StringOperations as SO
from src.Operations import URLOperations as UO
from src.Operations import HTMLOperations as HO
from src.Operations import JsonOperations as JO
from src.Operations import MathOperations as MO

from src.Core import Settings

def NextPage(url, receivedCount):
    """Generates the URL for the next page of an API review request by incrementing
    pagination query parameters (such as page numbers or item offsets) based on
    the number of items received so far.

    Args:
        url (str): The current API request URL containing pagination query parameters.
        receivedCount (int): The number of items received in the current batch, used to
                             increment offset-based pagination.

    Returns:
        str | None: The updated URL for the next page, or None if no recognized pagination parameter is found.

    Examples:
        # Increments a page parameter by 1:
        NextPage("https://store.com/api/reviews?page=1", receivedCount=10)
        # Returns: "https://store.com/api/reviews?page=2"

        # Increments an offset parameter by receivedCount:
        NextPage("https://store.com/api/reviews?offset=0", receivedCount=15)
        # Returns: "https://store.com/api/reviews?offset=15"
    """
    parsed = urlparse(url)
    query = parse_qsl(parsed.query, keep_blank_values=True)

    # Iterate through query parameters to identify page or offset keys
    for i, (key, value) in enumerate(query):
        if value.isdigit() and key.lower() in SC.PAGE_PARAMS | SC.OFFSET_PARAMS:
            # Page params increment by 1; offset params increment by the number of items received
            step = 1 if key.lower() in SC.PAGE_PARAMS else max(receivedCount, 1)
            query[i] = (key, str(int(value) + step))
            return urlunparse(parsed._replace(query=urlencode(query)))

    return None


def AnnouncedTotals(data, received):
    """Extracts announced total item counts and page counts from API JSON response
    dictionaries (such as pagination metadata) using iterative traversal.

    Args:
        data (dict): The parsed JSON response dictionary containing potential metadata or pagination keys.
        received (int): The number of items already received or collected, used to validate minimum item counts.

    Returns:
        tuple[int | None, int | None]: A tuple of (items, pages), where each element is an integer count
                                      if discovered, or None if not present or invalid.

    Examples:
        # Extracts total items and pages from a pagination metadata structure:
        response_json = {"data": {"pagination": {"totalPages": 5, "totalItems": 120}}}
        totals, pages = AnnouncedTotals(response_json, received=20)
        # Returns: (120, 5)
    """
    items = pages = None
    stack = [data] if isinstance(data, dict) else []

    # Traverse the dictionary iteratively using a stack to find total/page keys
    while stack:
        node = stack.pop()
        for key, value in node.items():
            if isinstance(value, dict):
                stack.append(value)
            elif isinstance(value, int) and not isinstance(value, bool) and value > 0:
                key = str(key).lower()
                if key in SC.TOTAL_PAGE_KEYS and pages is None:
                    pages = value
                elif key in SC.TOTAL_ITEM_KEYS and items is None and value >= received:
                    items = value

    return items, pages


def PredictPages(currentURL, nextURL, count):
    """Predicts and generates URLs for subsequent paginated pages in advance when the
    pagination pattern follows a predictable sequence (e.g., query parameters like
    ?page=2 or path segments like /page/2), enabling concurrent pre-fetching.

    Args:
        currentURL (str): The URL of the current or first page.
        nextURL (str): The URL of the immediate next page used to detect the pattern.
        count (int): The maximum number of subsequent page URLs to generate.

    Returns:
        list[str]: A list of Predicted URLs for upcoming pages, or an empty list if no pattern is detected.

    Examples:
        # Given currentURL ending in ?page=1 and nextURL ending in ?page=2, predicts 3 pages ahead:
        predictPages("https://store.com/items?page=1", "https://store.com/items?page=2", 3)
        # Returns: [
        #     "https://store.com/items?page=2",
        #     "https://store.com/items?page=3",
        #     "https://store.com/items?page=4"
        # ]
    """
    a, b = urlparse(currentURL), urlparse(nextURL)
    if a.netloc != b.netloc or count < 1:
        return []

    qa, qb = dict(parse_qsl(a.query)), parse_qsl(b.query)

    # Handle query-parameter based pagination (e.g., ?page=2, ?start=20)
    if a.path == b.path:
        for i, (key, value) in enumerate(qb):
            others = all(qa.get(k) == v for k, v in qb if k != key)
            previous = qa.get(key)
            if value.isdigit() and others and previous != value and (previous is None or previous.isdigit()):
                start = int(value)
                step = start - int(previous) if previous is not None else (1 if start == 2 else start)
                if step <= 0:
                    return []
                urls = []
                for k in range(count):
                    query = list(qb)
                    query[i] = (key, str(start + k * step))
                    urls.append(urlunparse(b._replace(query=urlencode(query))))
                return urls
        return []

    # Handle path-segment based pagination (e.g., /page/2, /page/3)
    pageInPath = re.match(r"^(.*?/page[/=-]?)(\d+)(/?)$", b.path)
    if a.query == b.query and pageInPath and pageInPath.group(2) == "2" and \
            re.sub(r"/page[/=-]?\d+/?$", "", a.path).rstrip("/") == \
            pageInPath.group(1).rstrip("/=-").rsplit("/page", 1)[0].rstrip("/"):
        return [urlunparse(b._replace(path=f"{pageInPath.group(1)}{2 + k}{pageInPath.group(3)}")) for k in range(count)]

    return []



def SchemaTypes(node):
    """Extracts and normalizes all Schema.org types from a JSON-LD node dictionary,
    stripping URI prefixes or namespaces and converting them to lowercase lowercase sets.

    Args:
        node (dict): A Schema.org JSON-LD data node dictionary.

    Returns:
        set[str]: A set of normalized, lowercase schema type strings (e.g., {"product", "review"}).

    Examples:
        # Extracts normalized types from a schema node:
        node = {"@type": ["https://schema.org/Product", "Review"]}
        types = SchemaTypes(node)
        # Returns: {"product", "review"}
    """
    t = node.get("@type")
    # Normalize '@type' value into a list whether it's a single string, a list of strings, or missing
    t = [t] if isinstance(t, str) else t if isinstance(t, list) else []

    # Strip URL bases/namespaces (e.g., 'http://schema.org/Product' -> 'Product') and lowercase
    return {str(x).rsplit("/", 1)[-1].rsplit(":", 1)[-1].lower() for x in t if x}


def SchemaNodes(data, depth=0):
    """Recursively yields all valid Schema.org JSON-LD objects from a parsed data structure
    up to a maximum recursion depth, pruning irrelevant branches such as navigation elements,
    breadcrumbs, and related products.

    Args:
        data (dict | list): The parsed JSON-LD data structure or node.
        depth (int, optional): The current recursion depth used to prevent stack overflows. Defaults to 0.

    Yields:
        dict: Valid Schema.org data nodes encountered during traversal.

    Examples:
        # Yields all valid schema nodes from a parsed JSON-LD block:
        for node in SchemaNodes(json_ld_data):
            print(SchemaTypes(node))
    """
    if depth > 15:
        return

    if isinstance(data, list):
        for item in data:
            yield from SchemaNodes(item, depth + 1)
    elif isinstance(data, dict):
        # Skip breadcrumbs and site navigation elements to focus on primary content
        if SchemaTypes(data) & {"breadcrumblist", "sitenavigationelement"}:
            return

        yield data

        # Recurse into nested dictionaries and lists while skipping unrelated product keys
        for key, value in data.items():
            if key not in SC.RELATED_KEYS and isinstance(value, (dict, list)):
                yield from SchemaNodes(value, depth + 1)



def SchemaProducts(doc):
    """Extracts all product schema objects and HTML5 microdata product items from a
    parsed HTML document, filtering out irrelevant related items.

    Args:
        doc: The parsed HTML document tree (e.g., lxml element).

    Returns:
        list[dict]: A list of dictionaries representing extracted product schema nodes and microdata items.

    Examples:
        # Extracts all product schemas and microdata from an HTML document:
        products = SchemaProducts(parsed_doc)
        for product in products:
            print(product.get("@type"))
    """
    products = [n for n in SchemaNodes(JO.JsonLdBlocks(doc)) if
                SchemaTypes(n) & SC.PRODUCT_TYPES]

    # Extract microdata products from elements marked with itemscope and Product itemtype
    for scope in doc.xpath('//*[@itemscope][contains(@itemtype,"Product") or contains(@itemtype,"product")]'):
        if not set((scope.get("itemprop") or "").split()) & SC.RELATED_KEYS:
            products.append(HO.MicrodataItem(scope))

    return products


def SchemaPrice(node, depth=0):
    """Extracts and formats product pricing and currency information (e.g., '49999.00 TRY')
    from Schema.org product nodes, supporting direct pricing, offers, AggregateOffers,
    price specifications, and product variants.

    Args:
        node (dict): A Schema.org product or offer node dictionary.
        depth (int, optional): The current recursion depth used to limit variant traversal. Defaults to 0.

    Returns:
        str | None: A formatted price and currency string, or None if no valid price is found.

    Examples:
        # Extracts price from a product node with an offer:
        product_node = {
            "@type": "Product",
            "offers": {"price": "49999.00", "priceCurrency": "TRY"}
        }
        price_str = SchemaPrice(product_node)
        # Returns: "49999.00 TRY"
    """
    offers = node.get("offers")
    # Fallback: if offers are missing but price exists directly on the node, treat node as its own offer
    if not isinstance(offers, (dict, list)) and node.get("price") not in (None, ""):
        offers = node

    flat = []
    # Flatten offer structures (handling single offers, lists, and nested AggregateOffers)
    for offer in offers if isinstance(offers, list) else [offers]:
        if isinstance(offer, dict):
            flat.append(offer)
            inner = offer.get("offers")
            flat.extend(o for o in (inner if isinstance(inner, list) else [inner]) if isinstance(o, dict))

    # Iterate through flattened offers to extract price and currency
    for offer in flat:
        value = offer.get("price") if offer.get("price") not in (None, "") else offer.get("lowPrice")
        currency = SO.Clean(offer.get("priceCurrency"))
        specs = offer.get("priceSpecification")

        # Check price specifications if direct price is missing
        for spec in specs if isinstance(specs, list) else [specs]:
            if value in (None, "") and isinstance(spec, dict) and spec.get("price") not in (None, "") and \
                    not re.search(r"strikethrough|listprice|msrp", str(spec.get("priceType", "")), re.I):
                value, currency = spec.get("price"), currency or SO.Clean(spec.get("priceCurrency"))

        if value not in (None, "") and not isinstance(value, (dict, list)):
            return f"{SO.Clean(value)} {currency or ''}".strip()

    # Fallback: recursively search through product variants if allowed by depth limit
    variants = node.get("hasVariant")
    for variant in (variants if isinstance(variants, list) else [variants]) if depth < 2 else []:
        if isinstance(variant, dict):
            price = SchemaPrice(variant, depth + 1)
            if price:
                return price

    return None


def SchemaReviews(value):
    """Extracts and cleans review text strings from Schema.org Review objects,
    dictionaries, or lists of reviews by checking common text fields (`reviewBody`,
    `description`, `text`, or `name`).

    Args:
        value: A single Schema.org review dictionary, raw review string, or a list of review objects/strings.

    Returns:
        list[str]: A list of cleaned review text strings.

    Examples:
        # Extracts text from a Schema.org review dictionary:
        review_node = {"@type": "Review", "reviewBody": "Great product!", "author": "John"}
        texts = SchemaReviews(review_node)
        # Returns: ["Great product!"]
    """
    texts = []
    # Normalize input to always iterate over a list of review items
    for review in value if isinstance(value, list) else [value]:
        if isinstance(review, dict):
            # Fallback across common schema review text keys
            text = (SO.Clean(review.get("reviewBody")) or
                    SO.Clean(review.get("description")) or
                    SO.Clean(review.get("text")) or
                    SO.Clean(review.get("name")))
        else:
            text = SO.Clean(review)

        if text:
            texts.append(text)

    return texts



def NextPageLink(doc, pageURL):
    """Finds and extracts the absolute URL for the 'next page' of a paginated review list
    from an HTML document using semantic attributes, link relations, and text matching
    (supporting both English and Turkish descriptors).

    Args:
        doc: The parsed HTML document tree
        pageURL (str): The URL of the current page, used for relative link resolution and path validation.

    Returns:
        str | None: The absolute URL pointing to the next review page, or None if no valid link is found.

    Examples:
        # Extracts the 'next page' URL from a parsed DOM tree:
        next_url = NextPageLink(parsed_doc, "https://store.com/item/reviews?page=1")
    """
    # Extract path pattern without digits to ensure pagination stays within the same structural path
    samePattern = re.sub(r"\d+", "", urlparse(pageURL).path.rstrip("/"))

    # Gather candidate hrefs from rel="next" links and anchor elements matching text or semantic hints
    hrefs = doc.xpath('//link[@rel="next"]/@href | //a[@rel="next"]/@href')
    hrefs += [a.get("href") for a in doc.xpath("//a[@href]")
              if RE.NEXT_TEXT_RE.match(SO.TextOf(a) or SO.Clean(a.get("aria-label")) or SO.Clean(a.get("title")) or "")
              or "next" in HO.ExtractSemantic(a) or "sonraki" in HO.ExtractSemantic(a)]

    for href in hrefs:
        href = (href or "").strip()
        if href and not href.startswith(("#", "javascript:")):
            url = UO.CleanURL(urljoin(pageURL, href))
            # Validate that the candidate URL differs from current and matches the pagination pattern structure
            if UO.CleanSortURL(url) != UO.CleanSortURL(pageURL) and re.sub(r"\d+", "", urlparse(url).path.rstrip(
                    "/")) == samePattern:
                return url

    return None



def SchemaReviews(value):
    """Extracts and cleans review text strings from Schema.org Review objects,
    dictionaries, or lists of reviews by checking common text fields (`reviewBody`,
    `description`, `text`, or `name`).

    Args:
        value: A single Schema.org review dictionary, raw review string, or a list of review objects/strings.

    Returns:
        list[str]: A list of cleaned review text strings.

    Examples:
        # Extracts text from a Schema.org review dictionary:
        review_node = {"@type": "Review", "reviewBody": "Great product!", "author": "John"}
        texts = SchemaReviews(review_node)
        # Returns: ["Great product!"]
    """
    texts = []
    # Normalize input to always iterate over a list of review items
    for review in value if isinstance(value, list) else [value]:
        if isinstance(review, dict):
            # Fallback across common schema review text keys
            text = (SO.Clean(review.get("reviewBody")) or
                    SO.Clean(review.get("description")) or
                    SO.Clean(review.get("text")) or
                    SO.Clean(review.get("name")))
        else:
            text = SO.Clean(review)

        if text:
            texts.append(text)

    return texts



def FromSchema(node, pageURL):
    variants = node.get("hasVariant") if isinstance(node.get("hasVariant"), list) else [node.get("hasVariant")]
    variant = next((v for v in variants if isinstance(v, dict)), {})
    data = {"productName": SO.Clean(node.get("name")),
            "imageURL": UO.FirstURL(node.get("image"), pageURL) or UO.FirstURL(variant.get("image"), pageURL),
            "price": SchemaPrice(node), "rating": None, "ratingAmount": None,
            "reviews": SchemaReviews(node.get("review") or node.get("reviews"))}
    rating = node.get("aggregateRating")
    rating = rating[0] if isinstance(rating, list) and rating else rating
    if isinstance(rating, dict):
        data["rating"] = MO.ConvertValueToMaxOf5(rating.get("ratingValue"), rating.get("bestRating"))
        data["ratingAmount"] = SO.GetCount(rating.get("ratingCount") if rating.get("ratingCount") not in (None, "")
                                          else rating.get("reviewCount"))
    return data


def LinkedPages(doc, pageURL, nextURL):
    """Discovers and extracts pagination links belonging to the same paginated list
    structure as the provided nextURL (e.g., '1 2 3 4 ... Next' page links).

    Args:
        doc: The parsed HTML document tree (e.g., lxml element).
        pageURL (str): The absolute URL of the current page.
        nextURL (str): The absolute URL of the next page, used as a structural pattern reference.

    Returns:
        list[str]: A sorted list of cleaned, unique pagination URLs matching the list shape.

    Examples:
        # Finds all accessible review list pagination pages:
        pagination_urls = LinkedPages(parsed_doc, "https://store.com/reviews", "https://store.com/reviews?page=2")
    """
    if not nextURL:
        return []

    shape = re.sub(r"\d+", "", urlparse(nextURL).path.rstrip("/"))
    keys = set()

    for href in doc.xpath("//a/@href"):
        href = href.strip()
        if href and not href.startswith(("#", "javascript:")):
            url = UO.CleanURL(urljoin(pageURL, href))
            if urlparse(url).netloc == urlparse(nextURL).netloc and \
                    re.sub(r"\d+", "", urlparse(url).path.rstrip("/")) == shape:
                keys.add(UO.CleanSortURL(url))

    return sorted(keys)


def ReviewsOnPage(html, pageURL, captured=()):
    """Extracts all product reviews and pagination metadata from a raw HTML document
    and captured JSON payloads, aggregating them from schema markup, DOM elements,
    and embedded JSON.

    Args:
        html (str): The raw HTML content of the page.
        pageURL (str): The URL of the current page, used as a reference for relative link resolution.
        captured (tuple/list, optional): Captured network/API JSON payloads containing auxiliary review data. Defaults to ().

    Returns:
        dict: A dictionary containing:
            - 'reviews' (list[str]): An aggregated list of unique extracted review texts.
            - 'next' (str | None): The resolved URL pointing to the next review page, if found.
            - 'linked' (list[str]): A list of all discovered pagination or linked review page URLs.

    Examples:
        # Extracts reviews and pagination links from an HTML page string:
        result = ReviewsOnPage(html_content, "https://store.com/item/reviews")
        print(result["reviews"])
        print(result["next"])
    """
    doc = HO.ParseHTML(html)
    reviews = []

    # Extract reviews from Schema.org JSON-LD blocks (Product types containing reviews or standalone review nodes)
    for node in SchemaNodes(JO.JsonLdBlocks(doc)):
        if SchemaTypes(node) & SC.PRODUCT_TYPES:
            SO.MergeReviews(reviews, SchemaReviews(node.get("review") or node.get("reviews")))
        elif "review" in SchemaTypes(node):
            SO.MergeReviews(reviews, SchemaReviews(node))

    # Extract reviews from standard schema products in the DOM
    for node in SchemaProducts(doc):
        SO.MergeReviews(reviews, SchemaReviews(node.get("review") or node.get("reviews")))

    # Extract reviews directly from DOM elements using store selectors
    SO.MergeReviews(reviews, DP.DOMReviews(doc))

    # Extract reviews from any embedded JSON scripts found in the document
    SO.MergeReviews(reviews, SO.GetReviewsFromJSONIfAny(JO.EmbeddedJson(doc)))

    # Extract reviews from any auxiliary captured network JSON items
    for item in captured:
        SO.MergeReviews(reviews, SO.GetReviewsFromJSONIfAny(item["data"]))

    # Determine the 'next page' pagination URL and all linked review pages
    nextURL = NextPageLink(doc, pageURL)

    return {
        "reviews": reviews,
        "next": nextURL,
        "linked": LinkedPages(doc, pageURL, nextURL)
    }


async def JsReviews(fetcher, api, url, ids, into):
    """Asynchronously fetches reviews that only appear after JavaScript execution or
    dynamic API requests. It first attempts using a learned API template, falling back
    to full browser rendering and pattern learning if necessary, with concurrency locks
    to handle simultaneous learning phases.

    Args:
        fetcher: The network/browser fetching utility instance.
        api (object): The API helper instance managing review endpoints, templates, and learning state.
        url (str): The target product page URL.
        ids (list/dict): Product identification attributes needed for API review queries.
        into (list): A mutable collection where collected review texts are merged in-place.

    Examples:
        # Fetches dynamic reviews via learned API template or falls back to browser rendering:
        await JsReviews(fetcher, store["reviewApi"], pdpURL, data["ids"], reviews)
    """
    # Wait if another product task is currently learning the review request pattern
    if api.learning is not None and not api.learning.is_set():
        await api.learning.wait()

        # Attempt fetching using a pre-established API template if available
    if api.template and await api.fetch(fetcher, ids, url, into):
        return

    # Skip browser rendering if browsers previously failed or the store consistently yields no reviews
    if fetcher.browserFailed or (api.renders >= 3 and api.rendersWithReviews == 0):
        return

    learner = api.learning is None
    if learner:
        api.learning = asyncio.Event()

    try:
        # Fall back to a full browser fetch to render dynamic content and capture review payloads
        page = await fetcher.FetchDataThroughBrowser(url, navigate=True, openReviews=True)
        api.renders += 1

        texts = (await TO.ParallelDispatch(ReviewsOnPage, page["html"], page["url"], page["json"]))["reviews"] \
            if page["html"] else []

        api.rendersWithReviews += bool(texts)
        SO.MergeReviews(into, texts)

        # If no template exists yet, attempt to learn API patterns from network/JSON responses
        if not api.template and api.LearnPatterns(page["json"], ids):
            await api.fetch(fetcher, ids, url, into)  # Fetch subsequent review pages using the newly learned request
    finally:
        if learner:
            api.learning.set()


async def CollectReviewPages(fetcher, firstURL, referer, into):
    """Asynchronously paginates through multiple pages of product reviews up to a configured
    maximum, fetching linked review pages concurrently in batches and then following sequential
    pagination links until no new reviews are found or limits are reached.

    Args:
        fetcher: The network/browser fetching utility instance.
        firstURL (str): The starting URL for the first page of reviews.
        referer (str): The originating product detail page URL used as a referer header.
        into (list): A mutable collection where all collected review texts are merged in-place.

    Collects all reviews across paginated review sections up to MAX_REVIEW_PAGES:
    await CollectReviewPages(fetcher, "https://store.com/item/reviews?page=1", "https://store.com/item/123", reviews)
    """
    found, limit = [], Settings.MAX_REVIEW_PAGES or 200

    async def ReadPage(url):
        page = await fetcher.get(url, referer=referer, renderOptions={"navigate": True, "openReviews": True})
        if not page["html"] or page["status"] >= 400:
            return None, None
        return page, await TO.ParallelDispatch(ReviewsOnPage, page["html"], page["url"], page["json"])

    def Add(result):  # True when the page brought new reviews
        before = len(found)
        texts = result["reviews"] if result else []
        SO.MergeReviews(found, texts)
        SO.MergeReviews(into, texts)
        return len(found) > before

    page, result = await ReadPage(firstURL)
    if not Add(result) or not result["next"] or limit <= 1:
        return

    read, visited, last = 1, {UO.CleanSortURL(firstURL), UO.CleanSortURL(page["url"])}, result
    linked = set(result["linked"]) | {UO.CleanSortURL(result["next"])}
    batch = []

    # Predict and gather concurrently linked review pages (e.g., page 2, 3, etc.)
    for url in PredictPages(page["url"], result["next"], limit - 1):
        if UO.CleanSortURL(url) not in linked:
            break
        batch.append(url)

    if batch:
        for url, (_, res) in zip(batch, await asyncio.gather(*(ReadPage(u) for u in batch))):
            read += 1
            visited.add(UO.CleanSortURL(url))
            if not Add(res):
                return  # A page without new reviews signals the end of valid pagination
            last = res

    # Follow any remaining subsequent pagination links sequentially
    url = last["next"]
    while url and UO.CleanSortURL(url) not in visited and read < limit:
        visited.add(UO.CleanSortURL(url))
        _, res = await ReadPage(url)
        read += 1
        if not Add(res):
            break
        url = res["next"]



def PageTexts(root, start=None):
    """Yields every text fragment in an HTML document tree in document order along with
    its associated element (starting from an optional 'start' element). Text fragments
    following inline elements (like currency symbols or icons) are correctly attributed
    to their parent container.

    Args:
        root: The root HTML element tree (e.g., lxml element).
        start (optional): An element node to begin traversal from. Defaults to None (starts from root).

    Yields:
        tuple[str, etree.Element]: A tuple containing the text string and its associated lxml Element.

    Examples:
        # Iterates through all text segments starting from a specific product container:
        for text, el in PageTexts(product_root, start_element):
            print(f"{el.tag}: {text}")
    """
    started = start is None
    for event, el in etree.iterwalk(root, events=("start", "end")):
        if event == "start":
            if not started:
                if el is not start:
                    continue
                started = True
            if el.text and isinstance(el.tag, str):
                yield el.text, el
        elif started and el.tail and el is not root:
            yield el.tail, el.getparent()


def PickPrice(candidates, lowestWins=False):
    """Selects the most accurate current product price from a list of price candidates,
    preferring active/current non-crossed-out prices, explicitly marked sale prices,
    or falling back to the first or lowest available price.

    Args:
        candidates (list[tuple[etree.Element, str]]): A list of tuples containing price elements and their string values.
        lowestWins (bool, optional): If True and multiple unmarked prices exist, selects the lowest price (useful for product cards containing old and new prices). Defaults to False.

    Returns:
        str | None: The selected price string, or None if no candidates are provided.

    Examples:
        # Selects the active current price from extracted candidates:
        active_price = PickPrice(price_candidates, lowestWins=True)
    """
    if not candidates:
        return None

    current = [c for c in candidates if not DP.IsOldPrice(c[0])] or candidates
    marked = [c for c in current if DP.PriceWords(c[0]) & SC.NOW_WORDS or
              (c[0].getparent() is not None and DP.PriceWords(c[0].getparent()) & SC.NOW_WORDS)]

    if marked:
        return marked[0][1]

    if lowestWins and len(current) > 1:  # Two unmarked prices in a card typically represent old price + new price
        return min(current, key=lambda c: SO.ExtractNumbersFromText(c[1])[0])[1]

    return current[0][1]


def RatingFromPage(root, skip=None):
    """Extracts product rating scores and review counts from HTML rating widgets, supporting
    aria-labels, star rating percentages, rating text values, and localized rating counts
    (compatible with English, Turkish, and multilingual patterns).

    Args:
        root: The root HTML element tree (e.g., lxml element).
        skip (callable, optional): A filter function taking an element and returning True to skip it. Defaults to None.

    Returns:
        tuple[float | None, int | None]: A tuple containing the normalized rating (out of 5) and the total review/rating count.

    Examples:
        # Extracts rating and review count from a product page tree:
        rating, review_count = RatingFromPage(parsed_doc)
        print(f"Rating: {rating}/5 ({review_count} reviews)")
    """
    rating = amount = None
    for el in root.iter():
        if not isinstance(el.tag, str) or el.tag in SC.SKIP_TAGS:
            continue

        words = HO.ExtractSemantic(el)
        isRating = any(t.startswith(SC.RATING_WORDS) or t.endswith(("rating", "stars")) for t in words) and \
                   "count" not in words  # 'rating-count' / 'ratingCount' designates the review count, not the score itself

        ratingHere = False
        if rating is None and isRating and not (skip and skip(el)):
            for value in (el.get("aria-label"), el.get("title"), el.get("data-rating"), el.get("data-value"),
                          el.get("content") if el.get("itemprop") == "ratingValue" else None):
                rating = MO.ConvertValueToMaxOf5(value) if value and re.search(r"\d", value) else None
                if rating is not None:
                    break

            if rating is None:
                width = re.search(r"width:\s*([\d.]+)%", el.get("style") or "")
                if width and 0 < float(width.group(1)) <= 100:
                    rating = round(float(width.group(1)) / 20, 2)

            if rating is None:
                value = SO.TextOf(el)
                if len(value) <= 40 and re.search(r"^\s*\d(?:[.,]\d{1,2})?\s*$|\d\s*(?:/|out of|von|sur|su|de|z|"
                                                  r"üzerinden|中)\s*\d|\d\s*\D{0,12}\s*(?:/|out of|üzerinden)", value):
                    rating = MO.ConvertValueToMaxOf5(value)

            if rating is None:  # E.g., '4,6' written next to star icons, with count in a child element: '4,6 (1.234)'
                own = SO.Clean(" ".join(t for t in [el.text] + [child.tail for child in el] if t)) or ""
                if re.fullmatch(r"\d[.,]\d{1,2}", own):
                    rating = MO.ConvertValueToMaxOf5(own)

            ratingHere = rating is not None

        # Extract the review count from count elements or rating elements whose text represents a count ('320 ratings')
        if amount is None and not ratingHere and (not isRating or RE.COUNT_NEAR_RE.search(SO.TextOf(el))):
            value = None
            if words & SC.COUNT_WORDS:  # E.g., '(1.234)', '87 reviews', 'Yorumlar (12)'
                text = SO.TextOf(el)
                numbers = SO.ExtractNumbersFromText(text)
                countName = bool(
                    words & {"count", "total"})  # 'review-count', 'ratingCount': any single number is valid
                value = text if numbers and len(text) <= 40 and "%" not in text and not RE.RATING_TEXT_RE.search(text) \
                                and not RE.DATE_RE.search(text) and (
                                            RE.COUNT_NEAR_RE.match(text) or len(numbers) == 1 and (
                                            countName or RE.BARE_COUNT_RE.fullmatch(text) or RE.COUNT_NEAR_RE.search(
                                        text))) else None
            elif len(el) == 0 and el.tag in ("span", "div", "a", "small", "p", "b", "strong"):
                match = RE.COUNT_TEXT_RE.fullmatch(SO.TextOf(el))
                value = (match.group(1) or match.group(2)) if match else None

            if value and not (skip and skip(el)):
                amount = SO.GetCount(value)

        if rating is not None and amount is not None:
            break

    return rating, amount


def InNoise(el):
    """Inside header/footer/menus or a 'related products' / 'recently viewed' block."""
    for node in [el] + list(el.iterancestors()):
        if node.tag in ("header", "footer", "nav") or HO.ExtractSemantic(node) & SC.NOISE_WORDS:
            return True
    return False


def BestImage(root, pageURL):
    """The main product image of a page region (main/zoom image first, thumbnails and logos last)."""
    best, bestScore = None, -99
    for img in root.xpath(".//img"):
        src = None
        for attr in ("data-old-hires", "data-zoom-image", "data-large", "data-full", "data-src", "data-original",
                     "data-lazy", "data-lazy-src", "src"):
            value = (img.get(attr) or "").strip()
            if value and not value.startswith("data:"):
                src = value
                break
        if not src and img.get("srcset"):
            src = img.get("srcset").split(",")[-1].strip().split(" ")[0]
        if not src or re.search(r"logo|icon|sprite|badge|placeholder|blank\.|spacer|transparent|loading|flag|"
                                r"payment|avatar|\.svg", src, re.I):
            continue
        words = set()  # the image's own names, short data-* values, and its 3 closest containers
        for k, v in img.attrib.items():
            if k.startswith("data-") and v and len(v) < 60 and "/" not in v:
                words |= {t for t in re.split(r"[\W_]+", RE.CAMEL_RE.sub(r"\1 \2", v).lower()) if t}
        for node in [img] + list(img.iterancestors())[:3]:
            words |= HO.ExtractSemantic(node)
        small = any(re.fullmatch(r"\d{1,2}|100", (img.get(a) or "").strip().replace("px", "")) for a in ("width", "height"))
        score = 3 * bool(words & SC.MAIN_IMAGE_WORDS) + \
            2 * any(img.get(a) for a in ("data-old-hires", "data-zoom-image", "data-large", "data-full")) - \
            3 * bool(words & SC.THUMB_IMAGE_WORDS) - 2 * small
        if score > bestScore:
            best, bestScore = urljoin(pageURL, src), score
    return best


def DOMProduct(doc, pageURL):
    """Extracts product details (title, price, rating, review count, and main image URL)
    from a product page lacking structured data (JSON-LD or microdata) by analyzing
    DOM structure, heading elements, document order, and visual/semantic regions.

    Args:
        doc: The parsed HTML document tree (e.g., lxml element).
        pageURL (str): The absolute URL of the page used for resolving relative image links.

    Returns:
        dict: A dictionary containing extracted product fields: 'productName', 'price',
              'rating', 'ratingAmount', and 'imageURL'.

    Examples:
        # Extracts product information purely from DOM heuristics:
        product_data = DOMProduct(parsed_doc, "https://store.com/item/123")
        print(product_data.get("productName"), product_data.get("price"))
    """
    body = doc.find("body") if doc.find("body") is not None else doc
    data = {"productName": None, "price": None, "rating": None, "ratingAmount": None, "imageURL": None}

    # Locate the primary product <h1> heading (ignoring boilerplate noise)
    h1 = next((h for h in body.iter("h1") if len(SO.TextOf(h)) >= 3 and not InNoise(h)), None)
    data["productName"] = SO.TextOf(h1) if h1 is not None else None

    # Establish document order map for element positioning
    order = {el: i for i, el in enumerate(body.iter())}
    start = order.get(h1, 0)

    # Search for price candidates appearing after the title, falling back to page-wide search if needed
    candidates = []
    if h1 is not None:  # The product price typically appears after its title
        candidates = DP.PriceCandidates(
            body,
            start=h1,
            accept=lambda el: order.get(el, 0) > start and not InNoise(el),
            stopAfter=40
        )

    if not candidates:  # Fallback: scan all valid prices on the page outside noise regions
        candidates = DP.PriceCandidates(body, accept=lambda el: not InNoise(el))

    candidates.sort(key=lambda c: order.get(c[0], 0))
    data["price"] = PickPrice(candidates[:8])

    # Define the bounding region for rating and image extraction around the title and price
    region = body
    if h1 is not None and candidates:  # Find the smallest ancestor element enclosing both title and price
        h1Ancestors = set(h1.iterancestors())
        region = next((a for a in candidates[0][0].iterancestors() if a in h1Ancestors), body)
    elif h1 is not None:  # Fallback if no price found: expand around title until sufficient text length
        region = h1.getparent()
        while region is not None and region.getparent() is not None and region.getparent().tag != "html" and \
                len(SO.TextOf(region)) < 300:
            region = region.getparent()
        region = region if region is not None else body

    if h1 is not None:
        data["rating"], data["ratingAmount"] = RatingFromPage(
            region, skip=lambda el: order.get(el, 0) < start or InNoise(el))

        holder = region
        for _ in range(3):  # Expand search upwards as image galleries are frequently siblings of the title/price block
            data["imageURL"] = BestImage(holder, pageURL)
            if data["imageURL"] or holder.getparent() is None or holder.getparent().tag in ("body", "html"):
                break
            holder = holder.getparent()

    return data


def ProductLinksFromListing(doc, pageURL, blocks):
    """Aggregates and extracts all product detail page URLs from a catalog or listing page
    using schema.org microdata, DOM product cards, embedded JSON objects, and structural pattern matching.

    Args:
        doc: The parsed HTML document tree (e.g., lxml element).
        pageURL (str): The absolute URL of the listing page.
        blocks (list): Embedded JSON blocks extracted from the page scripts.

    Returns:
        list[str]: A deduplicated list of absolute product URLs discovered on the page.

    Examples:
        # Extracts all product URLs from a category or search listing page:
        product_urls = ProductLinksFromListing(parsed_doc, "https://store.com/search", json_blocks)
    """
    site, pageKey, found = UO.GetDomainFromURL(pageURL), UO.CleanSortURL(pageURL), {}

    def add(url):
        if isinstance(url, str) and url.strip():
            url = UO.CleanURL(urljoin(pageURL, url.strip()))
            if url.startswith("http") and UO.GetDomainFromURL(url) == site and UO.CleanSortURL(url) != pageKey:
                found.setdefault(UO.CleanSortURL(url), url)

    # 1. Schema.org product lists and JSON-LD nodes
    for node in SchemaNodes(JO.JsonLdBlocks(doc)):
        types = SchemaTypes(node)
        item = node.get("item")
        if types & SC.PRODUCT_TYPES:
            add(node.get("url"))
        elif "listitem" in types:
            add((item.get("url") or item.get("@id")) if isinstance(item, dict) else (node.get("url") or item))

    # Microdata product scopes
    for scope in doc.xpath('//*[@itemscope][contains(@itemtype,"Product")]'):
        add(HO.MicrodataItem(scope).get("url"))

    # 2. Product cards (price + link association)
    for url in HO.CardLinks(doc, pageURL):
        add(url)

    # 3. Product objects embedded in page JSON blocks
    for url in JO.JsonProductLinks(blocks, pageURL):
        add(url)

    # 4. Fallback: repeated link pattern matching
    if not found:
        for url in UO.PatternLinks(doc, pageURL):
            add(url)

    return list(found.values())


def ExtractProductPage(html, pageURL, captured=()):
    """Extracts all comprehensive product details from a product page HTML document,
    including metadata, schema structured data, DOM fallback heuristics, reviews,
    review page pagination links, store names, and product identifiers.

    Args:
        html (str): The raw HTML content of the product page.
        pageURL (str): The absolute URL of the product page.
        captured (tuple, optional): Captured network payloads or embedded data items. Defaults to ().

    Returns:
        dict: A dictionary containing all extracted product fields ('productName', 'imageURL',
              'price', 'rating', 'ratingAmount', 'reviews', 'pageTitle', 'storeName', 'reviewLinks', 'ids').

    Examples:
        # Extracts full product details and reviews from a product page:
        product_info = ExtractProductPage(html_content, "https://store.com/item/123")
    """
    doc = HO.ParseHTML(html)
    metas = DP.ExtractMetaTags(doc)
    canonical = doc.xpath('//link[translate(@rel,"CANONICAL","canonical")="canonical"]/@href')
    keys = {UO.CleanSortURL(pageURL)} | ({UO.CleanSortURL(urljoin(pageURL, canonical[0]))} if canonical else set())
    products = SchemaProducts(doc)
    node = next(
        (n for n in products if isinstance(n.get("url"), str) and UO.CleanSortURL(urljoin(pageURL, n["url"])) in keys),
        None) or next((n for n in products if SchemaPrice(n)), None) or (products[0] if products else None)

    empty = {"productName": None, "imageURL": None, "price": None, "rating": None, "ratingAmount": None, "reviews": []}
    data = FromSchema(node, pageURL) if node else empty

    # Fill gaps using meta tags, then fallback to visible DOM heuristics
    if not data["imageURL"]:
        data["imageURL"] = UO.FirstURL(metas.get("og:image") or metas.get("og:image:secure_url") or
                                       metas.get("twitter:image"), pageURL)
    if not data["price"]:
        amount = metas.get("product:price:amount") or metas.get("og:price:amount") or metas.get(
            "product:sale_price:amount")
        currency = metas.get("product:price:currency") or metas.get("og:price:currency") or ""
        data["price"] = f"{SO.Clean(amount)} {SO.Clean(currency) or ''}".strip() if SO.Clean(amount) else None

    if any(data[k] in (None, "") for k in ("productName", "price", "rating", "ratingAmount", "imageURL")):
        dom = DOMProduct(doc, pageURL)
        for key in ("productName", "price", "rating", "ratingAmount", "imageURL"):
            if data[key] in (None, ""):
                data[key] = dom[key]

    data["productName"] = data["productName"] or SO.Clean(metas.get("og:title"))
    data["pageTitle"] = SO.Clean(doc.findtext(".//title"))  # Fallback name (browser tab title)

    # Aggregate reviews from schema, DOM, embedded JSON blocks, and captured data
    reviews = SO.MergeReviews(list(data["reviews"]), DP.DOMReviews(doc))
    SO.MergeReviews(reviews, SO.GetReviewsFromJSONIfAny(JO.EmbeddedJson(doc)))
    for item in captured:
        SO.MergeReviews(reviews, SO.GetReviewsFromJSONIfAny(item["data"]))
    data["reviews"] = reviews

    data["storeName"] = DP.StoreNameOf(doc, metas, pageURL)
    data["reviewLinks"] = DP.ReviewPageLinks(doc, pageURL)

    idKeys = ("sku", "productID", "productGroupID", "mpn", "gtin13", "gtin", "gtin12", "gtin8")
    variant = next((v for v in (node.get("hasVariant") if isinstance(node.get("hasVariant"), list) else
                                [node.get("hasVariant")]) if isinstance(v, dict)), {}) if node else {}
    data["ids"] = UO.ExtractIDs(pageURL, [(k, node.get(k)) for k in idKeys] + [("variant" + k, variant.get(k))
                                                                               for k in idKeys] if node else [])
    return data


def ReviewsOnPage(html, pageURL, captured=()):
    """Extracts all review opinions present on a given page (product page or dedicated review page)
    along with pagination links for subsequent review pages ('next' and 'linked').

    Args:
        html (str): The raw HTML content of the review page.
        pageURL (str): The absolute URL of the review page.
        captured (tuple, optional): Captured network payloads or embedded data items. Defaults to ().

    Returns:
        dict: A dictionary containing 'reviews' (list of review strings), 'next' (next page URL),
              and 'linked' (sorted list of matching pagination URLs).

    Examples:
        # Extracts reviews and pagination links from a product review page:
        review_data = ReviewsOnPage(html_content, "https://store.com/item/123/reviews")
    """
    doc = HO.ParseHTML(html)
    reviews = []

    for node in SchemaNodes(JO.JsonLdBlocks(doc)):
        if SchemaTypes(node) & SC.PRODUCT_TYPES:
            SO.MergeReviews(reviews, SchemaReviews(node.get("review") or node.get("reviews")))
        elif "review" in SchemaTypes(node):
            SO.MergeReviews(reviews, SchemaReviews(node))

    for node in SchemaProducts(doc):
        SO.MergeReviews(reviews, SchemaReviews(node.get("review") or node.get("reviews")))

    SO.MergeReviews(reviews, DP.DOMReviews(doc))
    SO.MergeReviews(reviews, SO.GetReviewsFromJSONIfAny(JO.EmbeddedJson(doc)))

    for item in captured:
        SO.MergeReviews(reviews, SO.GetReviewsFromJSONIfAny(item["data"]))

    nextURL = NextPageLink(doc, pageURL)
    return {"reviews": reviews, "next": nextURL, "linked": LinkedPages(doc, pageURL, nextURL)}
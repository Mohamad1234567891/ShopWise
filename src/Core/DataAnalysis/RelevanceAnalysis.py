"""Query-aware relevance filtering for product results.

ShopWise scrapes whatever the stores return for a search, and stores often
include accessories, bundles or other models next to the product the user
actually asked for. Those unrelated results crowd the list and distort the
price-based scoring in StatisticalAnalysis.

This module scores how well a product name matches the searched query and
drops ONLY the products that are clearly a different product:

- a model number of the query is missing ("iphone 17" vs "iphone 16 charger")
- a conflicting model number appears ("iphone 17" vs "iphone 16 ...")

There is deliberately NO list of words in any language:
- names are split into digit/letter runs ("12x" -> ["12", "x"]), so matching
  works for every script (Latin, Cyrillic, Arabic, CJK, ...) and for merged
  forms like "iphone17" as well as spaced forms like "12 X";
- accessory words are never banned - accessories are perfectly valid results
  when the user searches for one ("iphone 17 charger" matches itself exactly).

Products that pass this filter but have a very different price are separated
afterwards by the price-cluster logic in StatisticalAnalysis.AssignPoints.
"""

import re
import unicodedata

from src.Constants import Constants as C
from src.Constants import RegexConstants as RE


def NormalizeRuns(text):
    """Splits a name into alternating digit/letter runs, case- and
    accent-insensitive, for any script.

    "Apple İphone 17 Pro Max 256 GB" -> ["apple", "iphone", "17", "pro", "max", "256", "gb"]
    "Huawei MatePad 12 X"          -> ["huawei", "matepad", "12", "x"]
    "华为平板 12x"                  -> ["华为平板", "12", "x"]
    """
    if not isinstance(text, str):
        return []
    text = unicodedata.normalize("NFKD", text)                         # İ -> I + combining dot
    text = "".join(ch for ch in text if not unicodedata.combining(ch))   # remove accents
    text = text.casefold()

    runs = []
    for token in re.findall(r"[^\W_]+", text, re.UNICODE):  # words of any script
        runs.extend(re.findall(r"\d+|\D+", token))           # split into digit/letter runs
    return runs


def RunMatches(queryRun, productRun):
    """Does one query run match one product run?"""
    if queryRun == productRun:
        return True
    if queryRun.isdigit() or productRun.isdigit():
        return False  # numbers only match the exact same number
    if not RE.LATIN_CHAR_RE.search(queryRun):
        return queryRun in productRun  # non-Latin run: substring is enough
    return False


def IsVariantDigit(runs, index):
    """True when runs[index] is a size/capacity/power number such as '256' in
    '256 gb' (or '16' in '16 pro'), rather than a model number."""
    nxt = runs[index + 1] if index + 1 < len(runs) else ""
    if nxt in C.UNITS:
        return True
    # a short alphabetic run right after a number is usually an attribute
    # ("16 pro", "45 w", "256 гб") - not a different model
    return bool(nxt) and nxt.isalpha() and len(nxt) <= 4 and not any(ch.isdigit() for ch in nxt)


def ProductRelevance(query, productName):
    """Scores how likely 'productName' is the product the user searched for.

    1.0 = the name contains the whole query (in order);
    0.0 = a query model number is missing, or another model number appears.
    """
    queryRuns = NormalizeRuns(query)
    productRuns = NormalizeRuns(productName)
    if not queryRuns or not productRuns:
        return 0.0

    queryDigits = [run for run in queryRuns if run.isdigit()]

    # 1. every model number of the query must appear in the product name
    #    ("huawei matepad 12x" vs "huawei matepad 11.5")
    for number in queryDigits:
        if not any(run == number for run in productRuns if run.isdigit()):
            return 0.0

    # 2. a different model number in the title means another model
    #    ("iphone 17" vs "iphone 16 charger"). Sizes/powers/years are ignored.
    if queryDigits:
        for index, run in enumerate(productRuns):
            if (run.isdigit() and len(run) >= 2 and run not in queryDigits
                    and not RE.YEAR_RE.match(run) and not IsVariantDigit(productRuns, index)):
                return 0.0

    # 3. coverage: the share of query runs found, in order, in the product name
    matched = 0
    position = 0
    for run in queryRuns:
        foundAt = None
        for index in range(position, len(productRuns)):
            if RunMatches(run, productRuns[index]):
                foundAt = index
                break
        if foundAt is None:
            break
        matched += 1
        position = foundAt + 1

    if matched == 0:
        return 0.0
    return matched / len(queryRuns)


def FilterProducts(products, query, alternateQueries=()):
    """Removes only the products that clearly do not match the query.

    Conservative on purpose: hard mismatches (score 0) and names clearly
    below the best match in the batch are dropped; everything else is left
    for the price-cluster logic to judge. When the user searches for an
    accessory, the accessory is the best match and stays.

    alternateQueries: extra forms of the same query (e.g. a translation into
    the region's language). A product's relevance is the best score against
    ANY of the forms, so local names match even when the original query is
    in a different language."""
    if not products or not query or not query.strip():
        return products

    queries = [query] + [alt for alt in alternateQueries if alt and alt != query]

    scored = []
    for item in products:
        name = item.get("productName") or item.get("pageTitle") or ""
        relevance = max((ProductRelevance(singleQuery, name) for singleQuery in queries), default=0.0)
        item["relevance"] = relevance
        scored.append((relevance, item))

    if not scored:
        return products

    best = max(rel for rel, _ in scored)
    if best <= 0:
        # nothing matches the query at all: we cannot tell right from wrong,
        # so keep everything (never filter blindly)
        return products

    cutoff = max(0.5, 0.7 * best)
    return [item for rel, item in scored if rel >= cutoff]

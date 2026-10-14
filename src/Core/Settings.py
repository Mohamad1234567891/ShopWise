# ================================================================ SETTINGS
MAX_PRODUCTS = None  # None = every product found on the listing page
MAX_SEARCH_RESULTS = 7  # Maximum Results From querying DuckDuckGo
GET_REVIEWS = (
    True  # False = skip reviews entirely (fastest: product data only)
)
MAX_REVIEW_PAGES = (
    5  # review pages read per product (None = all of them; slower on big products)
)
HTTP_PER_STORE = (
    6  # downloads at the same time on one store (6 = what Chrome does)
)
BROWSER_TABS = 4  # browser tabs running at the same time
REQUEST_TIMEOUT = 20  # seconds per download
PRODUCT_TIME_LIMIT = 60  # seconds for one product's reviews
VERBOSE = False  # print every product as JSON while running
##########################################################################################################################

_NOT_GIVEN = object()


def UpdateSettings(
    maxProducts=_NOT_GIVEN,
    maxSearchResults=_NOT_GIVEN,
    getReviews=_NOT_GIVEN,
    maxReviewPages=_NOT_GIVEN,
    httpPerStore=_NOT_GIVEN,
    browserTabs=_NOT_GIVEN,
    requestTimeout=_NOT_GIVEN,
    productTimeLimit=_NOT_GIVEN,
    verbose=_NOT_GIVEN,
):
  global MAX_PRODUCTS, MAX_SEARCH_RESULTS, GET_REVIEWS, MAX_REVIEW_PAGES, HTTP_PER_STORE, BROWSER_TABS, REQUEST_TIMEOUT, PRODUCT_TIME_LIMIT, VERBOSE

  if maxProducts is not _NOT_GIVEN and maxProducts:
    MAX_PRODUCTS = maxProducts
  if maxSearchResults is not _NOT_GIVEN and maxSearchResults:
    MAX_SEARCH_RESULTS = maxSearchResults
  if getReviews is not _NOT_GIVEN and getReviews:
    GET_REVIEWS = getReviews
  if maxReviewPages is not _NOT_GIVEN and maxReviewPages:
    MAX_REVIEW_PAGES = maxReviewPages
  if httpPerStore is not _NOT_GIVEN and httpPerStore:
    HTTP_PER_STORE = httpPerStore
  if browserTabs is not _NOT_GIVEN and browserTabs:
    BROWSER_TABS = browserTabs
  if requestTimeout is not _NOT_GIVEN and requestTimeout:
    REQUEST_TIMEOUT = requestTimeout
  if productTimeLimit is not _NOT_GIVEN and productTimeLimit:
    PRODUCT_TIME_LIMIT = productTimeLimit
  if verbose is not _NOT_GIVEN and verbose:
    VERBOSE = verbose
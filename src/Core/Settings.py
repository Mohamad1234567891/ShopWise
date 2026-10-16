# ================================================================ SETTINGS
MAX_PRODUCTS = 30  # products per store (None = every product found on the listing page)
MAX_SEARCH_RESULTS = 7  # Maximum Results From querying DuckDuckGo
GET_REVIEWS = (
    True  # False = skip reviews entirely (fastest: product data only)
)
MAX_REVIEW_PAGES = (
    3  # review pages read per product (None = all of them; slower on big products)
)
HTTP_PER_STORE = (
    6  # downloads at the same time on one store (6 = what Chrome does)
)
BROWSER_TABS = 4  # browser tabs running at the same time
REQUEST_TIMEOUT = 20  # seconds per download
PRODUCT_TIME_LIMIT = 20  # seconds for one product's reviews
SCRAPE_TIME_LIMIT = 240  # seconds allowed for the whole scraping session before showing the results collected so far
VERBOSE = False  # print every product as JSON while running
CLUSTER_GAP_FACTOR = 1.5  # a jump larger than 50% starts a new price cluster
KEEP_MIN_FACTOR = 0.45  # clusters closer than this (x the main cluster median) stay in the results
KEEP_MAX_FACTOR = 2.2  # clusters farther than this (x the main cluster median) are removed
##########################################################################################################################

NOT_GIVEN = object()


def UpdateSettings(
    maxProducts=NOT_GIVEN,
    maxSearchResults=NOT_GIVEN,
    getReviews=NOT_GIVEN,
    maxReviewPages=NOT_GIVEN,
    httpPerStore=NOT_GIVEN,
    browserTabs=NOT_GIVEN,
    requestTimeout=NOT_GIVEN,
    productTimeLimit=NOT_GIVEN,
    verbose=NOT_GIVEN,
    clusterGapFactor=NOT_GIVEN,
    minFactor=NOT_GIVEN,
    maxFactor=NOT_GIVEN,
):
  global MAX_PRODUCTS, MAX_SEARCH_RESULTS, GET_REVIEWS, MAX_REVIEW_PAGES, HTTP_PER_STORE, BROWSER_TABS, REQUEST_TIMEOUT, PRODUCT_TIME_LIMIT, VERBOSE, CLUSTER_GAP_FACTOR, KEEP_MIN_FACTOR, KEEP_MAX_FACTOR

  if maxProducts is not NOT_GIVEN and maxProducts:
    MAX_PRODUCTS = maxProducts
  if maxSearchResults is not NOT_GIVEN and maxSearchResults:
    MAX_SEARCH_RESULTS = maxSearchResults
  if getReviews is not NOT_GIVEN and getReviews:
    GET_REVIEWS = getReviews
  if maxReviewPages is not NOT_GIVEN and maxReviewPages:
    MAX_REVIEW_PAGES = maxReviewPages
  if httpPerStore is not NOT_GIVEN and httpPerStore:
    HTTP_PER_STORE = httpPerStore
  if browserTabs is not NOT_GIVEN and browserTabs:
    BROWSER_TABS = browserTabs
  if requestTimeout is not NOT_GIVEN and requestTimeout:
    REQUEST_TIMEOUT = requestTimeout
  if productTimeLimit is not NOT_GIVEN and productTimeLimit:
    PRODUCT_TIME_LIMIT = productTimeLimit
  if verbose is not NOT_GIVEN and verbose:
    VERBOSE = verbose
  if clusterGapFactor is not NOT_GIVEN and clusterGapFactor:
    CLUSTER_GAP_FACTOR = clusterGapFactor
  if minFactor is not NOT_GIVEN and minFactor:
    KEEP_MIN_FACTOR = minFactor
  if maxFactor is not NOT_GIVEN and maxFactor:
    KEEP_MAX_FACTOR = maxFactor
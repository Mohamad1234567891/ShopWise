# ================================================================ SETTINGS
MAX_PRODUCTS = None        # None = every product found on the listing page
MAX_SEARCH_RESULTS = 7     # Maximum Results From querying DuckDuckGo
GET_REVIEWS = True         # False = skip reviews entirely (fastest: product data only)
MAX_REVIEW_PAGES = 5       # review pages read per product (None = all of them; slower on big products)
HTTP_PER_STORE = 6         # downloads at the same time on one store (6 = what Chrome does; more is faster
                           # only on stores without bot protection - others block you, which makes it slower)
BROWSER_TABS = 4           # browser tabs running at the same time (only used when needed)
REQUEST_TIMEOUT = 20       # seconds per download
PRODUCT_TIME_LIMIT = 60    # seconds for one product's reviews; after that it is saved with the reviews found
VERBOSE = False      # print every product as JSON while running (False = only the progress line)
##########################################################################################################################
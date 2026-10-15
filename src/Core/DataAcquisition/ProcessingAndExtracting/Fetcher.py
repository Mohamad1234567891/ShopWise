import asyncio
import sys
import json
import time

from src.Core.DataAcquisition import AsyncSession as AM
from src.Core.DataAcquisition import JavaScripts as JS

from src.Operations import URLOperations as UO
from src.Operations import HTMLOperations as HO

from src.Constants import Constants as C
from src.Constants import RegexConstants as RE

from src.Helpers import HTTPHelper as HH

from src.Core.DataAcquisition.AsyncSlotsManager import AsyncSlotsManager
from src.Core import Settings

class Fetcher:
    """Fetches webpages from a URL using http requests, if an http request fails it launches a headless browser to try and fetch the webpage from, but it always tries http requests
       first as it is much faster.

       It always tries its best to hide that it is an automatic system and tries to trick anti-bots into making it think that this is a human"""

    def __init__(self):
        self.httpRequestor = None
        self.playwright = self.browser = self.context = None
        self.storeSlotsManagers = {}  # one Gate per store: HTTP_PER_STORE downloads at the same time
        self.tabs = AsyncSlotsManager(Settings.BROWSER_TABS)
        self.browserLock = asyncio.Lock()
        self.browserFailed = False
        self.browserOnly = set()
        self.stats = {"http": 0, "browser": 0}

    async def __aenter__(self):
        AsyncSession = AM.GetAsyncSession()
        if AsyncSession is not None:
            """Trying to mimic google chrome's fingerprint, HTTP/2 headers, and handshakes to trick anti-bots that this is a Chrome browser and that a 
            normal human is using it, preventing us from getting blocked"""
            self.httpRequestor = AsyncSession(impersonate="chrome", timeout=Settings.REQUEST_TIMEOUT, max_clients=64)
        return self

    async def __aexit__(self, *exc):
        for closer in (self.context, self.browser):
            try:
                if closer:
                    await closer.close()
            except Exception:
                pass
        if self.playwright:
            await self.playwright.stop()
        if self.httpRequestor:
            await self.httpRequestor.close()

    def InitiateSlotManagerForStore(self, url):
        """Creates an AsyncSlotsManager Object for each url(store), if an object already exists for that url it will just return it"""

        domain = UO.GetDomainFromURL(url)
        if domain not in self.storeSlotsManagers:
            self.storeSlotsManagers[domain] = AsyncSlotsManager(Settings.HTTP_PER_STORE)
        return self.storeSlotsManagers[domain]

    async def get(self, url, referer=None, renderOptions=None, priority=C.NOW):
        """Returns a webpage data from a URL like (html data, json data, etc.) as a dictionary, it uses the ultra-fast http requests to fetch the data, if the
                   http request was blocked by an anti-bot, we would then proceed with mimicking Google Chrome using the 'curl_ciffi' library to bypass the anti-bot,
                   this approach is slow, so we try http requests first.

                url: A string holding the url.

                referer: A string holding the URL of the previous page. In http header there is something that we call a 'referer' that holds a URL that tells the website the page
                         you where previously in before visiting this website. Many websites including e-commerce websites checks the referer, if the referer was empty some of them
                         assumes that this client is a bot and blocks it, so we can use it to trick anti-bots into thinking this is a normal person.

                priority: An int value, we pass it to the UseSlot function to start processing data when a slot is available.
                """

        domain = UO.GetDomainFromURL(url)

        if self.httpRequestor is None or domain in self.browserOnly:
            return await self.FetchDataThroughBrowser(url, priority=priority,
                                                      **(renderOptions or {}))  # fetching data using a browser (slow)

        page = await self.FetchDataThroughHTTPRequest(url, referer=referer,
                                                      priority=priority)  # fetching data using an http request very fast

        dropped = page["status"] == 0 and "resolve host" not in (
                page.get("error") or "")  # no successful connection happened, likely an anti-bot has blocked us
        if (page["blocked"] or dropped) and not self.browserFailed:
            if domain not in self.browserOnly:
                if Settings.VERBOSE:
                    print(f"  [!] {domain} blocks plain HTTP requests -> using the browser for this store")
                self.browserOnly.add(
                    domain)  # Adding this domain to the browserOnly set so that the next time we immediately use the browser

            data = await self.FetchDataThroughBrowser(url, priority=priority,
                                                      **(renderOptions or {}))  # fetching data using a browser (slow)

            # if no html was returned(empty), we then return the page variable, because page would hold an error like "403 forbidden" which is more useful than an empty string
            return data if data["html"] else page

        return page

    async def FetchDataThroughHTTPRequest(self, url, referer=None, wantJson=False, retries=1, priority=C.NOW):
        """Tries to fetch a webpage data using an http request, it returns a dictionary containing the webpage data of the dictionary it returns
        keys:{"html", "url", "status", "via", "json", "blocked", "error"}


        url: Holds the url of the webpage we want to fetch data from.

        referer: A string holding the URL of the previous page. In http header there is something that we call a 'referer' that holds a URL that tells the website the page
                 you where previously in before visiting this website. Many websites including e-commerce websites checks the referer, if the referer was empty some of them
                 assumes that this client is a bot and blocks it, so we can use it to trick anti-bots into thinking this is a normal person.

        wantJson: A boolean, determines whether the caller of this method wants json payloads or not.

        retries: Amount of times to retry the request if the first fails

        priority: the importance of this request, passed to the SlotsManager to know where to put it in the waiting list if it needs to.
        """

        headers = {"Accept-Language": "en-US,en;q=0.9"}

        if referer:
            headers["Referer"] = referer
        if wantJson:
            headers["Accept"] = "application/json, text/plain, */*"  # requests JSON Payloads rather

        error = None
        for attempt in range(retries + 1):

            # The wait variable holds the amount of time we have to wait before retrying to request, if you don't have a delay we risk being detected as a bot
            wait = 0.5 * (attempt + 1)

            # requesting a slot to start the fetching process, max is five slots, if no slots available the fetching process will hold on, and it will get putten in a waiting list
            async with self.InitiateSlotManagerForStore(url).UseSlot(priority):
                try:

                    response = await self.httpRequestor.get(url, headers=headers,
                                                            allow_redirects=True)  # requesting the webpage and getting the response as a binary
                    self.stats["http"] += 1
                    html = HO.DecodeBody(response.content,
                                      response.headers.get("content-type", ""))  # decoding the binary into html

                    status = response.status_code
                    if status == 429 and attempt < retries:  # "too many requests": wait, then try again
                        retryAfter = response.headers.get("retry-after", "")  # getting the time needed to wait
                        wait = min(float(retryAfter), 10) if retryAfter.isdigit() else 2 * (attempt + 1)


                    elif status < 500 or attempt == retries:
                        """If the code was less than 500 then that means that the request has either successfully returned the data of the webpage(code 200) or that, something
                           wrong happened like the code 403 which means forbidden or 404 which means page not found etc. usually these indicates that an anti-bot is blocking
                           us from accessing the webpage, but whether it the page data was given to us successfully or not we will return that data, and the caller of this
                           function will deal with that data accordingly."""

                        return {"html": html, "url": str(response.url), "status": status, "via": "http", "json": [],
                                "blocked": HH.LooksBlocked(status, html)}

                except Exception as e:  # timeout, DNS, connection reset...
                    error = str(e)

                    """ if the string 'resolve host' was in the error, this means that we could not find the DNS IP address, in that case thre is no point of trying again so we
                      break out of the loop """
                    if "resolve host" in error:
                        break

            await asyncio.sleep(wait)

        return {"html": "", "url": url, "status": 0, "via": "http", "json": [], "blocked": False, "error": error}

    async def StartBrowser(self):
        """Starts a headless browser using parameters that would hide that this is an automatic system"""

        async with self.browserLock:

            """Checks if there is already a browser(meaning a browser instance is already running) or if a browser already failed before if one of these was true then it would return
               True meaning an instance is already running, or false meaning there is something wrong the browser instances are failing."""
            if self.browser or self.browserFailed:
                return self.browser is not None
            try:
                if Settings.VERBOSE:
                    print("[*] Starting the browser")
                from playwright.async_api import async_playwright

                self.playwright = await async_playwright().start()

                """Setting the flags for the browser so that it acts like a normal browser to baypass anti-bots

                --disable-blink-features=AutomationControlled -> hide all automation flags.

                --no-sandbox -> sometimes a sandbox causes a headless browser to crash, therefore we disable it.

                --disable-dev-shm-usage -> when the shared-memory is exhausted a headless browser usually crashes, so we are telling it not to use shared-memory to prevent any crashes.
                """
                args = ["--disable-blink-features=AutomationControlled", "--no-sandbox", "--disable-dev-shm-usage"]

                try:  # full Chromium in "new headless" mode looks like a normal browser to websites
                    self.browser = await self.playwright.chromium.launch(headless=True, channel="chromium", args=args)
                except Exception:
                    self.browser = await self.playwright.chromium.launch(headless=True,
                                                                         args=args)  # if there is no chromium on the system, we run the bundled version with playwright

                major = self.browser.version.split(".")[0]  # extracting the major version of the browser

                system = {"darwin": "Macintosh; Intel Mac OS X 10_15_7", "win32": "Windows NT 10.0; Win64; x64"}

                systemInfo = (f"Mozilla/5.0 ({system.get(sys.platform, 'X11; Linux x86_64')}) AppleWebKit/537.36 "
                              f"(KHTML, like Gecko) Chrome/{major}.0.0.0 Safari/537.36")

                self.context = await self.browser.new_context(user_agent=systemInfo, locale="en-US",
                                                              viewport={"width": 1366, "height": 900})

                """Injecting a javascript lambda function to the webpage before it loads, that overwrites the navigator.webdriver and make it return undefined instead of true.
                   The navigator.webdriver detects automation software and returns true when it detects that."""
                await self.context.add_init_script(
                    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")

                # Intercepting heavy media(videos, fonts, etc.), and tracker software(Google Analytics, Facebook pixels, etc.), so that the page is loaded faster
                await self.context.route(RE.HEAVY_RE, lambda route: route.abort())
                await self.context.route(RE.TRACKER_RE, lambda route: route.abort())
                return True

            except Exception as e:
                self.browserFailed = True
                print(f"[!] The browser could not start ({e}). Run: playwright install chromium")
                return False

    async def FetchDataThroughBrowser(self, url, navigate=True, openReviews=False, priority=C.NOW):
        """Starts a headless browser, opens the page from the url, and extracts the page data. it returns a dictionary containing the webpage data of the dictionary it returns
        keys:{"html", "url", "status", "via", "json", "blocked", "error"}


        url: Holds the url of the webpage we want to fetch data from.

        navigate: A boolean variable that indicates we want navigation through the webpage

        openReviews: A boolean variable that indicates if we want it to open the review section of a product

        priority: the importance of this request, passed to the SlotsManager to know where to put it in the waiting list if it needs to.
        """

        if not await self.StartBrowser():
            return {"html": "", "url": url, "status": 0, "via": "browser", "json": [], "blocked": False}

        async with self.tabs.UseSlot(priority):
            try:
                page = await self.context.new_page()
            except Exception as e:  # the browser crashed or was closed
                return {"html": "", "url": url, "status": 0, "via": "browser", "json": [], "blocked": False,
                        "error": str(e)}

            captured, pending, inflight = [], [], {}

            async def KeepJson(response):
                try:
                    body = await response.text()
                    if 20 < len(body) < 10_000_000:
                        captured.append({"url": response.url, "method": response.request.method,
                                         "data": json.loads(body)})
                except Exception:
                    pass

            def OnResponse(response):
                if len(pending) < 150 and response.request.resource_type in ("xhr", "fetch") and \
                        "json" in (response.headers.get("content-type") or ""):
                    pending.append(asyncio.ensure_future(KeepJson(response)))  # running the KeepJson method

            def OnRequest(request):
                inflight[request] = time.perf_counter()

            page.on("response", OnResponse)
            page.on("request", OnRequest)
            page.on("requestfinished", lambda request: inflight.pop(request, None))
            page.on("requestfailed", lambda request: inflight.pop(request, None))

            try:
                response = await page.goto(url, wait_until="domcontentloaded", timeout=(Settings.REQUEST_TIMEOUT + 10) * 1000)

                status = response.status if response else 0

                await self.LoadAllPageElements(page, inflight, navigate, openReviews)
                html = await self.content(page)

                for _ in range(5):  # letting JavaScript challenges clear by themselves
                    if not HH.LooksBlocked(status, html):
                        break
                    await page.wait_for_timeout(2000)
                    html = await self.content(page)
                    if not HH.LooksBlocked(200, html):
                        status = 200
                        await self.LoadAllPageElements(page, inflight, navigate, openReviews)
                        html = await self.content(page)

                if pending:
                    await asyncio.wait(pending, timeout=3)
                self.stats["browser"] += 1

                if not HH.LooksBlocked(status, html) and self.httpRequestor is not None:

                    # we extract all cookies generated by the browser to share with the http request, so that future requests is done with http requests as it is faster
                    for cookie in await self.context.cookies():
                        self.httpRequestor.cookies.set(cookie["name"], cookie["value"], domain=cookie.get("domain", ""),
                                                       path=cookie.get("path", "/"))

                return {"html": html, "url": page.url, "status": status, "via": "browser", "json": captured,
                        "blocked": HH.LooksBlocked(status, html)}

            except Exception as e:
                return {"html": "", "url": url, "status": 0, "via": "browser", "json": captured, "blocked": False,
                        "error": str(e)}

            finally:
                await page.close()

    @staticmethod
    async def WaitUntilPageLoads(page, inflight, maxSeconds, quietSeconds=0.5):
        """Makes the program wait for a page to load before attempting to do any processes on it, while taking the precautions not to wait forever, in case a page never loads.

        page: The page we want to wait for it to load

        inflight: A dictionary that tracks the currently active network requests that is in progress

        maxSeconds: Maximum seconds we can wait for the page to load, before considering that something has gone wrong

        quietSeconds: The required duration that the page has to stay stable in(network activity stops, and No Document Object Model(DOM) changes), to consider the page has loaded
                      successfully.
        """

        end, last, quietSince, idleSince = time.perf_counter() + maxSeconds, -1, None, None
        while True:
            try:
                count = await page.evaluate(JS.COUNT_JS)
            except Exception:  # the page is navigating and changing (it is still loading)
                return

            now = time.perf_counter()

            busy = any(now - started < 4.0 for started in inflight.values())

            idleSince = None if busy else (idleSince or now)
            quietSince = None if (busy or count != last) else (quietSince or now)

            """if the page is quiet for a time peroid more that what is allowed, or the time to process took more than what is allowed, or the page has been idle for more than 1 second
               then we exit the function, because it is likely that this will go on forever, as either we got blocked, lost internet connection, or there is something wrong with the
               server"""
            if (quietSince and now - quietSince >= quietSeconds) or now >= end or (
                    idleSince and now - idleSince >= 1.0):
                return

            last = count
            await asyncio.sleep(0.1)  # pausing for 100ms

    async def LoadAllPageElements(self, page, inflight, scroll, openReviews):
        """Loads everything in page including the lazy-loaded content, by scrolling down the page, and clicking teh more buttons

        page: The page we want to load its contents.

        inflight: A dictionary that tracks the currently active network requests that is in progress.

        scroll: A boolean that indicates whether we want to scroll through the page or not.

        openReviews: A boolean that indicates whether we want to attempt to open the reviews section of the product webpage.
        """

        await self.WaitUntilPageLoads(page, inflight, 5.0)
        try:
            # Some websites do not load everything at once, it loads only parts of the page, once you scroll it loads more, to we try to scroll through the page to load everything
            if scroll:
                await page.evaluate(JS.SCROLL_JS)
                await self.WaitUntilPageLoads(page, inflight, 3.0, 0.4)  # wait until everything loads(after scrolling)

            # Usually Reviews are not loaded with the page, they would load when a user click on a 'see reviews' button or a similar button, here we try to load the reviews
            if openReviews and Settings.GET_REVIEWS:
                clicked = await page.evaluate(JS.CLICK_REVIEW_TAB_JS, JS.REVIEW_WORDS_JS)

                if clicked:
                    await self.WaitUntilPageLoads(page, inflight, 4.0, 0.7)

                # Trying to find a more reviews button to click
                for _ in range(Settings.MAX_REVIEW_PAGES or 30):
                    beforeClicking = await page.evaluate(JS.CLICK_MORE_REVIEWS_JS, JS.REVIEW_WORDS_JS)

                    if beforeClicking < 0:  # if beforeClicking < 0 then there is no buttons to click
                        break

                    clicked = True
                    await self.WaitUntilPageLoads(page, inflight, 4.0, 0.6)

                    # if the page elements state was less than or equal to the beforeClicking variable then that means that the button we clicked did nothing
                    if await page.evaluate(JS.COUNT_JS) <= beforeClicking:
                        break

                if clicked:
                    # if the button is successffully clicked, we scroll to the button of the page to make sure that everything is loaded.
                    await page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
                    await self.WaitUntilPageLoads(page, inflight, 2.0, 0.4)

        except Exception:
            pass

    @staticmethod
    async def content(page):
        """Outputs the Page content

        page: The page we want to output its content.
        """

        # if getting the page content fails we wait a little bit(5 seconds) for the page to load and then retry, if it fails three times we return an empty string
        for _ in range(3):
            try:
                return await page.content()

            except Exception:
                try:
                    await page.wait_for_load_state("domcontentloaded", timeout=5000)

                except Exception:
                    pass
        return ""
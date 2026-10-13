import math
import json
import asyncio

from urllib.parse import quote

from src.Core.DataAcquisition.ProcessingAndExtracting import ProductPage

from src.Operations import StringOperations as SO

from src.Core import Settings

class ProductReviewExtractor:
    """Many stores load reviews with JavaScript from a JSON request. The browser opens ONE product,
    we find that request (it contains the product's ID), and every other product reuses it directly."""

    def __init__(self):
        self.template = None       # e.g. https://api.store.com/reviews?productId={id}&page=0
        self.idKind = None         # which product identifier goes into {id}
        self.learning = None       # set while the first product is being rendered
        self.renders = 0
        self.rendersWithReviews = 0

    def LearnPatterns(self, captured, ids):
        """This method discovers a store's API patterns and learns them to reuse later in other products from the same store instead of
        loading an entire webpages and scraping for data, which this method we save an enormous time.

        captured: this parameter contains all the JSON data received from the website
        ids: this parameter contains all the product ids captured(most stores assign each product on their store id our program captures it and store it for later usage)
        """


        for item in captured:

            """ we are trying to read fetched data, and fetched data usually exists in 'GET' HTTP method, so if this current item is not a 'GET' method or it does not
                contain any reviews, then we skip the current iteration because we are not interested in that data"""
            if item["method"] != "GET" or not SO.GetReviewsFromJSONIfAny(item["data"]):
                continue

            #kind: the kind of id (lasturl or sku)
            for kind, id in sorted(ids.items(), key=lambda kv: -len(kv[1])): #loop through the ids sorted from the longest strings to shortest
                for form in (id, quote(id)):
                    if form in item["url"]:
                        self.template, self.idKind = item["url"].replace(form, "{id}"), kind
                        return True
        return False

    @staticmethod
    async def getJson(fetcher, url, referer):
        response = await fetcher.FetchDataThroughHTTPRequest(url, referer=referer, wantJson=True, retries=1)
        try:
            return json.loads(response["html"]) if response["status"] == 200 else None
        except ValueError:
            return None

    async def fetch(self, fetcher, ids, referer, into):
        """The product's review pages through the learned request (MAX_REVIEW_PAGES pages at most).
        Reviews are added to 'into' as they arrive. Returns how many new reviews were found."""
        value = ids.get(self.idKind)
        if not self.template or not value or fetcher.httpRequestor is None:
            return 0
        found, limit = [], Settings.MAX_REVIEW_PAGES or 200

        def add(data):  # how many new reviews the page brought
            before = len(found)
            texts = SO.GetReviewsFromJSONIfAny(data) if data is not None else []
            SO.MergeReviews(found, texts)
            SO.MergeReviews(into, texts)
            return len(found) - before

        url = self.template.replace("{id}", quote(value))
        first = await self.getJson(fetcher, url, referer)
        if not add(first) or limit <= 1:
            return len(found)
        pageSize, done = len(found), 1
        items, pages = ProductPage.AnnouncedTotals(first, pageSize)
        pages = pages or (math.ceil(items / pageSize) if items else None)
        if pages and pages > 1:  # the response says how many pages there are: download them at the same time
            urls = []
            for _ in range(min(pages, limit) - 1):
                url = ProductPage.NextPage(url, pageSize)
                if not url:
                    break
                urls.append(url)
            newPerPage = [add(data) for data in await asyncio.gather(*(self.getJson(fetcher, u, referer) for u in urls))]
            done += len(urls)
            if not urls or min(newPerPage) == 0 or newPerPage[-1] < pageSize:
                return len(found)  # an empty or a part-filled page: that was the last one
        url = ProductPage.NextPage(url, pageSize)  # then one page after another until a page brings nothing new
        while url and done < limit:
            if not add(await self.getJson(fetcher, url, referer)):
                break
            done += 1
            url = ProductPage.NextPage(url, pageSize)
        return len(found)
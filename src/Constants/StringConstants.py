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

Multilingual semantic word sets used to understand unknown store pages. Defines the keys that identify names, prices, ratings, reviews, reviewers, dates and pagination inside HTML attributes or JSON, plus the review words (review, yorum, bewertung...) used to find reviews in every supported language.
"""

TOTAL_ITEM_KEYS = {"total", "totalcount", "total_count", "totalelements", "totalitems", "total_items", "totalresults",
                   "total_results", "totalreviews", "total_reviews", "reviewcount", "review_count", "numberofreviews",
                   "numfound", "totalhits"}

TOTAL_PAGE_KEYS = {"totalpages", "total_pages", "pagecount", "page_count", "lastpage", "last_page", "numpages"}

NOT_REVIEW_KEYS = {"price", "offers", "pricecurrency", "question", "questiontext", "answers", "answertext"}

PERSON_KEYS = {"author", "authorname", "author_name", "username", "user_name", "user", "customer", "customername",
               "customer_name", "nickname", "usernickname", "reviewer", "reviewername", "userfullname", "displayname",
               "display_name", "buyer", "member", "profile"}

RATING_KEYS = {"rating", "rate", "star", "stars", "score", "ratingvalue", "rating_value", "overallrating",
               "starrating", "productrating"}

DATE_KEYS = {"createdat", "created_at", "createddate", "creationdate", "date", "submissiontime", "submittedat",
             "reviewdate", "publishedat", "published_at", "createdate", "commentdate", "commentdateisotype",
             "datecreated", "timestamp"}

STRONG_TEXT_KEYS = ("reviewbody", "reviewtext", "review_text", "reviewcontent", "review_content", "commenttext",
                    "comment_text", "comment", "comments", "opinion", "usercomment", "review")

WEAK_TEXT_KEYS = ("text", "body", "content", "message", "description", "details", "detail")

HINT_ATTRIBUTES = ("class", "id", "itemprop", "data-testid", "data-test-id", "data-test", "data-qa", "data-hook",
                   "data-automation-id", "data-cy", "data-component", "aria-label", "role")

PRODUCT_TYPES = {"product", "productgroup", "individualproduct", "productmodel", "someproducts", "book", "vehicle"}

RELATED_KEYS = {"isRelatedTo", "isSimilarTo", "isAccessoryOrSparePartFor", "isConsumableFor", "isVariantOf", "review", "reviews", "itemReviewed"}

STORE_TYPES = {"website", "organization", "onlinestore", "store", "onlinebusiness", "corporation", "localbusiness"}

PAGE_PARAMS = {"page", "p", "pagenumber", "pageindex", "currentpage", "pageno", "pagenum", "pg"}
OFFSET_PARAMS = {"from", "offset", "start", "skip", "startindex"}

URL_KEYS = ("url", "productUrl", "product_url", "productURL", "link", "href", "pdpUrl", "pdp_url", "canonicalUrl",
            "seoUrl", "seo_url", "permalink", "uri", "webUrl", "path")

NAME_KEYS = ("name", "title", "productName", "product_name", "displayName", "item_name", "itemName", "productTitle")

REVIEW_WORDS = {"review", "reviews", "rev", "comment", "comments", "yorum", "yorumlar", "degerlendirme",
                "değerlendirme", "degerlendirmeler", "değerlendirmeler", "bewertung", "bewertungen", "rezension",
                "rezensionen", "avis", "resena", "reseña", "resenas", "reseñas", "opinion", "opinions", "opiniones",
                "recensione", "recensioni", "testimonial", "testimonials", "beoordeling", "beoordelingen",
                "recensie", "recensies", "opinia", "opinie", "avaliacao", "avaliacoes", "avaliação", "avaliações",
                "valoracion", "valoraciones", "отзыв", "отзывы", "ugc"}

REVIEW_BODY_WORDS = {"text", "body", "content", "comment", "comments", "description", "desc", "message", "msg",
                     "reviewtext", "reviewbody", "commenttext", "opinion", "yorum", "quote"}

# parts of a review card that are not the opinion itself, and UI around the reviews
REVIEW_PART_WORDS = {"title", "headline", "heading", "header", "author", "name", "profile", "avatar",
                     "username", "nickname", "date", "time", "rating", "ratings", "stars", "star",
                     "score", "helpful", "vote", "votes", "report", "abuse", "reply", "replies", "response", "answer",
                     "answers", "question", "questions", "count", "total", "histogram", "stats", "statistics", "filter",
                     "filters", "sort", "sorting", "form", "write", "input", "placeholder", "button", "btn",
                     "pagination", "pager", "paging", "nav", "navigation", "tab", "tabs", "image", "images", "img",
                     "media", "photo", "photos", "gallery", "video", "thumbnail", "thumbnails", "badge", "verified",
                     "meta", "footer", "alert", "error", "success", "warning", "status", "notification", "toast",
                     "translate", "translation", "prompt", "link", "ad", "ads", "sponsored", "sponsor", "advert",
                     "advertisement", "variant", "variants", "format", "attribute", "attributes", "seller", "empty",
                     "loading", "skeleton", "cta", "label", "tooltip", "popover", "modal", "dialog", "menu", "dropdown"}

# names of the box that holds all reviews (not one review)
REVIEW_LIST_WORDS = {"reviews", "comments", "yorumlar", "degerlendirmeler", "değerlendirmeler", "testimonials",
                     "bewertungen", "rezensionen", "opiniones", "opinions", "recensioni", "reseñas", "resenas",
                     "avaliacoes", "avaliações", "valoraciones", "beoordelingen", "recensies", "отзывы", "list", "lists",
                     "container", "section", "wrapper", "widget", "views", "medley", "area", "block", "group", "feed",
                     "carousel", "slider", "grid", "summary", "overview", "panel", "tabs", "tab", "header"}
REVIEW_ITEM_WORDS = {"item", "card", "entry", "single", "post", "tile", "row"}

# one review (the last word of a class name says what the element is: "bv-content-review" is a review,
# "review-text" is a text, "reviews-list" is a list)
REVIEW_SINGLE_WORDS = {"review", "rev", "comment", "yorum", "degerlendirme", "değerlendirme", "bewertung", "rezension",
                       "avis", "resena", "reseña", "opinion", "recensione", "testimonial", "beoordeling", "recensie",
                       "opinia", "opinie", "avaliacao", "avaliação", "valoracion", "valoración", "отзыв"}
TRANSPARENT_NAME_WORDS = {"module", "component", "root", "inner", "outer", "wrapper", "wrap", "container", "box", "el",
                          "element", "js", "default", "active"}
UI_NAME_WORDS = {"more", "load", "all", "see", "view", "no", "none", "zero", "write", "add", "new", "leave", "submit"}

STRONG_BODY_WORDS = {"text", "body", "content", "description", "message", "reviewtext", "reviewbody", "commenttext"}

AD_WORDS = {"ad", "ads", "sponsored", "sponsor", "advert", "advertisement", "adplacement", "adholder"}

INVISIBLE_TAGS = {"script", "style", "noscript", "template", "svg", "head", "title"}

REVIEW_SKIP_TAGS = {"a", "button", "label", "input", "textarea", "select", "option", "img", "svg", "time", "form",
                    "h1", "h2", "h3", "h4", "h5", "h6", "script", "style", "noscript", "template", "head", "title"}

SKIP_TAGS = {"script", "style", "noscript", "template", "svg", "head", "title", "option", "select", "textarea"}
BIG_TAGS = {"body", "html", "main", "section", "article", "ul", "ol", "table", "tbody", "form", "header", "footer", "nav"}
PRICE_WORDS = {"price", "prices", "pricing", "prix", "preis", "precio", "prezzo", "preco", "preço", "prijs", "pris",
               "cena", "cijena", "цена", "ціна", "amount", "tutar", "fiyat", "fiyati", "fiyatı"}
STRONG_OLD_WORDS = {"old", "was", "strike", "strikethrough", "crossed", "original", "eski", "rrp", "msrp", "uvp",
                    "statt", "before", "prev", "previous", "compare"}

WEAK_OLD_WORDS = {"list", "regular", "retail", "market", "base"}  # only count next to the word "price"

NOW_WORDS = {"sale", "final", "current", "now", "special", "offer", "discounted", "discount", "actual", "selling",
             "basket", "sepet", "sepette", "promo", "deal", "reduced"}
RATING_WORDS = ("rating", "stars", "star", "puan", "yildiz", "yıldız", "score", "rate", "rated", "bewertung", "note")
COUNT_WORDS = {"review", "reviews", "comment", "comments", "yorum", "yorumlar", "degerlendirme", "değerlendirme",
               "count", "ratings", "votes", "total"}
NOISE_WORDS = {"related", "recommend", "recommended", "recommendation", "recommendations", "similar", "carousel",
               "slider", "upsell", "crosssell", "cross", "benzer", "recent", "recently", "history", "bundle", "also"}

# A rating count is a bare number ('(1.234)') or a number next to what it counts ('1.234 değerlendirme',
# 'Yorumlar (12)', 'Based on 87 reviews') - unlike a review text that happens to contain a number.
_COUNTED = (r"(?:reviews?|ratings?|rated|de[gğ]erlendir|yorum|comments?|oy\b|oyla|votes?\b|bewertung|rezension|avis\b|"
            r"notes?\b|opini|rese[nñ]|valoraci|valutazion|recensi|avalia|beoordeling|recensie|ocen|отзыв|оцен|"
            r"レビュー|評価|件|评价|评论|評論|리뷰|후기|평가|تقييم|مراجع)")

MAIN_IMAGE_WORDS = {"main", "landing", "primary", "hero", "zoom", "large", "featured", "big", "cover"}

THUMB_IMAGE_WORDS = {"thumb", "thumbs", "thumbnail", "thumbnails", "small", "mini", "icon", "logo", "avatar", "badge",
                     "swatch", "swatches", "alt"}
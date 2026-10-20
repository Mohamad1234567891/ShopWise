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

Central regex library used across the scraping and analysis pipeline: numbers in international formats, tracking and analytics query parameters, camelCase splitting, 'show more' UI boilerplate in many languages, review links, pagination labels, JavaScript state assignments and junk path segments. Keeping every pattern here means the extraction rules stay in one auditable place.
"""

import re

from src.Constants import StringConstants as SC

# a number with . , ' as separators; a space only counts when exactly 3 digits follow ("1 299")
NUMBER_RE = re.compile(r"\d+(?:(?:[.,'’]| (?=\d{3}(?!\d)))\d+)*")


"""This regex, help us detect common marketing, and analytics URLs
utm_* -> Google Analytics
msclkid -> Microsoft adds"""
TRACKING_PARAM_RE = re.compile(r"^(utm_.*|gclid|fbclid|msclkid|yclid|gbraid|wbraid|_ga|_gl|srsltid|spm|scm|ref|ref_|"r"qid|sr|keywords|crid|sprefix|_pos|_sid|_ss|_psq)$", re.I)


CAMEL_RE = re.compile(r"([a-z])([A-Z])")

UI_TEXT_RE = re.compile(
    r"^(?:read|show|see|view|load)\s+(?:more|less|all|full)|^daha\s+(?:fazla|az)|^devamını\s+oku|^tümünü\s+gör|"
    r"mehr\s+anzeigen|weniger\s+anzeigen|^weiterlesen|^voir\s+(?:plus|moins)|^lire\s+la\s+suite|^ver\s+(?:más|menos)|"
    r"^leer\s+más|^leggi\s+(?:di\s+più|tutto)|^mostra\s+(?:di\s+più|meno)|^toon\s+(?:meer|minder)|^lees\s+meer|"
    r"^pokaż\s+(?:więcej|mniej)|^ler\s+mais|^ver\s+mais|^показать|^читать\s+далее|もっと見る|查看更多|더보기|عرض المزيد",
    re.I)

REVIEW_LINK_RE = re.compile(r"review|yorum|degerlendirme|değerlendirme|bewertung|rezension|avis|opini|resen|reseñ|"
                            r"recensi|valoraci|avaliac|beoordeling|recensie|otzyv|otzivy|отзыв", re.I)

NOT_REVIEW_LINK_RE = re.compile(r"write|create|new|add|submit|yaz|ekle|form|login|signin|giris|policy|guideline|"
                                r"kural|help|yardim|vote|report|helpful", re.I)

NEXT_TEXT_RE = re.compile(r"^(?:next|next page|›|»|>|→|sonraki|sonraki sayfa|ileri|weiter|nächste|suivant|siguiente|"
                          r"successivo|próxima|proxima|volgende|następna|далее|次へ|下一页|다음)$", re.I)

ASSIGN_RE = re.compile(r"=\s*[\[{]")

VARIABLE_BEFORE_RE = re.compile(r"([A-Za-z_$][\w$.]*)\s*$")

STATE_NAME_RE = re.compile(r"state|data|props|store|product|catalog|listing|search|initial|preload|apollo|redux|"
                           r"context|result|items|review", re.I)

JUNK_PATH_RE = re.compile(r"/(?:cart|basket|sepet|sepetim|checkout|login|signin|sign-in|giris|register|uye-ol|account|"
                          r"hesabim|my-account|wishlist|favorites|favoriler|compare|karsilastir|help|yardim|"
                          r"customer-service|contact|iletisim|privacy|cookie|blog|magaza|satici|brand|marka|"
                          r"campaign|campaigns|kampanya|kampanyalar|membership|uyelik|"
                          r"product-reviews|reviews|yorumlar)(?:[/?#.]|$)", re.I)

HASH_RE = re.compile(r"^(?=[A-Za-z0-9]*\d)[A-Za-z0-9]{5,}$")

REVIEW_HINT_RE = re.compile(r"review|rev|comment|yorum|de[gğ]erlendirme|bewertung|rezension|avis|rese[nñ]|opini|"
                            r"recensi|testimonial|beoordeling|recensie|avalia|valoraci|отзыв|ugc", re.I)

COUNT_NEAR_RE = re.compile(r"\d[\d.,\s]*[kKmM]?\s*(?:\w+\s+){0,2}\S{0,3}?" + SC._COUNTED + r"|" + SC._COUNTED +
                           r"\w*\s*[(:]?\s*\d[\d.,\s]*[kK]?\s*\)?\s*$", re.I)

BARE_COUNT_RE = re.compile(r"[★☆⭐]?\s*[(\[]?\s*\d[\d.,\s]*\s*[kK]?\s*[)\]]?")

DATE_RE = re.compile(r"\d{1,2}[./-]\d{1,2}[./-]\d{2,4}|\d{4}-\d{2}-\d{2}|\d{1,2}:\d{2}")

COUNT_TEXT_RE = re.compile(r"\(\s*([\d.,]+)\s*[^\d()]{0,25}\)|([\d.,]+)\s+(?:global\s+)?(?:reviews?|ratings?|"
                           r"de[gğ]erlendirme|yorum|bewertungen|sternebewertungen|avis|notes|rese[nñ]as|valoraciones|"
                           r"recensioni|opiniones|avalia[cç][oõ]es|отзыв|件のレビュー|件の評価)\w*", re.I)

RATING_TEXT_RE = re.compile(r"out of|üzerinden|von \d|sur \d|de \d|su \d|\bstars?\b|yıldız|sterne|étoiles|estrellas|"
                            r"stelle|/\s*(?:5|10)\b|つ星", re.I)

CURRENCY_RE = re.compile(r"[$€£₺₹₽₩₫₱฿₪₴₸₦৳₼₾₲¥￥]|(?<![A-Za-z])(?:TL|USD|EUR|GBP|TRY|JPY|CNY|INR|RUB|KRW|BRL|MXN|"
                         r"CAD|AUD|NZD|CHF|SEK|NOK|DKK|PLN|CZK|HUF|RON|BGN|UAH|KZT|AED|SAR|QAR|KWD|BHD|OMR|JOD|EGP|"
                         r"MAD|ILS|ZAR|NGN|KES|PKR|BDT|IDR|MYR|SGD|THB|VND|PHP|HKD|TWD|ARS|CLP|COP|PEN|Rs\.?|Rp|RM|zł|"
                         r"Kč|kr|Ft|lei|лв|руб|грн|R\$|S/|Dhs?|SR|KD)(?![A-Za-z])|ر\.س|د\.إ|ج\.م|د\.ك|ر\.ق|元|円|원")

# prices that are not the product's price: instalments, shipping thresholds, unit prices
NOT_PRICE_RE = re.compile(r"taksit|/\s*ay\b|ayl[ıi]k|\bx\s*\d|\d\s*x\b|per month|/\s*mo\b|/\s*month|monthly|a month|"
                          r"install?ment|financ|mensual|/\s*mes\b|par mois|/\s*monat|al mese|cuotas|parcela|"
                          r"payments? of|interest[- ]free|pay in \d|shipping|delivery|kargo|versand|livraison|"
                          r"env[ií]o|spedizione|\b(?:over|above|üzeri)\b|/\s*(?:kg|g|l|lt|ml|adet|pc|unit|stk|100\s?g)\b",
                          re.I)

BLOCK_RE = re.compile(
    r"<title>\s*(?:Just a moment|Attention Required|Access Denied|Robot Check|Pardon Our Interruption|Security Check|"
    r"Erişim Engellendi|Bot Verification|Are you a robot|Request Rejected)|cf-browser-verification|cf_chl_opt|"
    r"/_sec/cp_challenge|px-captcha|captcha-delivery\.com|_Incapsula_Resource|Request unsuccessful\. Incapsula|"
    r"/errors/validateCaptcha", re.I)

HEAVY_RE = re.compile(r"^[^?#]*\.(?:png|jpe?g|gif|webp|avif|svg|ico|bmp|woff2?|ttf|otf|eot|mp4|webm|mp3)(?:[?#]|$)", re.I)

# analytics and ad trackers, matched on the host name only (never on a product's own address)
TRACKER_RE = re.compile(r"^https?://[^/?#]*(?:google-analytics\.com|googletagmanager\.com|doubleclick\.net|facebook\.net|"
                        r"hotjar|criteo|segment\.(?:io|com)|clarity\.ms|tiktok|snapchat|bat\.bing\.com|newrelic|"
                        r"nr-data\.net|mc\.yandex|googlesyndication\.com|googleadservices\.com|amazon-adsystem\.com|"
                        r"adnxs\.com|taboola\.com|outbrain\.com|scorecardresearch\.com)[^/?#]*(?:[/?#]|$)", re.I)

# Years in titles ("2024 edition") are not model numbers.
YEAR_RE = re.compile(r"^(?:19|20)\d{2}$")

# Detects Latin letters/digits inside a run, to tell Latin runs (where exact
# equality is required) from non-Latin runs (where substring is enough).
LATIN_CHAR_RE = re.compile(r"[a-z0-9]")

# Image URLs that look like a store logo, icon, banner or placeholder rather
# than a product image. "/org/" and "a1/\d{1,2}/" catch store-asset paths
# (e.g. n11 serves its logo and tiny icons from n11scdn.akamaized.net/a1/org/
# and .../a1/30/ .../a1/70/).
LOGO_IMAGE_RE = re.compile(
    r"logo|sprite|icon|badge|placeholder|blank\.|spacer|transparent|loading|loader|"
    r"flag|payment|avatar|favicon|pixel|skeleton|banner|advert|sponsor|profile|"
    r"user|header|footer|nav|menu|cart|/org/|a1/\d{1,2}/|\.svg", re.I)
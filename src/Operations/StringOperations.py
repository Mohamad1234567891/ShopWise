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

Text cleaning, numbers, names and reviews. The workhorse string utilities: HTML-entity and invisible-character cleaning, international number parsing (1.234,50 / 1,234.50 / Arabic-Indic digits), count suffixes (1.2K), review merging and review extraction from JSON, plus the class/id tokenization that identifies review cards, lists and bodies on unknown store pages.
"""

import re
import unicodedata

from html import unescape
from lxml import etree
from lxml import html as lxmlHtml
from functools import lru_cache

from src.Core.DataAcquisition.ProcessingAndExtracting import DataProcessing as DP

from src.Constants import RegexConstants as RE
from src.Constants import StringConstants as SC

from src.Operations import JsonOperations as JO

def Clean(value):
    """Cleans raw scraped HTML data into a clean single-line string. It intelligently handles different types(list, tuple, dictionary, string) extract the first valid value, and
       decodes HTML entities, and removes whitespaces, tabs, and new lines.

       value: The input to clean, can be a list, tuple, dictionary, or a string.

       Examples:
        value = "  Wireless &amp; Bluetooth&nbsp;Mouse\n  "
        output -> "Wireless & Bluetooth Mouse"
        ----------------------
        value = ["", None, "  Gaming &amp; Office Chair  "]
        output -> "Gaming & Office Chair"
        ----------------------
        value = {"name": "Laptop &amp; Tablet &quot;Pro&quot;"}
        output -> 'Laptop & Tablet "Pro"'
        ----------------------
        value = "Item&#x2F;Part\u200b#123"  #Encoded slash and zero-width space
        output -> "Item/Part #123"
    """


    if value is None or isinstance(value, bool):
        return None

    if isinstance(value, (list, tuple)):
        return Clean(next((v for v in value if v not in (None, "")), None))

    if isinstance(value, dict):
        return Clean(value.get("name") or value.get("@value") or value.get("value"))


       #final cleaning of the text:
       #r"\s+": a regex pattern thad detects any spaces, tabs, new lines
       #unescape(str(value)): converting any encoded html text back to its decoded form
       #                      Examples:
       #                          &amp; -> &
       #                          &quot; -> "
       #                          &#x27; -> '
       #                          etc.
       #
       #replace("​", "") and replace("﻿", "")): those are invisible characters, usually websites use them to trick pattern matching like regex, so we try to get rid of them.
       #
       #note the replace("​", "") and the replace("​", "") looks empty but they have the replace("ZWSP", "") and the replace("ZWNBSP", "") characters inside them.

    text = re.sub(r"\s+", " ", unescape(str(value)).replace("​", "").replace("﻿", "")).strip()

    return text or None

def ToASCIIDigits(text):
    """Converts non ASCII numerical characters into an ASCII numerical characters. Alot these non-ASCII character are found in different non-english speaking countries, like persia
       and china"""


    if text.isascii():
        return text

    out = []
    for ch in text:
        # using unicodedata database to find if this character is a decimal value, if it is it will return it as ASCII otherwise it will return None
        digit = unicodedata.decimal(ch, None) if not ch.isascii() else None
        out.append(str(digit) if digit is not None else ch)

    return "".join(out).replace("٫", ".").replace("٬", ",")


def ToNumber(strNumber):
    """Converts different international numerical formats into a standard Python float.

    strNumber: contains the number to convert as a string

    Examples:
        '4,6' -> 4.6
        ----------------------
        '1.234' -> 1234
        ----------------------
        '1,234.50' -> 1234.5   '
        ----------------------
        1 234' -> 1234"""


    s = strNumber.replace(" ", "").replace("'", "").replace("’", "")

    if "." in s and "," in s:
        decimal = "." if s.rfind(".") > s.rfind(",") else ","
        s = s.replace("," if decimal == "." else ".", "").replace(decimal, ".")

    elif "." in s or "," in s:
        sep = "." if "." in s else ","
        parts = s.split(sep)

        if len(parts) > 2:
            s = "".join(parts) if len(parts[-1]) == 3 else "".join(parts[:-1]) + "." + parts[-1]

        else:
            head, tail = parts
            s = head + tail if (len(tail) == 3 and 0 < len(head) <= 3 and head != "0") else head + "." + tail
    try:
        return float(s)
    except ValueError:
        return None

def ExtractNumbersFromText(text):
    """Extracts all numbers in a string, returns a list of float numbers.

    text: A string value that we wish to extract the numbers from.

    Examples:
        text = "The product price is 49.99 USD."
        output -> [49.99]
        ----------------------
        text = ""Now $1,234.50 (Save $200.00)"
        output -> [1234.5, 200.0]
        ----------------------
        text = ""Poids: 1 250g — Prix special: 99,50 €"
        output -> [1250.0, 99.5]
    """


    #Converting text into a string, replacing NBSP and NNBSP characters with a regular space and passing that value to the ToASCIIDigits function
    text = ToASCIIDigits(str(text)).replace(" ", " ").replace(" ", " ")


    return [n for n in (ToNumber(m.group(0)) for m in RE.NUMBER_RE.finditer(text)) if n is not None]

def GetCount(value):
    """Extracts an Integer count(total amount of reviews, amount of people rated a product, etc.)

    value: Any input(string, int, float, list, tuple)

    Examples:
        value = "1.234 ratings"
        output -> 1234
        ----------------------
        value = "(2,345)"
        output -> 2345
        ----------------------
        value = "1.2K ratings"
        output -> 1200
    """


    if value is None or isinstance(value, bool):
        return None

    if isinstance(value, (int, float)):
        return int(value) if value >= 0 else None

    text = ToASCIIDigits(Clean(value) or "")

    #trying to find any numbers within the string, if the numbers are found the match variable will hold the first number found, if none are found it will hold None
    match = RE.NUMBER_RE.search(text)
    if not match:
        return None

    number = ToNumber(match.group(0))
    if number is None:
        return None

    """Trying to grab the next 5 character after the matched numbers, this is most likely to be the suffix, the reason we grab the next 5 characters is that suffixes are usually 1, 2,
       or 3 characters long, so five would guarantee us to find most suffixes, then we clean them from any white spaces and lowercase them"""
    suffix = text[match.end():match.end() + 5].strip().lower()
    if re.match(r"(k|bin|mil)\b", suffix):
        number *= 1000

    elif re.match(r"m\b", suffix):
        number *= 1_000_000

    # if the number is not an integer then we return None, because it does not make sense for a count to be a non-integer value
    elif number != int(number):
        return None

    return int(number)


def StripHTMLTags(html):
    """ Removes all html markups and tags and returns back only the text within the html

    html: A string variable containing the html content

    Example:
        if the variable 'html' contained the following html content:
        <div class="review-box">
            <h3>Amazing Quality!</h3>
            <p>I bought this and <b>truly loved</b> it.</p>
        </div>

        then the function would return the following string:
        "Amazing Quality! I bought this and truly loved it."

    """


    if "<" in html and ">" in html:
        try:
            return Clean(lxmlHtml.fromstring(html).text_content())
        except (etree.ParserError, ValueError):
            pass
    return Clean(html)

def MergeReviews(reviews1, reviews2):
    """Merges two review lists together, while eliminating all duplicates and intelligently, merges to parts of a review if one part existed in review1 and the complete version
    was in the second.


    reviews1: is a list of strings containing some reviews
    reviews2: is a list of string containing some reviews

    Example:
        reviews1 = ["this is a good...", "I like it", "nice product"]
        reviews2 = ["I like it", "bad product", "this is a good product"]

        out put -> ["this is a good product", "I like it", "nice product", "bad product"]
    """


    for review2 in reviews2:

        # sometimes UI elements hide part of a long text and replaces it with '...', this variable stores that unfinished review without these extra characters
        unfinishedReview = review2.rstrip(".… ")

        # if the review2 is empty or None or exists in reviews1 or reviews1 contains the full version of the review then skip merging it(because we do not want duplicates)
        if not review2 or any(review1 == review2 or review1.startswith(unfinishedReview) for review1 in reviews1):
            continue

        reviews1[:] = [review1 for review1 in reviews1 if not review2.startswith(review1.rstrip(".… "))] + [review2] # adding what remains(review2) from review1 to it
    return reviews1


def GetReviewsFromJSONIfAny(data):
    """Tries to filter out and extract customer reviews from a JSON file, returns a list of all the reviews it found if none found it will return an empty list"""

    reviews = []
    for node, parent in JO.GetJsonHeirarchy(data):

        keys = {str(k).lower(): v for k, v in node.items()} # making each key in the dictionary lower cased and mapping it to its value

        if keys.keys() & SC.NOT_REVIEW_KEYS:
            continue

        allKeys = set(keys) | ({str(k).lower() for k in parent} if isinstance(parent, dict) else set()) #putting all keys in a single set including the parent keys

        person, rating, date = bool(allKeys & SC.PERSON_KEYS), bool(allKeys & SC.RATING_KEYS), bool(allKeys & SC.DATE_KEYS)

        review = None
        if person or rating or date:
            """ Filters out the keys for the STRONG_TEXT_KEYS. If keys contains one of the STRONG_TEXT_KEYS and its value is a string and its value is not empty
            then it sets the variable review to that value otherwise it sets review to None"""
            review = next((keys[k] for k in SC.STRONG_TEXT_KEYS if isinstance(keys.get(k), str) and keys[k].strip()), None)

        if review is None and (person or (rating and date)):
            # Same idea as the previous check, but using WEAK_TEXT_KEYS instead of STRONG_TEXT_KEYS
            review = next((keys[k] for k in SC.WEAK_TEXT_KEYS if isinstance(keys.get(k), str) and keys[k].strip()), None)

        # Filtering out any left over html tags, after filtering the tags out if review is still not empty we set it to its value without the tags otherwise we set it to None
        review = StripHTMLTags(review) if review else None

        #not re.fullmatch(r"[\d\W_]+", review) -> making sure that the review is not only numbers and signs(none alphabetical characters)
        if review and len(review) >= 2 and not re.fullmatch(r"[\d\W_]+", review) and not review.startswith("http"):
            reviews.append(review)

    return MergeReviews([], reviews)


@lru_cache(maxsize=200_000)
def WordsOfText(attrs):
    return frozenset(t for t in re.split(r"[\W_]+", RE.CAMEL_RE.sub(r"\1 \2", attrs).lower()) if t)

def TextOf(el):
    return Clean(el.text_content()) or ""


def IsHashPart(part):
    """Detects whether a class or identifier name segment represents an auto-generated
    hash or randomized build artifact (e.g., 'KaU17BbDowCW', 'oaYMIoxDJcUiSeaVW') rather
    than a meaningful semantic name like 'ReviewCard'.

    Args:
        part (str): A token or substring split from a class or ID attribute.

    Returns:
        bool: True if the segment matches hash regex patterns or exhibits high uppercase entropy, False otherwise.

    Examples:
        # Checks if an auto-generated CSS module hash should be stripped:
        if IsHashPart("KaU17BbDowCW"):
            print("Detected hash token, discarding from semantic analysis.")
    """
    if RE.HASH_RE.match(part):
        return True
    if part.islower() or len(part) < 6:
        return False
    upper = sum(ch.isupper() for ch in part[1:])
    return upper >= 3 and upper / len(part) >= 0.25


def SplitName(name):
    """Splits a compound class, ID, or hook name into normalized lowercase word tokens,
    automatically filtering out auto-generated hash segments and handling camelCase boundaries
    (cached for performance).

    Args:
        name (str): A raw class name, ID string, or attribute value.

    Returns:
        tuple[str, ...]: A tuple of normalized, clean semantic word tokens.

    Examples:
        # Splits a CSS module class name into semantic words:
        tokens = SplitName("hermes-ReviewCard-module-KaU17Bb")
        # Returns: ('hermes', 'review', 'card', 'module')
    """
    parts = [part for part in re.split(r"[\W_]+", name) if part and not IsHashPart(part)]
    return tuple(t for part in parts for t in RE.CAMEL_RE.sub(r"\1 \2", part).lower().split() if t)


@lru_cache(maxsize=200_000)
def NameSet(name):
    """Converts a raw class or attribute name into a frozen set of normalized word tokens."""
    return frozenset(SplitName(name))


def ElementNames(el):
    """Extracts all raw class strings and hint attributes from an HTML element,
    excluding aria-labels and roles.

    Args:
        el: The HTML element node (e.g., lxml element) to inspect.

    Returns:
        list[str]: A list of raw class names and attribute strings.

    Examples:
        # Retrieves all class names and hooks from a review container:
        names = ElementNames(review_element)
    """
    names = []
    for key, value in el.attrib.items():
        if key == "class":
            names += value.split()
        elif key in SC.HINT_ATTRIBUTES and key not in ("aria-label", "role"):
            names.append(value)
    return names


def NameTokens(el):
    """Extracts ordered token sequences for each class, ID, or data-hook name on an element
    ('bv-content-review reviewText' -> [(bv, content, review), (review, text)]),
    stripping out randomized hash parts.

    Args:
        el: The HTML element node (e.g., lxml element).

    Returns:
        list[tuple[str, ...]]: A list of token tuples representing each attribute value.
    """
    return [SplitName(n) for n in ElementNames(el)]


def NameWords(el):
    """Extracts a list of frozen word sets for each class or hint attribute on an element."""
    return [NameSet(n) for n in ElementNames(el)]


@lru_cache(maxsize=100_000)
def NameKind(words):
    """Classifies an element's semantic role based on its class/ID word tokens,
    identifying whether it represents a single review card ('card'), review list ('list'),
    review body text ('body'), UI part ('part'), or None.

    Args:
        words (tuple | frozenset): A collection of word tokens extracted from element classes or attributes.

    Returns:
        str | None: The semantic category ('card', 'list', 'body', 'part'), or None.

    Examples:
        # Determines the semantic component type from word tokens:
        kind = NameKind(frozenset(['review', 'item']))
        # Returns: 'card'
    """
    meaningful = list(words)
    while meaningful and (meaningful[-1] in SC.TRANSPARENT_NAME_WORDS or meaningful[-1].isdigit() or
                          (len(meaningful[-1]) >= 6 and re.search(r"\d", meaningful[-1]))):
        meaningful.pop()  # Skip layout/module suffixes like '-module-KaU17Bb', '-wrapper', '-container'

    if not meaningful:
        return None

    wordSet = set(words)
    if wordSet & (SC.REVIEW_PART_WORDS | SC.UI_NAME_WORDS):
        return "part"

    last = meaningful[-1]
    if last in SC.REVIEW_SINGLE_WORDS or (last in SC.REVIEW_ITEM_WORDS and len(meaningful) >= 2 and
                                          meaningful[
                                              -2] in SC.REVIEW_WORDS):  # 'review-item' matches, 'comment-info-item' does not
        return "card"

    if wordSet & SC.REVIEW_WORDS and last in SC.REVIEW_LIST_WORDS:
        return "list"

    if last in SC.REVIEW_BODY_WORDS:
        return "body"

    return None

def IsOpinionText(text):
    """Determines whether a text string represents a valid product review opinion or comment,
    filtering out code snippets, UI boilerplate, counters, and excessively short or long strings.

    Args:
        text (str): The text string to evaluate.

    Returns:
        bool: True if the text qualifies as an opinion, False otherwise.

    Examples:
        # Validates whether an extracted text block is a real review:
        if isOpinionText(candidate_text):
            print("Valid opinion text found!")
    """
    return bool(text) and 2 <= len(text) <= 20000 and not re.fullmatch(r"[\d\W_]+", text) and \
        not DP.IsCounterText(text) and not (len(text) < 40 and RE.UI_TEXT_RE.search(text)) and \
        not re.search(r"function\s*\(|=>\s*\{|\bvar\s+\w+\s*=|\{\s*\"\w+\"\s*:", text)


def ToFloat(value):
    try:
        return float(str(value).replace(",", ".").strip())
    except (ValueError, TypeError):
        return None



import json
import re

from urllib.parse import urljoin

from src.Constants import RegexConstants as RE
from src.Constants import StringConstants as SC

def GetJsonHeirarchy(data, maxNodes=300_000):
    """Iterate through a nested Json (Dictionaries and Lists) using a depth first search(DFS) stack. Yields all dictionaries it finds along with its parent

    data: the json structured data we will process
    maxNodes: amount of nodes we are allowed to process, preventing any potential crashes

    Yields:
        a pair of node parent as a tuple (node, parent)
        node: the current dictionary being processed
        parent: the dictionary, list, or None that the node was found inside it, a None value means that the node is at the root and have no parent


    Examples:
        data = {"name": "Phone", "price": 123, "specs": {"ram": "8GB"}}

        # Step 1: Yields the root dict (no parent)
        # -> ({"name": "Phone", "price": 123, "specs": {"ram": "8GB"}}, None)

        # Step 2: Yields the nested "specs" dict, paired with its parent root dict
        # -> ({"ram": "8GB"}, {"name": "Phone", "price": 123, "specs": {"ram": "8GB"}})
    """

    #(data, parent)
    stack, seen = [(data, None)], 0

    while stack and seen < maxNodes:
        node, parent = stack.pop()
        seen += 1

        if isinstance(node, dict):
            yield node, parent
            stack.extend((v, node) for v in reversed(list(node.values())) if isinstance(v, (dict, list)))

        elif isinstance(node, list):
            stack.extend((v, parent) for v in reversed(node) if isinstance(v, (dict, list)))



def LoadJson(text):
    """json.loads that survives HTML comments, CDATA, trailing commas and several objects in one script."""


    if not text:
        return []

    text = re.sub(r"^\s*(?:<!--|//\s*<!\[CDATA\[)|(?:-->|//\s*\]\]>)\s*$", "", text.strip()).strip()

    for candidate in (text, re.sub(r",\s*([}\]])", r"\1", text)):
        try:
            return [json.loads(candidate, strict=False)]
        except ValueError:
            pass

    out, decoder, i = [], json.JSONDecoder(strict=False), 0

    while True:
        starts = [p for p in (text.find("{", i), text.find("[", i)) if p != -1]
        if not starts:
            return out
        try:
            obj, i = decoder.raw_decode(text, min(starts))
            out.append(obj)
        except ValueError:
            i = min(starts) + 1


def JsonLdBlocks(doc):
    """Extracts and parses all Schema.org JSON-LD script blocks from an HTML
    document tree using case-insensitive XPath queries.

    Args:
        doc: The parsed HTML document tree (lxml element).

    Returns:
        list: A list of parsed JSON-LD data objects (dictionaries or lists) extracted from script tags.

    Examples:
        # Extracts JSON-LD blocks from a parsed HTML document:
        ld_blocks = JsonLdBlocks(parsed_doc)
    """
    blocks = []
    for script in doc.xpath('//script[contains(translate(@type,"LDJSON","ldjson"),"ld+json")]'):
        blocks.extend(LoadJson(script.text))
    return blocks

def EmbeddedJson(doc):
    """Extracts and parses embedded JSON data blocks from <script> tags within an HTML
    document (supporting __NEXT_DATA__, application/json mime types, and window initial state assignments).

    Args:
        doc: The parsed HTML document tree (e.g., lxml element).

    Returns:
        list: A list of parsed JSON objects/dictionaries extracted from the script tags.

    Examples:
        # Extracts embedded JSON state data from a React/Next.js page:
        json_data_blocks = EmbeddedJson(parsed_doc)
    """
    blocks, decoder = [], json.JSONDecoder(strict=False)
    for script in doc.xpath("//script[not(@src)]"):
        text, kind = script.text or "", (script.get("type") or "").lower()
        if "ld+json" in kind or len(text) < 40 or len(text) > 25_000_000:
            continue
        if "json" in kind:
            blocks.extend(LoadJson(text))
        elif not kind or "javascript" in kind or kind == "module":
            tries = 0
            for match in RE.ASSIGN_RE.finditer(text):
                start = match.start()
                if start == 0 or text[start - 1] in "=!<>+-*/%&|^?:":  # '==', '<=', '+=' are not assignments
                    continue
                name = RE.VARIABLE_BEFORE_RE.search(text, max(0, start - 80), start)
                if not name or not RE.STATE_NAME_RE.search(name.group(1)):
                    continue
                tries += 1
                try:
                    blocks.append(decoder.raw_decode(text, match.end() - 1)[0])
                except ValueError:
                    pass
                if tries >= 40:
                    break
    return blocks


def JsonProductLinks(blocks, pageURL):
    """Extracts product link URLs from embedded JSON blocks by scanning for objects
    containing product names, price attributes, and valid navigation keys.

    Args:
        blocks (list): A list of parsed JSON data structures (dictionaries or lists).
        pageURL (str): The absolute URL of the current page for resolving relative links.

    Returns:
        list[str]: A list of absolute resolved product URLs found within the JSON blocks.

    Examples:
        # Extracts product links from embedded JSON-LD or state blocks:
        json_links = JsonProductLinks(json_blocks, "https://store.com/shop")
    """
    links = []
    for node, _ in GetJsonHeirarchy(blocks):
        name = next((node[k] for k in SC.NAME_KEYS if isinstance(node.get(k), str) and len(node[k].strip()) >= 3), None)
        if not name or not any("price" in str(k).lower() and v not in (None, "", 0) for k, v in node.items()):
            continue

        for key in SC.URL_KEYS:
            value = node.get(key)
            if isinstance(value, dict):
                value = value.get("href") or value.get("url") or value.get("path")
            if isinstance(value, str) and value.strip().startswith(("http", "/")) and \
                    not re.search(r"\.(?:jpe?g|png|gif|webp|svg|js|css|json)(?:[?#]|$)|/api/", value):
                links.append(urljoin(pageURL, value.strip()))
                break

    return links
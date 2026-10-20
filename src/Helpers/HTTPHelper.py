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

Anti-bot detection. LooksBlocked(...) recognizes bot-blocked responses by status code and by known challenge signatures (Cloudflare, Akamai, DataDome, PerimeterX...) so the Fetcher can fall back to the browser for that page.
"""

from src.Constants import RegexConstants as RE

def LooksBlocked(status, html):
    """Detects whether an HTTP response indicates anti-bot protection, rate-limiting,
    or CAPTCHA challenges (such as Cloudflare, Akamai, DataDome, PerimeterX, or Imperva)
    based on HTTP status codes and HTML response signatures.

    Args:
        status (int): The HTTP response status code.
        html (str): The raw HTML response body content.

    Returns:
        bool: True if the response exhibits characteristics of being blocked or challenged, False otherwise.

    Examples:
        # Checks if a 403 response or small HTML body indicates a Cloudflare challenge:
        if LooksBlocked(403, html_content):
            print("Request was blocked by anti-bot protection!")
    """
    # Check for typical blocking status codes or suspiciously short 503 error pages
    if status in (401, 403, 407, 429) or (status == 503 and len(html) < 100_000):
        return True

    # Check for known anti-bot keyword signatures within the leading portion of small or medium-sized HTML bodies
    return len(html) < 400_000 and bool(RE.BLOCK_RE.search(html[:200_000]))
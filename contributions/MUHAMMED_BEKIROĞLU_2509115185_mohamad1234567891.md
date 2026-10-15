# Contribution Report — Muhammed Bekiroğlu

**Student Name:** MUHAMMED BEKİROĞLU  
**Student ID:** 2509115185  
**GitHub Username:** [mohamad1234567891](https://github.com/mohamad1234567891)  
**Project:** ShopWise  
**Role:** **Team Leader** — Backend, Web Scraping & Data Engineering

---

## Overview

As the team leader of ShopWise, I was responsible for organizing the team, distributing work according to each member's capabilities, assigning daily tasks, and mentoring teammates whenever they needed help. On the technical side, I designed and implemented the **core web-scraping and data-filtration engine** that powers the entire application, along with the shared utility libraries, the runtime settings system, the result-quality (relevance and scoring) systems, the cross-platform setup automation, and the command-line interface.

The engine I built is what makes ShopWise what it is: it searches dozens of regional stores at once, extracts product names, prices, ratings and reviews from pages of any structure, defends itself against anti-bot protections, filters out irrelevant products, and ranks the remaining offers by their true value.

---

## 1. Project Leadership & Team Coordination

- **Organized the team and distributed the work** among members according to each member's strengths and capabilities.
- **Planned and assigned the everyday tasks** for every member, tracked their progress, and made sure the work stayed on schedule.
- **Mentored and supported teammates** — debugging their code, explaining parts of the codebase, and reviewing their work before it was merged.
- **Owned the project's architecture** — designed the folder structure, the module boundaries, and how the pieces connect to each other.
- Coordinated the team.

---

## 2. Web Scraping & Data-Acquisition Engine — `src/Core/DataAcquisition/`

I designed and implemented the entire data-acquisition engine from scratch. It is the heart of the application.

### `Fetcher.py` — the dual-transport fetching engine
- Fetches pages with **ultra-fast HTTP requests first**, and automatically falls back to a **headless Chromium browser (Playwright)** whenever a store blocks plain requests.
- Uses `curl_cffi` to **impersonate Google Chrome's TLS fingerprint**, so anti-bot systems see a normal browser instead of a script.
- Applies stealth countermeasures in the browser: disables the `AutomationControlled` flag, overrides `navigator.webdriver`, builds a realistic user agent from the real browser version, and shares cookies from the browser back into the HTTP session.
- Blocks heavy media and tracking/analytics requests to make pages load faster.
- Implements automatic **block detection** (`403`, `429`, CAPTCHA/Cloudflare challenge pages) and per-domain browser escalation.
- Detects when the visited page *is* a product page and captures its product data directly, so a store that returns a product link instead of a listing is never lost.

### `AsyncSession.py` & `AsyncSlotsManager.py` — concurrency & rate control
- A session factory that gracefully degrades when `curl_cffi` is not installed.
- A priority-based **async slot manager**: limits the number of simultaneous requests per store (like a browser does) and orders waiting tasks by priority, so work for products already in progress always finishes first.

### `JavaScripts.py` — in-page browser automation
- JavaScript snippets that **scroll pages step-by-step** to trigger lazy-loaded products and reviews, click the "Reviews" tab, and press "show more reviews" buttons until everything is loaded.
- Review-word detection works **in 20+ languages** (`review`, `yorum`, `bewertung`, `отзыв`, `レビュー`, `评价`, …), so the browser finds review sections on stores worldwide.

### `ProcessingAndExtracting/` — the extraction brain
- **`DataProcessing.py`** — multilingual extraction heuristics for prices (currency symbols, old/current/sale prices, installments), review cards, review-page links, store names and listing links.
- **`ProductPage.py`** — the product-page extraction pipeline: reads Schema.org JSON-LD, microdata, OpenGraph meta tags, embedded JSON and raw DOM, then merges everything into one record (name, price, rating, rating count, image, reviews). Also handles review pagination: predicts and prefetches page URLs, follows "next" links, and collects linked pages in parallel.
- **`ProductReviewExtractor.py`** — **learns each store's internal review API** by watching the network traffic of the first rendered product, extracts the API template, and then reuses it for every other product of that store — which avoids re-rendering pages and saves an enormous amount of time.

### `Scraping/` — orchestration & store resolution
- **`Scraper.py`** — the scraping pipeline shared by the CLI and the GUI: navigates the listing, extracts product links, falls back to the browser when raw HTML has nothing, limits results per store, processes all product pages concurrently, and gracefully isolates store failures so one broken site never stops the others.
- **`FindRegion.py`** — detects the user's country via IP geolocation and maps every regional store **directly to its own search page** using built-in templates — no search engine is involved, so every store in the region is queried instantly.

---

## 3. Result Quality — Relevance Filtering & Value Scoring

The engine alone was not enough: stores return accessories, bundles and other models next to the product the user searched for, and those irrelevant results ruined the ranking. I designed and implemented the two-layer solution that fixes this.

### `RelevanceAnalysis.py` — language-independent product-name matching
- Splits query and product names into **digit/letter runs** (`"12x"` → `["12", "x"]`), so `"12 X"`, `"12x"` and `"12X"` all match, and merged forms like `"iphone17"` match `"iphone 17"`.
- Unicode normalization makes it work **in every language and script** (Turkish `İ`, Cyrillic, Arabic, Chinese…) — with **no word lists anywhere**.
- Hard rules use only **model numbers**, which are universal: a missing model number or a conflicting one (`"iphone 17"` vs `"iphone 16 charger"`) rejects the product, while storage/power numbers (`256 gb`, `45 w`) and years are correctly ignored.
- Accessories are never banned — when the user searches for `"iphone 17 charger"`, the charger matches itself perfectly and stays.

### `StatisticalAnalysis.py` — price-cluster filtering & the value score
- **Price clustering:** prices are split into clusters at large gaps, and the scoring is anchored to the *dominant* cluster (the real product's price band). Accessories in far-away clusters are removed entirely, so they can no longer shift the statistics or crowd the results.
- **Wilson lower-bound rating quality:** a 5.0★ rating backed by 1 review scores far below a 4.7★ backed by 5000 reviews, so unreliable ratings can never win the ranking.
- **Continuous value score:** `value = rating quality ÷ price ratio − review penalty` — the best-value offer becomes gold, the cheapest stays blue, and the weakest offers sink to red.
- All cluster thresholds are tunable at runtime (`-c`, `--minFactor`, `--maxFactor`).

---

## 4. Settings System & Command-Line Interface

- **`Settings.py`** — the central runtime configuration with sensible defaults for every knob of the engine (concurrency limits, timeouts, review depth, cluster factors), plus `UpdateSettings()` which applies only the options the user actually provided.
- **`ArgumentsParser.py`** — the complete command-line interface: product name handling, positive-integer and positive-float validators, and every engine option, including the cluster-tuning flags `-c` / `--minFactor` / `--maxFactor`.
- **`CLI.py`** — the application entry point that orchestrates the whole pipeline: parses arguments, applies settings, runs the scraping session, scores the results and renders them, with graceful Ctrl+C handling.

---

## 5. Shared Libraries — `src/Constants/`, `src/Helpers/`, `src/Operations/`

I created and maintain the shared foundation used by the whole team:

### `Constants/`
- **`Constants.py`** — the regional store database: **150+ store domains across 35+ regions**, plus the **search-page templates for every store** and the unit symbols used by the relevance engine.
- **`RegexConstants.py`** — the project's regex library: prices and numbers, tracking-parameter stripping, block-page detection, review/rating/review-link patterns, junk-path (cart/login/campaigns) detection, heavy-media and tracker filters, years and Latin-run detection.
- **`StringConstants.py`** — multilingual semantic word sets (review words, price words, old-price words, noise words, units…) that make the extraction heuristics work across languages.
- **`URLConstants.py`** — URL-related constants.

### `Helpers/`
- **`HTTPHelper.py`** — detects anti-bot blocks from status codes and challenge-page signatures (Cloudflare, Akamai, DataDome, PerimeterX, Imperva).

### `Operations/`
| Module | Purpose |
| ------ | ------- |
| `URLOperations.py` | URL cleaning (tracking-parameter removal), canonical sorting, ID extraction, search-URL detection |
| `HTMLOperations.py` | HTML parsing, semantic extraction, microdata, card/link discovery |
| `StringOperations.py` | Text cleaning, number extraction, review merging/dedup, name tokens |
| `JsonOperations.py` | Embedded JSON & JSON-LD traversal and extraction |
| `MathOperations.py` | Rating conversion to a 0–5 scale |
| `ThreadOperations.py` | Worker process/thread pools and async dispatch (so parsing never blocks the event loop) |
| `DictionaryOperations.py` | Dictionary helpers |

---

## 6. Cross-Platform Setup Automation — `Setup.py`

To make the project runnable by anyone (including the professor) with a single command, I wrote a **fully automated, cross-platform setup script**:

- Uses **only Python's standard library** — nothing needs to be installed to run it.
- Detects the operating system and a suitable Python 3.10+ interpreter, creates the virtual environment, upgrades pip, installs all dependencies, installs the Playwright Chromium browser, downloads the NLTK resources, offers the Argos Translate language models, and verifies every dependency imports correctly.
- Prints **every step live** to the terminal and prints the exact activation commands for the user's OS at the end.

---

## 7. Testing, Debugging & Continuous Improvement

- Continuously tested the engine against real searches across Turkish and international stores and diagnosed failures from the verbose logs.
- Fixed pipeline-level problems found during testing: stores being skipped by search-engine discovery (replaced with direct store templates), product pages being scraped as listings without capturing their own product, and navigation/campaign/review pages leaking into the results.
- Fixed scoring bugs, including the review key mismatch (`"review"` vs `"reviews"`) that silently disabled review-based scoring.
- Maintained the project documentation (`README.md`) and kept it in sync with the code.

---

## Important Note Regarding a Teammate

My teammate **Bashir Alzoubi** has a smaller contribution than the rest of the team because he joined us late: he replaced a member (AbdulAziz) who had left the team, and by the time he joined there was little remaining work, so he contributed the PowerPoint animations. I respectfully ask that his late arrival be taken into consideration and that his grade not be penalized for the smaller contribution.

---

*This report describes the work I personally performed and led during the development of ShopWise.*

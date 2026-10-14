# 🛒 ShopWise

> **Search a product once. Compare it across every major store in your region — prices, ratings and reviews, ranked for you.**

ShopWise is a cross-store product comparison engine that finds a product on the web, scrapes its details and customer reviews from many online stores at the same time, then scores and ranks every offer so you can instantly see where the best deal is.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![Status](https://img.shields.io/badge/Status-University%20Project-important)

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [How It Works](#how-it-works)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
  - [Running ShopWise](#running-shopwise)
  - [Command-Line Reference](#command-line-reference)
  - [Examples](#examples)
- [How Products Are Scored](#how-products-are-scored)
- [Supported Regions & Stores](#supported-regions--stores)
- [Team](#team)
- [Disclaimer](#disclaimer)

---

## Overview

ShopWise automates the entire product-research workflow:

1. It **detects your country** automatically and picks a curated list of popular online stores for that region.
2. It **finds the product** on each store using DuckDuckGo search.
3. It **scrapes every listing and product page** concurrently, extracting the product name, price, rating, review count, image and customer reviews.
4. It **analyzes the results** — translating reviews to English, scoring their sentiment, and combining price, rating and review data into a single ranking.
5. It **presents a ranked comparison** in a beautiful terminal table (or a graphical interface), with the best overall value first.

---

## Features

- 🌍 **Region-aware store discovery** — auto-detects your country (IP geolocation) and searches a curated list of 150+ store domains across 35+ regions worldwide.
- ⚡ **Dual fetching engine** — ultra-fast HTTP requests that impersonate Google Chrome (`curl_cffi`), with automatic fallback to a stealth headless browser (Playwright/Chromium) whenever a store's anti-bot protection blocks plain requests.
- 🧲 **Deep product extraction** — pulls structured data from JSON-LD, microdata, embedded JSON and DOM heuristics, so it works even on stores without consistent markup.
- 💬 **Review intelligence** — crawls paginated reviews, clicks "show more" buttons in the browser, **learns each store's internal review API** and reuses it for the remaining products, translates reviews to English, and scores their sentiment.
- 🏆 **Smart ranking** — every product is scored on price position (quartiles & IQR), rating, rating volume and review sentiment, then color-coded: **gold** (best overall), **blue** (cheapest), **red** (lowest scores) and white.
- 🖥️ **Interactive CLI** — a rich, colorized results table; type a product's number to open its store page directly in your browser.
- 🎨 **Modern GUI** — a polished PySide6 desktop interface with a search bar, product cards, loading states and smooth scrolling.
- 🧵 **Concurrency & rate control** — per-store request slots, browser-tab limits, priority-based task scheduling and per-request/per-product timeouts keep scraping fast while staying polite to the stores.
- 🛡️ **Anti-bot resilience** — Chrome fingerprinting, realistic user agents, `navigator.webdriver` masking, referer spoofing, cookie sharing between the browser and HTTP sessions, and automatic block detection.

---

## How It Works

```
CLI arguments ──► Region auto-detection ──► Store discovery (DuckDuckGo)
                                                    │
                                                    ▼
   Ranked results ◄── Scoring & sentiment analysis ◄── Review collection
                                                    ▲
                                                    │
                              Product pages ◄── Listing scraping (HTTP first, browser fallback)
```

1. **Parse arguments** — product name, mode, limits and timeouts are read from the command line.
2. **Detect region** — the user's country code is resolved via `ipapi.co` and mapped to a regional store list.
3. **Discover stores** — DuckDuckGo is queried per store (in parallel) to locate each store's search-results URL for the product.
4. **Scrape listings** — each listing page is fetched (fast HTTP first, headless Chromium fallback), lazy-loaded content is scrolled in, and all product links are extracted.
5. **Process products** — every product page is fetched concurrently; name, price, rating, review count, image and reviews are extracted and merged from every available source.
6. **Collect reviews** — review tabs are clicked, "load more" buttons are pressed, review pages are paginated, and store review APIs are learned and reused.
7. **Analyze** — reviews are translated to English (Argos Translate), scored with VADER sentiment analysis, and combined with price/rating statistics into points.
8. **Rank & display** — results are sorted by score and rendered in an interactive table (CLI) or cards (GUI).

---

## Tech Stack

| Layer            | Technology |
| ---------------- | ---------- |
| Language         | Python 3.10+ (`asyncio`, `multiprocessing`, `argparse`) |
| Fast HTTP        | `curl_cffi` (Chrome impersonation), `httpx`, `requests` |
| Browser fallback | `Playwright` (headless Chromium, stealth flags) |
| Store discovery  | `ddgs` (DuckDuckGo search) |
| HTML parsing     | `lxml`, `bs4` (BeautifulSoup) |
| CLI rendering    | `rich` |
| GUI              | `PySide6` (Qt for Python) |
| Sentiment        | `nltk` (VADER) |
| Translation      | `argostranslate`, `langdetect` |

---

## Project Structure

```
ShopWise/
├── contributions/                          # Individual team-member contribution reports
├── src/
│   ├── CLI.py                              # Entry point — orchestrates the full pipeline
│   ├── Constants/
│   │   ├── Constants.py                    # Regional store lists & priority constants
│   │   ├── RegexConstants.py               # Price/review/block-detection regexes
│   │   ├── StringConstants.py              # Multilingual semantic word sets
│   │   └── URLConstants.py                 # URL-related constants
│   ├── Core/
│   │   ├── ArgumentsParser.py              # Command-line argument parsing
│   │   ├── CLIRenderer.py                  # Rich terminal table & interactive picker
│   │   ├── Settings.py                     # Runtime tunables and their defaults
│   │   ├── DataAcquisition/
│   │   │   ├── AsyncSession.py             # Chrome-impersonating HTTP session factory
│   │   │   ├── AsyncSlotsManager.py        # Priority-based concurrency slot limiter
│   │   │   ├── JavaScripts.py              # In-page JS (scrolling, review tabs, load-more)
│   │   │   ├── ProcessingAndExtracting/
│   │   │   │   ├── Fetcher.py              # HTTP-first fetching with browser fallback
│   │   │   │   ├── DataProcessing.py       # Price/review/listings extraction heuristics
│   │   │   │   ├── ProductPage.py          # Product data extraction & review pagination
│   │   │   │   └── ProductReviewExtractor.py # Learns & reuses store review APIs
│   │   │   └── Scraping/
│   │   │       ├── Search.py               # DuckDuckGo store-URL discovery
│   │   │       └── Scraper.py              # Per-store scraping orchestration
│   │   └── DataAnalysis/
│   │       ├── SentimentAnalysis.py        # VADER-based review sentiment scoring
│   │       ├── StatisticalAnalysis.py      # Scoring, ranking & color-coding
│   │       └── Translator.py               # Detects & translates reviews to English
│   ├── GUI/
│   │   ├── Components/                     # Buttons, cards, search bar, scrolling, loaders
│   │   └── Window/                         # Main application window (PySide6)
│   ├── Helpers/
│   │   └── HTTPHelper.py                   # Anti-bot / block-page detection
│   ├── Operations/                         # HTML, JSON, URL, string, math & threading utilities
│   └── products.json                       # Sample exported search results
├── requirements.txt                        # Python dependencies
├── .gitignore
└── README.md
```

---

## Prerequisites

- **Python 3.10 or newer** ([python.org](https://www.python.org/downloads/))
- **Git** ([git-scm.com](https://git-scm.com/downloads))
- An **internet connection** (the first run also downloads NLTK language resources automatically)

---

## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/Mohamad1234567891/ShopWise.git
cd ShopWise
```

### 2. Create a virtual environment

> If the `python` command is not found, use `python3` (Linux/macOS) or `py` (Windows) instead.

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

Choose the instructions that match **your operating system and terminal**.

#### 🐧 Linux — bash / zsh

```bash
source .venv/bin/activate
```

#### 🐧 Linux — fish

```fish
source .venv/bin/activate.fish
```

#### 🍎 macOS — bash / zsh (default terminal)

```bash
source .venv/bin/activate
```

#### 🍎 macOS — fish

```fish
source .venv/bin/activate.fish
```

#### 🪟 Windows — Command Prompt (cmd)

```cmd
.venv\Scripts\activate
```

#### 🪟 Windows — PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

> **Note:** if PowerShell blocks the activation script, allow it once with:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

When the environment is active, your prompt is prefixed with `(.venv)`. To leave it at any time, run `deactivate`.

### 4. Install the Python dependencies

```bash
pip install -r requirements.txt
```

### 5. Install the browser used by the scraper

```bash
playwright install
```

> ShopWise only drives **Chromium**, so installing just that browser is enough and faster:
> `playwright install chromium`

### 6. (Optional) Install translation models

ShopWise translates product reviews to English before analyzing them. To enable translation for the languages of your region's stores, install the matching Argos Translate packages, for example:

```bash
argospm update
argospm install translate-tr_en translate-de_en translate-es_en
```

Skip this step if you don't need review translation — reviews are still collected and displayed in their original language.

---

## Usage

### Running ShopWise

Make sure the virtual environment is **active** and you are in the repository root, then run:

```bash
python -m src.CLI <productName> --mode CLI
```

or, on systems where Python 3 is invoked as `python3`:

```bash
python3 -m src.CLI <productName> --mode CLI
```

| Mode | What it does |
| ---- | ------------ |
| `--mode CLI` | Runs ShopWise in the terminal — results are shown in an interactive table |
| `--mode GUI` | Opens the graphical user interface (desktop application window) |

> The mode is case-insensitive: `cli` and `gui` work too.

---

### Command-Line Reference

```
usage: python -m src.CLI [-h] -m {CLI,GUI} [--maxProducts N] [--maxSearch N] [-g] [--maxPages N] [--HTTPPerStore N] [-b N] [-r SECONDS] [-p SECONDS] [-v]
                         PRODUCT_NAME [PRODUCT_NAME ...]

ShopWise - search a product across stores and compare results.

positional arguments:
  PRODUCT_NAME          name of the product to search for (quotes are optional for multiple words)

options:
  -h, --help            show this help message and exit
  -m, --mode {CLI,GUI}  interface to run: CLI or GUI (case-insensitive)
  --maxProducts N       maximum number of products to return
  --maxSearch N         maximum number of search results to consider
  -g, --getReviews      also fetch product reviews
  --maxPages N          maximum number of result pages to scan per store
  --HTTPPerStore N      number of concurrent HTTP requests per store
  -b, --browserTabs N   number of browser tabs to use
  -r, --requestTimeout SECONDS
                        timeout for each request, in seconds
  -p, --productTimeLimit SECONDS
                        time limit for processing a single product, in seconds
  -v, --verbose         enable verbose output
```

### Examples

```bash
# Search for an iPhone 15 in the terminal
python -m src.CLI iphone 15 -m CLI

# Open the graphical interface, get up to 10 products per store, with reviews
python -m src.CLI "gaming mouse" --mode GUI --maxProducts 10 -g

# Scan up to 3 pages per store with 4 browser tabs and a 20s request timeout
python -m src.CLI laptop -m CLI --maxPages 3 -b 4 -r 20 -v
```

> Product names with spaces can be written with or without quotes — `iphone 15` and `"iphone 15"` are equivalent.

---

## How Products Are Scored

Each product earns points across four dimensions:

1. **Price position** — prices are split into quartiles and checked for outliers (IQR rule). The best-priced offers (lowest quartile) earn the most points; outliers earn none.
2. **Rating** — higher average ratings (out of 5) earn more points.
3. **Rating volume** — a larger number of ratings means a more trustworthy score and earns more points.
4. **Review sentiment** — every collected review is translated to English and analyzed for severity (positive / neutral / mildly negative / severely negative), and the results are combined into the product's total.

The totals are then used to sort the results and to color-code offers: 🥇 **gold** = best overall value, 🔵 **blue** = cheapest, 🔴 **red** = the five lowest-scoring offers, ⚪ white = everything in between.**Note that these colors only appears in the GUI.**

---

## Supported Regions & Stores

ShopWise auto-detects your region and searches the major stores for it — including the US, Canada, Mexico, Brazil, the UK, Germany, France, Italy, Spain, the Netherlands, Turkey, Japan, China, South Korea, India, Australia, Saudi Arabia and many more (35+ regions, 150+ store domains in total).

The complete mapping lives in [`src/Constants/Constants.py`](src/Constants/Constants.py). If you want to add or remove stores for your region, edit the `STORES_BY_REGION` dictionary there.

---

## Team

| Member | Contribution |
| ------ | ------------ |
| **Muhammed Bekiroğlu** *(team lead)* | Project organization & task distribution; scraping and filtering engine (`Constants`, `Helpers`, `Operations`, `DataAcquisition`), settings system |
| **Ömer Ağaoğlu** | GUI architecture and components (PySide6), visual styling & UX |
| **Abdulrab Almusali** | Product rating algorithms; review translation utility |
| **Y.H.Y.M Bakr Raiyan** | Sentiment analysis (NLTK/VADER); project presentation |
| **Bashir Alzoubi** | Presentation animations |

Individual, detailed contribution reports are available in the [`contributions/`](contributions/) directory.

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
- [Automatic Setup (Recommended)](#automatic-setup-recommended)
- [Manual Setup](#manual-setup)
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
2. It **maps every regional store** to its own search page using built-in templates and finds the product on each one.
3. It **scrapes every listing and product page** concurrently, extracting the product name, price, rating, review count, image and customer reviews.
4. It **analyzes the results** — translating reviews to English, scoring their sentiment, and combining price, rating and review data into a single ranking.
5. It **presents a ranked comparison** in a beautiful terminal table (or a graphical interface), with the best overall value first.

---

## Features

- 🌍 **Region-aware store discovery** — auto-detects your country (IP geolocation) and hits a curated list of 150+ store domains across 35+ regions directly through their own search pages, with no search engine in between.
- ⚡ **Dual fetching engine** — ultra-fast HTTP requests that impersonate Google Chrome (`curl_cffi`), with automatic fallback to a stealth headless browser (Playwright/Chromium) whenever a store's anti-bot protection blocks plain requests.
- 🧲 **Deep product extraction** — pulls structured data from JSON-LD, microdata, embedded JSON and DOM heuristics, so it works even on stores without consistent markup.
- 💬 **Review intelligence** — crawls paginated reviews, clicks "show more" buttons in the browser, **learns each store's internal review API** and reuses it for the remaining products, translates reviews to English, and scores their sentiment.
- 🏆 **Smart ranking** — every product earns a continuous **value score** (`rating quality ÷ price ratio − review penalty`), then gets color-coded: **gold** (best value), **blue** (cheapest), **red** (lowest scores) and white. Colors only show in GUI mode.
- 🖥️ **Interactive CLI** — a rich, colorized results table; type a product's number to open its store page directly in your browser.
- 🎨 **Modern GUI** — a polished PySide6 desktop interface with a live search bar, product cards, loading states and smooth scrolling, powered by the same scraping engine as the CLI.
- 🧵 **Concurrency & rate control** — per-store request slots, browser-tab limits, priority-based task scheduling and per-request/per-product timeouts keep scraping fast while staying polite to the stores.
- 🛡️ **Anti-bot resilience** — Chrome fingerprinting, realistic user agents, `navigator.webdriver` masking, referer spoofing, cookie sharing between the browser and HTTP sessions, and automatic block detection.

---

## How It Works

```
CLI arguments ──► Region auto-detection ──► Store search pages (built-in templates)
                                                    │
                                                    ▼
   Ranked results ◄── Scoring & sentiment analysis ◄── Review collection
                                                    ▲
                                                    │
                              Product pages ◄── Listing scraping (HTTP first, browser fallback)
```

1. **Parse arguments** — the product name, limits and timeouts are read from the command line (entering `GUI` as the name opens the graphical interface instead).
2. **Detect region** — the user's country code is resolved via `ipapi.co` and mapped to a regional store list.
3. **Resolve stores** — the user's region is detected and every regional store is mapped instantly to its search-results URL using the built-in templates.
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
| Store discovery  | Direct store search-page templates (no search engine) |
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
│   ├── ABDULRAB_ALMUSALI_2409115801_AbdulrabAlmusali.md      # Abdulrab Almusali
│   ├── BASHIR_ALZOUBI_2409115364_bashir515.md                # Bashir Alzoubi
│   ├── MUHAMMED_BEKIROĞLU_2509115185_mohamad1234567891.md   # Muhammed Bekiroğlu (team lead)
│   ├── OMER_AGAOGLU_2509115344_omeragaoglu.md.md            # Ömer Ağaoğlu
│   └── Y.H.Y.M_BAKR_RAIYAN_2309116473_yrayan-coder.md       # Y.H.Y.M Bakr Raiyan
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
│   │   │       ├── FindRegion.py           # Region detection & store search-page templates
│   │   │       └── Scraper.py              # Scraping pipeline shared by the CLI and the GUI
│   │   └── DataAnalysis/
│   │       ├── RelevanceAnalysis.py        # Query-aware product-name matching
│   │       ├── SentimentAnalysis.py        # VADER-based review sentiment scoring
│   │       ├── StatisticalAnalysis.py      # Scoring, ranking & color-coding
│   │       └── Translator.py               # Detects & translates reviews to English
│   ├── GUI/
│   │   ├── Components/
│   │   │   ├── Button.py                   # "View Offer" button that opens product URLs
│   │   │   ├── Card.py                     # Product card (image, price, rating, badges)
│   │   │   ├── loading.py                  # Animated loading indicator
│   │   │   ├── Scroll.py                   # Scrollable results container
│   │   │   └── SearchBar.py                # Search bar with suggestions & signals
│   │   └── Core/
│   │       ├── Window.py                   # Main application window & GUI entry point (PySide6)
│   │       └── GUISrapeWorker.py           # Background thread running the scraping engine for the GUI
│   ├── Helpers/
│   │   └── HTTPHelper.py                   # Anti-bot / block-page detection
│   ├── Operations/
│   │   ├── DictionaryOperations.py         # Dictionary helper functions
│   │   ├── HTMLOperations.py               # HTML parsing, semantics & microdata
│   │   ├── JsonOperations.py               # Embedded JSON & JSON-LD extraction
│   │   ├── MathOperations.py               # Rating conversion to a 0-5 scale
│   │   ├── StringOperations.py             # Text cleaning, numbers, reviews & names
│   │   ├── ThreadOperations.py             # Worker pools & async dispatch
│   │   └── URLOperations.py                # URL cleaning, IDs & link patterns
│   └── products.json                       # Sample exported search results
├── Setup.py                                # One-command, cross-platform setup script
├── requirements.txt                        # Python dependencies
├── .gitignore
└── README.md
```

> Generated folders such as `.venv/` and `__pycache__/` are git-ignored and intentionally not shown.

---

## Prerequisites

- **Python 3.10 or newer** ([python.org](https://www.python.org/downloads/))
- **Git** ([git-scm.com](https://git-scm.com/downloads))
- An **internet connection** (the first run also downloads NLTK language resources automatically)

---

## Automatic Setup (Recommended)

The fastest way to get ShopWise running is the bundled [`Setup.py`](Setup.py) script. It performs the entire setup for you and **prints everything that is happening** to the terminal as it runs. It is **cross-platform** (Windows, macOS and Linux) and uses **only Python's standard library**, so nothing needs to be installed to run it.

After cloning the repository, simply run:

```bash
cd ShopWise
python3 Setup.py
```

> On Windows, use `python Setup.py` (or `py Setup.py`).

The script will:

1. Pick a suitable Python interpreter (3.10 or newer).
2. Create the virtual environment `.venv`.
3. Upgrade `pip` inside the environment.
4. Install all dependencies from `requirements.txt`.
5. Install the Playwright **Chromium** browser used by the scraper.
6. Download the NLTK language resources used by the sentiment analysis.
7. Ask whether to install the optional **Argos Translate** language models for review translation (default: **yes** — just press Enter). Installing Translations would give better results, because it translates people's product reviews for analysis which would then be used in ranking the product.
8. Verify that every dependency imports correctly.

You can also control step 7 from the command line:

```bash
python3 Setup.py --install-translations   # install them without asking
python3 Setup.py --skip-translations      # skip them without asking
```

When the script finishes, the setup is complete — activate the environment and run ShopWise as described in [Running ShopWise](#running-shopwise).

> ✋ **Prefer to do everything by hand?** You can skip this section entirely and follow the [manual setup instructions](#manual-setup) below — `Setup.py` simply automates those same steps.

> ⚠️ **Seeing a `ModuleNotFoundError: No module named ...` when running ShopWise?**
>
> If, after the setup, you try to run ShopWise with something like `python -m src.CLI "iphone 17"` and get an error like this (any "No module named ..." dependency, for example `requests`, `PySide6`, or `curl_cffi`):
>
> ```
> Traceback (most recent call last):
>   File "<frozen runpy>", line 203, in _run_module_as_main
>   File "<frozen runpy>", line 88, in _run_code
>   File ".../ShopWise/src/CLI.py", line 8, in <module>
>     from src.Core.DataAcquisition.Scraping import Scraper
>   File ".../ShopWise/src/Core/DataAcquisition/Scraping/Scraper.py", line 10, in <module>
>     from src.Core.DataAcquisition.Scraping import FindRegion
> ModuleNotFoundError: No module named 'requests'
> ```
>
> it means the virtual environment is **not active** — the packages were installed inside `.venv`, so Python must run from inside it. Activate the environment first, depending on your operating system and terminal:
>
> **Linux — bash / zsh**
>
> ```bash
> source .venv/bin/activate
> ```
>
> **Linux — fish**
>
> ```fish
> source .venv/bin/activate.fish
> ```
>
> **macOS — bash / zsh (default terminal)**
>
> ```bash
> source .venv/bin/activate
> ```
>
> **macOS — fish**
>
> ```fish
> source .venv/bin/activate.fish
> ```
>
> **Windows — Command Prompt (cmd)**
>
> ```cmd
> .venv\Scripts\activate
> ```
>
> **Windows — PowerShell**
>
> ```powershell
> .venv\Scripts\Activate.ps1
> ```

---

## Manual Setup

If you prefer to run every step yourself (or want to know exactly what `Setup.py` does), follow the instructions below.

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
python -m src.CLI <productName>          # runs in the terminal (CLI mode)
python -m src.CLI GUI                    # opens the graphical user interface
```

or, on systems where Python 3 is invoked as `python3`:

```bash
python3 -m src.CLI <productName>         # runs in the terminal (CLI mode)
python3 -m src.CLI GUI                   # opens the graphical user interface
```

| Command | What it does |
| ------- | ------------ |
| `python -m src.CLI <productName>` | Searches for the product and shows the ranked results in an interactive terminal table (CLI mode) |
| `python -m src.CLI GUI` | Opens the graphical user interface (desktop application window) |

> `GUI` is the keyword that launches the interface, and it is case-insensitive — `gui`, `Gui` and `GUI` all work.

> 💡 **Tip — be specific for accurate results.** To get the most out of ShopWise, always be as specific as possible with the product name. Instead of something generic like `iphone`, `samsung` or `phone`, search for the exact model — for example `samsung s24` or `iphone 17`. ShopWise scores offers by comparing the **same product** across different sellers and stores; a vague name can make it compare different products against each other, which leads to misleading results.

---

### Command-Line Reference

```
usage: python -m src.CLI [-h] [--maxProducts N] [--maxSearch N] [-g] [--maxPages N] [--HTTPPerStore N] [-b N] [-r SECONDS] [-p SECONDS] [-v]
                         [-c FACTOR] [--minFactor FACTOR] [--maxFactor FACTOR]
                         PRODUCT_NAME [PRODUCT_NAME ...]

ShopWise - search a product across stores and compare results.

positional arguments:
  PRODUCT_NAME          name of the product to search for (quotes are optional for multiple words);
                        use the keyword GUI instead to open the graphical interface

options:
  -h, --help            show this help message and exit
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
  -c, --cluster FACTOR  price gap (x) that starts a new price cluster (default: 1.5)
  --minFactor FACTOR    keep clusters priced above this x the main cluster median (default: 0.45)
  --maxFactor FACTOR    keep clusters priced below this x the main cluster median (default: 2.2)
```

### Examples

```bash
# Search for an iPhone 15 in the terminal (CLI mode)
python -m src.CLI iphone 15

# Open the graphical user interface (case-insensitive keyword)
python -m src.CLI GUI

# Get up to 10 products per store and fetch their reviews (CLI mode)
python -m src.CLI "gaming mouse" --maxProducts 10 -g

# Scan up to 3 pages per store with 4 browser tabs and a 20s request timeout
python -m src.CLI laptop --maxPages 3 -b 4 -r 20 -v

# Tune the price-cluster logic (gap factor, min/max keep factors)
python -m src.CLI "huawei matepad 12x" -c 2.0 --minFactor 0.5 --maxFactor 3.0
```

> Product names with spaces can be written with or without quotes — `iphone 15` and `"iphone 15"` are equivalent.

---

## How Products Are Scored

Every product that survives the relevance and price-cluster filters earns a continuous **value score**:

1. **Price ratio** — the product's price divided by the cheapest offer in the dominant price cluster (1.0 = cheapest). Offers from nearby clusters (other storage sizes or variants) are treated as twice the price, so they cannot outrank the real product.
2. **Rating quality** — a **Wilson lower-bound** score of the star rating. This is the standard way to rank rated items: a 5.0★ with 1 review scores far below a 4.7★ with 5000 reviews, so unreliable ratings can never win. Products without a rating get a neutral quality floor and are then ranked purely by price.
3. **Review sentiment penalty** — reviews are translated to English and each one is classified (positive / neutral / mildly negative / severely negative); the average severity subtracts a small penalty from the value.

The final score is `value = rating quality ÷ price ratio − review penalty`, and the results are sorted from the highest value to the lowest.

The colors: 🥇 **gold** = best value, 🔵 **blue** = cheapest offer, 🔴 **red** = the five lowest scores, ⚪ white = everything in between. **Note that these colors only appears in the GUI.**

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

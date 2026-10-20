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

Command-line argument parsing for the CLI. Defines the PositiveInt and PositiveFloat argparse types (values must be >= 1 and > 0) and builds the parser for the product name plus all scraping options, which default to the values in Settings.py.
"""

import argparse


def PositiveInt(value: str) -> int:
    """argparse type: accepts only integers >= 1."""
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a valid integer")
    if number < 1:
        raise argparse.ArgumentTypeError(f"'{value}' must be 1 or greater")
    return number


def PositiveFloat(value: str) -> float:
    """argparse type: accepts only numbers > 0."""
    try:
        number = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a valid number")
    if number <= 0:
        raise argparse.ArgumentTypeError(f"'{value}' must be greater than 0")
    return number


def parseArguments(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Usage: python -m src.CLI <product name> [options]

    Mandatory: product name. Everything else is optional and defaults to the
    values in Settings.py (or False for flags).
    """


    parser = argparse.ArgumentParser(
        prog="python -m src.CLI",
        description="ShopWise - search a product across stores and compare results.",
        epilog=(
            "examples:\n"
            "  python -m src.CLI iphone 15\n"
            "  python -m src.CLI GUI\n"
            "  python -m src.CLI \"gaming mouse\" --maxProducts 10 -g\n"
            "  python -m src.CLI laptop --maxPages 3 -b 4 -r 20 -v"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "productName",
        nargs="+",
        metavar="PRODUCT_NAME",
        help="name of the product to search for (quotes are optional for multiple words); use the keyword GUI instead to open the graphical interface",
    )
    parser.add_argument("--maxProducts", type=PositiveInt, metavar="N",
                        help="maximum number of products to return")
    parser.add_argument("--maxSearch", type=PositiveInt, metavar="N",
                        help="maximum number of search results to consider")
    parser.add_argument("-g", "--getReviews", action="store_true",
                        help="also fetch product reviews")
    parser.add_argument("--maxPages", type=PositiveInt, metavar="N",
                        help="maximum number of result pages to scan per store")
    parser.add_argument("--HTTPPerStore", type=PositiveInt, metavar="N",
                        help="number of concurrent HTTP requests per store")
    parser.add_argument("-b", "--browserTabs", type=PositiveInt, metavar="N",
                        help="number of browser tabs to use")
    parser.add_argument("-r", "--requestTimeout", type=PositiveInt, metavar="SECONDS",
                        help="timeout for each request, in seconds")
    parser.add_argument("-p", "--productTimeLimit", type=PositiveInt, metavar="SECONDS",
                        help="time limit for processing a single product, in seconds")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="enable verbose output")
    parser.add_argument("-c", "--cluster", type=PositiveFloat, metavar="FACTOR",
                        help="price gap (x) that starts a new price cluster (default: 1.5)")
    parser.add_argument("--minFactor", type=PositiveFloat, metavar="FACTOR",
                        help="keep clusters priced above this x the main cluster median (default: 0.45)")
    parser.add_argument("--maxFactor", type=PositiveFloat, metavar="FACTOR",
                        help="keep clusters priced below this x the main cluster median (default: 2.2)")

    args = parser.parse_intermixed_args(argv)

    args.productName = " ".join(args.productName).strip()
    if not args.productName:
        parser.error("PRODUCT_NAME must not be empty")

    return args
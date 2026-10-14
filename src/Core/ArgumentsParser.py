import argparse


def _positiveInt(value: str) -> int:
    """argparse type: accepts only integers >= 1."""
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a valid integer")
    if number < 1:
        raise argparse.ArgumentTypeError(f"'{value}' must be 1 or greater")
    return number


def parseArguments(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Usage: python main.py <product name> -m {CLI,GUI} [options]

    Mandatory: product name and --mode. Everything else is optional and
    defaults to None (or False for flags).
    """
    parser = argparse.ArgumentParser(
        prog="python main.py",
        description="ShopWise - search a product across stores and compare results.",
        epilog=(
            "examples:\n"
            "  python main.py iphone 15 -m CLI\n"
            "  python main.py \"gaming mouse\" --mode GUI --maxProducts 10 -g\n"
            "  python main.py laptop -m CLI --maxPages 3 -b 4 -r 20 -v"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "productName",
        nargs="+",
        metavar="PRODUCT_NAME",
        help="name of the product to search for (quotes are optional for multiple words)",
    )
    parser.add_argument(
        "-m", "--mode",
        required=True,
        type=str.upper,
        choices=["CLI", "GUI"],
        help="interface to run: CLI or GUI (case-insensitive)",
    )

    parser.add_argument("--maxProducts", type=_positiveInt, metavar="N",
                        help="maximum number of products to return")
    parser.add_argument("--maxSearch", type=_positiveInt, metavar="N",
                        help="maximum number of search results to consider")
    parser.add_argument("-g", "--getReviews", action="store_true",
                        help="also fetch product reviews")
    parser.add_argument("--maxPages", type=_positiveInt, metavar="N",
                        help="maximum number of result pages to scan per store")
    parser.add_argument("--HTTPPerStore", type=_positiveInt, metavar="N",
                        help="number of concurrent HTTP requests per store")
    parser.add_argument("-b", "--browserTabs", type=_positiveInt, metavar="N",
                        help="number of browser tabs to use")
    parser.add_argument("-r", "--requestTimeout", type=_positiveInt, metavar="SECONDS",
                        help="timeout for each request, in seconds")
    parser.add_argument("-p", "--productTimeLimit", type=_positiveInt, metavar="SECONDS",
                        help="time limit for processing a single product, in seconds")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="enable verbose output")

    args = parser.parse_intermixed_args(argv)

    args.productName = " ".join(args.productName).strip()
    if not args.productName:
        parser.error("PRODUCT_NAME must not be empty")

    return args
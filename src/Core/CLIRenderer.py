import sys
import webbrowser
from urllib.parse import urlparse

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from src.Constants import Constants as C


def _make_console():
    if sys.stdout.isatty():
        return Console(force_terminal=True, color_system="standard")
    return Console()


def _is_valid_url(url):
    try:
        parsed = urlparse(url)
    except (ValueError, AttributeError):
        return False
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def _open_url(console: Console, url):
    try:
        if not webbrowser.open(url, new=2):
            console.print("[yellow]Could not open a browser. Copy the link manually:[/yellow]")
            console.print(url, markup=False, highlight=False, soft_wrap=True)
    except Exception as exc:
        console.print(f"[red]Failed to open browser:[/red] {exc}")


def _format_price(value):
    if isinstance(value, (int, float)):
        return f"{value:,.2f}"
    return str(value) if value not in (None, "") else "-"


def FormatCount(value):
    if isinstance(value, bool):
        return "-"
    if isinstance(value, (int, float)):
        return f"{int(value):,}"
    return str(value) if value not in (None, "", "N/A") else "-"


# The color of each row in the terminal table and the legend text both live
# in Constants.py, shared with the GUI.


def DisplayOnCli(products):
    console = _make_console()

    if not products:
        console.print("[yellow]No products to display.[/yellow]")
        return

    table = Table(
        title="ShopWise Results",
        box=box.ROUNDED,
        header_style="bold cyan",
        show_lines=True,
    )
    table.add_column("#", justify="right", style="dim", no_wrap=True)
    table.add_column("Product Name", overflow="fold")
    table.add_column("Rating", justify="center", no_wrap=True)
    table.add_column("Rating Count", justify="right", no_wrap=True)
    table.add_column("Store Name", overflow="fold")
    table.add_column("Price", justify="right", no_wrap=True)

    valid_urls = {}

    for index, product in enumerate(products, start=1):
        url = str(product.get("productURL", "")).strip()
        rating = product.get("rating", product.get("reating"))

        if _is_valid_url(url):
            valid_urls[index] = url

        table.add_row(
            str(index),
            str(product.get("productName", "-")),
            str(rating) if rating not in (None, "") else "-",
            FormatCount(product.get("ratingAmount")),
            str(product.get("storeName", "-")),
            _format_price(product.get("price")),
            style=C.ROW_COLORS.get(str(product.get("color", "")).lower()),
        )

    console.print(table)

    if not console.is_terminal:
        return

    # Printed once, before the interactive loop.
    console.print()
    console.print(
        "[yellow]Our top products are listed first, with the best options usually found "
        "in the top five. We recommend checking prices and reviews, as the fifth item "
        "can sometimes outmatch the first; however, the top five will almost always "
        "give you the best value.[/yellow]"
    )
    console.print(Panel(C.LEGEND_TEXT, title="Color Legend", border_style="dim", padding=(0, 2)))
    console.print()

    while True:
        choice = Prompt.ask(
            "\nEnter a product number to open its store page (q to finish, s for a new search)",
            default="",
            show_default=False,
            console=console,
        ).strip()

        if choice.lower() == "q":
            return False
        elif choice.lower() == "s":
            return True

        if not choice.isdigit() or int(choice) not in range(1, len(products) + 1):
            console.print("[red]Invalid input.[/red]")
            continue

        number = int(choice)
        if number not in valid_urls:
            console.print("[red]That product has no valid URL.[/red]")
            continue

        _open_url(console, valid_urls[number])
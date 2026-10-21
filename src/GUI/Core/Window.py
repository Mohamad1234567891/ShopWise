"""
This file is part of ShopWise, an open-source multi-region, multi-store
price-comparison and product-search engine.

Copyright (c) 2026 Muhammed Bekiroğlu and the ShopWise contributors.

Original ShopWise repository: https://github.com/Mohamad1234567891/ShopWise

Muhammed Bekiroğlu (ShopWise team leader and top contributor) YouTube channel:
    https://www.youtube.com/@ALShajaraComputerScienceInstit

Licensed under the Mozilla Public License 2.0 with Additional Attribution
Terms — see the LICENSE file.
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QGridLayout
)
from PySide6.QtCore import Qt

from src.Constants import Constants as C
from src.GUI.Components.Scroll import ScrollContainer
from src.GUI.Components.SearchBar import SearchBar
from src.GUI.Components.Card import ProductCard
from src.GUI.Components.loading import SmallLoader

from src.GUI.Core import GUISrapeWorker as GSW
from src.GUI.Components.EmojiIcon import EmojiIcon

class Window(QMainWindow):
    """Main ShopWise window: search bar, color-legend box, loading hint and the scrollable product-card grid; launches a background ScrapeWorker per search and renders the results as cards."""
    def __init__(self):
        super().__init__()
        self.worker = None

        self.setWindowTitle("ShopWise")
        self.setWindowIcon(EmojiIcon("🛒"))
        self.resize(850, 650)
        self.setMinimumSize(345, 560)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.layout = QVBoxLayout(central_widget)
        self.layout.setContentsMargins(20, 20, 30, 20)
        self.layout.setSpacing(12)

        self.logo_space = QWidget()
        self.logo_space.setFixedHeight(30)
        self.layout.addWidget(self.logo_space)

        search_row = QHBoxLayout()
        search_row.setContentsMargins(0, 0, 0, 0)
        search_row.setSpacing(10)

        suggestions = ["Samsung Galaxy S25 256GB", "Apple iPhone 16", "Google Pixel 9"]
        self.search_bar = SearchBar(suggestions=suggestions)
        self.search_bar.setMaximumWidth(700)


        self.loader = SmallLoader(size=24)

        search_row.addStretch()
        search_row.addWidget(self.search_bar)
        search_row.addWidget(self.loader)
        search_row.addStretch()

        self.layout.addLayout(search_row)
        self.search_bar.search_submitted.connect(self.on_search)

        # Color legend box - sits under the search bar, above the results,
        # and never overlaps the loading hint (which appears below it).
        # The text comes from the same constants the CLI legend uses.
        legendBox = QFrame()
        legendBox.setObjectName("LegendBox")
        legendBox.setStyleSheet("""
            QFrame#LegendBox {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 10px;
            }
        """)
        legendGrid = QGridLayout(legendBox)
        legendGrid.setContentsMargins(14, 10, 14, 10)
        legendGrid.setHorizontalSpacing(14)
        legendGrid.setVerticalSpacing(6)
        legendGrid.setColumnStretch(0, 1)
        legendGrid.setColumnStretch(1, 1)

        for index, (title, richColor, htmlColor, description) in enumerate(C.LEGEND_ITEMS):
            row, column = divmod(index, 2)

            itemWidget = QWidget()
            itemLayout = QHBoxLayout(itemWidget)
            itemLayout.setContentsMargins(0, 0, 0, 0)
            itemLayout.setSpacing(6)

            dotLabel = QLabel("●")
            dotLabel.setFixedWidth(14)
            dotLabel.setStyleSheet(f"color: {htmlColor}; font-size: 12px; background: transparent;")

            textLabel = QLabel(f"<b>{title}</b> — {description}")
            textLabel.setTextFormat(Qt.RichText)
            textLabel.setWordWrap(True)
            textLabel.setToolTip(description)
            textLabel.setStyleSheet("color: #cbd5e1; font-size: 10px; background: transparent;")

            itemLayout.addWidget(dotLabel, 0, Qt.AlignTop)
            itemLayout.addWidget(textLabel, 1)
            legendGrid.addWidget(itemWidget, row, column)

        self.layout.addWidget(legendBox)

        # No-results message - sits right under the color legend and shows
        # in yellow when a search ends with zero products.
        self.noResultsLabel = QLabel("No products was found")
        self.noResultsLabel.setAlignment(Qt.AlignCenter)
        self.noResultsLabel.setStyleSheet("""
            QLabel {
                color: #ca8a04;
                font-size: 14px;
                font-weight: 600;
                letter-spacing: 0.3px;
                background: transparent;
                padding-top: 2px;
            }
        """)

        self.noResultsLabel.hide()
        self.layout.addWidget(self.noResultsLabel)

        self.loading_hint = QLabel("Scraping the network, hold on this might take about 30 seconds...")
        self.loading_hint.setAlignment(Qt.AlignCenter)
        self.loading_hint.setStyleSheet("""
            QLabel {
                color: #94a3b8;
                font-size: 13px;
                font-weight: 500;
                letter-spacing: 0.3px;
                background: transparent;
                padding-top: 2px;
            }
        """)

        self.loading_hint.hide()
        self.layout.addWidget(self.loading_hint)


        self.scroll_container = ScrollContainer()
        self.layout.addWidget(self.scroll_container)

    def on_search(self, query):          # note: plain def, not async
        if self.worker is not None and self.worker.isRunning():
            return                       # ignore a second search while one is running

        self.scroll_container.clear()
        self.noResultsLabel.hide()

        self.loader.start()
        self.loading_hint.show()

        self.worker = GSW.ScrapeWorker(query, self)
        self.worker.finished_ok.connect(self.on_results)
        self.worker.failed.connect(self.on_error)
        self.worker.finished.connect(self.stop_loading_ui)   # runs on success and failure
        self.worker.start()

    def on_results(self, products, stats):
        if not products:
            self.noResultsLabel.show()
            return

        for product in products:
            card = ProductCard(product["storeName"], product["productName"], product["imageURL"], product["price"], product["rating"], product["ratingAmount"], "view Offer", product["productURL"], product["color"])
            self.scroll_container.add_item(card)


    def on_error(self, message):
        print(f"[!] Search failed: {message}")

    def stop_loading_ui(self):
        self.loader.close_loading()
        self.loading_hint.hide()


def StartGUI():
    """Starts the graphical user interface"""

    app = QApplication(sys.argv)
    app.setWindowIcon(EmojiIcon("🛒"))
    window = Window()
    window.show()
    sys.exit(app.exec())
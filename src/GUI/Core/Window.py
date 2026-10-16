import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
)
from PySide6.QtCore import Qt

from src.GUI.Components.Scroll import ScrollContainer
from src.GUI.Components.SearchBar import SearchBar
from src.GUI.Components.Card import ProductCard
from src.GUI.Components.loading import SmallLoader

from src.GUI.Core import GUISrapeWorker as GSW
from src.GUI.Components.EmojiIcon import EmojiIcon

class Window(QMainWindow):
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

        self.loading_hint = QLabel("Scraping the network, hold on this might take from 2 to 3 minutes...")
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

        self.loader.start()
        self.loading_hint.show()

        self.worker = GSW.ScrapeWorker(query, self)
        self.worker.finished_ok.connect(self.on_results)
        self.worker.failed.connect(self.on_error)
        self.worker.finished.connect(self.stop_loading_ui)   # runs on success and failure
        self.worker.start()

    def on_results(self, products, stats):
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
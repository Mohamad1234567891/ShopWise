import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QPen

from src.GUI.Components import Button
from src.GUI.Components.Scroll import ScrollContainer
from src.GUI.Components.SearchBar import SearchBar
from src.GUI.Components.Card import ProductCard


class SmallLoader(QWidget):


    def __init__(self, size: int = 24, parent=None):
        super().__init__(parent)
        self.size_val = size
        self.setFixedSize(size, size)
        self.angle = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._rotate)
        self.hide()

    def start(self):
        self.angle = 0
        self.show()
        self.timer.start(16)

    def close_loading(self):
        self.timer.stop()
        self.hide()

    def _rotate(self):
        self.angle = (self.angle + 8) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen()
        pen.setWidth(3)
        pen.setCapStyle(Qt.RoundCap)


        pen.setColor(QColor(255, 255, 255, 25))
        painter.setPen(pen)
        margin = 3
        draw_size = self.size_val - (margin * 2)
        painter.drawEllipse(margin, margin, draw_size, draw_size)


        pen.setColor(QColor("#38bdf8"))
        painter.setPen(pen)
        painter.drawArc(margin, margin, draw_size, draw_size, -self.angle * 16, 90 * 16)


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ShopWise")
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

        self.loading_hint = QLabel("This might take a few minutes...")
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

    def on_search(self, query):
        print(f"User searched for: {query}")

        self.loader.start()
        self.loading_hint.show()

        # self.stop_loading_ui()

    def stop_loading_ui(self):
        self.loader.close_loading()
        self.loading_hint.hide()


app = QApplication(sys.argv)
window = Window()

card1 = ProductCard(
    store_name="Amazon",
    product_name="Samsung Galaxy S25 256GB - Phantom Black",
    image_url="https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=400",
    price="₺42,490",
    rating=4.8,
    button_text="View Offer",
    button_url="https://www.amazon.com",
    color="blue"
)


card2 = ProductCard(
    store_name="Hepsiburada",
    product_name="Samsung Galaxy S25 256GB - Phantom Black",
    image_url="https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=400",
    price="₺41,430",
    rating=3.4,
    button_text="View Offer",
    button_url="https://www.amazon.com"
    ,color="gold"
)
card3 = ProductCard(
    store_name="Trendyol",
    product_name="Samsung Galaxy S25 256GB - Phantom Black",
    image_url="https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=400",
    price="₺40,100",
    rating=4.0,
    button_text="View Offer",
    button_url="https://www.amazon.com",
    color="red"
)
card3.brockProdact()
card3.lowRating()
card3.lowPrice()
card3.proplemProdact()
card4 = ProductCard(
    store_name="Trendyol",
    product_name="Samsung Galaxy S25 256GB - Phantom Black",
    image_url="https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=400",
    price="₺40,100",
    rating=4.0,
    button_text="View Offer",
    button_url="https://www.amazon.com"
)
card5 = ProductCard(
    store_name="Trendyol",
    product_name="Samsung Galaxy S25 256GB - Phantom Black",
    image_url="https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=400",
    price="₺40,100",
    rating=4.0,
    button_text="View Offer",
    button_url="https://www.amazon.com"
)
card6 = ProductCard(
    store_name="Trendyol",
    product_name="Samsung Galaxy S25 256GB - Phantom Black",
    image_url="https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=400",
    price="₺40,100",
    rating=4.0,
    button_text="View Offer",
    button_url="https://www.amazon.com"
)

window.scroll_container.add_item(card1)
window.scroll_container.add_item(card2)
window.scroll_container.add_item(card3)
window.scroll_container.add_item(card4)
window.scroll_container.add_item(card5)
window.scroll_container.add_item(card6)

window.show()
sys.exit(app.exec())
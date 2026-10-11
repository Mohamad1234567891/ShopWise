import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout
)
from PySide6.QtCore import Qt
from src.GUI.Components import Button
from src.GUI.Components.Scroll import ScrollContainer
from src.GUI.Components.SearchBar import SearchBar
from src.GUI.Components.Card import ProductCard


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ShopWise")
        self.resize(850, 650)
        self.setMinimumSize(345, 560)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.layout = QVBoxLayout(central_widget)
        self.layout.setContentsMargins(30, 20, 30, 20)
        self.layout.setSpacing(15)

        # مساحة اللوجو
        self.logo_space = QWidget()
        self.logo_space.setFixedHeight(30)
        self.layout.addWidget(self.logo_space)

        # شريط البحث
        suggestions = ["Samsung Galaxy S25 256GB", "Apple iPhone 16", "Google Pixel 9"]
        self.search_bar = SearchBar(suggestions=suggestions)
        self.layout.addWidget(self.search_bar, alignment=Qt.AlignCenter)
        self.search_bar.search_submitted.connect(self.on_search)

        self.scroll_container = ScrollContainer()
        self.layout.addWidget(self.scroll_container)

    def on_search(self, query):
        print(f"User searched for: {query}")


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
)
card3 = ProductCard(
    store_name="Trendyol",
    product_name="Samsung Galaxy S25 256GB - Phantom Black",
    image_url="https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=400",
    price="₺40,100",
    rating=4.0,
    button_text="View Offer",
    button_url="https://www.amazon.com"
)
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
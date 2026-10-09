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

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.layout = QVBoxLayout(central_widget)
        self.layout.setContentsMargins(30, 20, 30, 20)
        self.layout.setSpacing(15)


        self.logo_space = QWidget()
        self.logo_space.setFixedHeight(70)
        self.layout.addWidget(self.logo_space)


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
    button_url="https://www.amazon.com"
)
card2 = ProductCard(
    store_name="hepseburda",
    product_name="Samsung Galaxy S25 256GB - Phantom Black",
    image_url="https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=400",
    price="₺41,430",
    rating=3.4,
    button_text="View Offer",
    button_url="https://www.amazon.com"
)
card3 = ProductCard(
    store_name="Trandyol",
    product_name="Samsung Galaxy S25 256GB - Phantom Black",
    image_url="https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=400",
    price="₺40,100",
    rating=4.0,
    button_text="View Offer",
    button_url="https://www.amazon.com"
)


window.scroll_container.add_item(card1, row=0, col=0)
window.scroll_container.add_item(card2, row=0, col=1)
window.scroll_container.add_item(card3, row=0, col=2)


googleButton = Button.Button("Google", "https://www.google.com")
youtubeButton = Button.Button("Youtube", "https://www.youtube.com")
githubButton = Button.Button("Github", "https://www.github.com")

#window.scroll_container.add_item(googleButton, row=1, col=0)
#window.scroll_container.add_item(youtubeButton, row=1, col=1)
#window.scroll_container.add_item(githubButton, row=1, col=2)

#deepButton = Button.Button("Down Button", "https://www.google.com")
#window.scroll_container.add_item(deepButton, row=5, col=0)

window.show()
sys.exit(app.exec())
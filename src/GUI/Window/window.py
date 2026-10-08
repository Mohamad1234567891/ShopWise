import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout
)
from PySide6.QtCore import Qt
from src.GUI.Components import Button
from src.GUI.Components.Scroll import ScrollContainer
from src.GUI.Components.SearchBar import SearchBar


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
        self.layout.addWidget(self.search_bar)
        self.search_bar.search_submitted.connect(self.on_search)
        self.layout.addWidget(self.search_bar, alignment=Qt.AlignCenter)


        self.scroll_container = ScrollContainer()
        self.layout.addWidget(self.scroll_container)

    def on_search(self, query):
        print(f"User searched for: {query}")


app = QApplication(sys.argv)
window = Window()

googleButton = Button.Button("Google", "https://www.google.com")
youtubeButton = Button.Button("yotube", "https://www.youtube.com")
githubButton = Button.Button("Github", "https://www.github.com")

window.scroll_container.add_item(googleButton, row=7, col=0)
window.scroll_container.add_item(youtubeButton, row=7, col=3)
window.scroll_container.add_item(githubButton, row=7, col=6)

deepButton = Button.Button("Down Button", "https://www.google.com")
window.scroll_container.add_item(deepButton, row=25, col=1)

window.show()
sys.exit(app.exec())
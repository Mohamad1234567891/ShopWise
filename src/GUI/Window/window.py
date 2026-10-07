import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout
)
from src.GUI.Components import Button
from src.GUI.Components.Scroll import ScrollContainer

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ShopWise")
        self.resize(800, 600)


        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        self.layout = QVBoxLayout(centralWidget)

          #call the scroll class to but it in the window
        self.scroll_container = ScrollContainer()
        self.layout.addWidget(self.scroll_container)


app = QApplication(sys.argv)
window = Window()

googleButton = Button.Button("Google", "https://www.google.com")
youtubeButton = Button.Button("Youtube", "https://www.youtube.com")
githubButton = Button.Button("Github", "https://www.github.com")
gitbotoon = Button.Button("Github", "https://www.github.com")


window.scroll_container.add_item(googleButton)
window.scroll_container.add_item(youtubeButton)
window.scroll_container.add_item(githubButton)

for i in range(1, 20):#>>>>just a test to see if the Scroll working
    extra_btn = Button.Button(f"Store Offer #{i}", "https://google.com")
    window.scroll_container.add_item(extra_btn)



window.show()
sys.exit(app.exec())
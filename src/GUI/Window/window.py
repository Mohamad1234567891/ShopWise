import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from src.GUI.Components import Button

class Window(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("ShopWise")

        self.resize(800, 600)

        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        self.layout = QVBoxLayout(centralWidget)


app = QApplication(sys.argv)
window = Window()

googleButton = Button.Button("Google", "https://www.google.com")
youtubeButton = Button.Button("Youtube", "https://www.youtube.com")
githubButton = Button.Button("Github", "https://www.github.com")

window.layout.addWidget(googleButton)
window.layout.addWidget(youtubeButton)
window.layout.addWidget(githubButton)

window.show()
sys.exit(app.exec())
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton
from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices

class Button(QPushButton):
    def __init__(self, text, urlString):
        QPushButton.__init__(self, text)
        self.urlString = urlString
        self.clicked.connect(self.OnClicked)

    def OnClicked(self):
        url = QUrl(self.urlString)
        QDesktopServices.openUrl(url)



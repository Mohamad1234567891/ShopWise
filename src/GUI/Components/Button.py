from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton
from PySide6.QtCore import QUrl,Qt
from PySide6.QtGui import QDesktopServices,QCursor

class Button(QPushButton):
    def __init__(self, text, urlString):
        QPushButton.__init__(self, text)
        self.urlString = urlString
        self.clicked.connect(self.OnClicked)


        #style using Qt,QCursor
        self.setFixedSize(110, 34)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setStyleSheet("""
                    QPushButton {
                        background-color: #1f3a52;
                        color: #ffffff;
                        font-size: 13px;
                        font-weight: 600;
                        border-radius: 17px;
                        border: none;
                        padding: 4px 10px;
                    }
                    QPushButton:hover {
                        background-color: #2b4f70;
                    }
                    QPushButton:pressed {
                        background-color: #142738;
                    }
                """)


    def OnClicked(self):
        url = QUrl(self.urlString)
        QDesktopServices.openUrl(url)



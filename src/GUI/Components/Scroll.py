from PySide6.QtWidgets import QWidget, QScrollArea, QGridLayout, QFrame
from PySide6.QtCore import Qt


class ScrollContainer(QScrollArea):
    def __init__(self, columns=3, parent=None):
        super().__init__(parent)

        self.columns = columns
        self.item_count = 0

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)
        self.setAlignment(Qt.AlignHCenter)

        self.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
        """)

        self.content_widget = QWidget()
        self.content_widget.setMaximumWidth(1020)
        self.content_widget.setStyleSheet("background: transparent;")

        self.content_layout = QGridLayout(self.content_widget)
        self.content_layout.setSpacing(25)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        for c in range(self.columns):
            self.content_layout.setColumnStretch(c, 1)

        self.setWidget(self.content_widget)

    def add_item(self, widget, row=None, col=None):
        if row is not None and col is not None:
            self.content_layout.addWidget(widget, row, col, alignment=Qt.AlignCenter)
            return

        auto_row = self.item_count // self.columns
        auto_col = self.item_count % self.columns

        self.content_layout.addWidget(widget, auto_row, auto_col, alignment=Qt.AlignCenter)
        self.item_count += 1
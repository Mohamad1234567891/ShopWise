from PySide6.QtWidgets import QWidget, QScrollArea, QGridLayout, QFrame
from PySide6.QtCore import Qt


class ScrollContainer(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.card_width = 280
        self.items = []

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)

        self.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
        """)

        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background: transparent;")

        self.content_layout = QGridLayout(self.content_widget)
        self.content_layout.setSpacing(20)
        self.content_layout.setContentsMargins(10, 10, 24, 10)
        self.content_layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        self.setWidget(self.content_widget)

    def add_item(self, widget):
        self.items.append(widget)
        self._rebuild_grid()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._rebuild_grid()

    def _rebuild_grid(self):
        if not self.items:
            return

        available_width = self.viewport().width() - 40
        if available_width <= 0:
            return


        columns = max(1, available_width // self.card_width)


        for i in range(self.content_layout.count()):
            item = self.content_layout.takeAt(0)


        for c in range(columns):
            self.content_layout.setColumnStretch(c, 1)


        for index, widget in enumerate(self.items):
            row = index // columns
            col = index % columns
            self.content_layout.addWidget(widget, row, col, alignment=Qt.AlignCenter)
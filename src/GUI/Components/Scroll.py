from PySide6.QtWidgets import QWidget, QScrollArea, QGridLayout, QFrame
from PySide6.QtCore import Qt


class ScrollContainer(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.card_width = 280
        self.spacing = 20
        self.items = []

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)
        self.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        self.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
        """)

        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background: transparent;")
        #product cards into an organized grid anchored to the top and centered horizontally.
        self.content_layout = QGridLayout(self.content_widget)
        self.content_layout.setSpacing(self.spacing)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
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

        # the view space
        viewport_w = self.viewport().width()
        margins_w = self.content_layout.contentsMargins().left() + self.content_layout.contentsMargins().right()
        usable_width = max(1, viewport_w - margins_w)

        # see the amount of the col accordig to size of card
        columns = max(1, (usable_width + self.spacing) // (self.card_width + self.spacing))

        # remove every think form layout
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)


        total_cols = columns + 2
        for c in range(total_cols + 2):
            self.content_layout.setColumnStretch(c, 0)

        self.content_layout.setColumnStretch(0, 1)
        self.content_layout.setColumnStretch(columns + 1, 1)


        for index, widget in enumerate(self.items):
            row = index // columns
            col = (index % columns) + 1
            self.content_layout.addWidget(widget, row, col, alignment=Qt.AlignCenter)
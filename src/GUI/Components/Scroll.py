from PySide6.QtWidgets import QWidget, QScrollArea, QGridLayout, QFrame
from PySide6.QtCore import Qt


class ScrollContainer(QScrollArea):
    def __init__(self, columns=6, parent=None):
        super().__init__(parent)

        self.columns = columns
        self.item_count = 0

        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.content_widget = QWidget()
        self.content_layout = QGridLayout(self.content_widget)
        self.content_layout.setSpacing(15)
        self.content_layout.setSizeConstraint(QGridLayout.SetMinAndMaxSize)

        # جعل كل الأعمدة (من 0 إلى 5) تتمدد بالتساوي لتغطي كامل العرض
        for c in range(self.columns):
            self.content_layout.setColumnStretch(c, 1)

        self.setWidget(self.content_widget)

    def add_item(self, widget, row=None, col=None):
        if row is not None and col is not None:
            self.content_layout.addWidget(widget, row, col)
            for r in range(row + 1):
                self.content_layout.setRowMinimumHeight(r, 50)
            return

        auto_row = self.item_count // self.columns
        auto_col = self.item_count % self.columns

        self.content_layout.addWidget(widget, auto_row, auto_col)
        self.content_layout.setRowMinimumHeight(auto_row, 50)
        self.item_count += 1
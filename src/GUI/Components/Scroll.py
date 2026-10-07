from PySide6.QtWidgets import QWidget, QScrollArea, QGridLayout, QFrame
from PySide6.QtCore import Qt


class ScrollContainer(QScrollArea):
    def __init__(self, columns=3, parent=None):
        super().__init__(parent)

        self.columns = columns
        self.item_count = 0

        # Allow vertical expanding and disable horizontal scrolling
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Disables horizontal scrollbar

        self.content_widget = QWidget()
        self.content_layout = QGridLayout(self.content_widget)
        self.content_layout.setSpacing(15)#spac between the bottun by 15px
        self.content_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        self.setWidget(self.content_widget)

    def add_item(self, widget, row=None, col=None): #==>function to can add the row and col in the window
        if row is not None and col is not None:
            self.content_layout.addWidget(widget, row, col)
            return

        auto_row = self.item_count // self.columns# to chous the col auto by see the remainder her is =0
        auto_col = self.item_count % self.columns # here to make auto chouse for row by remainder

        self.content_layout.addWidget(widget, auto_row, auto_col)
        self.item_count += 1# to change place if teh fir button is in the same location for ex:{o,o}>{0,1}
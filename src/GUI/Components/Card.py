import urllib.request
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImage, QColor
from src.GUI.Components.Button import Button


class ProductCard(QWidget):
    def __init__(
        self,
        store_name: str,
        product_name: str,
        image_url: str,
        price: str,
        rating: str,
        button_text: str,
        button_url: str,
        parent=None
    ):
        super().__init__(parent)

        self.store_name = store_name
        self.product_name = product_name
        self.price = price
        self.rating = rating

       #card size
        self.setFixedHeight(380)
        self.setMinimumWidth(260)
        self.setMaximumWidth(320)

        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setStyleSheet("""
            ProductCard {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
            }
        """)

        # maek ligh araound the card
        self.glow_effect = QGraphicsDropShadowEffect(self)
        self.glow_effect.setBlurRadius(28)
        self.glow_effect.setOffset(0, 0)
        self.glow_effect.setColor(QColor(59, 130, 246, 160))
        self.glow_effect.setEnabled(False)
        self.setGraphicsEffect(self.glow_effect)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(8)

        # butting a photo to card
        self.image_label = QLabel()
        self.image_label.setFixedHeight(170)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            background-color: #f8fafc;
            border-radius: 10px;
        """)
        self._load_product_image(image_url)
        main_layout.addWidget(self.image_label)

        # name of the store in card
        store_label = QLabel(self.store_name)
        store_label.setStyleSheet("font-size: 12px; font-weight: 600; color: #64748b; text-transform: uppercase;")
        main_layout.addWidget(store_label)

        # name of of podact
        product_label = QLabel(self.product_name)
        product_label.setWordWrap(True)
        product_label.setStyleSheet("font-size: 14px; font-weight: 700; color: #0f172a;")
        product_label.setFixedHeight(38)
        main_layout.addWidget(product_label)


        bottom_bar = QHBoxLayout()
        bottom_bar.setContentsMargins(0, 4, 0, 0)
        bottom_bar.setSpacing(6)

        price_label = QLabel(self.price)
        price_label.setStyleSheet("font-size: 15px; font-weight: 800; color: #0f172a;")
        bottom_bar.addWidget(price_label)

        rating_badge = QLabel(f"★ {self.rating}")
        rating_badge.setFixedHeight(22)
        rating_badge.setAlignment(Qt.AlignCenter)
        rating_badge.setStyleSheet("""
            background-color: #1e3a5f;
            color: #fbbf24;
            font-size: 11px;
            font-weight: 700;
            padding: 0px 8px;
            border-radius: 11px;
        """)
        bottom_bar.addWidget(rating_badge)

        bottom_bar.addStretch()

        self.action_button = Button(button_text, button_url)
        self.action_button.setFixedHeight(34)
        self.action_button.setStyleSheet("""
            QPushButton {
                background-color: #1e3a5f;
                color: #ffffff;
                font-size: 12px;
                font-weight: 600;
                padding: 0 14px;
                border-radius: 17px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2b4f7a;
            }
            QPushButton:pressed {
                background-color: #152942;
            }
        """)
        bottom_bar.addWidget(self.action_button)

        main_layout.addLayout(bottom_bar)

    def enterEvent(self, event):
        self.glow_effect.setEnabled(True)
        self.setStyleSheet("""
            ProductCard {
                background-color: #ffffff;
                border: 1px solid #3b82f6;
                border-radius: 16px;
            }
        """)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.glow_effect.setEnabled(False)
        self.setStyleSheet("""
            ProductCard {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
            }
        """)
        super().leaveEvent(event)

    def _load_product_image(self, url_or_path: str):
        pixmap = QPixmap()
        try:
            if url_or_path.startswith("http://") or url_or_path.startswith("https://"):
                req = urllib.request.Request(
                    url_or_path,
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                with urllib.request.urlopen(req, timeout=3) as resp:
                    raw_data = resp.read()
                image = QImage()
                if image.loadFromData(raw_data):
                    pixmap = QPixmap.fromImage(image)
            else:
                pixmap.load(url_or_path)
        except Exception:
            pass

        if not pixmap.isNull():
            scaled = pixmap.scaled(
                320, 170,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled)
        else:
            self.image_label.setText("📦 No Image")
            self.image_label.setStyleSheet("""
                background-color: #f1f5f9;
                color: #94a3b8;
                font-size: 13px;
                border-radius: 10px;
            """)
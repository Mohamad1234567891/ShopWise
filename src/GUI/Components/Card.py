import webbrowser
from PySide6.QtWidgets import (
    QApplication, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QPixmap, QColor
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

from src.Operations import StringOperations as SO


class ProductCard(QFrame):
    # One network manager shared by all cards (instead of one per card)
    _network_manager = None

    @classmethod
    def _get_manager(cls):
        if cls._network_manager is None:
            cls._network_manager = QNetworkAccessManager(QApplication.instance())
            cls._network_manager.setRedirectPolicy(
                QNetworkRequest.RedirectPolicy.NoLessSafeRedirectPolicy
            )
        return cls._network_manager

    def __init__(
        self,
        store_name: str,
        product_name: str,
        image_url: str,
        price: str,
        rating: float,
        ratingAmount: str = "N/A",
        button_text: str = "View Offer",
        button_url: str = "",
        color: str = "white",
        parent=None
    ):
        super().__init__(parent)
        self.button_url = button_url
        self.color_theme = str(color or "white").lower()
        self.reply = None
        self.setFixedSize(280, 450)

        # Base card styling & glow colors based on theme
        if self.color_theme == "blue":
            self.setStyleSheet("""
                ProductCard {
                    background-color: #bfdbfe;
                    border: 2px solid #3b82f6;
                    border-radius: 18px;
                }
            """)
            self.title_color = "#1e293b"
            self.store_color = "#475569"
            self.price_color = "#0f172a"
            self.base_glow_color = QColor(59, 130, 246, 60)
            self.hover_glow_color = QColor(59, 130, 246, 170)
        elif self.color_theme == "gold":
            self.setStyleSheet("""
                ProductCard {
                    background-color: #fef9c3;
                    border: 2px solid #eab308;
                    border-radius: 18px;
                }
            """)
            self.title_color = "#713f12"
            self.store_color = "#854d0e"
            self.price_color = "#713f12"
            self.base_glow_color = QColor(234, 179, 8, 60)
            self.hover_glow_color = QColor(234, 179, 8, 170)
        elif self.color_theme == "red":
            self.setStyleSheet("""
                ProductCard {
                    background-color: #fee2e2;
                    border: 2px solid #ef4444;
                    border-radius: 18px;
                }
            """)
            self.title_color = "#7f1d1d"
            self.store_color = "#991b1b"
            self.price_color = "#7f1d1d"
            self.base_glow_color = QColor(239, 68, 68, 60)
            self.hover_glow_color = QColor(239, 68, 68, 170)
        else:
            self.setStyleSheet("""
                ProductCard {
                    background-color: #ffffff;
                    border: 1px solid #e2e8f0;
                    border-radius: 18px;
                }
            """)
            self.title_color = "#0f172a"
            self.store_color = "#64748b"
            self.price_color = "#0f172a"
            self.base_glow_color = QColor(255, 255, 255, 25)
            self.hover_glow_color = QColor(255, 255, 255, 140)

        # Ambient Glow Effect
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(15)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(self.base_glow_color)
        self.setGraphicsEffect(self.shadow)

        # Layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(14, 14, 14, 14)
        self.main_layout.setSpacing(8)

        # Product Image Container
        self.image_label = QLabel()
        self.image_label.setFixedHeight(150)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #0f172a;
                border-radius: 12px;
            }
        """)
        self.main_layout.addWidget(self.image_label)

        self._load_image(str(image_url or ""))

        # Store Name
        self.store_label = QLabel(str(store_name or "").upper())
        self.store_label.setStyleSheet(f"""
            QLabel {{
                color: {self.store_color};
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 0.5px;
                background: transparent;
            }}
        """)
        self.main_layout.addWidget(self.store_label)

        # Product Title
        self.title_label = QLabel(str(product_name or ""))
        self.title_label.setWordWrap(True)
        self.title_label.setFixedHeight(36)
        self.title_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.title_label.setStyleSheet(f"""
            QLabel {{
                color: {self.title_color};
                font-size: 13px;
                font-weight: 700;
                line-height: 1.2;
                background: transparent;
            }}
        """)
        self.main_layout.addWidget(self.title_label)

        # Rating Count (right under the product name)
        self.rating_count_label = QLabel(ProductCard.FormatRatingCount(ratingAmount))
        self.rating_count_label.setStyleSheet(f"""
            QLabel {{
                color: {self.store_color};
                font-size: 10px;
                font-weight: 600;
                background: transparent;
            }}
        """)
        self.main_layout.addWidget(self.rating_count_label)

        # Warnings / Badges Layout (Stacked Vertically)
        self.tags_layout = QVBoxLayout()
        self.tags_layout.setContentsMargins(0, 2, 0, 2)
        self.tags_layout.setSpacing(4)
        self.tags_layout.setAlignment(Qt.AlignLeft)
        self.main_layout.addLayout(self.tags_layout)

        self.main_layout.addStretch()

        # Bottom Row: Price, Rating, Action Button
        bottom_row = QHBoxLayout()
        bottom_row.setContentsMargins(0, 0, 0, 0)
        bottom_row.setSpacing(8)

        self.price_label = QLabel(str(price) if price not in (None, "") else "-")
        self.price_label.setStyleSheet(f"""
            QLabel {{
                color: {self.price_color};
                font-size: 14px;
                font-weight: 800;
                background: transparent;
            }}
        """)
        bottom_row.addWidget(self.price_label)

        ratingValue = SO.ToFloat(rating)
        self.rating_label = QLabel(
            f"★ {ratingValue:.1f}" if ratingValue is not None else "★ N/A"
        )
        self.rating_label.setStyleSheet("""
            QLabel {
                background-color: #2563eb;
                color: #ffffff;
                font-size: 11px;
                font-weight: 700;
                padding: 3px 6px;
                border-radius: 6px;
            }
        """)
        bottom_row.addWidget(self.rating_label)

        bottom_row.addStretch()

        self.action_button = QPushButton(button_text)
        self.action_button.setFixedHeight(32)
        self.action_button.setCursor(Qt.PointingHandCursor)
        self.action_button.setStyleSheet("""
            QPushButton {
                background-color: #1e293b;
                color: #ffffff;
                font-size: 11px;
                font-weight: 700;
                padding: 0 12px;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #334155;
            }
            QPushButton:pressed {
                background-color: #0f172a;
            }
        """)
        self.action_button.clicked.connect(self._open_url)
        bottom_row.addWidget(self.action_button)

        self.main_layout.addLayout(bottom_row)

    # --- Mouse Hover Glow Events ---
    def enterEvent(self, event):
        """Intensifies color glow and spreads blur on hover."""
        super().enterEvent(event)
        self.shadow.setBlurRadius(35)
        self.shadow.setColor(self.hover_glow_color)

    def leaveEvent(self, event):
        """Restores default ambient glow when mouse leaves."""
        super().leaveEvent(event)
        self.shadow.setBlurRadius(15)
        self.shadow.setColor(self.base_glow_color)

    def _open_url(self):
        if self.button_url:
            webbrowser.open(self.button_url)

    # --- Image loading ---
    def _show_no_image(self):
        self.image_label.setText("No Image")
        self.image_label.setStyleSheet(
            "color: #64748b; background-color: #0f172a; border-radius: 12px;"
        )

    def _load_image(self, url: str):
        self.reply = None
        if not url:
            self._show_no_image()
            return

        request = QNetworkRequest(QUrl(url))
        request.setHeader(
            QNetworkRequest.KnownHeaders.UserAgentHeader,
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120 Safari/537.36",
        )
        request.setTransferTimeout(10000)  # 10 seconds

        self.reply = self._get_manager().get(request)
        self.reply.finished.connect(self._on_image_downloaded)
        self.reply.finished.connect(self.reply.deleteLater)

    def _on_image_downloaded(self):
        reply, self.reply = self.reply, None
        if reply is None:
            return

        if reply.error() == QNetworkReply.NetworkError.NoError:
            pixmap = QPixmap()
            if pixmap.loadFromData(reply.readAll()) and not pixmap.isNull():
                self.image_label.setPixmap(
                    pixmap.scaled(240, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                )
                return
        self._show_no_image()

    def cancel_image(self):
        """Abort a pending download. Call this before deleting the card."""
        reply, self.reply = self.reply, None
        if reply is not None:
            try:
                reply.finished.disconnect(self._on_image_downloaded)
            except (TypeError, RuntimeError):
                pass
            reply.abort()

    # --- Badge Helper ---
    @staticmethod
    def FormatRatingCount(value):
        """'1234' -> '1,234 ratings', 'N/A' -> 'No ratings'."""
        text = str(value if value not in (None, "") else "")
        count = 0
        try:
            count = int(float(text.replace(".", "").replace(",", "")))
        except ValueError:
            count = 0
        if count > 0:
            return f"{count:,} ratings"
        return "No ratings"

    def _add_tag(self, text: str, bg_color: str, text_color: str, tooltip: str = ""):
        tag = QLabel(text)
        if tooltip:
            tag.setToolTip(tooltip)
        tag.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
                font-size: 10px;
                font-weight: 700;
                padding: 3px 8px;
                border-radius: 4px;
                border: 1px solid {text_color}40;
            }}
        """)
        self.tags_layout.addWidget(tag)

    # --- Warning Methods ---
    def brockProdact(self):
        self._add_tag("Broken Product", "rgba(239, 68, 68, 0.15)", "#ef4444", "Damaged reports on delivery.")

    def lowPrice(self):
        self._add_tag("Suspicious Low Price", "rgba(234, 88, 12, 0.18)", "#ea580c", "Abnormally low price. Potential scam.")

    def lowRating(self):
        self._add_tag("Low Rating", "rgba(234, 179, 8, 0.18)", "#ca8a04", "Customer rating is critically low.")

    def proplemProdact(self):
        self._add_tag("Problem Product", "rgba(225, 29, 72, 0.18)", "#e11d48", "Frequent buyer complaints.")
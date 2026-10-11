import urllib.request
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImage, QColor
from src.GUI.Components.Button import Button


class ProductCard(QWidget):
    # إعدادات الألوان الصريحة للخلفية، الحدود، والتوهج
    COLOR_MAP = {
        # 1. ذهبي: للأفضل في كل شيء
        "gold": {
            "bg": "#fef08a",                   # خلفية صفراء ذهبية واضحة
            "border": "#eab308",               # إطار ذهبي
            "glow": QColor(234, 179, 8, 220),  # توهج بلور ذهبي
            "text": "#0f172a",                 # لون النص
            "badge_bg": "#ca8a04",
            "badge_color": "#ffffff"
        },
        # 2. أزرق: لأفضل قيمة مقابل السعر
        "blue": {
            "bg": "#bfdbfe",                   # خلفية زرقاء واضحة
            "border": "#2563eb",               # إطار أزرق
            "glow": QColor(37, 99, 235, 220),  # توهج بلور أزرق
            "text": "#0f172a",                 # لون النص
            "badge_bg": "#1d4ed8",
            "badge_color": "#ffffff"
        },
        # 3. أحمر: لأسوأ تقييم وسعر مرتفع
        "red": {
            "bg": "#fecaca",                   # خلفية حمراء واضحة
            "border": "#ef4444",               # إطار أحمر ناصع
            "glow": QColor(239, 68, 68, 220),  # توهج بلور أحمر
            "text": "#0f172a",                 # لون النص
            "badge_bg": "#dc2626",
            "badge_color": "#ffffff"
        },
        # 4. أبيض: للكروت العادية
        "white": {
            "bg": "#ffffff",                   # خلفية بيضاء
            "border": "#e2e8f0",               # إطار رمادي ناعم
            "glow": QColor(241, 245, 249, 180),# توهج أبيض/فضي هادئ
            "text": "#0f172a",
            "badge_bg": "#1e3a5f",
            "badge_color": "#fbbf24"
        }
    }

    def __init__(
        self,
        store_name: str,
        product_name: str,
        image_url: str,
        price: str,
        rating: str,
        button_text: str,
        button_url: str,
        color: str = "white",
        badge_text: str = None,
        parent=None
    ):
        super().__init__(parent)

        self.store_name = store_name
        self.product_name = product_name
        self.price = price
        self.rating = rating

        choice = color.strip().lower()
        self.theme = self.COLOR_MAP.get(choice, self.COLOR_MAP["white"])

        self.setFixedHeight(380)
        self.setMinimumWidth(260)
        self.setMaximumWidth(340)
        self.setAttribute(Qt.WA_StyledBackground, True)

        self._apply_idle_style()

        # تأثير البلور اللامع بلون الكارد
        self.glow_effect = QGraphicsDropShadowEffect(self)
        self.glow_effect.setBlurRadius(32)
        self.glow_effect.setOffset(0, 0)
        self.glow_effect.setColor(self.theme["glow"])
        self.glow_effect.setEnabled(False)
        self.setGraphicsEffect(self.glow_effect)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(8)

        # 1. صورة المنتج (بخلفية شفافة حتى لا تحجب لون الكارد)
        self.image_label = QLabel()
        self.image_label.setFixedHeight(170)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: transparent; border-radius: 10px;")
        self._load_product_image(image_url)
        main_layout.addWidget(self.image_label)

        # 2. اسم المتجر وشارة الفئة
        store_row = QHBoxLayout()
        store_label = QLabel(self.store_name)
        store_label.setStyleSheet("font-size: 12px; font-weight: 700; color: #475569; text-transform: uppercase;")
        store_row.addWidget(store_label)

        if badge_text:
            tag_label = QLabel(badge_text)
            tag_label.setStyleSheet(f"""
                font-size: 11px;
                font-weight: 700;
                color: {self.theme['badge_color']};
                background-color: {self.theme['badge_bg']};
                padding: 2px 8px;
                border-radius: 8px;
            """)
            store_row.addStretch()
            store_row.addWidget(tag_label)

        main_layout.addLayout(store_row)

        # 3. عنوان المنتج
        product_label = QLabel(self.product_name)
        product_label.setWordWrap(True)
        product_label.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {self.theme['text']};")
        product_label.setFixedHeight(38)
        main_layout.addWidget(product_label)

        # 4. السعر والتقييم والزر (الزر ثابت بلونه الكحلي)
        bottom_bar = QHBoxLayout()
        bottom_bar.setContentsMargins(0, 4, 0, 0)
        bottom_bar.setSpacing(6)

        price_label = QLabel(self.price)
        price_label.setStyleSheet(f"font-size: 15px; font-weight: 800; color: {self.theme['text']};")
        bottom_bar.addWidget(price_label)

        rating_badge = QLabel(f"★ {self.rating}")
        rating_badge.setFixedHeight(22)
        rating_badge.setAlignment(Qt.AlignCenter)
        rating_badge.setStyleSheet(f"""
            background-color: {self.theme['badge_bg']};
            color: {self.theme['badge_color']};
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
                font-weight: 700;
                padding: 0 14px;
                border-radius: 17px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2b4f7a;
            }
            QPushButton:pressed {
                background-color: #0f172a;
            }
        """)
        bottom_bar.addWidget(self.action_button)

        main_layout.addLayout(bottom_bar)

    def _apply_idle_style(self):
        self.setStyleSheet(f"""
            ProductCard {{
                background-color: {self.theme['bg']};
                border: 2px solid {self.theme['border']};
                border-radius: 16px;
            }}
        """)

    def enterEvent(self, event):
        self.glow_effect.setEnabled(True)
        self.setStyleSheet(f"""
            ProductCard {{
                background-color: {self.theme['bg']};
                border: 2px solid {self.theme['border']};
                border-radius: 16px;
            }}
        """)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.glow_effect.setEnabled(False)
        self._apply_idle_style()
        super().leaveEvent(event)

    def _load_product_image(self, url_or_path: str):
        pixmap = QPixmap()
        try:
            if url_or_path.startswith("http://") or url_or_path.startswith("https://"):
                req = urllib.request.Request(url_or_path, headers={"User-Agent": "Mozilla/5.0"})
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
            scaled = pixmap.scaled(320, 170, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled)
        else:
            self.image_label.setText("📦 No Image")
            self.image_label.setStyleSheet("background-color: transparent; color: #94a3b8; font-size: 13px; border-radius: 10px;")
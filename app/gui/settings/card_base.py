"""
Lớp cơ sở SettingsCard và các định dạng giao diện chuẩn cho màn hình Cài đặt.
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from core.i18n import t
from gui.theme import (
    COLOR_BG_CARD, COLOR_BG_INPUT, COLOR_BORDER,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_MUTED,
    COLOR_ACCENT_INDIGO, COLOR_ACCENT_CYAN, COLOR_ACCENT_EMERALD, COLOR_ACCENT_ROSE
)

STYLE_COMBOBOX = f"""
    QComboBox {{
        background-color: {COLOR_BG_INPUT};
        border: 1px solid #1E293B;
        border-radius: 8px;
        color: {COLOR_TEXT_PRIMARY};
        padding: 6px 14px;
        font-size: 13px;
        font-weight: 500;
    }}
    QComboBox:hover {{
        border: 1px solid #334155;
    }}
    QComboBox:focus {{
        border: 1px solid {COLOR_ACCENT_INDIGO};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {COLOR_BG_INPUT};
        color: {COLOR_TEXT_PRIMARY};
        border: 1px solid #1E293B;
        border-radius: 8px;
        selection-background-color: {COLOR_ACCENT_INDIGO};
        selection-color: #FFFFFF;
        padding: 6px;
        outline: none;
    }}
"""

STYLE_CHECKBOX = f"""
    QCheckBox {{
        font-size: 13px;
        font-weight: 600;
        color: {COLOR_TEXT_PRIMARY};
        spacing: 10px;
    }}
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border-radius: 4px;
        border: 1px solid #334155;
        background-color: {COLOR_BG_INPUT};
    }}
    QCheckBox::indicator:hover {{
        border: 1px solid {COLOR_ACCENT_INDIGO};
    }}
    QCheckBox::indicator:checked {{
        background-color: {COLOR_ACCENT_INDIGO};
        border: 1px solid #818CF8;
    }}
"""

STYLE_LINEEDIT = f"""
    QLineEdit {{
        background-color: {COLOR_BG_INPUT};
        border: 1px solid #1E293B;
        border-radius: 8px;
        color: {COLOR_TEXT_PRIMARY};
        padding: 7px 12px;
        font-size: 13px;
    }}
    QLineEdit:focus {{
        border: 1px solid {COLOR_ACCENT_INDIGO};
        background-color: #111C38;
    }}
    QLineEdit:disabled {{
        background-color: #0A1020;
        color: {COLOR_TEXT_MUTED};
        border: 1px solid #1E293B;
    }}
"""

class SettingsCard(QFrame):
    """Container dạng thẻ (Card) chuẩn phong cách Dark Glassmorphic với tiêu đề & phụ đề tinh tế."""
    def __init__(self, icon: str, title_key: str, sub_key: str, parent=None):
        super().__init__(parent)
        self.icon_char = icon
        self.title_key = title_key
        self.sub_key = sub_key

        self.setStyleSheet(f"""
            SettingsCard {{
                background-color: {COLOR_BG_CARD};
                border: 1px solid {COLOR_BORDER};
                border-radius: 12px;
            }}
            SettingsCard:hover {{
                border: 1px solid rgba(99, 102, 241, 0.25);
            }}
        """)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 18, 20, 20)
        self.main_layout.setSpacing(14)

        # Header của Card: Icon tròn + Tiêu đề + Phụ đề
        header_row = QHBoxLayout()
        header_row.setSpacing(12)

        self.lbl_icon = QLabel(self.icon_char)
        self.lbl_icon.setAlignment(Qt.AlignCenter)
        self.lbl_icon.setFixedSize(36, 36)
        self.lbl_icon.setStyleSheet(f"""
            background-color: rgba(99, 102, 241, 0.12);
            border: 1px solid rgba(99, 102, 241, 0.25);
            border-radius: 18px;
            font-size: 17px;
        """)
        header_row.addWidget(self.lbl_icon)

        text_vbox = QVBoxLayout()
        text_vbox.setSpacing(2)

        self.lbl_title = QLabel()
        self.lbl_title.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {COLOR_TEXT_PRIMARY};")
        self.lbl_sub = QLabel()
        self.lbl_sub.setStyleSheet(f"font-size: 12px; color: {COLOR_TEXT_MUTED};")
        self.lbl_sub.setWordWrap(True)

        text_vbox.addWidget(self.lbl_title)
        text_vbox.addWidget(self.lbl_sub)
        header_row.addLayout(text_vbox, stretch=1)

        self.main_layout.addLayout(header_row)

        # Đường kẻ chia phần nhẹ
        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background-color: rgba(255, 255, 255, 0.05);")
        self.main_layout.addWidget(divider)

        # Vùng chứa các control bên trong Card
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(12)
        self.content_layout.setContentsMargins(0, 4, 0, 0)
        self.main_layout.addLayout(self.content_layout)

    def retranslate_ui(self):
        self.lbl_title.setText(t(self.title_key))
        self.lbl_sub.setText(t(self.sub_key))

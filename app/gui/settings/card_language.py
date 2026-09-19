"""
Thẻ cấu hình ngôn ngữ hiển thị (Language Settings Card).
"""

from PySide6.QtWidgets import QHBoxLayout, QLabel, QComboBox
from PySide6.QtCore import Qt
from core.i18n import t
from gui.settings.card_base import SettingsCard, STYLE_COMBOBOX

class LanguageSettingsCard(SettingsCard):
    def __init__(self, parent=None):
        super().__init__("globe", "card_lang_title", "card_lang_sub", parent)

        row = QHBoxLayout()
        row.setSpacing(16)

        self.lbl_lang_label = QLabel()
        self.lbl_lang_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #CBD5E1;")
        self.lbl_lang_label.setFixedWidth(160)

        self.cb_language = QComboBox()
        self.cb_language.addItems(["Tiếng Việt", "English"])
        self.cb_language.setMinimumHeight(38)
        self.cb_language.setMinimumWidth(220)
        self.cb_language.setStyleSheet(STYLE_COMBOBOX)
        self.cb_language.setCursor(Qt.PointingHandCursor)

        row.addWidget(self.lbl_lang_label)
        row.addWidget(self.cb_language)
        row.addStretch()

        self.content_layout.addLayout(row)

    def retranslate_ui(self):
        super().retranslate_ui()
        self.lbl_lang_label.setText(t("lbl_language"))

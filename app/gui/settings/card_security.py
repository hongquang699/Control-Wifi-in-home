"""
Thẻ cấu hình Bảo mật & Tường lửa Máy chủ (Security Settings Card).
"""

from PySide6.QtWidgets import QVBoxLayout, QLabel, QCheckBox
from PySide6.QtCore import Qt
from core.i18n import t
from gui.settings.card_base import SettingsCard, STYLE_CHECKBOX

class SecuritySettingsCard(SettingsCard):
    def __init__(self, parent=None):
        super().__init__("🛡️", "card_sec_title", "card_sec_sub", parent)

        # 1. Checkbox Firewall + Hint
        fw_vbox = QVBoxLayout()
        fw_vbox.setSpacing(2)
        self.chk_firewall = QCheckBox()
        self.chk_firewall.setCursor(Qt.PointingHandCursor)
        self.chk_firewall.setStyleSheet(STYLE_CHECKBOX)
        self.lbl_hint_firewall = QLabel()
        self.lbl_hint_firewall.setStyleSheet("font-size: 11px; color: #64748B; margin-left: 28px;")
        fw_vbox.addWidget(self.chk_firewall)
        fw_vbox.addWidget(self.lbl_hint_firewall)
        self.content_layout.addLayout(fw_vbox)

        # 2. Checkbox Confirm + Hint
        cf_vbox = QVBoxLayout()
        cf_vbox.setSpacing(2)
        self.chk_confirm = QCheckBox()
        self.chk_confirm.setCursor(Qt.PointingHandCursor)
        self.chk_confirm.setStyleSheet(STYLE_CHECKBOX)
        self.lbl_hint_confirm = QLabel()
        self.lbl_hint_confirm.setStyleSheet("font-size: 11px; color: #64748B; margin-left: 28px;")
        cf_vbox.addWidget(self.chk_confirm)
        cf_vbox.addWidget(self.lbl_hint_confirm)
        self.content_layout.addLayout(cf_vbox)

    def retranslate_ui(self):
        super().retranslate_ui()
        self.chk_firewall.setText(t("chk_firewall").replace("&", "&&"))
        self.lbl_hint_firewall.setText(t("card_sec_firewall_hint"))
        self.chk_confirm.setText(t("chk_confirm").replace("&", "&&"))
        self.lbl_hint_confirm.setText(t("card_sec_confirm_hint"))

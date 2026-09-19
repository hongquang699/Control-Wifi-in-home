"""
Thẻ cấu hình quét mạng & giám sát (Scan Settings Card).
"""

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QLineEdit, QPushButton, QSpinBox
)
from PySide6.QtCore import Qt
from core.i18n import t
from gui.theme import COLOR_BG_INPUT, COLOR_ACCENT_INDIGO
from gui.settings.card_base import SettingsCard, STYLE_CHECKBOX, STYLE_LINEEDIT

class ScanSettingsCard(SettingsCard):
    def __init__(self, parent=None):
        super().__init__("antenna", "card_scan_title", "card_scan_sub", parent)

        # 1. Checkbox Auto-detect
        self.chk_autodetect = QCheckBox()
        self.chk_autodetect.setCursor(Qt.PointingHandCursor)
        self.chk_autodetect.setStyleSheet(STYLE_CHECKBOX)
        self.content_layout.addWidget(self.chk_autodetect)

        # 2. Checkbox Multi-subnet
        self.chk_multisubnet = QCheckBox()
        self.chk_multisubnet.setCursor(Qt.PointingHandCursor)
        self.chk_multisubnet.setStyleSheet(STYLE_CHECKBOX)
        self.content_layout.addWidget(self.chk_multisubnet)

        # 3. Custom Subnets Input
        subnet_vbox = QVBoxLayout()
        subnet_vbox.setSpacing(4)
        self.lbl_custom_subnet = QLabel()
        self.lbl_custom_subnet.setStyleSheet("font-size: 13px; font-weight: 600; color: #CBD5E1;")
        self.txt_custom_subnet = QLineEdit()
        self.txt_custom_subnet.setMinimumHeight(38)
        self.txt_custom_subnet.setStyleSheet(STYLE_LINEEDIT)

        subnet_vbox.addWidget(self.lbl_custom_subnet)
        subnet_vbox.addWidget(self.txt_custom_subnet)
        self.content_layout.addLayout(subnet_vbox)

        # 4. Timer SpinBoxes
        timer_row = QHBoxLayout()
        timer_row.setSpacing(20)

        # Cột Chu kỳ quét
        col_interval = QVBoxLayout()
        col_interval.setSpacing(4)
        self.lbl_scan_interval = QLabel()
        self.lbl_scan_interval.setStyleSheet("font-size: 13px; font-weight: 600; color: #CBD5E1;")
        self.spin_interval = QSpinBox()
        self.spin_interval.setRange(10, 3600)
        self.spin_interval.setMinimumHeight(38)
        self.spin_interval.setStyleSheet(f"""
            QSpinBox {{
                background-color: {COLOR_BG_INPUT};
                border: 1px solid #1E293B;
                border-radius: 8px;
                color: #F8FAFC;
                padding: 6px 12px;
                font-size: 13px;
                font-weight: 600;
            }}
            QSpinBox:focus {{
                border: 1px solid {COLOR_ACCENT_INDIGO};
            }}
        """)
        self.lbl_hint_interval = QLabel()
        self.lbl_hint_interval.setStyleSheet("font-size: 11px; color: #64748B;")

        col_interval.addWidget(self.lbl_scan_interval)
        col_interval.addWidget(self.spin_interval)
        col_interval.addWidget(self.lbl_hint_interval)
        timer_row.addLayout(col_interval, stretch=1)

        # Cột Ngưỡng Offline
        col_offline = QVBoxLayout()
        col_offline.setSpacing(4)
        self.lbl_offline_thresh = QLabel()
        self.lbl_offline_thresh.setStyleSheet("font-size: 13px; font-weight: 600; color: #CBD5E1;")
        self.spin_offline_thresh = QSpinBox()
        self.spin_offline_thresh.setRange(30, 7200)
        self.spin_offline_thresh.setMinimumHeight(38)
        self.spin_offline_thresh.setStyleSheet(f"""
            QSpinBox {{
                background-color: {COLOR_BG_INPUT};
                border: 1px solid #1E293B;
                border-radius: 8px;
                color: #F8FAFC;
                padding: 6px 12px;
                font-size: 13px;
                font-weight: 600;
            }}
            QSpinBox:focus {{
                border: 1px solid {COLOR_ACCENT_INDIGO};
            }}
        """)
        self.lbl_hint_offline = QLabel()
        self.lbl_hint_offline.setStyleSheet("font-size: 11px; color: #64748B;")

        col_offline.addWidget(self.lbl_offline_thresh)
        col_offline.addWidget(self.spin_offline_thresh)
        col_offline.addWidget(self.lbl_hint_offline)
        timer_row.addLayout(col_offline, stretch=1)

        self.content_layout.addLayout(timer_row)

        # 5. Đường dẫn Nmap kèm nút Duyệt tệp
        nmap_vbox = QVBoxLayout()
        nmap_vbox.setSpacing(4)
        self.lbl_nmap_path = QLabel()
        self.lbl_nmap_path.setStyleSheet("font-size: 13px; font-weight: 600; color: #CBD5E1;")

        nmap_row = QHBoxLayout()
        nmap_row.setSpacing(8)

        self.txt_nmap_path = QLineEdit()
        self.txt_nmap_path.setMinimumHeight(38)
        self.txt_nmap_path.setStyleSheet(STYLE_LINEEDIT)

        self.btn_browse_nmap = QPushButton()
        self.btn_browse_nmap.setMinimumHeight(38)
        self.btn_browse_nmap.setCursor(Qt.PointingHandCursor)
        self.btn_browse_nmap.setStyleSheet("""
            QPushButton {
                background-color: #1E293B;
                color: #38BDF8;
                border: 1px solid rgba(56, 189, 248, 0.35);
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
                padding: 0 16px;
            }
            QPushButton:hover {
                background-color: rgba(56, 189, 248, 0.15);
                border: 1px solid #38BDF8;
                color: #E0F2FE;
            }
            QPushButton:pressed {
                background-color: rgba(56, 189, 248, 0.25);
            }
        """)

        nmap_row.addWidget(self.txt_nmap_path, stretch=1)
        nmap_row.addWidget(self.btn_browse_nmap)

        nmap_vbox.addWidget(self.lbl_nmap_path)
        nmap_vbox.addLayout(nmap_row)
        self.content_layout.addLayout(nmap_vbox)

    def retranslate_ui(self):
        super().retranslate_ui()
        self.chk_autodetect.setText(t("chk_autodetect").replace("&", "&&"))
        self.chk_multisubnet.setText(t("chk_multisubnet").replace("&", "&&"))
        self.lbl_custom_subnet.setText(t("lbl_custom_subnet"))
        self.txt_custom_subnet.setPlaceholderText(t("custom_subnets_placeholder"))
        self.lbl_scan_interval.setText(t("lbl_scan_interval"))
        self.spin_interval.setSuffix(f" {t('sec_unit')}")
        self.lbl_hint_interval.setText(t("hint_scan_interval"))
        self.lbl_offline_thresh.setText(t("lbl_offline_thresh"))
        self.spin_offline_thresh.setSuffix(f" {t('sec_unit')}")
        self.lbl_hint_offline.setText(t("hint_offline_thresh"))
        self.lbl_nmap_path.setText(t("lbl_nmap_path"))
        self.btn_browse_nmap.setText(t("btn_browse"))

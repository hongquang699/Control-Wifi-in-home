"""
Thanh công cụ chân trang (Action Bar) cho màn hình Cài đặt.
"""

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QSize
from core.i18n import t
from gui.icons import get_app_icon

class SettingsActionBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #0B1326;
                border-top: 1px solid rgba(255, 255, 255, 0.08);
            }
        """)
        bar_layout = QHBoxLayout(self)
        bar_layout.setContentsMargins(28, 14, 28, 14)
        bar_layout.setSpacing(14)

        # Trạng thái bên trái
        self.lbl_action_status = QLabel()
        self.lbl_action_status.setStyleSheet("color: #64748B; font-size: 12px; font-weight: 500;")
        bar_layout.addWidget(self.lbl_action_status)
        bar_layout.addStretch()

        # Nút Khôi phục mặc định
        self.btn_reset = QPushButton()
        self.btn_reset.setIcon(get_app_icon("refresh"))
        self.btn_reset.setIconSize(QSize(16, 16))
        self.btn_reset.setMinimumHeight(42)
        self.btn_reset.setCursor(Qt.PointingHandCursor)
        self.btn_reset.setStyleSheet("""
            QPushButton {
                background-color: #1E293B;
                color: #94A3B8;
                border: 1px solid rgba(148, 163, 184, 0.2);
                border-radius: 8px;
                font-weight: 600;
                font-size: 13px;
                padding: 0 18px;
            }
            QPushButton:hover {
                background-color: #334155;
                color: #F8FAFC;
                border: 1px solid rgba(148, 163, 184, 0.4);
            }
            QPushButton:pressed {
                background-color: #0F172A;
            }
        """)
        bar_layout.addWidget(self.btn_reset)

        # Nút Lưu Cấu hình
        self.btn_save = QPushButton()
        self.btn_save.setIcon(get_app_icon("save"))
        self.btn_save.setIconSize(QSize(16, 16))
        self.btn_save.setMinimumHeight(42)
        self.btn_save.setMinimumWidth(160)
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4F46E5, stop:1 #06B6D4);
                color: #FFFFFF;
                font-weight: 700;
                font-size: 13px;
                padding: 0 24px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4338CA, stop:1 #0891B2);
            }
            QPushButton:pressed {
                background: #3730A3;
            }
        """)
        bar_layout.addWidget(self.btn_save)

    def retranslate_ui(self):
        self.lbl_action_status.setText(f"• {t('settings_synced')}")
        self.btn_reset.setText(f" {t('btn_reset_defaults')}")
        self.btn_save.setText(f" {t('btn_save_settings')}")

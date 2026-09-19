"""
Thẻ Kiểm tra và Cập nhật Phiên bản Phần mềm (Software Update Settings Card).
"""

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QWidget
)
from PySide6.QtCore import Qt, QSize, QTimer, QUrl
from PySide6.QtGui import QDesktopServices
from core.i18n import t, i18n
from gui.settings.card_base import SettingsCard
from gui.icons import get_app_icon
from gui.theme import STYLE_BTN_PRIMARY, STYLE_BTN_SLATE
from services.updater import UpdateChecker, UpdateInfo, CURRENT_VERSION, GITHUB_REPO_URL


class UpdateSettingsCard(SettingsCard):
    """Thẻ cấu hình kiểm tra bản phát hành mới nhất từ GitHub."""

    def __init__(self, parent=None):
        super().__init__("refresh", "card_update_title", "card_update_sub", parent)
        self.updater = UpdateChecker(current_version=CURRENT_VERSION)
        self.last_info: UpdateInfo = None

        # 1. Hàng thông tin phiên bản & Badge
        ver_row = QHBoxLayout()
        ver_row.setSpacing(10)

        self.lbl_ver_title = QLabel()
        self.lbl_ver_title.setStyleSheet("font-size: 13px; font-weight: 600; color: #F8FAFC;")
        ver_row.addWidget(self.lbl_ver_title)

        self.lbl_ver_code = QLabel(f"v{CURRENT_VERSION}")
        self.lbl_ver_code.setStyleSheet("""
            background-color: rgba(56, 189, 248, 0.15);
            color: #38BDF8;
            font-family: 'Fira Code', monospace;
            font-size: 12px;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 6px;
            border: 1px solid rgba(56, 189, 248, 0.3);
        """)
        ver_row.addWidget(self.lbl_ver_code)

        self.lbl_ver_badge = QLabel("LATEST")
        self.lbl_ver_badge.setStyleSheet("""
            background-color: rgba(16, 185, 129, 0.15);
            color: #10B981;
            font-size: 10px;
            font-weight: 800;
            padding: 3px 8px;
            border-radius: 6px;
            border: 1px solid rgba(16, 185, 129, 0.35);
        """)
        ver_row.addWidget(self.lbl_ver_badge)
        ver_row.addStretch()

        self.content_layout.addLayout(ver_row)

        # 2. Hộp thông điệp trạng thái
        self.msg_box = QFrame()
        self.msg_box.setStyleSheet("""
            QFrame {
                background-color: #0A1224;
                border: 1px solid #1E293B;
                border-radius: 8px;
                padding: 10px 12px;
            }
        """)
        mb_layout = QVBoxLayout(self.msg_box)
        mb_layout.setContentsMargins(10, 8, 10, 8)
        mb_layout.setSpacing(4)

        self.lbl_status = QLabel()
        self.lbl_status.setStyleSheet("color: #94A3B8; font-size: 12px; line-height: 1.4;")
        self.lbl_status.setWordWrap(True)
        mb_layout.addWidget(self.lbl_status)
        self.content_layout.addWidget(self.msg_box)

        # 3. Nút Thao tác: [Kiểm tra cập nhật] + [Xem bản phát hành]
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.btn_check = QPushButton()
        self.btn_check.setIcon(get_app_icon("refresh"))
        self.btn_check.setIconSize(QSize(14, 14))
        self.btn_check.setCursor(Qt.PointingHandCursor)
        self.btn_check.setStyleSheet(STYLE_BTN_PRIMARY)
        self.btn_check.clicked.connect(self._start_check_update)
        btn_row.addWidget(self.btn_check)

        self.btn_view_release = QPushButton()
        self.btn_view_release.setIcon(get_app_icon("globe"))
        self.btn_view_release.setIconSize(QSize(14, 14))
        self.btn_view_release.setCursor(Qt.PointingHandCursor)
        self.btn_view_release.setStyleSheet(STYLE_BTN_SLATE)
        self.btn_view_release.clicked.connect(self._open_release_url)
        btn_row.addWidget(self.btn_view_release)

        btn_row.addStretch()
        self.content_layout.addLayout(btn_row)

    def _start_check_update(self):
        self.btn_check.setEnabled(False)
        self.lbl_status.setText(t("update_status_checking"))
        self.lbl_status.setStyleSheet("color: #38BDF8; font-size: 12px;")
        QTimer.singleShot(250, self._perform_check)

    def _perform_check(self):
        try:
            info = self.updater.check_for_updates(timeout=3)
            self.last_info = info

            if info.is_update_available:
                self.lbl_ver_badge.setText("UPDATE AVAILABLE")
                self.lbl_ver_badge.setStyleSheet("""
                    background-color: rgba(245, 158, 11, 0.15);
                    color: #F59E0B;
                    font-size: 10px;
                    font-weight: 800;
                    padding: 3px 8px;
                    border-radius: 6px;
                    border: 1px solid rgba(245, 158, 11, 0.35);
                """)
                self.lbl_status.setText(f"🎉 Đã có bản cập nhật mới v{info.latest_version}! Nhấp 'Xem bản phát hành GitHub' để tải về.")
                self.lbl_status.setStyleSheet("color: #34D399; font-size: 12px; font-weight: 600;")
            else:
                self.lbl_ver_badge.setText("LATEST")
                self.lbl_ver_badge.setStyleSheet("""
                    background-color: rgba(16, 185, 129, 0.15);
                    color: #10B981;
                    font-size: 10px;
                    font-weight: 800;
                    padding: 3px 8px;
                    border-radius: 6px;
                    border: 1px solid rgba(16, 185, 129, 0.35);
                """)
                self.lbl_status.setText(t("update_status_latest"))
                self.lbl_status.setStyleSheet("color: #94A3B8; font-size: 12px;")
        except Exception as e:
            self.lbl_status.setText(f"Không thể kết nối máy chủ GitHub ({e}).")
            self.lbl_status.setStyleSheet("color: #F87171; font-size: 12px;")
        finally:
            self.btn_check.setEnabled(True)

    def _open_release_url(self):
        url = self.last_info.download_url if self.last_info and self.last_info.download_url else f"{GITHUB_REPO_URL}/releases"
        QDesktopServices.openUrl(QUrl(url))

    def retranslate_ui(self):
        super().retranslate_ui()
        self.lbl_ver_title.setText(t("update_cur_ver"))
        self.btn_check.setText(f" {t('update_btn_check')}")
        self.btn_view_release.setText(f" {t('update_btn_view_release')}")
        if not self.last_info or not self.last_info.is_update_available:
            self.lbl_status.setText(t("update_status_latest"))

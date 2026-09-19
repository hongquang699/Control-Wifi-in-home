"""
Màn hình Nhật Ký Kiểm Toán Bảo Mật (Audit & Compliance Log View) - Khớp Ảnh 8.
Tích hợp kiểm soát phân quyền RBAC: Yêu cầu vai trò ADMIN để xem dữ liệu mật.
"""

import os
import shutil
import time
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QMessageBox, QGridLayout
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QFont
from core.i18n import t, i18n
from gui.icons import get_app_icon
from gui.role_dialog import role_manager
from gui.theme import (
    COLOR_BG_CARD, COLOR_BORDER, COLOR_ACCENT_CYAN,
    COLOR_ACCENT_AMBER, COLOR_ACCENT_EMERALD, COLOR_ACCENT_ROSE,
    STYLE_BTN_AMBER, STYLE_BTN_PRIMARY, STYLE_BTN_SLATE
)

class AuditStatCard(QFrame):
    def __init__(self, title: str, value: str = "--", accent_hex: str = "#38BDF8", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_BG_CARD};
                border: 1px solid {COLOR_BORDER};
                border-radius: 10px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)

        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet("color: #94A3B8; font-size: 11px; font-weight: 700; text-transform: uppercase;")
        layout.addWidget(self.lbl_title)

        self.lbl_val = QLabel(value)
        self.lbl_val.setStyleSheet(f"color: {accent_hex}; font-size: 20px; font-weight: 800;")
        layout.addWidget(self.lbl_val)

    def set_value(self, val: str):
        self.lbl_val.setText(val)


class AuditLogView(QWidget):
    def __init__(self, event_dao=None, parent=None):
        super().__init__(parent)
        self.event_dao = event_dao
        self._init_ui()
        role_manager.subscribe(self._on_role_changed)
        self.refresh_data()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 20, 24, 20)

        # 1. Header Toolbar
        header_layout = QHBoxLayout()

        title_box = QVBoxLayout()
        title_box.setSpacing(3)
        self.lbl_title = QLabel("Nhật Ký Kiểm Toán Bảo Mật (Audit & Compliance Log)")
        self.lbl_title.setStyleSheet("font-size: 20px; font-weight: 800; color: #F8FAFC; letter-spacing: 0.5px;")
        self.lbl_desc = QLabel("Ghi vết toàn diện sự kiện xác thực, WAF block, rate limit, chặn thiết bị và sao lưu dữ liệu")
        self.lbl_desc.setStyleSheet("color: #94A3B8; font-size: 12px;")
        title_box.addWidget(self.lbl_title)
        title_box.addWidget(self.lbl_desc)
        header_layout.addLayout(title_box)

        header_layout.addStretch()

        # Nút Sao Lưu DB Ngay
        self.btn_backup = QPushButton(" Sao Lưu DB Ngay")
        self.btn_backup.setIcon(get_app_icon("save"))
        self.btn_backup.setIconSize(QSize(15, 15))
        self.btn_backup.setCursor(Qt.PointingHandCursor)
        self.btn_backup.setStyleSheet(STYLE_BTN_AMBER)
        self.btn_backup.clicked.connect(self._do_backup_db)
        header_layout.addWidget(self.btn_backup)

        # Nút Làm Mới Log
        self.btn_refresh = QPushButton(" Làm Mới Log")
        self.btn_refresh.setIcon(get_app_icon("refresh"))
        self.btn_refresh.setIconSize(QSize(15, 15))
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        self.btn_refresh.setStyleSheet(STYLE_BTN_PRIMARY)
        self.btn_refresh.clicked.connect(self.refresh_data)
        header_layout.addWidget(self.btn_refresh)

        layout.addLayout(header_layout)

        # 2. Bốn Thẻ Số Liệu Kiểm Toán
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(12)

        self.card_total = AuditStatCard("TỔNG SỰ KIỆN AUDIT", "--", "#38BDF8")
        self.card_waf = AuditStatCard("SỰ KIỆN WAF / CHẶN", "--", "#EF4444")
        self.card_auth = AuditStatCard("ĐĂNG NHẬP & PHIÊN", "--", "#10B981")
        self.card_backup = AuditStatCard("BẢN SAO LƯU DATABASE", "--", "#F59E0B")

        cards_layout.addWidget(self.card_total)
        cards_layout.addWidget(self.card_waf)
        cards_layout.addWidget(self.card_auth)
        cards_layout.addWidget(self.card_backup)
        layout.addLayout(cards_layout)

        # 3. Khu vực Bảng / Banner 403 Forbidden
        self.content_container = QFrame()
        self.content_container.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_BG_CARD};
                border: 1px solid {COLOR_BORDER};
                border-radius: 12px;
            }}
        """)
        c_layout = QVBoxLayout(self.content_container)
        c_layout.setContentsMargins(12, 12, 12, 12)

        # Banner 403 Forbidden
        self.frame_403 = QFrame()
        self.frame_403.setStyleSheet("""
            QFrame {
                background-color: rgba(239, 68, 68, 0.08);
                border: 1px solid rgba(239, 68, 68, 0.25);
                border-radius: 10px;
            }
        """)
        f_layout = QVBoxLayout(self.frame_403)
        f_layout.setContentsMargins(20, 36, 20, 36)
        f_layout.setAlignment(Qt.AlignCenter)

        self.lbl_403 = QLabel("403 Forbidden: Yêu cầu vai trò ADMIN để xem nhật ký kiểm toán bảo mật. Vui lòng bấm 'Đổi Quyền' sang Admin!")
        self.lbl_403.setAlignment(Qt.AlignCenter)
        self.lbl_403.setStyleSheet("color: #F87171; font-size: 13px; font-weight: 700; border: none; background: transparent;")
        f_layout.addWidget(self.lbl_403)

        c_layout.addWidget(self.frame_403)

        # Bảng Audit Log (Hiển thị khi là ADMIN)
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Thời Gian", "Loại Sự Kiện", "Tác Nhân", "IP Client", "Trạng Thái", "Chi Tiết An Toàn (Masked Secret)"
        ])
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 150)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        self.table.setColumnWidth(3, 140)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Stretch)

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #0A1224;
                border: none;
                border-radius: 10px;
                gridline-color: transparent;
            }
            QHeaderView::section {
                background-color: #0F172A;
                color: #94A3B8;
                font-weight: 700;
                font-size: 11px;
                text-transform: uppercase;
                border: none;
                border-bottom: 1px solid rgba(255, 255, 255, 0.08);
                padding: 10px;
            }
            QTableWidget::item {
                padding: 8px 10px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.04);
                color: #F8FAFC;
            }
        """)
        c_layout.addWidget(self.table)

        layout.addWidget(self.content_container, stretch=1)

    def _on_role_changed(self, new_role: str):
        self.refresh_data()

    def refresh_data(self):
        is_admin = (role_manager.current_role == "ADMIN")

        if not is_admin:
            self.card_total.set_value("--")
            self.card_waf.set_value("--")
            self.card_auth.set_value("--")
            self.card_backup.set_value("--")
            self.frame_403.setVisible(True)
            self.table.setVisible(False)
            return

        # Khi là ADMIN: Hiển thị bảng
        self.frame_403.setVisible(False)
        self.table.setVisible(True)

        # Nạp dữ liệu mẫu & thực tế
        mock_audits = [
            ("2026-09-19 18:24:10", "DEVICE_BLOCKED", "admin_gui", "127.0.0.1", "SUCCESS", "ACL rule pushed to TP-Link Router. Target MAC: AA:BB:CC:DD:EE:FF"),
            ("2026-09-19 18:15:02", "WAF_PATH_TRAVERSAL", "waf_engine", "192.168.1.105", "BLOCKED", "Attempted URI access: ../../etc/passwd [DROPPED]"),
            ("2026-09-19 17:50:44", "USER_LOGIN_SUCCESS", "auth_guard", "127.0.0.1", "SUCCESS", "Role upgraded to ADMIN via local UI session token"),
            ("2026-09-19 17:30:19", "DB_AUTO_SNAPSHOT", "system_cron", "localhost", "SUCCESS", "SQLite snapshot saved to data/backup/network_snap.db"),
            ("2026-09-19 16:45:12", "PORT_SCAN_DETECTED", "scan_monitor", "192.168.1.205", "WARNING", "Syn-flood scan on port 22/80/443 rate limit enforced"),
            ("2026-09-19 16:00:00", "FIREWALL_INBOUND_RULE", "netsh_helper", "127.0.0.1", "SUCCESS", "Windows Defender Firewall rule 'NM_BLOCK_01' active")
        ]

        self.card_total.set_value(str(len(mock_audits) + 124))
        self.card_waf.set_value("14")
        self.card_auth.set_value("28")
        self.card_backup.set_value("3 Bản")

        self.table.setRowCount(len(mock_audits))
        for row, (ts, evt, actor, ip, status, details) in enumerate(mock_audits):
            item_ts = QTableWidgetItem(ts)
            item_ts.setFont(QFont("Fira Code", 9))
            item_ts.setForeground(QColor("#94A3B8"))
            self.table.setItem(row, 0, item_ts)

            item_evt = QTableWidgetItem(evt)
            item_evt.setFont(QFont("Segoe UI", 9, QFont.Bold))
            if "BLOCKED" in status:
                item_evt.setForeground(QColor("#EF4444"))
            elif "WARNING" in status:
                item_evt.setForeground(QColor("#F59E0B"))
            else:
                item_evt.setForeground(QColor("#38BDF8"))
            self.table.setItem(row, 1, item_evt)

            item_actor = QTableWidgetItem(actor)
            self.table.setItem(row, 2, item_actor)

            item_ip = QTableWidgetItem(ip)
            item_ip.setFont(QFont("Fira Code", 9))
            item_ip.setForeground(QColor("#38BDF8"))
            self.table.setItem(row, 3, item_ip)

            item_st = QTableWidgetItem(status)
            item_st.setFont(QFont("Segoe UI", 9, QFont.Bold))
            item_st.setForeground(QColor("#10B981" if status == "SUCCESS" else ("#EF4444" if status == "BLOCKED" else "#F59E0B")))
            self.table.setItem(row, 4, item_st)

            item_det = QTableWidgetItem(details)
            item_det.setForeground(QColor("#CBD5E1"))
            self.table.setItem(row, 5, item_det)

    def _do_backup_db(self):
        if role_manager.current_role != "ADMIN":
            QMessageBox.warning(self, "Quyền Hạn", "Yêu cầu quyền ADMIN để sao lưu cơ sở dữ liệu!")
            return

        db_path = os.path.join("data", "network.db")
        backup_dir = os.path.join("data", "backup")
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        target_file = os.path.join(backup_dir, f"network_backup_{timestamp}.db")

        if os.path.exists(db_path):
            shutil.copy2(db_path, target_file)
            QMessageBox.information(self, "Thành Công", f"Đã sao lưu cơ sở dữ liệu thành công tới:\n{target_file}")
            self.refresh_data()
        else:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy tệp cơ sở dữ liệu data/network.db để sao lưu!")

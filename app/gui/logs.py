"""
Màn hình Nhật Ký Hoạt Động & Kiểm Toán (Audit Logs View) - Hỗ trợ Song ngữ VI / EN.
Truy xuất lịch sử sự kiện mạng từ cơ sở dữ liệu SQLite: kết nối, ngắt kết nối, chặn và đổi IP.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QComboBox
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QColor, QFont
from database.events import EventDAO
from core.i18n import t, i18n
from gui.icons import get_app_icon
from typing import Optional

class LogsView(QWidget):
    def __init__(self, event_dao: EventDAO, parent=None):
        super().__init__(parent)
        self.event_dao = event_dao
        self._init_ui()
        self.retranslate_ui()
        self.load_logs()
        i18n.language_changed.connect(self._on_lang_changed)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 20, 24, 20)

        # 1. Header
        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(3)
        self.lbl_title = QLabel()
        self.lbl_title.setStyleSheet("font-size: 22px; font-weight: 800; color: #F8FAFC; letter-spacing: 0.5px;")
        self.lbl_subtitle = QLabel()
        self.lbl_subtitle.setStyleSheet("color: #94A3B8; font-size: 13px;")
        title_box.addWidget(self.lbl_title)
        title_box.addWidget(self.lbl_subtitle)
        header_layout.addLayout(title_box)
        header_layout.addStretch()

        self.btn_refresh = QPushButton()
        self.btn_refresh.setIcon(get_app_icon("refresh"))
        self.btn_refresh.setIconSize(QSize(16, 16))
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background: #1E293B;
                border: 1px solid rgba(255, 255, 255, 0.1);
                color: #F8FAFC;
                font-weight: 600;
                font-size: 12px;
                padding: 8px 16px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: #334155;
            }
        """)
        self.btn_refresh.clicked.connect(self.load_logs)
        header_layout.addWidget(self.btn_refresh)
        layout.addLayout(header_layout)

        # 2. Filter & Search
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)

        self.cbo_filter = QComboBox()
        self.cbo_filter.setStyleSheet("""
            QComboBox {
                background-color: #0D1322;
                border: 1px solid #1E293B;
                border-radius: 8px;
                color: #F8FAFC;
                padding: 6px 12px;
                min-width: 160px;
                font-size: 12px;
            }
            QComboBox::drop-down { border: none; }
        """)
        self.cbo_filter.currentIndexChanged.connect(self.load_logs)
        filter_layout.addWidget(self.cbo_filter)

        self.txt_search = QLineEdit()
        self.txt_search.addAction(get_app_icon("search"), QLineEdit.LeadingPosition)
        self.txt_search.setPlaceholderText("Tìm kiếm theo MAC, IP hoặc Mô tả...")
        self.txt_search.setStyleSheet("""
            QLineEdit {
                background-color: #0D1322;
                border: 1px solid #1E293B;
                border-radius: 8px;
                color: #F8FAFC;
                padding: 6px 12px;
                font-size: 12px;
            }
            QLineEdit:focus { border: 1px solid #38BDF8; }
        """)
        self.txt_search.textChanged.connect(self.load_logs)
        filter_layout.addWidget(self.txt_search, 1)
        layout.addLayout(filter_layout)

        # 3. Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["THỜI GIAN", "LOẠI SỰ KIỆN", "THIẾT BỊ", "IP / MAC", "CHI TIẾT"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #0D1322;
                border: 1px solid #1E293B;
                border-radius: 12px;
                gridline-color: transparent;
                color: #F8FAFC;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #161F30;
                color: #94A3B8;
                font-size: 11px;
                font-weight: 700;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #1E293B;
            }
            QTableWidget::item {
                padding: 8px 10px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.04);
            }
            QTableWidget::item:selected {
                background-color: rgba(56, 189, 248, 0.15);
            }
        """)
        layout.addWidget(self.table)

    def load_logs(self):
        self.table.setRowCount(0)
        events = self.event_dao.get_recent_events(limit=100)
        
        filter_type = self.cbo_filter.currentData() or "ALL"
        search_kw = self.txt_search.text().strip().lower()

        for ev in events:
            ev_type = ev.get("event_type", "")
            if filter_type != "ALL" and ev_type != filter_type:
                continue

            mac = ev.get("mac", "")
            ip = ev.get("ip", "")
            desc = ev.get("description", "")
            name = ev.get("custom_name") or ev.get("hostname") or ev.get("vendor") or "Thiết bị mạng"

            if search_kw:
                combined = f"{mac} {ip} {desc} {name}".lower()
                if search_kw not in combined:
                    continue

            row = self.table.rowCount()
            self.table.insertRow(row)

            # Cột 1: Thời gian
            item_time = QTableWidgetItem(ev.get("timestamp", ""))
            item_time.setFont(QFont("Fira Code", 9))
            item_time.setForeground(QColor("#94A3B8"))
            self.table.setItem(row, 0, item_time)

            # Cột 2: Loại sự kiện với icon vector chuẩn SVG
            container = QWidget()
            c_layout = QHBoxLayout(container)
            c_layout.setContentsMargins(6, 2, 6, 2)
            c_layout.setSpacing(5)
            c_layout.setAlignment(Qt.AlignCenter)

            lbl_icon = QLabel()
            lbl_icon.setFixedSize(13, 13)
            lbl_type = QLabel(ev_type)
            lbl_type.setFont(QFont("Segoe UI", 8, QFont.Bold))

            if "BLOCK" in ev_type:
                lbl_icon.setPixmap(get_app_icon("blocked").pixmap(13, 13))
                lbl_type.setStyleSheet("color: #F43F5E;")
                container.setStyleSheet("background: rgba(244, 63, 94, 0.12); border: 1px solid rgba(244, 63, 94, 0.25); border-radius: 6px;")
            elif "JOIN" in ev_type:
                lbl_icon.setPixmap(get_app_icon("check").pixmap(13, 13))
                lbl_type.setStyleSheet("color: #10B981;")
                container.setStyleSheet("background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 6px;")
            elif "LEFT" in ev_type or "OFFLINE" in ev_type:
                lbl_icon.setPixmap(get_app_icon("info").pixmap(13, 13))
                lbl_type.setStyleSheet("color: #94A3B8;")
                container.setStyleSheet("background: rgba(148, 163, 184, 0.12); border: 1px solid rgba(148, 163, 184, 0.25); border-radius: 6px;")
            else:
                lbl_icon.setPixmap(get_app_icon("info").pixmap(13, 13))
                lbl_type.setStyleSheet("color: #38BDF8;")
                container.setStyleSheet("background: rgba(56, 189, 248, 0.12); border: 1px solid rgba(56, 189, 248, 0.25); border-radius: 6px;")

            c_layout.addWidget(lbl_icon)
            c_layout.addWidget(lbl_type)
            self.table.setCellWidget(row, 1, container)

            # Cột 3: Tên thiết bị
            item_name = QTableWidgetItem(name)
            item_name.setFont(QFont("Segoe UI", 9, QFont.DemiBold))
            self.table.setItem(row, 2, item_name)

            # Cột 4: IP / MAC
            ip_mac_text = f"{ip or '--'}\n{mac or '--'}"
            item_ip_mac = QTableWidgetItem(ip_mac_text)
            item_ip_mac.setFont(QFont("Fira Code", 8))
            item_ip_mac.setForeground(QColor("#38BDF8"))
            self.table.setItem(row, 3, item_ip_mac)

            # Cột 5: Chi tiết
            item_desc = QTableWidgetItem(desc)
            item_desc.setForeground(QColor("#CBD5E1"))
            self.table.setItem(row, 4, item_desc)

    def _on_lang_changed(self, lang: str):
        self.retranslate_ui()
        self.load_logs()

    def retranslate_ui(self):
        is_vi = i18n.current_lang == "vi"
        if is_vi:
            self.lbl_title.setText("Nhật Ký Hoạt Động & Kiểm Toán")
            self.lbl_subtitle.setText("Lịch sử kết nối, ngắt kết nối và các thao tác bảo mật được ghi nhận vào SQLite cục bộ.")
            self.btn_refresh.setText(" Làm mới")
            self.txt_search.setPlaceholderText("Tìm kiếm theo MAC, IP hoặc Mô tả...")
            
            self.cbo_filter.clear()
            self.cbo_filter.addItem("Tất cả sự kiện", "ALL")
            self.cbo_filter.addItem("Gia nhập mạng (JOIN)", "DEVICE_JOINED")
            self.cbo_filter.addItem("Ngắt kết nối (LEFT)", "DEVICE_LEFT")
            self.cbo_filter.addItem("Chặn thiết bị (BLOCK)", "DEVICE_BLOCKED")
            self.cbo_filter.addItem("Bỏ chặn (UNBLOCK)", "DEVICE_UNBLOCKED")
            self.cbo_filter.addItem("Đổi IP (IP_CHANGED)", "IP_CHANGED")
        else:
            self.lbl_title.setText("Activity & Audit Logs")
            self.lbl_subtitle.setText("Connection history, disconnections, and security actions audited in local SQLite.")
            self.btn_refresh.setText(" Refresh")
            self.txt_search.setPlaceholderText("Search by MAC, IP or Description...")

            self.cbo_filter.clear()
            self.cbo_filter.addItem("All Events", "ALL")
            self.cbo_filter.addItem("Device Joined", "DEVICE_JOINED")
            self.cbo_filter.addItem("Device Disconnected", "DEVICE_LEFT")
            self.cbo_filter.addItem("Device Blocked", "DEVICE_BLOCKED")
            self.cbo_filter.addItem("Device Unblocked", "DEVICE_UNBLOCKED")
            self.cbo_filter.addItem("IP Changed", "IP_CHANGED")

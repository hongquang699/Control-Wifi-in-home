"""
Màn hình Cảnh Báo An Ninh Mạng (Security Alerts View) - Hỗ trợ Song ngữ VI / EN.
Hiển thị các phát hiện bất thường: Thiết bị lạ, Tranh chấp IP, Quét cổng, Băng thông đột biến.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QColor, QFont
from typing import List, Dict, Any
from core.i18n import t, i18n
from gui.icons import get_app_icon
import time

class AlertsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.alerts_data: List[Dict[str, Any]] = [
            {
                "id": "alt-101",
                "level": "INFO",
                "title": "Quét mạng định kỳ thành công",
                "title_en": "Periodic Scan Completed",
                "desc": "Đã quét 2 dải subnet 192.168.1.0/24 & 110.0/24. Tìm thấy 7 thiết bị trực tuyến.",
                "desc_en": "Scanned 2 subnets 192.168.1.0/24 & 110.0/24. Found 7 active devices.",
                "time": "2026-09-19 09:15:00"
            },
            {
                "id": "alt-102",
                "level": "WARNING",
                "title": "Phát hiện thiết bị mới kết nối",
                "title_en": "New Device Detected",
                "desc": "Thiết bị IP 192.168.1.115 (iPhone 15 Pro Max) vừa gia nhập Wi-Fi Tổng.",
                "desc_en": "Device IP 192.168.1.115 (iPhone 15 Pro Max) joined Primary Wi-Fi.",
                "time": "2026-09-19 08:45:12"
            },
            {
                "id": "alt-103",
                "level": "SUCCESS",
                "title": "Tường lửa đồng bộ an toàn",
                "title_en": "Firewall Synchronized",
                "desc": "Các quy tắc chặn 2 chiều Inbound/Outbound của Windows Firewall đang hoạt động tối ưu.",
                "desc_en": "Bidirectional Inbound/Outbound Windows Firewall rules operating properly.",
                "time": "2026-09-19 08:30:00"
            },
            {
                "id": "alt-104",
                "level": "INFO",
                "title": "Giám sát lưu lượng khởi động",
                "title_en": "Traffic Monitor Started",
                "desc": "Thuật toán theo dõi băng thông thời gian thực và tạo biểu đồ sóng đã kích hoạt.",
                "desc_en": "Real-time bandwidth tracker and waveform generator initialized.",
                "time": "2026-09-19 08:00:00"
            }
        ]
        self._init_ui()
        self.retranslate_ui()
        self.load_alerts()
        i18n.language_changed.connect(self._on_lang_changed)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
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
        self.btn_refresh.clicked.connect(self.load_alerts)
        header_layout.addWidget(self.btn_refresh)
        layout.addLayout(header_layout)

        # 2. Bảng cảnh báo
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["MỨC ĐỘ / LEVEL", "TIÊU ĐỀ / TITLE", "CHI TIẾT / DETAILS", "THỜI GIAN / TIME"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setShowGrid(False)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 130)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        self.table.setColumnWidth(3, 140)

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #0A1224;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
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
                padding: 10px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.04);
            }
            QTableWidget::item:selected {
                background-color: rgba(56, 189, 248, 0.15);
            }
        """)
        layout.addWidget(self.table)

    def load_alerts(self):
        self.table.setRowCount(0)
        is_vi = i18n.current_lang == "vi"
        for alert in self.alerts_data:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Cột 1: Level Badge với icon vector chuẩn SVG
            lvl = alert["level"]
            container = QWidget()
            c_layout = QHBoxLayout(container)
            c_layout.setContentsMargins(6, 3, 6, 3)
            c_layout.setSpacing(6)
            c_layout.setAlignment(Qt.AlignCenter)

            badge_icon = QLabel()
            badge_icon.setFixedSize(14, 14)
            badge_text = QLabel(lvl)
            badge_text.setFont(QFont("Segoe UI", 9, QFont.Bold))

            if lvl == "WARNING":
                badge_icon.setPixmap(get_app_icon("warning").pixmap(14, 14))
                badge_text.setStyleSheet("color: #F59E0B;")
                container.setStyleSheet("background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 6px;")
            elif lvl == "CRITICAL":
                badge_icon.setPixmap(get_app_icon("shield_block").pixmap(14, 14))
                badge_text.setStyleSheet("color: #F43F5E;")
                container.setStyleSheet("background: rgba(244, 63, 94, 0.12); border: 1px solid rgba(244, 63, 94, 0.3); border-radius: 6px;")
            elif lvl == "SUCCESS":
                badge_icon.setPixmap(get_app_icon("check").pixmap(14, 14))
                badge_text.setStyleSheet("color: #10B981;")
                container.setStyleSheet("background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 6px;")
            else:
                badge_icon.setPixmap(get_app_icon("info").pixmap(14, 14))
                badge_text.setStyleSheet("color: #38BDF8;")
                container.setStyleSheet("background: rgba(56, 189, 248, 0.12); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 6px;")

            c_layout.addWidget(badge_icon)
            c_layout.addWidget(badge_text)
            self.table.setCellWidget(row, 0, container)

            # Cột 2: Title
            title_text = alert["title"] if is_vi else alert["title_en"]
            item_title = QTableWidgetItem(title_text)
            item_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
            self.table.setItem(row, 1, item_title)

            # Cột 3: Desc
            desc_text = alert["desc"] if is_vi else alert["desc_en"]
            item_desc = QTableWidgetItem(desc_text)
            item_desc.setForeground(QColor("#94A3B8"))
            self.table.setItem(row, 2, item_desc)

            # Cột 4: Time
            item_time = QTableWidgetItem(alert["time"])
            item_time.setFont(QFont("Fira Code", 9))
            item_time.setForeground(QColor("#64748B"))
            self.table.setItem(row, 3, item_time)

    def _on_lang_changed(self, lang: str):
        self.retranslate_ui()
        self.load_alerts()

    def retranslate_ui(self):
        if i18n.current_lang == "vi":
            self.lbl_title.setText("Cảnh Báo An Ninh Mạng")
            self.lbl_subtitle.setText("Theo dõi các hành vi bất thường, phát hiện thiết bị lạ và xung đột IP trong thời gian thực.")
            self.btn_refresh.setText(" Làm mới")
        else:
            self.lbl_title.setText("Security Alerts & Incidents")
            self.lbl_subtitle.setText("Monitor network anomalies, rogue device arrivals, and IP address conflicts in real-time.")
            self.btn_refresh.setText(" Refresh")

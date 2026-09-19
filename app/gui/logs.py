"""
Màn hình Nhật Ký Hoạt Động & Kiểm Toán Mạng (Audit Logs View) - Chuẩn Thiết Kế Cyber Dark-Tech (Ảnh 6).
Bao gồm:
- Header với nút 'Xuất file CSV' (Emerald) và 'Xóa nhật ký'
- Bộ lọc loại sự kiện, ô tìm kiếm và bộ đếm bản ghi
- Bảng hiển thị 6 cột kèm cột Trạng thái '● AUDITED'
"""

import os
import csv
from typing import Optional, List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QComboBox, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QColor, QFont

from database.events import EventDAO
from core.i18n import t, i18n
from gui.icons import get_app_icon
from gui.theme import (
    COLOR_BG_CARD, COLOR_BORDER, COLOR_ACCENT_CYAN,
    COLOR_ACCENT_EMERALD, COLOR_ACCENT_ROSE, COLOR_ACCENT_AMBER,
    STYLE_BTN_EMERALD, STYLE_BTN_SLATE, STYLE_BTN_PRIMARY
)

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

        # 1. Header Toolbar
        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(3)
        self.lbl_title = QLabel("Nhật Ký Hoạt Động & Kiểm Toán Mạng")
        self.lbl_title.setStyleSheet("font-size: 22px; font-weight: 800; color: #F8FAFC; letter-spacing: 0.5px;")
        self.lbl_subtitle = QLabel("Lịch sử sự kiện, can thiệp tường lửa, biến động IP và thao tác quản trị viên")
        self.lbl_subtitle.setStyleSheet("color: #94A3B8; font-size: 13px;")
        title_box.addWidget(self.lbl_title)
        title_box.addWidget(self.lbl_subtitle)
        header_layout.addLayout(title_box)

        header_layout.addStretch()

        # Nút Xuất file CSV (Emerald)
        self.btn_export = QPushButton(" Xuất file CSV")
        self.btn_export.setIcon(get_app_icon("save"))
        self.btn_export.setIconSize(QSize(15, 15))
        self.btn_export.setCursor(Qt.PointingHandCursor)
        self.btn_export.setStyleSheet(STYLE_BTN_EMERALD)
        self.btn_export.clicked.connect(self._export_csv)
        header_layout.addWidget(self.btn_export)

        # Nút Xóa nhật ký (Slate)
        self.btn_clear = QPushButton(" Xóa nhật ký")
        self.btn_clear.setIcon(get_app_icon("delete"))
        self.btn_clear.setIconSize(QSize(15, 15))
        self.btn_clear.setCursor(Qt.PointingHandCursor)
        self.btn_clear.setStyleSheet(STYLE_BTN_SLATE)
        self.btn_clear.clicked.connect(self._clear_logs)
        header_layout.addWidget(self.btn_clear)

        layout.addLayout(header_layout)

        # 2. Filter Bar
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
                min-width: 180px;
                font-size: 12px;
            }
            QComboBox::drop-down { border: none; }
        """)
        self.cbo_filter.addItems([
            "Tất cả loại sự kiện",
            "Chỉ sự kiện Chặn / Bỏ chặn",
            "Chỉ sự kiện Thiết bị mới",
            "Chỉ biến động IP"
        ])
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
                padding: 6px 14px;
                font-size: 12px;
            }
            QLineEdit:focus { border: 1px solid #38BDF8; }
        """)
        self.txt_search.textChanged.connect(self.load_logs)
        filter_layout.addWidget(self.txt_search, 1)

        self.lbl_counter = QLabel("Hiển thị 0 bản ghi")
        self.lbl_counter.setStyleSheet("color: #94A3B8; font-size: 12px; font-weight: 500;")
        filter_layout.addWidget(self.lbl_counter)

        layout.addLayout(filter_layout)

        # 3. Bảng 6 Cột
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "THỜI GIAN",
            "LOẠI SỰ KIỆN",
            "THIẾT BỊ / ĐÍCH",
            "IP & MAC",
            "CHI TIẾT NỘI DUNG",
            "TRẠNG THÁI"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)

        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setShowGrid(False)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #0A1224;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
                gridline-color: transparent;
                color: #F8FAFC;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #0F172A;
                color: #94A3B8;
                font-weight: 700;
                font-size: 11px;
                text-transform: uppercase;
                border: none;
                border-bottom: 1px solid rgba(255, 255, 255, 0.08);
                padding: 10px 8px;
            }
            QTableWidget::item {
                padding: 8px 10px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.04);
            }
            QTableWidget::item:selected {
                background-color: rgba(56, 189, 248, 0.12);
            }
        """)
        layout.addWidget(self.table)

    def load_logs(self):
        self.table.setRowCount(0)
        events = self.event_dao.get_recent_events(limit=200)

        f_idx = self.cbo_filter.currentIndex()
        keyword = self.txt_search.text().strip().lower()

        filtered = []
        for ev in events:
            etype = (getattr(ev, "event_type", "") or "").upper()

            # Lọc loại sự kiện
            if f_idx == 1 and not any(k in etype for k in ("BLOCK", "UNBLOCK")):
                continue
            if f_idx == 2 and not any(k in etype for k in ("NEW", "ONLINE", "CONNECT")):
                continue
            if f_idx == 3 and "IP" not in etype:
                continue

            # Lọc từ khóa
            desc = getattr(ev, "description", "") or ""
            mac = getattr(ev, "device_mac", "") or ""
            ip = getattr(ev, "ip", "") or ""
            target = f"{desc} {mac} {ip} {etype}".lower()
            if keyword and keyword not in target:
                continue

            filtered.append(ev)

        self.lbl_counter.setText(f"Hiển thị {len(filtered)} bản ghi mới nhất")
        self.table.setRowCount(len(filtered))

        for row, ev in enumerate(filtered):
            self.table.setRowHeight(row, 46)

            # Cột 0: Thời gian
            item_t = QTableWidgetItem(str(getattr(ev, "timestamp", "--")))
            item_t.setFont(QFont("Fira Code", 9))
            item_t.setForeground(QColor("#94A3B8"))
            self.table.setItem(row, 0, item_t)

            # Cột 1: Loại sự kiện (Pill badge)
            etype = (getattr(ev, "event_type", "INFO") or "INFO").upper()
            lbl_type = QLabel(f" {etype} ")
            lbl_type.setAlignment(Qt.AlignCenter)
            if "BLOCK" in etype and "UN" not in etype:
                lbl_type.setStyleSheet("background: rgba(244, 63, 94, 0.15); color: #F43F5E; border: 1px solid rgba(244, 63, 94, 0.3); border-radius: 6px; font-size: 10px; font-weight: 800; padding: 2px 6px;")
            elif "UNBLOCK" in etype or "ONLINE" in etype or "SUCCESS" in etype:
                lbl_type.setStyleSheet("background: rgba(16, 185, 129, 0.15); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 6px; font-size: 10px; font-weight: 800; padding: 2px 6px;")
            elif "IP" in etype or "WARN" in etype:
                lbl_type.setStyleSheet("background: rgba(245, 158, 11, 0.15); color: #F59E0B; border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 6px; font-size: 10px; font-weight: 800; padding: 2px 6px;")
            else:
                lbl_type.setStyleSheet("background: rgba(56, 189, 248, 0.15); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 6px; font-size: 10px; font-weight: 800; padding: 2px 6px;")

            c_type = QWidget()
            c_tl = QHBoxLayout(c_type)
            c_tl.setContentsMargins(4, 6, 4, 6)
            c_tl.addWidget(lbl_type)
            self.table.setCellWidget(row, 1, c_type)

            # Cột 2: Thiết bị / Đích
            d_name = getattr(ev, "device_name", "") or getattr(ev, "device_mac", "Network Gateway")
            item_d = QTableWidgetItem(d_name)
            item_d.setIcon(get_app_icon("devices"))
            item_d.setFont(QFont("Segoe UI", 9, QFont.Bold))
            item_d.setForeground(QColor("#F8FAFC"))
            self.table.setItem(row, 2, item_d)

            # Cột 3: IP & MAC
            ip_val = getattr(ev, "ip", "") or "--"
            mac_val = getattr(ev, "device_mac", "") or "--"
            item_ipmac = QTableWidgetItem(f"{ip_val}  |  {mac_val}")
            item_ipmac.setFont(QFont("Fira Code", 9))
            item_ipmac.setForeground(QColor("#38BDF8"))
            self.table.setItem(row, 3, item_ipmac)

            # Cột 4: Chi tiết nội dung
            desc = getattr(ev, "description", "") or "--"
            item_desc = QTableWidgetItem(desc)
            item_desc.setForeground(QColor("#CBD5E1"))
            self.table.setItem(row, 4, item_desc)

            # Cột 5: Trạng thái AUDITED
            lbl_audit = QLabel("● AUDITED")
            lbl_audit.setStyleSheet("background: rgba(16, 185, 129, 0.12); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 6px; font-size: 9px; font-weight: 800; padding: 2px 6px;")
            c_aud = QWidget()
            c_al = QHBoxLayout(c_aud)
            c_al.setContentsMargins(4, 8, 4, 8)
            c_al.addWidget(lbl_audit)
            self.table.setCellWidget(row, 5, c_aud)

    def _export_csv(self):
        events = self.event_dao.get_recent_events(limit=500)
        if not events:
            QMessageBox.information(self, "Thông Báo", "Không có nhật ký nào để xuất.")
            return

        fpath, _ = QFileDialog.getSaveFileName(self, "Lưu file CSV", "audit_logs.csv", "CSV Files (*.csv)")
        if not fpath:
            return

        try:
            with open(fpath, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "EventType", "DeviceName", "MAC", "IP", "Description", "Status"])
                for ev in events:
                    writer.writerow([
                        getattr(ev, "timestamp", ""),
                        getattr(ev, "event_type", ""),
                        getattr(ev, "device_name", ""),
                        getattr(ev, "device_mac", ""),
                        getattr(ev, "ip", ""),
                        getattr(ev, "description", ""),
                        "AUDITED"
                    ])
            QMessageBox.information(self, "Thành Công", f"Đã xuất {len(events)} bản ghi ra file CSV:\n{fpath}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu file: {e}")

    def _clear_logs(self):
        reply = QMessageBox.question(
            self,
            "Xác Nhận",
            "Bạn có chắc chắn muốn làm sạch toàn bộ lịch sử sự kiện?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                self.event_dao.clear_events()
                self.load_logs()
                QMessageBox.information(self, "Đã Xóa", "Đã xóa sạch toàn bộ nhật ký thành công.")
            except Exception as e:
                QMessageBox.warning(self, "Lỗi", f"Không thể xóa nhật ký: {e}")

    def _on_lang_changed(self, lang: str):
        self.retranslate_ui()
        self.load_logs()

    def retranslate_ui(self):
        is_vi = i18n.current_lang == "vi"
        if is_vi:
            self.lbl_title.setText("Nhật Ký Hoạt Động & Kiểm Toán Mạng")
            self.lbl_subtitle.setText("Lịch sử sự kiện, can thiệp tường lửa, biến động IP và thao tác quản trị viên")
            self.btn_export.setText(" Xuất file CSV")
            self.btn_clear.setText(" Xóa nhật ký")
            self.txt_search.setPlaceholderText("Tìm kiếm theo MAC, IP hoặc Mô tả...")
            self.cbo_filter.setItemText(0, "Tất cả loại sự kiện")
            self.cbo_filter.setItemText(1, "Chỉ sự kiện Chặn / Bỏ chặn")
            self.cbo_filter.setItemText(2, "Chỉ sự kiện Thiết bị mới")
            self.cbo_filter.setItemText(3, "Chỉ biến động IP")
        else:
            self.lbl_title.setText("Activity & Network Audit Logs")
            self.lbl_subtitle.setText("Event history, firewall interventions, IP dynamics, and administrator actions")
            self.btn_export.setText(" Export CSV")
            self.btn_clear.setText(" Clear Logs")
            self.txt_search.setPlaceholderText("Search by MAC, IP, or Description...")
            self.cbo_filter.setItemText(0, "All Event Types")
            self.cbo_filter.setItemText(1, "Block / Unblock Events Only")
            self.cbo_filter.setItemText(2, "New Device Events Only")
            self.cbo_filter.setItemText(3, "IP Dynamics Only")

        self.table.setHorizontalHeaderLabels([
            "THỜI GIAN" if is_vi else "TIMESTAMP",
            "LOẠI SỰ KIỆN" if is_vi else "EVENT TYPE",
            "THIẾT BỊ / ĐÍCH" if is_vi else "DEVICE / TARGET",
            "IP & MAC",
            "CHI TIẾT NỘI DUNG" if is_vi else "DESCRIPTION",
            "TRẠNG THÁI" if is_vi else "STATUS"
        ])

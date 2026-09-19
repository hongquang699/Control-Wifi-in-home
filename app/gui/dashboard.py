"""
Màn hình Dashboard Tổng Quan (Network Manager Dashboard)
Thiết kế chuẩn xác theo ảnh mẫu:
- 5 Thẻ Chỉ số Ngang: ONLINE, OFFLINE, BLOCKED, TRAFFIC (Down/Up), CPU/RAM/UPTIME
- Biểu đồ Sóng Lưu lượng Thời gian thực (Live Traffic Waveform Chart)
- Thanh Lọc Subnet Dạng Viên Thuốc (Tất cả, 192.168.1.x, 192.168.110.x, Đang bị chặn) + Ô Tìm Kiếm
- Bảng Thiết Bị Đầy Đủ 7 Cột kèm Thao Tác Chặn / Bỏ Chặn Trực Tiếp
"""

import psutil
from typing import Optional, List

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QMessageBox
)
from PySide6.QtCore import Qt, Signal, QTimer, QSize
from PySide6.QtGui import QFont, QColor

from database.devices import DeviceDAO
from database.events import EventDAO
from security.blocker import BlockManager
from services.traffic_monitor import TrafficMonitor, TrafficStats
from core.device import Device
from core.i18n import t, i18n
from gui.widgets.waveform import LiveWaveformWidget
from gui.device_detail import DeviceDetailDialog
from gui.icons import get_app_icon


class DashboardView(QWidget):
    scan_requested = Signal()

    def __init__(
        self,
        device_dao: DeviceDAO,
        event_dao: EventDAO,
        block_manager: Optional[BlockManager] = None,
        traffic_monitor: Optional[TrafficMonitor] = None,
        parent=None
    ):
        super().__init__(parent)
        self.device_dao = device_dao
        self.event_dao = event_dao
        self.block_manager = block_manager
        self.traffic_monitor = traffic_monitor
        self.active_filter = "all"
        self.search_text = ""

        self._init_ui()
        self.retranslate_ui()
        self.refresh_data()

        # Lắng nghe cập nhật lưu lượng
        if self.traffic_monitor:
            self.traffic_monitor.stats_updated.connect(self._on_traffic_updated)

        # Timer cập nhật CPU / RAM định kỳ 2 giây
        self.sys_timer = QTimer(self)
        self.sys_timer.timeout.connect(self._update_system_metrics)
        self.sys_timer.start(2000)

        i18n.language_changed.connect(self._on_lang_changed)

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(14)

        # ==================== 1. TOP 5 METRICS ROW ====================
        top_cards_layout = QHBoxLayout()
        top_cards_layout.setSpacing(10)

        # Card 1: ONLINE
        self.card_online = QFrame()
        self.card_online.setStyleSheet("""
            QFrame {
                background-color: #0D1322;
                border: 1px solid #1E293B;
                border-radius: 14px;
            }
        """)
        c1_box = QVBoxLayout(self.card_online)
        c1_box.setContentsMargins(14, 12, 14, 12)
        c1_box.setSpacing(6)
        lbl_c1_title = QLabel("ONLINE")
        lbl_c1_title.setStyleSheet("color: #94A3B8; font-size: 11px; font-weight: 600; text-transform: uppercase;")
        c1_box.addWidget(lbl_c1_title)
        val_row1 = QHBoxLayout()
        val_row1.setSpacing(6)
        dot1 = QLabel("●")
        dot1.setStyleSheet("color: #10B981; font-size: 10px;")
        self.lbl_val_online = QLabel("0")
        self.lbl_val_online.setStyleSheet("color: #10B981; font-size: 24px; font-weight: 800; font-family: 'Fira Code', 'Segoe UI', monospace;")
        val_row1.addWidget(dot1)
        val_row1.addWidget(self.lbl_val_online)
        val_row1.addStretch()
        c1_box.addLayout(val_row1)
        top_cards_layout.addWidget(self.card_online, 1)

        # Card 2: OFFLINE
        self.card_offline = QFrame()
        self.card_offline.setStyleSheet("""
            QFrame {
                background-color: #0D1322;
                border: 1px solid #1E293B;
                border-radius: 14px;
            }
        """)
        c2_box = QVBoxLayout(self.card_offline)
        c2_box.setContentsMargins(14, 12, 14, 12)
        c2_box.setSpacing(6)
        lbl_c2_title = QLabel("OFFLINE")
        lbl_c2_title.setStyleSheet("color: #94A3B8; font-size: 11px; font-weight: 600; text-transform: uppercase;")
        c2_box.addWidget(lbl_c2_title)
        val_row2 = QHBoxLayout()
        val_row2.setSpacing(6)
        dot2 = QLabel("●")
        dot2.setStyleSheet("color: #64748B; font-size: 10px;")
        self.lbl_val_offline = QLabel("0")
        self.lbl_val_offline.setStyleSheet("color: #94A3B8; font-size: 24px; font-weight: 800; font-family: 'Fira Code', 'Segoe UI', monospace;")
        val_row2.addWidget(dot2)
        val_row2.addWidget(self.lbl_val_offline)
        val_row2.addStretch()
        c2_box.addLayout(val_row2)
        top_cards_layout.addWidget(self.card_offline, 1)

        # Card 3: BLOCKED
        self.card_blocked = QFrame()
        self.card_blocked.setStyleSheet("""
            QFrame {
                background-color: #0D1322;
                border: 1px solid #1E293B;
                border-radius: 14px;
            }
        """)
        c3_box = QVBoxLayout(self.card_blocked)
        c3_box.setContentsMargins(14, 12, 14, 12)
        c3_box.setSpacing(6)
        lbl_c3_title = QLabel("BLOCKED")
        lbl_c3_title.setStyleSheet("color: #94A3B8; font-size: 11px; font-weight: 600; text-transform: uppercase;")
        c3_box.addWidget(lbl_c3_title)
        val_row3 = QHBoxLayout()
        val_row3.setSpacing(6)
        dot3 = QLabel("●")
        dot3.setStyleSheet("color: #F43F5E; font-size: 10px;")
        self.lbl_val_blocked = QLabel("0")
        self.lbl_val_blocked.setStyleSheet("color: #F43F5E; font-size: 24px; font-weight: 800; font-family: 'Fira Code', 'Segoe UI', monospace;")
        val_row3.addWidget(dot3)
        val_row3.addWidget(self.lbl_val_blocked)
        val_row3.addStretch()
        c3_box.addLayout(val_row3)
        top_cards_layout.addWidget(self.card_blocked, 1)

        # Card 4: TRAFFIC
        self.card_traffic = QFrame()
        self.card_traffic.setStyleSheet("""
            QFrame {
                background-color: #0D1322;
                border: 1px solid #1E293B;
                border-radius: 14px;
            }
        """)
        c4_box = QVBoxLayout(self.card_traffic)
        c4_box.setContentsMargins(14, 12, 14, 12)
        c4_box.setSpacing(5)
        lbl_c4_title = QLabel("TRAFFIC")
        lbl_c4_title.setStyleSheet("color: #94A3B8; font-size: 11px; font-weight: 600; text-transform: uppercase;")
        c4_box.addWidget(lbl_c4_title)
        self.lbl_val_traffic_down = QLabel("↓ 0.0 KB/s")
        self.lbl_val_traffic_down.setStyleSheet("color: #38BDF8; font-size: 13px; font-weight: 700; font-family: 'Fira Code', 'Consolas', monospace;")
        self.lbl_val_traffic_up = QLabel("↑ 0.0 KB/s")
        self.lbl_val_traffic_up.setStyleSheet("color: #818CF8; font-size: 11px; font-weight: 600; font-family: 'Fira Code', 'Consolas', monospace;")
        c4_box.addWidget(self.lbl_val_traffic_down)
        c4_box.addWidget(self.lbl_val_traffic_up)
        top_cards_layout.addWidget(self.card_traffic, 1)

        # Card 5: CPU / RAM / UPTIME
        self.card_sys = QFrame()
        self.card_sys.setStyleSheet("""
            QFrame {
                background-color: #0D1322;
                border: 1px solid #1E293B;
                border-radius: 14px;
            }
        """)
        c5_box = QVBoxLayout(self.card_sys)
        c5_box.setContentsMargins(14, 12, 14, 12)
        c5_box.setSpacing(5)
        lbl_c5_title = QLabel("CPU / RAM / UPTIME")
        lbl_c5_title.setStyleSheet("color: #94A3B8; font-size: 11px; font-weight: 600; text-transform: uppercase;")
        c5_box.addWidget(lbl_c5_title)
        self.lbl_val_sys_usage = QLabel("CPU 14% | RAM 32%")
        self.lbl_val_sys_usage.setStyleSheet("color: #F59E0B; font-size: 12px; font-weight: 700; font-family: 'Fira Code', monospace;")
        self.lbl_val_sys_uptime = QLabel("99.98% (14d 6h)")
        self.lbl_val_sys_uptime.setStyleSheet("color: #64748B; font-size: 11px; font-family: 'Fira Code', monospace;")
        c5_box.addWidget(self.lbl_val_sys_usage)
        c5_box.addWidget(self.lbl_val_sys_uptime)
        top_cards_layout.addWidget(self.card_sys, 1)

        main_layout.addLayout(top_cards_layout)

        # ==================== 2. LIVE TRAFFIC WAVEFORM CARD ====================
        chart_card = QFrame()
        chart_card.setStyleSheet("""
            QFrame {
                background-color: #0D1322;
                border: 1px solid #1E293B;
                border-radius: 14px;
            }
        """)
        chart_box = QVBoxLayout(chart_card)
        chart_box.setContentsMargins(16, 12, 16, 14)
        chart_box.setSpacing(8)

        # Header của Chart
        chart_header = QHBoxLayout()
        chart_header.setSpacing(8)
        
        lbl_dot = QLabel("●")
        lbl_dot.setStyleSheet("color: #38BDF8; font-size: 14px;")
        lbl_chart_title = QLabel("Live Traffic Waveform Chart")
        lbl_chart_title.setStyleSheet("color: #F8FAFC; font-size: 13px; font-weight: 700;")
        chart_header.addWidget(lbl_dot)
        chart_header.addWidget(lbl_chart_title)
        chart_header.addStretch()

        # Chú thích Download / Upload
        lbl_leg_down = QLabel("■ Download")
        lbl_leg_down.setStyleSheet("color: #38BDF8; font-size: 11px; font-weight: 600; margin-right: 12px;")
        lbl_leg_up = QLabel("■ Upload")
        lbl_leg_up.setStyleSheet("color: #818CF8; font-size: 11px; font-weight: 600;")
        chart_header.addWidget(lbl_leg_down)
        chart_header.addWidget(lbl_leg_up)
        chart_box.addLayout(chart_header)

        # Wave Canvas
        self.wave_canvas = LiveWaveformWidget()
        chart_box.addWidget(self.wave_canvas)
        main_layout.addWidget(chart_card)

        # ==================== 3. FILTER & SEARCH BAR ====================
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)

        self.btn_filter_all = QPushButton("Tất cả (7)")
        self.btn_filter_primary = QPushButton("192.168.1.x")
        self.btn_filter_secondary = QPushButton("192.168.110.x")
        self.btn_filter_blocked = QPushButton("Đang bị chặn")

        self.filter_buttons = [
            ("all", self.btn_filter_all),
            ("primary", self.btn_filter_primary),
            ("secondary", self.btn_filter_secondary),
            ("blocked", self.btn_filter_blocked),
        ]

        for filter_key, btn in self.filter_buttons:
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, k=filter_key: self._set_filter(k))
            filter_layout.addWidget(btn)

        filter_layout.addStretch()

        # Ô tìm kiếm với Vector SVG Icon Flaticon
        self.txt_search = QLineEdit()
        self.txt_search.addAction(get_app_icon("search"), QLineEdit.LeadingPosition)
        self.txt_search.setPlaceholderText("Tìm theo IP, MAC, Tên...")
        self.txt_search.setStyleSheet("""
            QLineEdit {
                background-color: #0D1322;
                border: 1px solid #1E293B;
                border-radius: 8px;
                color: #F8FAFC;
                padding: 6px 14px;
                min-width: 240px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #38BDF8;
            }
        """)
        self.txt_search.textChanged.connect(self._on_search_changed)
        filter_layout.addWidget(self.txt_search)

        self._update_filter_styles()
        main_layout.addLayout(filter_layout)

        # ==================== 4. DEVICES TABLE ====================
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "THIẾT BỊ & TÊN",
            "IP ADDRESS",
            "MAC ADDRESS",
            "VENDOR",
            "PHƯƠNG THỨC",
            "TRẠNG THÁI",
            "THAO TÁC"
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        self.table.setColumnWidth(1, 135)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        self.table.setColumnWidth(2, 145)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        self.table.setColumnWidth(3, 120)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        self.table.setColumnWidth(4, 110)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        self.table.setColumnWidth(5, 95)
        header.setSectionResizeMode(6, QHeaderView.Fixed)
        self.table.setColumnWidth(6, 110)

        self.table.verticalHeader().setDefaultSectionSize(52)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setShowGrid(False)
        self.table.itemDoubleClicked.connect(self._on_table_double_clicked)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #0D1322;
                border: 1px solid #1E293B;
                border-radius: 14px;
                color: #F8FAFC;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #121A2D;
                color: #94A3B8;
                font-size: 11px;
                font-weight: 700;
                padding: 10px 8px;
                border: none;
                border-bottom: 1px solid #1E293B;
            }
            QTableWidget::item {
                padding: 8px 10px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.04);
            }
            QTableWidget::item:selected {
                background-color: rgba(56, 189, 248, 0.12);
            }
        """)
        main_layout.addWidget(self.table, 1)

    def _set_filter(self, filter_key: str):
        self.active_filter = filter_key
        self._update_filter_styles()
        self.refresh_devices_table()

    def _update_filter_styles(self):
        for k, btn in self.filter_buttons:
            if k == self.active_filter:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #0284C7;
                        color: #FFFFFF;
                        font-weight: 700;
                        font-size: 11px;
                        border: 1px solid #38BDF8;
                        border-radius: 7px;
                        padding: 6px 14px;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #0D1322;
                        color: #94A3B8;
                        font-weight: 600;
                        font-size: 11px;
                        border: 1px solid #1E293B;
                        border-radius: 7px;
                        padding: 6px 14px;
                    }
                    QPushButton:hover {
                        background-color: #1E293B;
                        color: #F8FAFC;
                    }
                """)

    def _on_search_changed(self, text: str):
        self.search_text = text.strip().lower()
        self.refresh_devices_table()

    def _update_system_metrics(self):
        try:
            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory().percent
            self.lbl_val_sys_usage.setText(f"CPU {cpu:.0f}% | RAM {ram:.0f}%")
        except Exception:
            pass

    def _on_traffic_updated(self, stats: TrafficStats):
        down_mb = stats.current_download_speed / (1024 * 1024)
        up_mb = stats.current_upload_speed / (1024 * 1024)
        self.lbl_val_traffic_down.setText(f"↓ {down_mb:.1f} MB/s")
        self.lbl_val_traffic_up.setText(f"↑ {up_mb:.1f} MB/s")
        self.wave_canvas.update_speeds(down_mb, up_mb)

    def refresh_data(self):
        counts = self.device_dao.get_device_counts()
        self.lbl_val_online.setText(str(counts.get("online", 0)))
        self.lbl_val_offline.setText(str(counts.get("offline", 0)))
        self.lbl_val_blocked.setText(str(counts.get("blocked", 0)))
        self.btn_filter_all.setText(f"Tất cả ({counts.get('total', 0)})")
        self.refresh_devices_table()

    def refresh_devices_table(self):
        self.table.setRowCount(0)
        devices = self.device_dao.get_all_devices()

        # Lọc danh sách
        filtered: List[Device] = []
        for d in devices:
            # 1. Lọc theo Subnet / Trạng thái
            if self.active_filter == "primary" and not (d.ip and d.ip.startswith("192.168.1.")):
                continue
            if self.active_filter == "secondary" and not (d.ip and (d.ip.startswith("192.168.110.") or d.ip.startswith("192.168.2."))):
                continue
            if self.active_filter == "blocked" and d.status != "BLOCKED":
                continue

            # 2. Lọc theo từ khóa tìm kiếm
            if self.search_text:
                q = self.search_text
                haystack = f"{d.custom_name or ''} {d.hostname or ''} {d.ip or ''} {d.mac or ''} {d.vendor or ''}".lower()
                if q not in haystack:
                    continue

            filtered.append(d)

        self.table.setRowCount(len(filtered))

        is_vi = i18n.current_lang == "vi"

        for row, dev in enumerate(filtered):
            self.table.setRowHeight(row, 50)

            # Cột 0: THIẾT BỊ & TÊN (Vector SVG Icon Flaticon)
            name = dev.custom_name or dev.hostname or dev.vendor or "Thiết bị mạng"
            dev_type = dev.device_type or "PC / Laptop"
            t_lower = (dev_type + " " + (dev.vendor or "") + " " + name).lower()
            if any(x in t_lower for x in ["router", "ap", "access point", "gateway", "switch"]):
                icon_key = "router"
            elif any(x in t_lower for x in ["phone", "iphone", "samsung", "xiaomi", "mobile", "android", "oppo", "vivo", "tablet", "ipad"]):
                icon_key = "smartphone"
            elif any(x in t_lower for x in ["laptop", "macbook", "notebook", "thinkpad"]):
                icon_key = "laptop"
            elif any(x in t_lower for x in ["tv", "television", "smart tv", "media", "roku", "chromecast", "firetv"]):
                icon_key = "tv"
            elif any(x in t_lower for x in ["printer", "canon", "epson", "hp print"]):
                icon_key = "printer"
            elif any(x in t_lower for x in ["camera", "cam", "cctv", "ipcam"]):
                icon_key = "camera"
            else:
                icon_key = "devices"

            c_name = QWidget()
            c_name_layout = QHBoxLayout(c_name)
            c_name_layout.setContentsMargins(6, 4, 6, 4)
            c_name_layout.setSpacing(10)

            icon_lbl = QLabel()
            icon_lbl.setPixmap(get_app_icon(icon_key).pixmap(22, 22))
            icon_lbl.setFixedSize(24, 24)

            text_box = QVBoxLayout()
            text_box.setSpacing(1)
            text_box.setContentsMargins(0, 0, 0, 0)
            lbl_n = QLabel(f"<b>{name}</b>")
            lbl_n.setStyleSheet("color: #F8FAFC; font-size: 12px; background: transparent;")
            lbl_t = QLabel(dev_type)
            lbl_t.setStyleSheet("color: #94A3B8; font-size: 10px; background: transparent;")
            text_box.addWidget(lbl_n)
            text_box.addWidget(lbl_t)

            c_name_layout.addWidget(icon_lbl)
            c_name_layout.addLayout(text_box)
            c_name_layout.addStretch()
            self.table.setCellWidget(row, 0, c_name)

            # Cột 1: IP ADDRESS
            item_ip = QTableWidgetItem(dev.ip or "--")
            item_ip.setFont(QFont("Fira Code", 10, QFont.Bold))
            item_ip.setForeground(QColor("#38BDF8"))
            self.table.setItem(row, 1, item_ip)

            # Cột 2: MAC ADDRESS
            item_mac = QTableWidgetItem(dev.mac or "--")
            item_mac.setFont(QFont("Fira Code", 9))
            item_mac.setForeground(QColor("#94A3B8"))
            self.table.setItem(row, 2, item_mac)

            # Cột 3: VENDOR
            item_vendor = QTableWidgetItem(dev.vendor or "Unknown")
            item_vendor.setForeground(QColor("#CBD5E1"))
            self.table.setItem(row, 3, item_vendor)

            # Cột 4: PHƯƠNG THỨC (Vector SVG Icon)
            medium = getattr(dev, "connection_type", "") or "Wi-Fi"
            is_wifi = "Wi-Fi" in medium or "wifi" in medium.lower()
            c_conn = QWidget()
            c_conn_layout = QHBoxLayout(c_conn)
            c_conn_layout.setContentsMargins(6, 4, 6, 4)
            c_conn_layout.setSpacing(6)
            conn_icon = QLabel()
            conn_icon.setPixmap(get_app_icon("wifi" if is_wifi else "ethernet").pixmap(14, 14))
            conn_lbl = QLabel("Wi-Fi" if is_wifi else "LAN")
            conn_lbl.setStyleSheet("color: #94A3B8; font-size: 11px; font-weight: 500; background: transparent;")
            c_conn_layout.addWidget(conn_icon)
            c_conn_layout.addWidget(conn_lbl)
            c_conn_layout.addStretch()
            self.table.setCellWidget(row, 4, c_conn)

            # Cột 5: TRẠNG THÁI (Pill Badge)
            lbl_status = QLabel()
            lbl_status.setAlignment(Qt.AlignCenter)
            if dev.status == "ONLINE":
                lbl_status.setText("ONLINE")
                lbl_status.setStyleSheet("color: #10B981; font-weight: 800; font-size: 10px; background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 9px; padding: 2px 8px;")
            elif dev.status == "BLOCKED":
                lbl_status.setText("BLOCKED")
                lbl_status.setStyleSheet("color: #F43F5E; font-weight: 800; font-size: 10px; background: rgba(244, 63, 94, 0.15); border: 1px solid rgba(244, 63, 94, 0.3); border-radius: 9px; padding: 2px 8px;")
            else:
                lbl_status.setText("OFFLINE")
                lbl_status.setStyleSheet("color: #94A3B8; font-weight: 800; font-size: 10px; background: rgba(148, 163, 184, 0.15); border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 9px; padding: 2px 8px;")
            
            c_status = QWidget()
            c_status_layout = QHBoxLayout(c_status)
            c_status_layout.setContentsMargins(4, 8, 4, 8)
            c_status_layout.addWidget(lbl_status)
            self.table.setCellWidget(row, 5, c_status)

            # Cột 6: THAO TÁC (Nút Chặn / Bỏ chặn dạng Pill đỏ/xanh chuẩn Demo Web)
            is_blocked = dev.status == "BLOCKED"
            btn_action = QPushButton(("Bỏ chặn" if is_vi else "Unblock") if is_blocked else ("Chặn" if is_vi else "Block"))
            btn_action.setIcon(get_app_icon("shield_check" if is_blocked else "shield_block"))
            btn_action.setIconSize(QSize(13, 13))
            btn_action.setCursor(Qt.PointingHandCursor)
            btn_action.setFixedHeight(28)
            if is_blocked:
                btn_action.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(16, 185, 129, 0.12);
                        color: #10B981;
                        border: 1px solid rgba(16, 185, 129, 0.4);
                        border-radius: 6px;
                        font-weight: 700;
                        font-size: 11px;
                        padding: 3px 12px;
                    }
                    QPushButton:hover {
                        background-color: rgba(16, 185, 129, 0.25);
                    }
                """)
            else:
                btn_action.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(244, 63, 94, 0.12);
                        color: #F43F5E;
                        border: 1px solid rgba(244, 63, 94, 0.4);
                        border-radius: 6px;
                        font-weight: 700;
                        font-size: 11px;
                        padding: 3px 12px;
                    }
                    QPushButton:hover {
                        background-color: rgba(244, 63, 94, 0.25);
                    }
                """)

            btn_action.clicked.connect(lambda chk=False, d=dev: self._toggle_block_device(d))
            
            c_act = QWidget()
            c_act_layout = QHBoxLayout(c_act)
            c_act_layout.setContentsMargins(4, 4, 4, 4)
            c_act_layout.setAlignment(Qt.AlignCenter)
            c_act_layout.addWidget(btn_action)
            self.table.setCellWidget(row, 6, c_act)

    def _on_table_double_clicked(self, item: QTableWidgetItem):
        row = item.row()
        item_ip = self.table.item(row, 1)
        if item_ip:
            ip_str = item_ip.text().strip()
            dev = self.device_dao.get_device_by_ip(ip_str)
            if dev:
                self._open_device_detail(dev)

    def _open_device_detail(self, dev: Device):
        dlg = DeviceDetailDialog(
            device=dev,
            device_dao=self.device_dao,
            event_dao=self.event_dao,
            block_manager=self.block_manager,
            parent=self
        )
        dlg.device_changed.connect(self.refresh_data)
        dlg.exec()

    def _toggle_block_device(self, dev: Device):
        if not self.block_manager:
            return

        is_blocked = dev.status == "BLOCKED"
        target_name = dev.custom_name or dev.hostname or dev.mac
        
        if is_blocked:
            ok, msg = self.block_manager.unblock_device(mac=dev.mac)
            if ok:
                QMessageBox.information(self, "Thành Công", f"Đã gỡ bỏ lệnh chặn thiết bị {target_name} ({dev.mac}).")
            else:
                QMessageBox.warning(self, "Thất Bại", f"Không thể bỏ chặn: {msg}")
        else:
            reply = QMessageBox.question(
                self,
                "Xác Nhận Chặn",
                f"Bạn có chắc chắn muốn chặn thiết bị '{target_name}' ({dev.mac}) qua Router và Tường lửa?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                ok, msg = self.block_manager.block_device(mac=dev.mac, ip=dev.ip, reason="Chặn qua Dashboard")
                if ok:
                    QMessageBox.information(self, "Đã Chặn", f"Đã gửi lệnh chặn thiết bị {target_name} ({dev.mac}) thành công.")
                else:
                    QMessageBox.warning(self, "Thất Bại", f"Không thể chặn thiết bị: {msg}")

        self.refresh_data()

    def _on_lang_changed(self, lang: str):
        self.retranslate_ui()
        self.refresh_data()

    def retranslate_ui(self):
        is_vi = i18n.current_lang == "vi"
        if is_vi:
            self.btn_filter_primary.setText("192.168.1.x")
            self.btn_filter_secondary.setText("192.168.110.x")
            self.btn_filter_blocked.setText("Đang bị chặn")
            self.txt_search.setPlaceholderText("Tìm theo IP, MAC, Tên...")
        else:
            self.btn_filter_primary.setText("192.168.1.x")
            self.btn_filter_secondary.setText("192.168.110.x")
            self.btn_filter_blocked.setText("Blocked Only")
            self.txt_search.setPlaceholderText("Search by IP, MAC, Name...")

    def update_network_info(self, iface):
        self.current_iface = iface

    def set_scanning_state(self, is_scanning: bool, progress: int = 0, message: str = ""):
        self.is_scanning = is_scanning


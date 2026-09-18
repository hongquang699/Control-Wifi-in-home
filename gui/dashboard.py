"""
Màn hình Dashboard tổng quan: số liệu thống kê, trạng thái mạng và sự kiện gần đây (Song ngữ VI / EN).
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QGridLayout, QGroupBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor
from typing import Dict, List, Optional
from database.devices import DeviceDAO
from database.events import EventDAO
from core.network import NetworkManagerCore
from core.i18n import t, i18n
from services.traffic_monitor import TrafficMonitor, TrafficStats
from gui.traffic_chart import TrafficChart
from gui.theme import (
    MetricCard, COLOR_BG_CARD, COLOR_BORDER, COLOR_ACCENT_INDIGO,
    COLOR_ACCENT_CYAN, COLOR_ACCENT_EMERALD, COLOR_ACCENT_ROSE
)

class StatCard(MetricCard):
    """Lớp tương thích ngược kế thừa từ MetricCard hiện đại."""
    def __init__(self, title_key: str, value: str = "0", color_hex: str = "#3B82F6", parent=None):
        icon = "📊"
        if "online" in title_key:
            icon = "🟢"
        elif "offline" in title_key:
            icon = "⚪"
        elif "blocked" in title_key:
            icon = "🚫"
        elif "total" in title_key:
            icon = "🌐"
        super().__init__(icon_str=icon, title_key=title_key, value=value, accent_hex=color_hex, parent=parent)

class DashboardView(QWidget):
    scan_requested = Signal()

    def __init__(self, device_dao: DeviceDAO, event_dao: EventDAO, traffic_monitor: Optional[TrafficMonitor] = None, parent=None):
        super().__init__(parent)
        self.device_dao = device_dao
        self.event_dao = event_dao
        self.traffic_monitor = traffic_monitor
        self.current_iface = None
        self._is_scanning = False
        self._last_progress = 0
        self._last_msg = ""
        self._init_ui()
        self.retranslate_ui()
        self.refresh_data()
        i18n.language_changed.connect(self._on_lang_changed)
        if self.traffic_monitor:
            self.traffic_monitor.stats_updated.connect(self._on_traffic_updated)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 20, 24, 20)

        # 1. Header & Nút Quét nhanh
        header_layout = QHBoxLayout()
        
        title_box = QVBoxLayout()
        title_box.setSpacing(3)
        self.lbl_title = QLabel()
        self.lbl_title.setStyleSheet("font-size: 22px; font-weight: 800; color: #F8FAFC; letter-spacing: 0.5px;")
        self.lbl_net_info = QLabel("...")
        self.lbl_net_info.setStyleSheet("color: #94A3B8; font-size: 13px;")
        title_box.addWidget(self.lbl_title)
        title_box.addWidget(self.lbl_net_info)
        
        header_layout.addLayout(title_box)
        header_layout.addStretch()

        self.btn_scan = QPushButton()
        self.btn_scan.setCursor(Qt.PointingHandCursor)
        self.btn_scan.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4F46E5, stop:1 #06B6D4);
                color: white;
                font-weight: bold;
                font-size: 13px;
                padding: 10px 22px;
                border-radius: 9px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4338CA, stop:1 #0891B2);
            }
            QPushButton:disabled {
                background: #1E293B;
                color: #64748B;
            }
        """)
        self.btn_scan.clicked.connect(self.scan_requested.emit)
        header_layout.addWidget(self.btn_scan)
        layout.addLayout(header_layout)

        # Progress bar khi quét
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 6px;
                background-color: #0A1224;
                text-align: center;
                color: white;
                font-weight: bold;
                height: 18px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4F46E5, stop:1 #06B6D4);
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.progress_bar)

        # 2. Thẻ số liệu thống kê (Hero MetricCards)
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(14)
        
        self.card_total = MetricCard("🌐", "card_total", "0", "#6366F1")
        self.card_online = MetricCard("🟢", "card_online", "0", "#10B981")
        self.card_offline = MetricCard("⚪", "card_offline", "0", "#64748B")
        self.card_blocked = MetricCard("🚫", "card_blocked", "0", "#F43F5E")
        
        cards_layout.addWidget(self.card_total)
        cards_layout.addWidget(self.card_online)
        cards_layout.addWidget(self.card_offline)
        cards_layout.addWidget(self.card_blocked)
        layout.addLayout(cards_layout)

        # 2.5 Biểu đồ Băng thông Mạng Mini
        traffic_frame = QFrame()
        traffic_frame.setObjectName("traffic_frame")
        traffic_frame.setStyleSheet("""
            QFrame#traffic_frame {
                background-color: #0E172E;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
            }
        """)
        traffic_box = QVBoxLayout(traffic_frame)
        traffic_box.setContentsMargins(14, 10, 14, 10)
        traffic_box.setSpacing(6)
        self.lbl_dash_traffic = QLabel()
        self.lbl_dash_traffic.setStyleSheet("color: #F8FAFC; font-size: 13px; font-weight: bold;")
        traffic_box.addWidget(self.lbl_dash_traffic)

        self.chart_mini = TrafficChart(max_samples=60, compact=True)
        self.chart_mini.setFixedHeight(115)
        traffic_box.addWidget(self.chart_mini)
        layout.addWidget(traffic_frame)

        # 3. Phân chia 2 cột: Thông tin mạng & Nhật ký sự kiện gần đây
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(14)

        # Cột trái: Chi tiết mạng & Phân loại thiết bị
        info_frame = QFrame()
        info_frame.setObjectName("info_frame")
        info_frame.setStyleSheet("""
            QFrame#info_frame {
                background-color: #0E172E;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
            }
        """)
        info_vbox = QVBoxLayout(info_frame)
        info_vbox.setContentsMargins(14, 12, 14, 12)
        info_vbox.setSpacing(6)
        
        self.lbl_sub_info = QLabel()
        self.lbl_sub_info.setStyleSheet("color: #F8FAFC; font-size: 14px; font-weight: bold;")
        info_vbox.addWidget(self.lbl_sub_info)

        self.lbl_detail_interface = QLabel("...")
        self.lbl_detail_ip = QLabel("...")
        self.lbl_detail_gateway = QLabel("...")
        self.lbl_detail_subnet = QLabel("...")
        self.lbl_type_dist = QLabel("...")
        self.lbl_net_dist = QLabel("...")
        self.lbl_conn_dist = QLabel("...")

        for lbl in [self.lbl_detail_interface, self.lbl_detail_ip, self.lbl_detail_gateway, self.lbl_detail_subnet, self.lbl_type_dist]:
            lbl.setStyleSheet("color: #CBD5E1; font-size: 12px; background: transparent; border: none;")
            lbl.setWordWrap(True)
            info_vbox.addWidget(lbl)

        dist_box = QFrame()
        dist_box.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 8px;
        """)
        dist_layout = QVBoxLayout(dist_box)
        dist_layout.setContentsMargins(10, 8, 10, 8)
        dist_layout.setSpacing(4)
        for lbl in [self.lbl_net_dist, self.lbl_conn_dist]:
            lbl.setStyleSheet("color: #38BDF8; font-size: 12px; font-weight: 600; background: transparent; border: none;")
            lbl.setWordWrap(True)
            dist_layout.addWidget(lbl)
        info_vbox.addWidget(dist_box)
        info_vbox.addStretch()
        bottom_layout.addWidget(info_frame, 1)

        # Cột phải: Bảng sự kiện mạng gần đây
        events_frame = QFrame()
        events_frame.setObjectName("events_frame")
        events_frame.setStyleSheet("""
            QFrame#events_frame {
                background-color: #0E172E;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
            }
        """)
        events_vbox = QVBoxLayout(events_frame)
        events_vbox.setContentsMargins(14, 12, 14, 12)
        events_vbox.setSpacing(6)
        
        self.lbl_events_title = QLabel()
        self.lbl_events_title.setStyleSheet("color: #F8FAFC; font-size: 14px; font-weight: bold;")
        events_vbox.addWidget(self.lbl_events_title)

        self.table_events = QTableWidget()
        self.table_events.setColumnCount(4)
        self.table_events.verticalHeader().setVisible(False)
        self.table_events.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_events.setShowGrid(False)

        ev_header = self.table_events.horizontalHeader()
        ev_header.setSectionResizeMode(QHeaderView.Interactive)
        ev_header.setSectionResizeMode(0, QHeaderView.Fixed)
        ev_header.setSectionResizeMode(1, QHeaderView.Fixed)
        ev_header.setSectionResizeMode(2, QHeaderView.Fixed)
        ev_header.setSectionResizeMode(3, QHeaderView.Stretch)
        self.table_events.setColumnWidth(0, 130)
        self.table_events.setColumnWidth(1, 110)
        self.table_events.setColumnWidth(2, 135)

        events_vbox.addWidget(self.table_events)

        bottom_layout.addWidget(events_frame, 2)
        layout.addLayout(bottom_layout, 1)

    def retranslate_ui(self):
        self.lbl_title.setText(t("dash_title"))
        if not self._is_scanning:
            self.btn_scan.setText(f"  {t('dash_scan_now')}")
        else:
            self.btn_scan.setText(f"  {t('dash_scanning')}")

        for card in (self.card_total, self.card_online, self.card_offline, self.card_blocked):
            card.retranslate_ui()

        self.lbl_dash_traffic.setText(t("dash_traffic_title"))
        self.chart_mini.update()

        self.lbl_sub_info.setText(t("net_params_title"))
        self.lbl_events_title.setText(t("recent_events_title"))
        self.table_events.setHorizontalHeaderLabels([
            t("col_time"), t("col_event_type"), t("col_mac"), t("col_desc")
        ])
        if self.current_iface:
            self.update_network_info(self.current_iface)

    def _on_traffic_updated(self, stats: TrafficStats):
        self.chart_mini.update_data(
            history=stats.history,
            current_down=stats.current_download_speed,
            current_up=stats.current_upload_speed,
            peak_down=stats.peak_download_speed,
            peak_up=stats.peak_upload_speed
        )

    def _on_lang_changed(self, lang: str):
        self.retranslate_ui()
        self.refresh_data()

    def update_network_info(self, iface):
        self.current_iface = iface
        if iface:
            self.lbl_net_info.setText(f"Subnet: {iface.cidr} | Gateway: {iface.gateway} | Host IP: {iface.ip}")
            self.lbl_detail_interface.setText(t("net_param_iface", val=iface.alias))
            self.lbl_detail_ip.setText(t("net_param_ip", val=iface.ip))
            self.lbl_detail_gateway.setText(t("net_param_gw", val=iface.gateway))
            self.lbl_detail_subnet.setText(t("net_param_subnet", val=iface.cidr, mask=iface.subnet_mask))

    def refresh_data(self):
        counts = self.device_dao.get_device_counts()
        self.card_total.set_value(counts["total"])
        self.card_online.set_value(counts["online"])
        self.card_offline.set_value(counts["offline"])
        self.card_blocked.set_value(counts["blocked"])

        # Phân loại thiết bị
        devices = self.device_dao.get_all_devices(status_filter="ONLINE")
        types_count = {}
        for d in devices:
            types_count[d.device_type] = types_count.get(d.device_type, 0) + 1
        summary_str = " | ".join([f"{k}: {v}" for k, v in types_count.items()])
        self.lbl_type_dist.setText(t("net_param_dist", val=summary_str or "N/A"))

        # Phân bố Mạng & Phương thức kết nối
        dist = self.device_dao.get_network_distribution()
        self.lbl_net_dist.setText(
            f"• Mạng kết nối: 🌐 Wi-Fi Tổng: {dist['primary_net']} | 📡 Router Phụ: {dist['secondary_net']}"
        )
        self.lbl_conn_dist.setText(
            f"• Phương thức: 📶 Wi-Fi: {dist['wifi']} | 🔌 Cáp LAN: {dist['ethernet']} | 🌐 WAN: {dist['wan']}"
        )

        # Lấy sự kiện gần đây
        events = self.event_dao.get_recent_events(limit=15)
        self.table_events.setRowCount(len(events))
        for row, ev in enumerate(events):
            item_time = QTableWidgetItem(ev["timestamp"])
            item_type = QTableWidgetItem(ev["event_type"])
            item_mac = QTableWidgetItem(ev["mac"])
            item_desc = QTableWidgetItem(ev["description"])

            if ev["event_type"] == "DEVICE_JOINED":
                item_type.setForeground(QColor("#10B981"))
            elif ev["event_type"] == "DEVICE_LEFT":
                item_type.setForeground(QColor("#94A3B8"))
            elif ev["event_type"] == "BLOCKED":
                item_type.setForeground(QColor("#EF4444"))
            elif ev["event_type"] == "UNBLOCKED":
                item_type.setForeground(QColor("#38BDF8"))

            self.table_events.setItem(row, 0, item_time)
            self.table_events.setItem(row, 1, item_type)
            self.table_events.setItem(row, 2, item_mac)
            self.table_events.setItem(row, 3, item_desc)

    def set_scanning_state(self, is_scanning: bool, progress: int = 0, message: str = ""):
        self._is_scanning = is_scanning
        self.btn_scan.setEnabled(not is_scanning)
        self.progress_bar.setVisible(is_scanning)
        if is_scanning:
            self.btn_scan.setText(f"  {t('dash_scanning')}")
            self.progress_bar.setValue(progress)
            self.progress_bar.setFormat(f"%p% - {message}")
        else:
            self.btn_scan.setText(f"  {t('dash_scan_now')}")

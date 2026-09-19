"""
Cửa sổ chính ứng dụng Network Manager (MainWindow) - Hỗ trợ Song ngữ VI / EN.
"""

import os
import sys
import json
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QStackedWidget, QLabel, QFrame, QMessageBox, QStatusBar, QComboBox
)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QIcon, QFont, QColor, QPixmap

from database.database import Database
from database.devices import DeviceDAO
from database.events import EventDAO
from security.blocker import BlockManager
from core.network import NetworkManagerCore, NetworkInterface
from services.discovery import NetworkDiscoveryService
from services.scheduler import ScanWorker, PeriodicScheduler

from gui.dashboard import DashboardView
from gui.devices import DevicesView
from gui.network_map import NetworkMapView
from gui.traffic import TrafficView
from gui.alerts import AlertsView
from gui.logs import LogsView
from gui.blocked import BlockedView
from gui.settings import SettingsView
from services.traffic_monitor import TrafficMonitor
from core.logger import logger
from core.i18n import t, i18n
from gui.icons import get_app_icon
from gui.theme import (
    GLOBAL_QSS, COLOR_BG_MAIN, COLOR_BG_SIDEBAR, COLOR_BG_CARD,
    COLOR_BORDER, COLOR_ACCENT_INDIGO, COLOR_ACCENT_CYAN, COLOR_ACCENT_EMERALD
)

class NavButton(QPushButton):
    def __init__(self, key: str, icon_name: str = "", parent=None):
        super().__init__(parent)
        self.key = key
        self.icon_name = icon_name
        self.setCheckable(True)
        self.setAutoExclusive(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(44)
        self.setFont(QFont("Segoe UI", 10, QFont.DemiBold))

        if self.icon_name:
            self.setIcon(get_app_icon(self.icon_name))
            self.setIconSize(QSize(20, 20))

        self.setStyleSheet(f"""
            NavButton {{
                text-align: left;
                padding-left: 14px;
                color: #94A3B8;
                background-color: transparent;
                border: none;
                border-left: 3px solid transparent;
                border-radius: 8px;
                margin: 2px 10px;
                font-size: 13px;
            }}
            NavButton:hover {{
                background-color: rgba(255, 255, 255, 0.05);
                color: #F8FAFC;
            }}
            NavButton:checked {{
                background-color: rgba(56, 189, 248, 0.12);
                color: #38BDF8;
                font-weight: 700;
                border-left: 3px solid #38BDF8;
            }}
        """)
        self.retranslate_ui()

    def retranslate_ui(self):
        self.setText(f"  {t(self.key)}")
        if self.icon_name:
            self.setIcon(get_app_icon(self.icon_name))
            self.setIconSize(QSize(20, 20))

class MainWindow(QMainWindow):
    def __init__(self, auto_scan_on_startup: bool = True):
        super().__init__()
        self.auto_scan_on_startup = auto_scan_on_startup
        self.setMinimumSize(1024, 700)
        self.resize(1280, 840)

        # Thiết lập Icon ứng dụng cho cửa sổ và taskbar
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_dir, "assets", "logo.ico")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(base_dir, "assets", "logo.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # 1. Khởi tạo Database và Services
        self.db = Database.get_instance()
        self.device_dao = DeviceDAO(self.db)
        self.event_dao = EventDAO(self.db)
        self.block_manager = BlockManager(device_dao=self.device_dao, event_dao=self.event_dao)
        self.discovery_service = NetworkDiscoveryService(device_dao=self.device_dao, event_dao=self.event_dao)

        self.current_iface = NetworkManagerCore.get_default_interface()
        self.config_data = self._load_config()

        # Áp dụng ngôn ngữ từ config
        saved_lang = self.config_data.get("ui", {}).get("language", "vi")
        i18n.current_lang = saved_lang

        # 2. Worker và Scheduler
        self.scan_worker = ScanWorker(discovery_service=self.discovery_service)
        self.scan_worker.scan_started.connect(self._on_scan_started)
        self.scan_worker.progress_updated.connect(self._on_scan_progress)
        self.scan_worker.scan_finished.connect(self._on_scan_finished)
        self.scan_worker.error_occurred.connect(self._on_scan_error)

        interval = self.config_data.get("network", {}).get("scan_interval_seconds", 60)
        self.scheduler = PeriodicScheduler(interval_seconds=interval)
        self.scheduler.trigger_scan.connect(self.start_scan)

        # 2.5 Dịch vụ theo dõi lưu lượng mạng thời gian thực
        self.traffic_monitor = TrafficMonitor(max_history_seconds=60)
        self.traffic_monitor.start()

        # 3. Khởi tạo giao diện
        self._init_ui()
        self.retranslate_ui()
        i18n.language_changed.connect(self._on_language_changed)

        # 4. Bắt đầu scheduler
        if self.auto_scan_on_startup and self.config_data.get("monitoring", {}).get("auto_scan", True):
            self.scheduler.start()

        if self.auto_scan_on_startup:
            QTimer.singleShot(800, self.start_scan)

    def _load_config(self) -> dict:
        try:
            cfg_path = "config/config.json"
            if not os.path.exists(cfg_path):
                app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                target = os.path.join(app_root, "config", "config.json")
                if os.path.exists(target):
                    cfg_path = target
            with open(cfg_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _init_ui(self):
        self.setStyleSheet(GLOBAL_QSS)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # A. Sidebar Trái
        sidebar = QFrame()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet(f"background-color: {COLOR_BG_SIDEBAR}; border-right: 1px solid {COLOR_BORDER};")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 16)
        sidebar_layout.setSpacing(6)

        # Brand Header (High-Tech NM Badge + Title)
        brand_card = QFrame()
        brand_card.setStyleSheet("background: transparent; margin: 0 10px 14px 10px;")
        brand_card_layout = QVBoxLayout(brand_card)
        brand_card_layout.setContentsMargins(4, 0, 4, 0)
        brand_card_layout.setSpacing(6)

        brand_top = QHBoxLayout()
        brand_top.setSpacing(10)
        lbl_logo = QLabel("NM")
        lbl_logo.setAlignment(Qt.AlignCenter)
        lbl_logo.setFixedSize(38, 38)
        lbl_logo.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0284C7, stop:1 #0369A1);
            border: 1px solid #38BDF8;
            border-radius: 10px;
            color: #FFFFFF;
            font-family: 'Fira Code', 'Consolas', monospace;
            font-weight: 900;
            font-size: 14px;
        """)

        title_vbox = QVBoxLayout()
        title_vbox.setSpacing(1)
        lbl_app_t1 = QLabel("NETWORK")
        lbl_app_t1.setStyleSheet("font-size: 13px; font-weight: 800; color: #F8FAFC; letter-spacing: 0.8px;")
        
        lbl_app_sub = QHBoxLayout()
        lbl_app_sub.setSpacing(6)
        lbl_app_t2 = QLabel("MANAGER")
        lbl_app_t2.setStyleSheet("font-size: 11px; font-weight: 800; color: #38BDF8; letter-spacing: 0.8px;")
        lbl_version_badge = QLabel("PRO")
        lbl_version_badge.setStyleSheet("""
            background-color: rgba(56, 189, 248, 0.15);
            color: #38BDF8;
            border: 1px solid rgba(56, 189, 248, 0.3);
            border-radius: 4px;
            padding: 1px 4px;
            font-size: 9px;
            font-weight: 800;
        """)
        lbl_app_sub.addWidget(lbl_app_t2)
        lbl_app_sub.addWidget(lbl_version_badge)
        lbl_app_sub.addStretch()

        title_vbox.addWidget(lbl_app_t1)
        title_vbox.addLayout(lbl_app_sub)

        brand_top.addWidget(lbl_logo)
        brand_top.addLayout(title_vbox)
        brand_top.addStretch()
        brand_card_layout.addLayout(brand_top)

        sidebar_layout.addWidget(brand_card)

        # 7 Navigation Buttons (Chuẩn vector SVG Flaticon)
        self.btn_nav_dashboard = NavButton("nav_dashboard", "dashboard")
        self.btn_nav_devices = NavButton("nav_devices", "devices")
        self.btn_nav_networks = NavButton("nav_networks", "network")
        self.btn_nav_traffic = NavButton("nav_traffic", "traffic")
        self.btn_nav_alerts = NavButton("nav_alerts", "alerts")
        self.btn_nav_logs = NavButton("nav_logs", "logs")
        self.btn_nav_settings = NavButton("nav_settings", "settings")

        self.nav_buttons = [
            self.btn_nav_dashboard,
            self.btn_nav_devices,
            self.btn_nav_networks,
            self.btn_nav_traffic,
            self.btn_nav_alerts,
            self.btn_nav_logs,
            self.btn_nav_settings
        ]

        for i, btn in enumerate(self.nav_buttons):
            sidebar_layout.addWidget(btn)
            btn.clicked.connect(lambda checked=False, idx=i: self._switch_page(idx))

        self.btn_nav_dashboard.setChecked(True)
        sidebar_layout.addStretch()

        # Bottom Agent Active Card
        self.agent_card = QFrame()
        self.agent_card.setStyleSheet("""
            QFrame {
                background-color: #0A1124;
                border: 1px solid #1E293B;
                border-radius: 10px;
                margin: 0 10px 12px 10px;
            }
        """)
        agent_layout = QVBoxLayout(self.agent_card)
        agent_layout.setContentsMargins(12, 10, 12, 10)
        agent_layout.setSpacing(4)
        
        agent_header = QHBoxLayout()
        agent_header.setSpacing(6)
        lbl_green_dot = QLabel("●")
        lbl_green_dot.setStyleSheet("color: #10B981; font-size: 12px;")
        lbl_agent_text = QLabel("Agent Active")
        lbl_agent_text.setStyleSheet("color: #10B981; font-size: 11px; font-weight: 700; font-family: 'Fira Code', monospace;")
        agent_header.addWidget(lbl_green_dot)
        agent_header.addWidget(lbl_agent_text)
        agent_header.addStretch()
        agent_layout.addLayout(agent_header)

        cidr_display = self.current_iface.cidr if self.current_iface else "192.168.1.0/24 & 110.0/24"
        self.lbl_agent_subnets = QLabel(cidr_display)
        self.lbl_agent_subnets.setStyleSheet("color: #94A3B8; font-size: 10px; font-family: 'Fira Code', monospace;")
        agent_layout.addWidget(self.lbl_agent_subnets)

        sidebar_layout.addWidget(self.agent_card)
        main_layout.addWidget(sidebar)

        # B. Right Content Area
        content_area = QWidget()
        content_area.setStyleSheet(f"background-color: {COLOR_BG_MAIN};")
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Top Bar
        top_bar = QFrame()
        top_bar.setFixedHeight(56)
        top_bar.setStyleSheet(f"background-color: #091022; border-bottom: 1px solid {COLOR_BORDER};")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 0, 20, 0)
        top_layout.setSpacing(12)

        # Breadcrumb / Page Title
        self.lbl_breadcrumb = QLabel("Tổng quan mạng (Dashboard)")
        self.lbl_breadcrumb.setStyleSheet("color: #F8FAFC; font-size: 14px; font-weight: 700;")
        top_layout.addWidget(self.lbl_breadcrumb)

        top_layout.addStretch()

        # Gateway Chip
        gw_ip = getattr(self.current_iface, "gateway", "") or "192.168.1.1"
        self.lbl_gateway_chip = QLabel(f"● Gateway: {gw_ip}")
        self.lbl_gateway_chip.setStyleSheet("""
            background-color: rgba(16, 185, 129, 0.12);
            color: #10B981;
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 13px;
            padding: 4px 12px;
            font-size: 11px;
            font-weight: 600;
            font-family: 'Fira Code', 'Consolas', monospace;
        """)
        top_layout.addWidget(self.lbl_gateway_chip)

        # Subnet Chip
        self.lbl_top_net = QLabel(f"Subnet: {cidr_display}")
        self.lbl_top_net.setStyleSheet("""
            background-color: rgba(6, 182, 212, 0.12);
            color: #06B6D4;
            border: 1px solid rgba(6, 182, 212, 0.3);
            border-radius: 13px;
            padding: 4px 12px;
            font-size: 11px;
            font-weight: 600;
            font-family: 'Fira Code', 'Consolas', monospace;
        """)
        top_layout.addWidget(self.lbl_top_net)

        # Quick Scan Button
        self.btn_quick_scan = QPushButton(" Quét mạng ngay")
        self.btn_quick_scan.setIcon(get_app_icon("scan"))
        self.btn_quick_scan.setIconSize(QSize(16, 16))
        self.btn_quick_scan.setCursor(Qt.PointingHandCursor)
        self.btn_quick_scan.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284C7, stop:1 #2563EB);
                color: #FFFFFF;
                border: 1px solid #38BDF8;
                border-radius: 8px;
                padding: 6px 14px;
                font-size: 12px;
                font-weight: 700;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0369A1, stop:1 #1D4ED8);
            }
            QPushButton:disabled {
                background: #1E293B;
                color: #64748B;
                border: 1px solid #334155;
            }
        """)
        self.btn_quick_scan.clicked.connect(self.start_scan)
        top_layout.addWidget(self.btn_quick_scan)

        # Status badge
        self.lbl_top_status = QLabel("● Sẵn sàng")
        self.lbl_top_status.setStyleSheet("""
            background-color: rgba(16, 185, 129, 0.12);
            color: #10B981;
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 13px;
            padding: 4px 12px;
            font-weight: 600;
            font-size: 11px;
        """)
        top_layout.addWidget(self.lbl_top_status)

        # Quick Language Dropdown
        self.cb_quick_lang = QComboBox()
        self.cb_quick_lang.addItems(["🇻🇳 Tiếng Việt", "🇬🇧 English"])
        self.cb_quick_lang.setCurrentIndex(0 if i18n.current_lang == "vi" else 1)
        self.cb_quick_lang.setStyleSheet("""
            QComboBox {
                background-color: #0D152A;
                color: #F8FAFC;
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 8px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 600;
                min-width: 125px;
            }
            QComboBox:hover {
                background-color: #131F3D;
                border: 1px solid #38BDF8;
            }
            QComboBox::drop-down { border: none; }
        """)
        self.cb_quick_lang.currentIndexChanged.connect(self._on_quick_lang_changed)
        top_layout.addWidget(self.cb_quick_lang)

        content_layout.addWidget(top_bar)

        # Stacked Views (7 Views matching sidebar buttons)
        self.stack = QStackedWidget()
        self.view_dashboard = DashboardView(self.device_dao, self.event_dao, block_manager=self.block_manager, traffic_monitor=self.traffic_monitor)
        self.view_devices = DevicesView(self.device_dao, self.event_dao, self.block_manager)
        self.view_map = NetworkMapView(self.device_dao, self.event_dao, self.block_manager, iface=self.current_iface)
        self.view_traffic = TrafficView(self.traffic_monitor)
        self.view_alerts = AlertsView()
        self.view_logs = LogsView(self.event_dao)
        self.view_settings = SettingsView(self.block_manager)

        self.view_dashboard.scan_requested.connect(self.start_scan)
        self.view_devices.data_changed.connect(self._sync_all_views)
        self.view_map.data_changed.connect(self._sync_all_views)
        self.view_settings.settings_saved.connect(self._on_settings_saved)

        self.stack.addWidget(self.view_dashboard)  # 0: Dashboard
        self.stack.addWidget(self.view_devices)    # 1: Devices
        self.stack.addWidget(self.view_map)        # 2: Networks
        self.stack.addWidget(self.view_traffic)    # 3: Traffic
        self.stack.addWidget(self.view_alerts)     # 4: Alerts
        self.stack.addWidget(self.view_logs)       # 5: Logs
        self.stack.addWidget(self.view_settings)   # 6: Settings

        content_layout.addWidget(self.stack)
        main_layout.addWidget(content_area)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        if self.current_iface:
            self.view_dashboard.update_network_info(self.current_iface)

    def retranslate_ui(self):
        self.setWindowTitle(t("app_title"))
        self.lbl_top_status.setText("● " + t("status_ready"))
        self.status_bar.showMessage(t("ready_msg"))
        is_vi = i18n.current_lang == "vi"
        self.btn_quick_scan.setText(" Quét mạng ngay" if is_vi else " Scan Network")
        self.btn_quick_scan.setIcon(get_app_icon("scan"))

        for btn in self.nav_buttons:
            btn.retranslate_ui()
        self._update_breadcrumb(self.stack.currentIndex())

    def _update_breadcrumb(self, index: int):
        titles_vi = [
            "Tổng quan mạng (Dashboard)",
            "Danh sách thiết bị (Connected Devices)",
            "Sơ đồ hạ tầng mạng (Network Map)",
            "Giám sát lưu lượng (Traffic Monitor)",
            "Cảnh báo bảo mật (Security Alerts)",
            "Nhật ký sự kiện hệ thống (Logs)",
            "Cấu hình hệ thống (Settings)"
        ]
        titles_en = [
            "Network Dashboard Overview",
            "Connected Devices Management",
            "Network Topology & Map",
            "Real-time Traffic Monitor",
            "Security & Threat Alerts",
            "System Event Logs",
            "System Settings"
        ]
        is_vi = i18n.current_lang == "vi"
        titles = titles_vi if is_vi else titles_en
        if 0 <= index < len(titles):
            self.lbl_breadcrumb.setText(titles[index])

    def _on_quick_lang_changed(self, idx: int):
        new_lang = "vi" if idx == 0 else "en"
        i18n.set_language(new_lang)

    def _on_language_changed(self, lang: str):
        self.cb_quick_lang.blockSignals(True)
        self.cb_quick_lang.setCurrentIndex(0 if lang == "vi" else 1)
        self.cb_quick_lang.blockSignals(False)
        self.retranslate_ui()

    def _switch_page(self, index: int):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
        self._update_breadcrumb(index)
        if index == 0:
            self.view_dashboard.refresh_data()
        elif index == 1:
            self.view_devices.load_devices()
        elif index == 2:
            self.view_map.refresh_map()
        elif index == 3:
            pass  # Traffic view cập nhật liên tục qua tín hiệu QTimer
        elif index == 4:
            self.view_alerts.load_alerts()
        elif index == 5:
            self.view_logs.load_logs()
        elif index == 6:
            pass  # Settings view

    def start_scan(self):
        if self.scan_worker.isRunning():
            return

        target_subnet = None
        if not self.config_data.get("network", {}).get("auto_detect_interface", True):
            target_subnet = self.config_data.get("network", {}).get("custom_subnet")
        elif not self.config_data.get("network", {}).get("scan_all_subnets", True):
            target_subnet = self.current_iface.cidr if self.current_iface else None

        self.scan_worker.set_subnet(target_subnet)
        self.scan_worker.start()

    def _on_scan_started(self):
        is_vi = i18n.current_lang == "vi"
        self.lbl_top_status.setText("● " + (t("status_scanning") if "status_scanning" in i18n.current_lang else ("Đang quét..." if is_vi else "Scanning...")))
        self.lbl_top_status.setStyleSheet("""
            background-color: rgba(56, 189, 248, 0.15);
            color: #38BDF8;
            border: 1px solid rgba(56, 189, 248, 0.4);
            border-radius: 13px;
            padding: 4px 12px;
            font-weight: 700;
            font-size: 11px;
        """)
        self.btn_quick_scan.setEnabled(False)
        self.btn_quick_scan.setText(" Đang quét..." if is_vi else " Scanning...")
        self.view_dashboard.set_scanning_state(True, progress=10, message="...")
        self.status_bar.showMessage(t("scanning_msg"))

    def _on_scan_progress(self, percent: int, msg: str):
        self.view_dashboard.set_scanning_state(True, progress=percent, message=msg)
        self.status_bar.showMessage(f"({percent}%): {msg}")

    def _on_scan_finished(self, devices: list):
        is_vi = i18n.current_lang == "vi"
        self.lbl_top_status.setText("● " + ("Sẵn sàng" if is_vi else "Ready"))
        self.lbl_top_status.setStyleSheet("""
            background-color: rgba(16, 185, 129, 0.12);
            color: #10B981;
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 13px;
            padding: 4px 12px;
            font-weight: 600;
            font-size: 11px;
        """)
        self.btn_quick_scan.setEnabled(True)
        self.btn_quick_scan.setText(" Quét mạng ngay" if is_vi else " Scan Network")
        self.btn_quick_scan.setIcon(get_app_icon("scan"))
        self.view_dashboard.set_scanning_state(False)
        self.status_bar.showMessage(t("scan_success_msg", count=len(devices)))
        self._sync_all_views()

    def _on_scan_error(self, error_msg: str):
        is_vi = i18n.current_lang == "vi"
        self.lbl_top_status.setText("● " + ("Lỗi" if is_vi else "Error"))
        self.lbl_top_status.setStyleSheet("""
            background-color: rgba(239, 68, 68, 0.15);
            color: #EF4444;
            border: 1px solid rgba(239, 68, 68, 0.4);
            border-radius: 13px;
            padding: 4px 12px;
            font-weight: 700;
            font-size: 11px;
        """)
        self.btn_quick_scan.setEnabled(True)
        self.btn_quick_scan.setText(" Quét mạng ngay" if is_vi else " Scan Network")
        self.btn_quick_scan.setIcon(get_app_icon("scan"))
        self.view_dashboard.set_scanning_state(False)
        self.status_bar.showMessage(f"Error: {error_msg}")
        QMessageBox.warning(self, t("scan_error_title"), t("scan_error_body", error=error_msg))

    def _sync_all_views(self):
        self.view_dashboard.refresh_data()
        self.view_devices.load_devices()
        self.view_map.refresh_map()
        self.view_alerts.load_alerts()
        self.view_logs.load_logs()

    def _on_settings_saved(self, new_config: dict):
        self.config_data = new_config
        new_interval = new_config.get("network", {}).get("scan_interval_seconds", 60)
        self.scheduler.set_interval(new_interval)
        self.status_bar.showMessage(t("save_settings_success"))

    def closeEvent(self, event):
        self.scheduler.stop()
        if hasattr(self, "traffic_monitor"):
            self.traffic_monitor.stop()
        if self.scan_worker.isRunning():
            self.scan_worker.terminate()
            self.scan_worker.wait(1000)
        event.accept()

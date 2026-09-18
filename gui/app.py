"""
Cửa sổ chính ứng dụng Network Manager (MainWindow) - Hỗ trợ Song ngữ VI / EN.
"""

import sys
import json
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QStackedWidget, QLabel, QFrame, QMessageBox, QStatusBar, QComboBox
)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QIcon, QFont, QColor

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
from gui.blocked import BlockedView
from gui.settings import SettingsView
from services.traffic_monitor import TrafficMonitor
from core.logger import logger
from core.i18n import t, i18n
from gui.theme import (
    GLOBAL_QSS, COLOR_BG_MAIN, COLOR_BG_SIDEBAR, COLOR_BG_CARD,
    COLOR_BORDER, COLOR_ACCENT_INDIGO, COLOR_ACCENT_CYAN, COLOR_ACCENT_EMERALD
)

class NavButton(QPushButton):
    def __init__(self, key: str, icon_str: str = "", parent=None):
        super().__init__(parent)
        self.key = key
        self.icon_str = icon_str
        self.setCheckable(True)
        self.setAutoExclusive(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(46)
        self.setFont(QFont("Segoe UI", 10, QFont.DemiBold))
        self.setStyleSheet(f"""
            NavButton {{
                text-align: left;
                padding-left: 18px;
                color: #94A3B8;
                background-color: transparent;
                border: none;
                border-left: 4px solid transparent;
                border-radius: 9px;
                margin: 3px 12px;
            }}
            NavButton:hover {{
                background-color: rgba(255, 255, 255, 0.05);
                color: #F8FAFC;
            }}
            NavButton:checked {{
                background-color: rgba(99, 102, 241, 0.16);
                color: #FFFFFF;
                font-weight: bold;
                border-left: 4px solid {COLOR_ACCENT_INDIGO};
            }}
        """)
        self.retranslate_ui()

    def retranslate_ui(self):
        self.setText(f"  {self.icon_str}  {t(self.key)}")

class MainWindow(QMainWindow):
    def __init__(self, auto_scan_on_startup: bool = True):
        super().__init__()
        self.auto_scan_on_startup = auto_scan_on_startup
        self.setMinimumSize(1024, 700)
        self.resize(1240, 820)

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
            with open("config/config.json", "r", encoding="utf-8") as f:
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
        sidebar.setFixedWidth(225)
        sidebar.setStyleSheet(f"background-color: {COLOR_BG_SIDEBAR}; border-right: 1px solid {COLOR_BORDER};")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 22, 0, 18)
        sidebar_layout.setSpacing(6)

        # Brand Header
        brand_card = QFrame()
        brand_card.setStyleSheet("background: transparent; margin: 0 14px 16px 14px;")
        brand_card_layout = QVBoxLayout(brand_card)
        brand_card_layout.setContentsMargins(6, 0, 6, 0)
        brand_card_layout.setSpacing(6)

        brand_top = QHBoxLayout()
        lbl_logo = QLabel("🛡️")
        lbl_logo.setAlignment(Qt.AlignCenter)
        lbl_logo.setFixedSize(36, 36)
        lbl_logo.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4F46E5, stop:1 #06B6D4);
            border-radius: 10px;
            font-size: 18px;
        """)
        self.lbl_app_name = QLabel("NETWORK MANAGER")
        self.lbl_app_name.setStyleSheet("font-size: 14px; font-weight: 800; color: #F8FAFC; letter-spacing: 1.2px;")
        brand_top.addWidget(lbl_logo)
        brand_top.addWidget(self.lbl_app_name)
        brand_top.addStretch()
        brand_card_layout.addLayout(brand_top)

        self.lbl_brand_status = QLabel("● TRỰC TUYẾN / ONLINE")
        self.lbl_brand_status.setStyleSheet("color: #10B981; font-size: 10px; font-weight: bold; margin-left: 42px; letter-spacing: 0.5px;")
        brand_card_layout.addWidget(self.lbl_brand_status)

        sidebar_layout.addWidget(brand_card)

        # Navigation Buttons
        self.btn_nav_dashboard = NavButton("nav_dashboard", "📊")
        self.btn_nav_devices = NavButton("nav_devices", "💻")
        self.btn_nav_map = NavButton("nav_map", "🗺️")
        self.btn_nav_traffic = NavButton("nav_traffic", "📈")
        self.btn_nav_blocked = NavButton("nav_blocked", "🚫")
        self.btn_nav_settings = NavButton("nav_settings", "⚙️")

        self.nav_buttons = [
            self.btn_nav_dashboard,
            self.btn_nav_devices,
            self.btn_nav_map,
            self.btn_nav_traffic,
            self.btn_nav_blocked,
            self.btn_nav_settings
        ]

        for i, btn in enumerate(self.nav_buttons):
            sidebar_layout.addWidget(btn)
            btn.clicked.connect(lambda checked=False, idx=i: self._switch_page(idx))

        self.btn_nav_dashboard.setChecked(True)
        sidebar_layout.addStretch()

        # Footer
        footer_frame = QFrame()
        footer_frame.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 10px;
            margin: 0 14px;
            padding: 8px;
        """)
        footer_layout = QVBoxLayout(footer_frame)
        footer_layout.setContentsMargins(10, 8, 10, 8)
        footer_layout.setSpacing(3)
        self.lbl_footer = QLabel("Network Manager v1.2")
        self.lbl_footer.setStyleSheet("color: #94A3B8; font-size: 11px; font-weight: bold;")
        lbl_subfooter = QLabel("Giám sát & Quản trị An toàn")
        lbl_subfooter.setStyleSheet("color: #64748B; font-size: 10px;")
        footer_layout.addWidget(self.lbl_footer)
        footer_layout.addWidget(lbl_subfooter)
        sidebar_layout.addWidget(footer_frame)

        main_layout.addWidget(sidebar)

        # B. Right Area
        content_area = QWidget()
        content_area.setStyleSheet(f"background-color: {COLOR_BG_MAIN};")
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Top Bar
        top_bar = QFrame()
        top_bar.setFixedHeight(60)
        top_bar.setStyleSheet(f"background-color: #0C152B; border-bottom: 1px solid {COLOR_BORDER};")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(24, 0, 24, 0)
        top_layout.setSpacing(14)

        self.lbl_top_status = QLabel()
        self.lbl_top_status.setStyleSheet("""
            background-color: rgba(16, 185, 129, 0.12);
            color: #10B981;
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 14px;
            padding: 5px 14px;
            font-weight: 600;
            font-size: 12px;
        """)
        top_layout.addWidget(self.lbl_top_status)

        top_layout.addStretch()

        # Nút chuyển nhanh ngôn ngữ ở góc phải Top Bar
        self.cb_quick_lang = QComboBox()
        self.cb_quick_lang.addItems(["🇻🇳 Tiếng Việt", "🇬🇧 English"])
        self.cb_quick_lang.setCurrentIndex(0 if i18n.current_lang == "vi" else 1)
        self.cb_quick_lang.setStyleSheet("""
            QComboBox {
                background-color: #101B33;
                color: #F8FAFC;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 5px 12px;
                font-size: 12px;
                font-weight: 600;
                min-width: 125px;
            }
            QComboBox:hover {
                background-color: #152445;
                border: 1px solid #6366F1;
            }
            QComboBox::drop-down { border: none; }
        """)
        self.cb_quick_lang.currentIndexChanged.connect(self._on_quick_lang_changed)
        top_layout.addWidget(self.cb_quick_lang)

        # Subnet chip
        self.lbl_top_net = QLabel(f"🌐 Subnet: {self.current_iface.cidr if self.current_iface else 'N/A'}")
        self.lbl_top_net.setStyleSheet("""
            background-color: rgba(6, 182, 212, 0.12);
            color: #06B6D4;
            border: 1px solid rgba(6, 182, 212, 0.3);
            padding: 5px 14px;
            border-radius: 14px;
            font-size: 12px;
            font-weight: bold;
        """)
        top_layout.addWidget(self.lbl_top_net)

        content_layout.addWidget(top_bar)

        # Stacked Views
        self.stack = QStackedWidget()
        self.view_dashboard = DashboardView(self.device_dao, self.event_dao, traffic_monitor=self.traffic_monitor)
        self.view_devices = DevicesView(self.device_dao, self.event_dao, self.block_manager)
        self.view_map = NetworkMapView(self.device_dao, self.event_dao, self.block_manager)
        self.view_traffic = TrafficView(self.traffic_monitor)
        self.view_blocked = BlockedView(self.device_dao, self.event_dao, self.block_manager)
        self.view_settings = SettingsView(self.block_manager)

        self.view_dashboard.scan_requested.connect(self.start_scan)
        self.view_devices.data_changed.connect(self._sync_all_views)
        self.view_map.data_changed.connect(self._sync_all_views)
        self.view_blocked.data_changed.connect(self._sync_all_views)
        self.view_settings.settings_saved.connect(self._on_settings_saved)

        self.stack.addWidget(self.view_dashboard)
        self.stack.addWidget(self.view_devices)
        self.stack.addWidget(self.view_map)
        self.stack.addWidget(self.view_traffic)
        self.stack.addWidget(self.view_blocked)
        self.stack.addWidget(self.view_settings)

        content_layout.addWidget(self.stack)
        main_layout.addWidget(content_area)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        if self.current_iface:
            self.view_dashboard.update_network_info(self.current_iface)

    def retranslate_ui(self):
        self.setWindowTitle(t("app_title"))
        self.lbl_app_name.setText(t("app_brand"))
        self.lbl_footer.setText(t("app_footer"))
        self.lbl_top_status.setText(t("status_ready"))
        self.status_bar.showMessage(t("ready_msg"))

        for btn in self.nav_buttons:
            btn.retranslate_ui()

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
        if index == 0:
            self.view_dashboard.refresh_data()
        elif index == 1:
            self.view_devices.load_devices()
        elif index == 2:
            self.view_map.refresh_map()
        elif index == 3:
            pass  # Traffic view cập nhật liên tục qua tín hiệu QTimer
        elif index == 4:
            self.view_blocked.load_blocked_devices()

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
        self.lbl_top_status.setText(t("status_scanning"))
        self.lbl_top_status.setStyleSheet("color: #38BDF8; font-weight: bold; font-size: 13px;")
        self.view_dashboard.set_scanning_state(True, progress=10, message="...")
        self.status_bar.showMessage(t("scanning_msg"))

    def _on_scan_progress(self, percent: int, msg: str):
        self.view_dashboard.set_scanning_state(True, progress=percent, message=msg)
        self.status_bar.showMessage(f"({percent}%): {msg}")

    def _on_scan_finished(self, devices: list):
        self.lbl_top_status.setText(t("status_ready"))
        self.lbl_top_status.setStyleSheet("color: #10B981; font-weight: 500; font-size: 13px;")
        self.view_dashboard.set_scanning_state(False)
        self.status_bar.showMessage(t("scan_success_msg", count=len(devices)))
        self._sync_all_views()

    def _on_scan_error(self, error_msg: str):
        self.lbl_top_status.setText(t("status_error"))
        self.lbl_top_status.setStyleSheet("color: #EF4444; font-weight: bold; font-size: 13px;")
        self.view_dashboard.set_scanning_state(False)
        self.status_bar.showMessage(f"Error: {error_msg}")
        QMessageBox.warning(self, t("scan_error_title"), t("scan_error_body", error=error_msg))

    def _sync_all_views(self):
        self.view_dashboard.refresh_data()
        self.view_devices.load_devices()
        self.view_map.refresh_map()
        self.view_blocked.load_blocked_devices()

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

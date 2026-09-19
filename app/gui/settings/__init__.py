"""
Màn hình Cấu hình Hệ thống (Settings View) - Được module hóa từ các Card độc lập.
"""

import json
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame,
    QMessageBox, QFileDialog, QScrollArea, QLineEdit
)
from PySide6.QtCore import Qt, Signal
from security.blocker import BlockManager
from core.logger import logger
from core.i18n import t, i18n
from gui.theme import COLOR_ACCENT_EMERALD, COLOR_ACCENT_ROSE
from gui.icons import get_app_icon

from gui.settings.card_base import SettingsCard
from gui.settings.card_language import LanguageSettingsCard
from gui.settings.card_scan import ScanSettingsCard
from gui.settings.card_router import RouterSettingsCard
from gui.settings.card_security import SecuritySettingsCard
from gui.settings.action_bar import SettingsActionBar

class SettingsView(QWidget):
    settings_saved = Signal(dict)

    def __init__(self, block_manager: BlockManager, parent=None):
        super().__init__(parent)
        self.block_manager = block_manager
        self.config_data = self._load_config()
        self.routers_data = self._load_routers()
        self.password_visible = False

        self._init_ui()
        self._populate_values()
        self.retranslate_ui()
        i18n.language_changed.connect(self._on_lang_changed)

    def _get_config_path(self, filename: str) -> str:
        if os.path.exists(os.path.join("config", filename)):
            return os.path.join("config", filename)
        app_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        target = os.path.join(app_root, "config", filename)
        if os.path.exists(target):
            return target
        return os.path.join("config", filename)

    def _load_config(self) -> dict:
        try:
            cfg_path = self._get_config_path("config.json")
            with open(cfg_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"[Settings] Lỗi đọc config.json: {e}")
            return {}

    def _load_routers(self) -> dict:
        try:
            routers_path = self._get_config_path("routers.json")
            with open(routers_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"[Settings] Lỗi đọc routers.json: {e}")
            return {}

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 1. TOP HEADER
        top_header = QFrame()
        top_header.setStyleSheet("""
            QFrame {
                background-color: #080D1A;
                border-bottom: 1px solid rgba(255, 255, 255, 0.06);
            }
        """)
        top_layout = QVBoxLayout(top_header)
        top_layout.setContentsMargins(28, 18, 28, 16)
        top_layout.setSpacing(3)

        self.lbl_main_title = QLabel()
        self.lbl_main_title.setStyleSheet("font-size: 20px; font-weight: 800; color: #F8FAFC; letter-spacing: 0.3px;")
        self.lbl_main_desc = QLabel()
        self.lbl_main_desc.setStyleSheet("color: #94A3B8; font-size: 13px;")

        top_layout.addWidget(self.lbl_main_title)
        top_layout.addWidget(self.lbl_main_desc)
        root_layout.addWidget(top_header)

        # 2. SCROLLABLE AREA
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #080D1A;
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background-color: #080D1A;
            }
            QScrollBar:vertical {
                background: #080D1A;
                width: 7px;
                margin: 0px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #334155;
                min-height: 30px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical:hover {
                background: #475569;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        self.scroll_area.viewport().setStyleSheet("background-color: #080D1A;")

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: #080D1A;")
        self.cards_layout = QVBoxLayout(scroll_content)
        self.cards_layout.setContentsMargins(28, 20, 28, 24)
        self.cards_layout.setSpacing(18)

        # Build cards
        self.card_lang = LanguageSettingsCard()
        self.cards_layout.addWidget(self.card_lang)

        self.card_scan = ScanSettingsCard()
        self.cards_layout.addWidget(self.card_scan)

        self.card_router = RouterSettingsCard()
        self.cards_layout.addWidget(self.card_router)

        self.card_sec = SecuritySettingsCard()
        self.cards_layout.addWidget(self.card_sec)

        self.cards_layout.addStretch()
        self.scroll_area.setWidget(scroll_content)
        root_layout.addWidget(self.scroll_area, stretch=1)

        # 3. ACTION BAR
        self.action_bar = SettingsActionBar()
        root_layout.addWidget(self.action_bar)

        # Expose convenient aliases for backward compatibility & testing
        self._bind_card_aliases()
        self._connect_signals()

    def _bind_card_aliases(self):
        # Lang
        self.cb_language = self.card_lang.cb_language
        self.lbl_lang_label = self.card_lang.lbl_lang_label

        # Scan
        self.chk_autodetect = self.card_scan.chk_autodetect
        self.chk_multisubnet = self.card_scan.chk_multisubnet
        self.lbl_custom_subnet = self.card_scan.lbl_custom_subnet
        self.txt_custom_subnet = self.card_scan.txt_custom_subnet
        self.lbl_scan_interval = self.card_scan.lbl_scan_interval
        self.spin_interval = self.card_scan.spin_interval
        self.lbl_hint_interval = self.card_scan.lbl_hint_interval
        self.lbl_offline_thresh = self.card_scan.lbl_offline_thresh
        self.spin_offline_thresh = self.card_scan.spin_offline_thresh
        self.lbl_hint_offline = self.card_scan.lbl_hint_offline
        self.lbl_nmap_path = self.card_scan.lbl_nmap_path
        self.txt_nmap_path = self.card_scan.txt_nmap_path
        self.btn_browse_nmap = self.card_scan.btn_browse_nmap

        # Router
        self.lbl_adapter_type = self.card_router.lbl_adapter_type
        self.cb_adapter = self.card_router.cb_adapter
        self.frame_mock_tip = self.card_router.frame_mock_tip
        self.lbl_mock_tip = self.card_router.lbl_mock_tip
        self.lbl_router_host = self.card_router.lbl_router_host
        self.txt_router_host = self.card_router.txt_router_host
        self.lbl_router_port = self.card_router.lbl_router_port
        self.txt_router_port = self.card_router.txt_router_port
        self.lbl_router_user = self.card_router.lbl_router_user
        self.txt_router_user = self.card_router.txt_router_user
        self.lbl_router_pass = self.card_router.lbl_router_pass
        self.txt_router_pass = self.card_router.txt_router_pass
        self.btn_toggle_pass = self.card_router.btn_toggle_pass
        self.btn_test_router = self.card_router.btn_test_router
        self.lbl_conn_status = self.card_router.lbl_conn_status

        # Security
        self.chk_firewall = self.card_sec.chk_firewall
        self.lbl_hint_firewall = self.card_sec.lbl_hint_firewall
        self.chk_confirm = self.card_sec.chk_confirm
        self.lbl_hint_confirm = self.card_sec.lbl_hint_confirm

        # Action bar
        self.lbl_action_status = self.action_bar.lbl_action_status
        self.btn_reset = self.action_bar.btn_reset
        self.btn_save = self.action_bar.btn_save

    def _connect_signals(self):
        self.cb_language.currentIndexChanged.connect(self._on_language_selection_changed)
        self.chk_autodetect.toggled.connect(self._on_autodetect_toggle)
        self.btn_browse_nmap.clicked.connect(self._browse_nmap_path)
        self.cb_adapter.currentIndexChanged.connect(self._on_adapter_changed)
        self.btn_toggle_pass.clicked.connect(self._toggle_password_visibility)
        self.btn_test_router.clicked.connect(self._test_router_connection)
        self.btn_reset.clicked.connect(self._reset_defaults)
        self.btn_save.clicked.connect(self._save_settings)

    def retranslate_ui(self):
        self.lbl_main_title.setText(t('set_title'))
        self.lbl_main_desc.setText(t("set_desc"))

        self.card_lang.retranslate_ui()
        self.card_scan.retranslate_ui()
        self.card_router.retranslate_ui()
        self.card_sec.retranslate_ui()
        self.action_bar.retranslate_ui()

    def _on_lang_changed(self, lang: str):
        self.retranslate_ui()

    def _on_language_selection_changed(self, idx: int):
        new_lang = "vi" if idx == 0 else "en"
        i18n.set_language(new_lang)

    def _on_autodetect_toggle(self, checked: bool):
        self.txt_custom_subnet.setEnabled(not checked)

    def _on_adapter_changed(self, idx: int):
        adapter_key = ["mock", "tplink", "openwrt", "mikrotik"][idx]
        cfg = self.routers_data.get(adapter_key, {})
        self.txt_router_host.setText(cfg.get("host", ""))
        self.txt_router_port.setText(str(cfg.get("port", 80)))
        self.txt_router_user.setText(cfg.get("username", "admin"))
        self.txt_router_pass.setText(cfg.get("password", ""))

        self.frame_mock_tip.setVisible(adapter_key == "mock")
        self.lbl_conn_status.setVisible(False)

    def _toggle_password_visibility(self):
        self.password_visible = not self.password_visible
        if self.password_visible:
            self.txt_router_pass.setEchoMode(QLineEdit.Normal)
            self.btn_toggle_pass.setIcon(get_app_icon("eye_off"))
            self.btn_toggle_pass.setToolTip(t("hide_pass"))
        else:
            self.txt_router_pass.setEchoMode(QLineEdit.Password)
            self.btn_toggle_pass.setIcon(get_app_icon("eye"))
            self.btn_toggle_pass.setToolTip(t("show_pass"))

    def _browse_nmap_path(self):
        initial_dir = r"C:\Program Files (x86)\Nmap" if os.path.exists(r"C:\Program Files (x86)\Nmap") else "C:\\"
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            t("choose_nmap_title"),
            initial_dir,
            "Nmap Executable (nmap.exe);;All Executables (*.exe);;All Files (*.*)"
        )
        if file_path:
            self.txt_nmap_path.setText(os.path.normpath(file_path))

    def _populate_values(self):
        ui_cfg = self.config_data.get("ui", {})
        saved_lang = ui_cfg.get("language", "vi")
        self.cb_language.blockSignals(True)
        self.cb_language.setCurrentIndex(0 if saved_lang == "vi" else 1)
        self.cb_language.blockSignals(False)

        net_cfg = self.config_data.get("network", {})
        self.chk_autodetect.setChecked(net_cfg.get("auto_detect_interface", True))
        self.chk_multisubnet.setChecked(net_cfg.get("scan_all_subnets", True))
        self.txt_custom_subnet.setText(net_cfg.get("custom_subnet", ""))
        self.txt_custom_subnet.setEnabled(not self.chk_autodetect.isChecked())
        self.spin_interval.setValue(net_cfg.get("scan_interval_seconds", 60))
        self.spin_offline_thresh.setValue(net_cfg.get("offline_threshold_seconds", 300))
        self.txt_nmap_path.setText(net_cfg.get("nmap_path", r"C:\Program Files (x86)\Nmap\nmap.exe"))

        sec_cfg = self.config_data.get("security", {})
        active_r = sec_cfg.get("active_router", "mock")
        r_map = {"mock": 0, "tplink": 1, "openwrt": 2, "mikrotik": 3}
        self.cb_adapter.setCurrentIndex(r_map.get(active_r, 0))
        self._on_adapter_changed(self.cb_adapter.currentIndex())

        self.chk_firewall.setChecked(sec_cfg.get("enable_host_firewall", True))
        self.chk_confirm.setChecked(sec_cfg.get("confirm_before_block", True))

    def _reset_defaults(self):
        reply = QMessageBox.question(
            self,
            t("btn_reset_defaults"),
            t("reset_defaults_confirm"),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.chk_autodetect.setChecked(True)
            self.chk_multisubnet.setChecked(True)
            self.txt_custom_subnet.setText("")
            self.spin_interval.setValue(60)
            self.spin_offline_thresh.setValue(300)
            self.txt_nmap_path.setText(r"C:\Program Files (x86)\Nmap\nmap.exe")
            self.cb_adapter.setCurrentIndex(0)
            self.chk_firewall.setChecked(True)
            self.chk_confirm.setChecked(True)
            QMessageBox.information(self, t("btn_reset_defaults"), t("reset_defaults_success"))

    def _test_router_connection(self, show_dialog: bool = True):
        adapter_idx = self.cb_adapter.currentIndex()
        adapter_key = ["mock", "tplink", "openwrt", "mikrotik"][adapter_idx]
        
        try:
            port_val = int(self.txt_router_port.text().strip() or 80)
        except ValueError:
            port_val = 80

        temp_cfg = {
            "name": adapter_key,
            "host": self.txt_router_host.text().strip(),
            "port": port_val,
            "username": self.txt_router_user.text().strip(),
            "password": self.txt_router_pass.text().strip()
        }

        self.lbl_conn_status.setVisible(True)
        self.lbl_conn_status.setText(f"⏳ {t('conn_testing')}")
        self.lbl_conn_status.setStyleSheet("color: #38BDF8; font-size: 13px;")

        test_adapter = BlockManager.create_adapter(adapter_key, temp_cfg)
        ok, msg = test_adapter.test_connection()
        if ok:
            self.lbl_conn_status.setText(f"● {t('conn_success')}")
            self.lbl_conn_status.setStyleSheet(f"color: {COLOR_ACCENT_EMERALD}; font-size: 13px; font-weight: bold;")
            if show_dialog:
                QMessageBox.information(self, t("conn_success"), msg)
        else:
            self.lbl_conn_status.setText(f"● {t('conn_fail')}")
            self.lbl_conn_status.setStyleSheet(f"color: {COLOR_ACCENT_ROSE}; font-size: 13px; font-weight: bold;")
            if show_dialog:
                QMessageBox.warning(self, t("conn_fail"), msg)

    def _save_settings(self):
        adapter_idx = self.cb_adapter.currentIndex()
        adapter_key = ["mock", "tplink", "openwrt", "mikrotik"][adapter_idx]
        selected_lang = "vi" if self.cb_language.currentIndex() == 0 else "en"

        try:
            port_val = int(self.txt_router_port.text().strip() or 80)
        except ValueError:
            port_val = 80

        self.config_data.setdefault("ui", {})["language"] = selected_lang
        self.config_data["network"]["auto_detect_interface"] = self.chk_autodetect.isChecked()
        self.config_data["network"]["scan_all_subnets"] = self.chk_multisubnet.isChecked()
        self.config_data["network"]["custom_subnet"] = self.txt_custom_subnet.text().strip()
        self.config_data["network"]["scan_interval_seconds"] = self.spin_interval.value()
        self.config_data["network"]["offline_threshold_seconds"] = self.spin_offline_thresh.value()
        self.config_data["network"]["nmap_path"] = self.txt_nmap_path.text().strip()

        self.config_data["security"]["active_router"] = adapter_key
        self.config_data["security"]["enable_host_firewall"] = self.chk_firewall.isChecked()
        self.config_data["security"]["confirm_before_block"] = self.chk_confirm.isChecked()

        if adapter_key in self.routers_data:
            self.routers_data[adapter_key]["host"] = self.txt_router_host.text().strip()
            self.routers_data[adapter_key]["port"] = port_val
            self.routers_data[adapter_key]["username"] = self.txt_router_user.text().strip()
            self.routers_data[adapter_key]["password"] = self.txt_router_pass.text().strip()
            self.routers_data[adapter_key]["enabled"] = True

        try:
            cfg_path = self._get_config_path("config.json")
            routers_path = self._get_config_path("routers.json")
            with open(cfg_path, "w", encoding="utf-8") as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
            with open(routers_path, "w", encoding="utf-8") as f:
                json.dump(self.routers_data, f, indent=2, ensure_ascii=False)

            new_adapter = BlockManager.create_adapter(adapter_key, self.routers_data.get(adapter_key, {}))
            self.block_manager.set_adapter(new_adapter)
            self.block_manager.enable_host_firewall = self.chk_firewall.isChecked()

            i18n.set_language(selected_lang)
            self.settings_saved.emit(self.config_data)
            self.lbl_action_status.setText(f"✓ {t('save_settings_success')}")
            self.lbl_action_status.setStyleSheet(f"color: {COLOR_ACCENT_EMERALD}; font-size: 12px; font-weight: 600;")
            QMessageBox.information(self, "Success", t("save_settings_success"))
        except Exception as e:
            logger.error(f"[Settings] Lỗi lưu cấu hình: {e}")
            QMessageBox.critical(self, "Error", f"Error saving file: {e}")

__all__ = ["SettingsView", "SettingsCard"]

"""
Màn hình Cấu hình Hệ thống (Settings View) - Song ngữ VI / EN.
"""

import json
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QCheckBox, QGroupBox, QMessageBox,
    QFormLayout, QSpinBox
)
from PySide6.QtCore import Signal
from security.blocker import BlockManager
from core.logger import logger
from core.i18n import t, i18n

class SettingsView(QWidget):
    settings_saved = Signal(dict)

    def __init__(self, block_manager: BlockManager, parent=None):
        super().__init__(parent)
        self.block_manager = block_manager
        self.config_data = self._load_config()
        self.routers_data = self._load_routers()
        self._init_ui()
        self._populate_values()
        self.retranslate_ui()
        i18n.language_changed.connect(self._on_lang_changed)

    def _load_config(self) -> dict:
        try:
            with open("config/config.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _load_routers(self) -> dict:
        try:
            with open("config/routers.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 20, 24, 20)

        # Header
        title_box = QVBoxLayout()
        title_box.setSpacing(3)
        self.lbl_title = QLabel()
        self.lbl_title.setStyleSheet("font-size: 22px; font-weight: 800; color: #F8FAFC; letter-spacing: 0.5px;")
        self.lbl_sub = QLabel()
        self.lbl_sub.setStyleSheet("color: #94A3B8; font-size: 13px;")
        title_box.addWidget(self.lbl_title)
        title_box.addWidget(self.lbl_sub)
        layout.addLayout(title_box)

        # 0. Cấu hình Ngôn ngữ (Language Setting)
        self.grp_lang = QGroupBox()
        lang_form = QFormLayout(self.grp_lang)
        lang_form.setSpacing(12)

        self.cb_language = QComboBox()
        self.cb_language.addItems(["🇻🇳 Tiếng Việt", "🇬🇧 English"])
        self.cb_language.currentIndexChanged.connect(self._on_language_selection_changed)
        self.lbl_lang_field = QLabel()
        lang_form.addRow(self.lbl_lang_field, self.cb_language)
        layout.addWidget(self.grp_lang)

        # 1. Cấu hình quét mạng
        self.grp_scan = QGroupBox()
        scan_form = QFormLayout(self.grp_scan)
        scan_form.setSpacing(12)

        self.chk_autodetect = QCheckBox()
        self.chk_autodetect.toggled.connect(self._on_autodetect_toggle)
        scan_form.addRow("", self.chk_autodetect)

        self.chk_multisubnet = QCheckBox()
        scan_form.addRow("", self.chk_multisubnet)

        self.txt_custom_subnet = QLineEdit()
        self.lbl_sub_field = QLabel()
        scan_form.addRow(self.lbl_sub_field, self.txt_custom_subnet)

        self.spin_interval = QSpinBox()
        self.spin_interval.setRange(10, 3600)
        self.lbl_interval_field = QLabel()
        scan_form.addRow(self.lbl_interval_field, self.spin_interval)

        self.spin_offline_thresh = QSpinBox()
        self.spin_offline_thresh.setRange(30, 7200)
        self.lbl_offline_field = QLabel()
        scan_form.addRow(self.lbl_offline_field, self.spin_offline_thresh)

        self.txt_nmap_path = QLineEdit()
        self.lbl_nmap_field = QLabel()
        scan_form.addRow(self.lbl_nmap_field, self.txt_nmap_path)

        layout.addWidget(self.grp_scan)

        # 2. Cấu hình Router Adapter
        self.grp_router = QGroupBox()
        router_form = QFormLayout(self.grp_router)
        router_form.setSpacing(10)

        self.cb_adapter = QComboBox()
        self.cb_adapter.addItems([
            "mock - Mock Router Adapter",
            "tplink - TP-Link Router",
            "openwrt - OpenWrt Router",
            "mikrotik - MikroTik RouterOS"
        ])
        self.cb_adapter.currentIndexChanged.connect(self._on_adapter_changed)
        self.lbl_adapter_field = QLabel()
        router_form.addRow(self.lbl_adapter_field, self.cb_adapter)

        self.txt_router_host = QLineEdit()
        self.lbl_host_field = QLabel()
        router_form.addRow(self.lbl_host_field, self.txt_router_host)

        self.txt_router_port = QLineEdit()
        self.lbl_port_field = QLabel()
        router_form.addRow(self.lbl_port_field, self.txt_router_port)

        self.txt_router_user = QLineEdit()
        self.lbl_user_field = QLabel()
        router_form.addRow(self.lbl_user_field, self.txt_router_user)

        self.txt_router_pass = QLineEdit()
        self.txt_router_pass.setEchoMode(QLineEdit.Password)
        self.lbl_pass_field = QLabel()
        router_form.addRow(self.lbl_pass_field, self.txt_router_pass)

        self.btn_test_router = QPushButton()
        self.btn_test_router.setStyleSheet("""
            QPushButton {
                background-color: #1E293B;
                color: #38BDF8;
                border: 1px solid rgba(56, 189, 248, 0.4);
                font-weight: 600;
                font-size: 13px;
                padding: 7px 16px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: rgba(56, 189, 248, 0.15);
                border: 1px solid #38BDF8;
            }
            QPushButton:pressed {
                background-color: rgba(56, 189, 248, 0.25);
            }
        """)
        self.btn_test_router.clicked.connect(self._test_router_connection)
        router_form.addRow("", self.btn_test_router)

        layout.addWidget(self.grp_router)

        # 3. Tùy chọn bảo mật
        self.grp_sec = QGroupBox()
        sec_vbox = QVBoxLayout(self.grp_sec)

        self.chk_firewall = QCheckBox()
        self.chk_confirm = QCheckBox()
        sec_vbox.addWidget(self.chk_firewall)
        sec_vbox.addWidget(self.chk_confirm)

        layout.addWidget(self.grp_sec)

        # 4. Nút Lưu
        self.btn_save = QPushButton()
        self.btn_save.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4F46E5, stop:1 #06B6D4);
                color: #FFFFFF;
                font-weight: 700;
                font-size: 14px;
                padding: 11px 26px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4338CA, stop:1 #0891B2);
            }
            QPushButton:pressed {
                background: #3730A3;
            }
        """)
        self.btn_save.clicked.connect(self._save_settings)
        layout.addWidget(self.btn_save)

        layout.addStretch()

    def retranslate_ui(self):
        self.lbl_title.setText(t("set_title"))
        self.lbl_sub.setText(t("set_desc"))
        
        self.grp_lang.setTitle(t("grp_lang_config"))
        self.lbl_lang_field.setText(t("lbl_language"))
        
        self.grp_scan.setTitle(t("grp_scan_config"))
        self.chk_autodetect.setText(t("chk_autodetect"))
        self.chk_multisubnet.setText(t("chk_multisubnet"))
        self.txt_custom_subnet.setPlaceholderText(t("custom_subnets_placeholder"))
        self.lbl_sub_field.setText(t("lbl_custom_subnet"))
        self.lbl_interval_field.setText(t("lbl_scan_interval"))
        self.spin_interval.setSuffix(f" s")
        self.lbl_offline_field.setText(t("lbl_offline_thresh"))
        self.spin_offline_thresh.setSuffix(f" s")
        self.lbl_nmap_field.setText(t("lbl_nmap_path"))

        self.grp_router.setTitle(t("grp_router_config"))
        self.lbl_adapter_field.setText(t("lbl_adapter_type"))
        self.lbl_host_field.setText(t("lbl_router_host"))
        self.lbl_port_field.setText(t("lbl_router_port"))
        self.lbl_user_field.setText(t("lbl_router_user"))
        self.lbl_pass_field.setText(t("lbl_router_pass"))
        self.btn_test_router.setText(t("btn_test_conn"))

        self.grp_sec.setTitle(t("grp_sec_config"))
        self.chk_firewall.setText(t("chk_firewall"))
        self.chk_confirm.setText(t("chk_confirm"))
        self.btn_save.setText(f"  {t('btn_save_settings')}")

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

    def _test_router_connection(self):
        adapter_idx = self.cb_adapter.currentIndex()
        adapter_key = ["mock", "tplink", "openwrt", "mikrotik"][adapter_idx]
        temp_cfg = {
            "name": adapter_key,
            "host": self.txt_router_host.text().strip(),
            "port": int(self.txt_router_port.text().strip() or 80),
            "username": self.txt_router_user.text().strip(),
            "password": self.txt_router_pass.text().strip()
        }
        test_adapter = BlockManager.create_adapter(adapter_key, temp_cfg)
        ok, msg = test_adapter.test_connection()
        if ok:
            QMessageBox.information(self, t("conn_success"), msg)
        else:
            QMessageBox.warning(self, t("conn_fail"), msg)

    def _save_settings(self):
        adapter_idx = self.cb_adapter.currentIndex()
        adapter_key = ["mock", "tplink", "openwrt", "mikrotik"][adapter_idx]
        selected_lang = "vi" if self.cb_language.currentIndex() == 0 else "en"

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
            self.routers_data[adapter_key]["port"] = int(self.txt_router_port.text().strip() or 80)
            self.routers_data[adapter_key]["username"] = self.txt_router_user.text().strip()
            self.routers_data[adapter_key]["password"] = self.txt_router_pass.text().strip()
            self.routers_data[adapter_key]["enabled"] = True

        try:
            with open("config/config.json", "w", encoding="utf-8") as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
            with open("config/routers.json", "w", encoding="utf-8") as f:
                json.dump(self.routers_data, f, indent=2, ensure_ascii=False)

            new_adapter = BlockManager.create_adapter(adapter_key, self.routers_data.get(adapter_key, {}))
            self.block_manager.set_adapter(new_adapter)
            self.block_manager.enable_host_firewall = self.chk_firewall.isChecked()

            i18n.set_language(selected_lang)
            self.settings_saved.emit(self.config_data)
            QMessageBox.information(self, "Success", t("save_settings_success"))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving file: {e}")

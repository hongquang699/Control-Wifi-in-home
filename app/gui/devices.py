"""
Màn hình Quản lý Danh sách Thiết bị (Connected Devices View) - Song ngữ VI / EN.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont
from typing import List, Optional
from core.device import Device
from database.devices import DeviceDAO
from database.events import EventDAO
from security.blocker import BlockManager
from gui.device_detail import DeviceDetailDialog
from core.i18n import t, i18n
from gui.icons import get_app_icon
from gui.theme import (
    StatusPill, SubnetTabButton, COLOR_BG_CARD, COLOR_BORDER,
    COLOR_ACCENT_INDIGO, COLOR_ACCENT_ROSE, COLOR_ACCENT_EMERALD
)

class DevicesView(QWidget):
    data_changed = Signal()

    def __init__(
        self,
        device_dao: DeviceDAO,
        event_dao: EventDAO,
        block_manager: BlockManager,
        parent=None
    ):
        super().__init__(parent)
        self.device_dao = device_dao
        self.event_dao = event_dao
        self.block_manager = block_manager
        self.devices_cache: List[Device] = []
        self.selected_subnet_prefix = ""
        self._init_ui()
        self.retranslate_ui()
        self.load_devices()
        i18n.language_changed.connect(self._on_lang_changed)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 20, 24, 20)

        # 1. Header & Thanh tìm kiếm
        top_layout = QHBoxLayout()
        
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        self.lbl_title = QLabel()
        self.lbl_title.setStyleSheet("font-size: 22px; font-weight: 800; color: #F8FAFC; letter-spacing: 0.5px;")
        self.lbl_subtitle = QLabel("...")
        self.lbl_subtitle.setStyleSheet("color: #94A3B8; font-size: 13px;")
        title_box.addWidget(self.lbl_title)
        title_box.addWidget(self.lbl_subtitle)
        top_layout.addLayout(title_box)

        top_layout.addStretch()

        # Ô tìm kiếm với Vector Icon Flaticon
        self.txt_search = QLineEdit()
        self.txt_search.addAction(get_app_icon("search"), QLineEdit.LeadingPosition)
        self.txt_search.setFixedWidth(260)
        self.txt_search.setPlaceholderText("Tìm theo IP, MAC, Tên...")
        self.txt_search.textChanged.connect(self.load_devices)
        top_layout.addWidget(self.txt_search)

        # Dropdown lọc trạng thái
        self.cb_status = QComboBox()
        self.cb_status.currentIndexChanged.connect(self.load_devices)
        top_layout.addWidget(self.cb_status)

        layout.addLayout(top_layout)

        # 1.5 Thanh lọc dải mạng phân đoạn (Segmented Subnet Tabs)
        subtabs_layout = QHBoxLayout()
        subtabs_layout.setSpacing(8)

        self.tab_all = SubnetTabButton("subtab_all", 0)
        self.tab_secondary = SubnetTabButton("subtab_secondary", 0)
        self.tab_primary = SubnetTabButton("subtab_primary", 0)
        self.tab_all.setChecked(True)

        self.tab_all.clicked.connect(lambda: self._set_subnet_filter(""))
        self.tab_secondary.clicked.connect(lambda: self._set_subnet_filter("192.168.110."))
        self.tab_primary.clicked.connect(lambda: self._set_subnet_filter("192.168.1."))

        subtabs_layout.addWidget(self.tab_all)
        subtabs_layout.addWidget(self.tab_secondary)
        subtabs_layout.addWidget(self.tab_primary)
        subtabs_layout.addStretch()
        layout.addLayout(subtabs_layout)

        # 2. Bảng hiển thị danh sách thiết bị
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setShowGrid(False)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        header.setSectionResizeMode(6, QHeaderView.Fixed)
        header.setSectionResizeMode(7, QHeaderView.Fixed)

        self.table.setColumnWidth(1, 115)
        self.table.setColumnWidth(2, 148)
        self.table.setColumnWidth(3, 105)
        self.table.setColumnWidth(4, 115)
        self.table.setColumnWidth(5, 80)
        self.table.setColumnWidth(6, 95)
        self.table.setColumnWidth(7, 145)

        layout.addWidget(self.table)

    def retranslate_ui(self):
        self.lbl_title.setText(t("dev_title"))
        self.txt_search.setPlaceholderText(t("search_placeholder"))
        
        self.tab_all.retranslate_ui()
        self.tab_secondary.retranslate_ui()
        self.tab_primary.retranslate_ui()
        
        # Cập nhật items của combo box giữ nguyên index
        current_idx = max(0, self.cb_status.currentIndex())
        self.cb_status.blockSignals(True)
        self.cb_status.clear()
        self.cb_status.addItems([
            t("filter_all"),
            t("filter_online"),
            t("filter_offline"),
            t("filter_blocked")
        ])
        self.cb_status.setCurrentIndex(current_idx)
        self.cb_status.blockSignals(False)

        self.table.setHorizontalHeaderLabels([
            t("col_name"), t("col_ip"), t("col_mac"), t("col_vendor"),
            t("col_network"), t("col_conn_type"), t("col_status"), t("col_actions")
        ])

    def _set_subnet_filter(self, prefix: str):
        self.selected_subnet_prefix = prefix
        self.load_devices()

    def _on_lang_changed(self, lang: str):
        self.retranslate_ui()
        self.load_devices()

    def load_devices(self):
        keyword = self.txt_search.text().strip()
        status_idx = self.cb_status.currentIndex()
        
        status_filter = None
        blocked_filter = None
        if status_idx == 1:
            status_filter = "ONLINE"
        elif status_idx == 2:
            status_filter = "OFFLINE"
        elif status_idx == 3:
            blocked_filter = True

        raw_devices = self.device_dao.get_all_devices(
            status_filter=status_filter,
            blocked_filter=blocked_filter,
            search_keyword=keyword
        )

        # Cập nhật đếm số lượng trên Subnet Tabs
        cnt_all = len(raw_devices)
        cnt_sec = sum(1 for d in raw_devices if d.ip.startswith("192.168.110."))
        cnt_pri = sum(1 for d in raw_devices if d.ip.startswith("192.168.1."))
        self.tab_all.set_count(cnt_all)
        self.tab_secondary.set_count(cnt_sec)
        self.tab_primary.set_count(cnt_pri)

        # Lọc theo tab subnet được chọn
        if self.selected_subnet_prefix:
            self.devices_cache = [d for d in raw_devices if d.ip.startswith(self.selected_subnet_prefix)]
        else:
            self.devices_cache = raw_devices

        self.table.setRowCount(len(self.devices_cache))
        self.lbl_subtitle.setText(t("dev_subtitle", count=len(self.devices_cache)))

        type_icons = {
            "Router": "router",
            "PC": "laptop",
            "Laptop": "laptop",
            "Phone": "smartphone",
            "TV": "tv",
            "Camera": "camera",
            "IoT": "devices",
            "Printer": "printer"
        }

        for row, dev in enumerate(self.devices_cache):
            self.table.setRowHeight(row, 40)

            # Cột 0: Tên thiết bị thông minh kèm Vector Icon Flaticon
            icon_key = type_icons.get(dev.device_type, "devices")
            if dev.custom_name:
                name_text = dev.custom_name
            elif dev.hostname:
                name_text = dev.hostname
            else:
                v_name = dev.vendor.split()[0] if dev.vendor and dev.vendor != "Unknown" else "Thiết bị"
                last_octet = dev.ip.split(".")[-1] if "." in dev.ip else dev.ip
                name_text = f"{v_name} #{last_octet}"

            item_name = QTableWidgetItem(name_text)
            item_name.setIcon(get_app_icon(icon_key))
            if dev.custom_name:
                item_name.setFont(QFont("Segoe UI", 10, QFont.Bold))
                item_name.setForeground(QColor("#F8FAFC"))
            else:
                item_name.setFont(QFont("Segoe UI", 9, QFont.DemiBold))
                item_name.setForeground(QColor("#E2E8F0"))
            self.table.setItem(row, 0, item_name)

            # Cột 1: Địa chỉ IP
            item_ip = QTableWidgetItem(dev.ip)
            item_ip.setFont(QFont("Segoe UI", 9, QFont.DemiBold))
            item_ip.setForeground(QColor("#38BDF8"))
            self.table.setItem(row, 1, item_ip)

            # Cột 2: Địa chỉ MAC
            item_mac = QTableWidgetItem(dev.mac)
            item_mac.setFont(QFont("Consolas", 9))
            item_mac.setForeground(QColor("#94A3B8"))
            self.table.setItem(row, 2, item_mac)

            # Cột 3: Nhà sản xuất & loại
            vendor_display = dev.vendor or "Unknown"
            if dev.device_type and dev.device_type != "Unknown":
                vendor_display += f" ({dev.device_type})"
            item_vendor = QTableWidgetItem(vendor_display)
            item_vendor.setForeground(QColor("#CBD5E1"))
            self.table.setItem(row, 3, item_vendor)

            # Cột 4: Mạng kết nối (Network Badge)
            net_badge = dev.display_network_badge
            item_net = QTableWidgetItem(net_badge)
            if "Wi-Fi Tổng" in net_badge or "Tổng" in net_badge:
                item_net.setForeground(QColor("#38BDF8"))  # Cyan
            elif "Router Phụ" in net_badge or "Phụ" in net_badge:
                item_net.setForeground(QColor("#818CF8"))  # Indigo
            else:
                item_net.setForeground(QColor("#94A3B8"))
            item_net.setFont(QFont("Segoe UI", 9, QFont.DemiBold))
            self.table.setItem(row, 4, item_net)

            # Cột 5: Phương thức kết nối (Connection Type)
            conn_badge = dev.display_connection_badge
            item_conn = QTableWidgetItem(conn_badge)
            is_wifi = "Wi-Fi" in conn_badge
            item_conn.setIcon(get_app_icon("wifi" if is_wifi else "ethernet"))
            if is_wifi:
                item_conn.setForeground(QColor("#34D399"))  # Emerald
            elif "LAN" in conn_badge:
                item_conn.setForeground(QColor("#FBBF24"))  # Amber
            elif "WAN" in conn_badge:
                item_conn.setForeground(QColor("#A78BFA"))  # Violet
            else:
                item_conn.setForeground(QColor("#94A3B8"))
            item_conn.setFont(QFont("Segoe UI", 9, QFont.DemiBold))
            self.table.setItem(row, 5, item_conn)

            # Cột 6: Huy hiệu trạng thái StatusPill bo tròn hiện đại
            pill = StatusPill("BLOCKED" if dev.blocked else dev.status)
            self.table.setCellWidget(row, 6, pill)

            # Cột 7: Các nút thao tác
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 2, 4, 2)
            actions_layout.setSpacing(6)
            actions_layout.setAlignment(Qt.AlignCenter)

            btn_detail = QPushButton(t("btn_detail"))
            btn_detail.setIcon(get_app_icon("info"))
            btn_detail.setCursor(Qt.PointingHandCursor)
            btn_detail.setStyleSheet("""
                QPushButton {
                    background-color: rgba(99, 102, 241, 0.15);
                    color: #818CF8;
                    border: 1px solid rgba(99, 102, 241, 0.35);
                    border-radius: 6px;
                    padding: 4px 8px;
                    font-size: 11px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #6366F1;
                    color: white;
                }
            """)
            btn_detail.clicked.connect(lambda checked=False, d=dev: self._open_detail(d))
            actions_layout.addWidget(btn_detail)

            btn_toggle_block = QPushButton(t("btn_unblock") if dev.blocked else t("btn_block"))
            btn_toggle_block.setIcon(get_app_icon("shield_check" if dev.blocked else "shield_block"))
            btn_toggle_block.setCursor(Qt.PointingHandCursor)
            if dev.blocked:
                btn_toggle_block.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(16, 185, 129, 0.15);
                        color: #10B981;
                        border: 1px solid rgba(16, 185, 129, 0.35);
                        border-radius: 6px;
                        padding: 4px 8px;
                        font-size: 11px;
                        font-weight: 600;
                    }
                    QPushButton:hover {
                        background-color: #10B981;
                        color: white;
                    }
                """)
            else:
                btn_toggle_block.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(244, 63, 94, 0.15);
                        color: #F43F5E;
                        border: 1px solid rgba(244, 63, 94, 0.35);
                        border-radius: 6px;
                        padding: 4px 8px;
                        font-size: 11px;
                        font-weight: 600;
                    }
                    QPushButton:hover {
                        background-color: #F43F5E;
                        color: white;
                    }
                """)
            btn_toggle_block.clicked.connect(lambda checked=False, d=dev: self._toggle_block(d))
            actions_layout.addWidget(btn_toggle_block)

            self.table.setCellWidget(row, 7, actions_widget)

    def _open_detail(self, dev: Device):
        dlg = DeviceDetailDialog(
            device=dev,
            device_dao=self.device_dao,
            event_dao=self.event_dao,
            block_manager=self.block_manager,
            parent=self
        )
        dlg.device_changed.connect(self._on_device_changed)
        dlg.exec()

    def _on_device_changed(self):
        self.load_devices()
        self.data_changed.emit()

    def _toggle_block(self, dev: Device):
        if dev.blocked:
            reply = QMessageBox.question(
                self, t("confirm_unblock_title"),
                t("confirm_unblock_msg", mac=dev.mac, ip=dev.ip),
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                success, msg = self.block_manager.unblock_device(dev.mac, dev.ip)
                if success:
                    dev.blocked = False
                    self.load_devices()
                    self.data_changed.emit()
                    QMessageBox.information(self, "Success", msg)
                else:
                    QMessageBox.warning(self, "Error", msg)
        else:
            reply = QMessageBox.warning(
                self, t("confirm_block_title"),
                t("confirm_block_msg", name=dev.display_name, mac=dev.mac, ip=dev.ip),
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                success, msg = self.block_manager.block_device(
                    dev.mac, ip=dev.ip, reason=f"Blocked: {dev.display_name}"
                )
                if success:
                    dev.blocked = True
                    self.load_devices()
                    self.data_changed.emit()
                    QMessageBox.information(self, "Success", msg)
                else:
                    QMessageBox.warning(self, "Error", msg)

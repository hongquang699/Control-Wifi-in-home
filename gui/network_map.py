"""
Màn hình Sơ đồ mạng Topology (Network Map View) - Hỗ trợ Đa dải mạng (Wi-Fi Tổng & Router Phụ).
"""

import ipaddress
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTreeWidget, QTreeWidgetItem, QHeaderView, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont
from typing import List, Optional, Dict
from core.device import Device
from database.devices import DeviceDAO
from database.events import EventDAO
from security.blocker import BlockManager
from core.network import NetworkManagerCore, NetworkInterface
from gui.device_detail import DeviceDetailDialog
from core.i18n import t, i18n

class NetworkMapView(QWidget):
    data_changed = Signal()

    def __init__(
        self,
        device_dao: DeviceDAO,
        event_dao: EventDAO,
        block_manager: BlockManager,
        iface: Optional[NetworkInterface] = None,
        parent=None
    ):
        super().__init__(parent)
        self.device_dao = device_dao
        self.event_dao = event_dao
        self.block_manager = block_manager
        self.iface = iface or NetworkManagerCore.get_default_interface()
        self._is_loaded = False
        self._init_ui()
        self.retranslate_ui()
        i18n.language_changed.connect(self._on_lang_changed)

    def ensure_loaded(self):
        """Khởi tạo dữ liệu topology khi tab được mở (lazy loading)."""
        if not self._is_loaded:
            self.refresh_map()

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
        self.lbl_desc = QLabel()
        self.lbl_desc.setStyleSheet("color: #94A3B8; font-size: 13px;")
        title_box.addWidget(self.lbl_title)
        title_box.addWidget(self.lbl_desc)
        header_layout.addLayout(title_box)

        header_layout.addStretch()

        self.btn_refresh = QPushButton()
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #101B33;
                color: #F8FAFC;
                font-weight: 600;
                padding: 8px 18px;
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            QPushButton:hover {
                background-color: #1E293B;
                border: 1px solid #6366F1;
            }
        """)
        self.btn_refresh.clicked.connect(self.refresh_map)
        header_layout.addWidget(self.btn_refresh)
        layout.addLayout(header_layout)

        # 2. Cây sơ đồ mạng (Network Topology Tree)
        self.tree = QTreeWidget()
        self.tree.setColumnCount(7)
        self.tree.setIndentation(16)
        
        header = self.tree.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        header.setSectionResizeMode(6, QHeaderView.Fixed)

        self.tree.setColumnWidth(0, 310)
        self.tree.setColumnWidth(1, 115)
        self.tree.setColumnWidth(2, 135)
        self.tree.setColumnWidth(3, 100)
        self.tree.setColumnWidth(4, 120)
        self.tree.setColumnWidth(5, 65)
        self.tree.setColumnWidth(6, 85)

        self.tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.tree)

    def retranslate_ui(self):
        self.lbl_title.setText(t("map_title"))
        self.lbl_desc.setText(t("map_desc"))
        self.btn_refresh.setText(t("btn_refresh_map"))
        self.tree.setHeaderLabels([
            t("col_map_node"), t("col_ip"), t("col_mac"),
            t("col_conn_type"), t("col_type"), t("col_latency"), t("col_status")
        ])

    def _on_lang_changed(self, lang: str):
        self.retranslate_ui()
        self.refresh_map()

    def refresh_map(self):
        self._is_loaded = True
        self.tree.clear()
        if not self.iface:
            self.iface = NetworkManagerCore.get_default_interface()

        devices = self.device_dao.get_all_devices()
        local_gw_ip = self.iface.gateway if self.iface else "192.168.110.1"
        local_cidr = self.iface.cidr if self.iface else "192.168.110.0/24"

        # Phân loại thiết bị theo subnet
        subnets_map: Dict[str, List[Device]] = {}
        main_modem_dev = next((d for d in devices if d.ip in ("192.168.1.1", "192.168.0.1") and d.ip != local_gw_ip), None)
        local_gw_dev = next((d for d in devices if d.ip == local_gw_ip), None)

        for dev in devices:
            # Xác định subnet của IP
            parts = dev.ip.split(".")
            if len(parts) == 4:
                net_key = f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
            else:
                net_key = "Other"
            subnets_map.setdefault(net_key, []).append(dev)

        # 0. Nút gốc cao nhất: 🌍 INTERNET TOÀN CẦU
        net_root = QTreeWidgetItem(self.tree)
        net_root.setText(0, " 🌍 [MẠNG INTERNET TOÀN CẦU] Cáp quang WAN Uplink")
        net_root.setText(1, "0.0.0.0/0")
        net_root.setText(3, "🌐 Cáp quang ISP")
        net_root.setText(4, "Global Internet")
        net_root.setText(6, t("val_online"))
        net_root.setForeground(6, QColor("#10B981"))
        net_root.setFont(0, QFont("Segoe UI", 10, QFont.Bold))

        # 1. Nút cấp 2: Nếu có Modem Tổng (192.168.1.1)
        if main_modem_dev:
            root_item = QTreeWidgetItem(net_root)
            root_item.setText(0, f" 🌐 [Modem / Wi-Fi Tổng ISP] {main_modem_dev.vendor} ({main_modem_dev.ip})")
            root_item.setText(1, main_modem_dev.ip)
            root_item.setText(2, main_modem_dev.mac)
            root_item.setText(3, "🌐 GPON ONT")
            root_item.setText(4, "Modem ONT Gateway")
            root_item.setText(5, f"{main_modem_dev.latency_ms} ms")
            root_item.setText(6, t("val_online") if main_modem_dev.status == "ONLINE" else t("val_offline"))
            root_item.setForeground(6, QColor("#10B981") if main_modem_dev.status == "ONLINE" else QColor("#64748B"))
            root_item.setFont(0, QFont("Segoe UI", 10, QFont.Bold))
            root_item.setData(0, Qt.UserRole, main_modem_dev)

            # A. Nhánh các thiết bị cắm/bắt Wi-Fi trực tiếp vào Modem Tổng
            modem_subnet_key = f"{main_modem_dev.ip.rsplit('.', 1)[0]}.0/24"
            modem_devices = [d for d in subnets_map.get(modem_subnet_key, []) if d.ip != main_modem_dev.ip]

            branch_modem = QTreeWidgetItem(root_item)
            branch_modem.setText(0, f" 📡 [Mạng Wi-Fi Tổng] {modem_subnet_key} ({len(modem_devices)} thiết bị)")
            branch_modem.setText(1, modem_subnet_key)
            branch_modem.setFont(0, QFont("Segoe UI", 9, QFont.Bold))
            self._populate_group_devices(branch_modem, modem_devices)

            # B. Nhánh Router Phụ (Ruijie) cắm vào Modem Tổng
            router_item = QTreeWidgetItem(root_item)
            gw_vendor = local_gw_dev.vendor if local_gw_dev else "Router"
            router_item.setText(0, f" 📶 [Router Wi-Fi Phụ] {gw_vendor} ({local_gw_ip})")
            router_item.setText(1, local_gw_ip)
            router_item.setText(2, local_gw_dev.mac if local_gw_dev else "")
            router_item.setText(3, "🔌 Cáp WAN Uplink")
            router_item.setText(4, "Secondary Wi-Fi Router")
            router_item.setText(6, t("val_online"))
            router_item.setForeground(6, QColor("#10B981"))
            router_item.setFont(0, QFont("Segoe UI", 10, QFont.Bold))
            if local_gw_dev:
                router_item.setData(0, Qt.UserRole, local_gw_dev)

            # Nhánh con của Router phụ
            local_devices = [d for d in subnets_map.get(local_cidr, []) if d.ip != local_gw_ip]
            branch_local = QTreeWidgetItem(router_item)
            branch_local.setText(0, f" 💻 [Mạng Wi-Fi Phụ LAN] {local_cidr} ({len(local_devices)} thiết bị)")
            branch_local.setText(1, local_cidr)
            branch_local.setFont(0, QFont("Segoe UI", 9, QFont.Bold))
            self._populate_group_devices(branch_local, local_devices)

        else:
            # Nếu chỉ có 1 router cục bộ
            gw_vendor = local_gw_dev.vendor if local_gw_dev else "Router"
            gw_mac = local_gw_dev.mac if local_gw_dev else ""

            root_item = QTreeWidgetItem(net_root)
            root_item.setText(0, f" 🌐 [Router Gateway] {gw_vendor} ({local_gw_ip})")
            root_item.setText(1, local_gw_ip)
            root_item.setText(2, gw_mac)
            root_item.setText(3, "🌐 Cáp WAN/LAN")
            root_item.setText(4, "Router / Gateway")
            root_item.setText(6, t("val_online"))
            root_item.setForeground(6, QColor("#10B981"))
            root_item.setFont(0, QFont("Segoe UI", 10, QFont.Bold))
            if local_gw_dev:
                root_item.setData(0, Qt.UserRole, local_gw_dev)

            # Nhánh Subnet
            for s_cidr, s_devs in subnets_map.items():
                s_item = QTreeWidgetItem(root_item)
                s_item.setText(0, f" [Dải mạng LAN] {s_cidr} ({len(s_devs)} thiết bị)")
                s_item.setText(1, s_cidr)
                s_item.setFont(0, QFont("Segoe UI", 9, QFont.Bold))
                self._populate_group_devices(s_item, [d for d in s_devs if d.ip != local_gw_ip])

        self.tree.expandAll()

    def _populate_group_devices(self, parent_item: QTreeWidgetItem, device_list: List[Device]):
        group_pcs = QTreeWidgetItem(parent_item)
        group_phones = QTreeWidgetItem(parent_item)
        group_iot = QTreeWidgetItem(parent_item)
        group_others = QTreeWidgetItem(parent_item)

        for grp in [group_pcs, group_phones, group_iot, group_others]:
            grp.setFont(0, QFont("Segoe UI", 9, QFont.DemiBold))

        count_pcs = 0
        count_phones = 0
        count_iot = 0
        count_others = 0

        for d in device_list:
            target_grp = group_others
            dtype = d.device_type.lower()
            if "pc" in dtype or "laptop" in dtype:
                target_grp = group_pcs
                count_pcs += 1
            elif "phone" in dtype or "mobile" in dtype:
                target_grp = group_phones
                count_phones += 1
            elif "iot" in dtype:
                target_grp = group_iot
                count_iot += 1
            else:
                target_grp = group_others
                count_others += 1

            d_item = QTreeWidgetItem(target_grp)
            v_title = d.vendor.split()[0] if d.vendor and d.vendor != "Unknown" else "Thiết bị"
            ip_suffix = d.ip.split(".")[-1] if "." in d.ip else d.ip
            display_name = d.custom_name or d.hostname or f"{v_title} #{ip_suffix}"
            d_item.setText(0, f"  {display_name}")
            d_item.setText(1, d.ip)
            d_item.setText(2, d.mac)
            
            # Cột 3: Phương thức kết nối
            conn_badge = d.display_connection_badge
            d_item.setText(3, conn_badge)
            if "Wi-Fi" in conn_badge:
                d_item.setForeground(3, QColor("#34D399"))
            elif "LAN" in conn_badge:
                d_item.setForeground(3, QColor("#FBBF24"))
            else:
                d_item.setForeground(3, QColor("#A78BFA"))

            d_item.setText(4, f"{d.vendor} ({d.device_type})")
            d_item.setText(5, f"{d.latency_ms} ms" if d.status == "ONLINE" else "-")
            
            if d.blocked:
                d_item.setText(6, t("card_blocked"))
                d_item.setForeground(6, QColor("#EF4444"))
                d_item.setFont(6, QFont("Segoe UI", weight=QFont.Bold))
            elif d.status == "ONLINE":
                d_item.setText(6, t("val_online"))
                d_item.setForeground(6, QColor("#10B981"))
            else:
                d_item.setText(6, t("val_offline"))
                d_item.setForeground(6, QColor("#64748B"))

            d_item.setData(0, Qt.UserRole, d)

        group_pcs.setText(0, f" 💻 {t('grp_pcs', count=count_pcs)}")
        group_phones.setText(0, f" 📱 {t('grp_phones', count=count_phones)}")
        group_iot.setText(0, f" 💡 {t('grp_iot', count=count_iot)}")
        group_others.setText(0, f" 🖨️ {t('grp_others', count=count_others)}")

    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        dev = item.data(0, Qt.UserRole)
        if isinstance(dev, Device):
            dlg = DeviceDetailDialog(
                device=dev,
                device_dao=self.device_dao,
                event_dao=self.event_dao,
                block_manager=self.block_manager,
                parent=self
            )
            dlg.device_changed.connect(self._on_detail_changed)
            dlg.exec()

    def _on_detail_changed(self):
        self.refresh_map()
        self.data_changed.emit()

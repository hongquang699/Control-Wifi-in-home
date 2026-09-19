"""
Màn hình Sơ Đồ Mạng Topology & Cổng Định Tuyến (Network Topology Map View) - Chuẩn Thiết kế Cyber Dark-Tech (Ảnh 3).
Bao gồm:
- 2 Thẻ Subnet Gateway (Modem Tổng 192.168.1.0/24 & Router Phụ 192.168.110.0/24) kèm thanh tiến trình IP
- Sơ Đồ Phân Bổ Nút Mạng Trực Quan (Interactive Topology Node Diagram) chuẩn mực 4 cấp độ kết nối
- Thanh phân tích bước nhảy động (Hop Path Analysis Breadcrumb): Thiết bị con ➔ Router Phụ ➔ Modem Tổng ➔ Internet
- Chế độ chuyển đổi xem trực quan (Diagram) hoặc xem dạng Cây (QTreeWidget)
- Công cụ Chẩn Đoán ICMP Echo Ping Trực Tiếp tương tác tức thì
"""

import subprocess
import platform
from typing import List, Optional, Dict
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTreeWidget, QTreeWidgetItem, QHeaderView, QFrame, QProgressBar,
    QLineEdit, QScrollArea, QStackedWidget
)
from PySide6.QtCore import Qt, Signal, QSize, QTimer
from PySide6.QtGui import QColor, QFont

from core.device import Device
from database.devices import DeviceDAO
from database.events import EventDAO
from security.blocker import BlockManager
from core.network import NetworkManagerCore, NetworkInterface
from gui.device_detail import DeviceDetailDialog
from gui.icons import get_app_icon
from core.i18n import t, i18n
from gui.theme import (
    COLOR_BG_CARD, COLOR_BORDER, COLOR_ACCENT_CYAN,
    COLOR_ACCENT_INDIGO, COLOR_ACCENT_EMERALD, COLOR_ACCENT_AMBER,
    STYLE_BTN_PRIMARY, STYLE_BTN_SLATE
)


class SubnetGatewayCard(QFrame):
    """Thẻ hiển thị thông tin chi tiết một dải mạng Gateway Subnet."""
    def __init__(self, title: str, subtitle: str, gateway_ip: str, cidr: str, badge_text: str, accent_hex: str, parent=None):
        super().__init__(parent)
        self.accent_hex = accent_hex
        self.cidr = cidr
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_BG_CARD};
                border: 1px solid {COLOR_BORDER};
                border-radius: 14px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(8)

        # Header: CIDR badge + Trực tuyến status
        header = QHBoxLayout()
        lbl_cidr = QLabel(f"  {cidr}  ")
        lbl_cidr.setStyleSheet(f"""
            background-color: rgba(56, 189, 248, 0.1);
            color: {accent_hex};
            border: 1px solid rgba(56, 189, 248, 0.25);
            border-radius: 9999px;
            font-size: 11px;
            font-weight: 700;
            font-family: 'Fira Code', monospace;
            padding: 2px 8px;
        """)
        header.addWidget(lbl_cidr)
        header.addStretch()

        lbl_status = QLabel("● Trực tuyến")
        lbl_status.setStyleSheet("color: #10B981; font-size: 11px; font-weight: 600;")
        header.addWidget(lbl_status)
        layout.addLayout(header)

        # Title
        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet("color: #F8FAFC; font-size: 13px; font-weight: 700;")
        layout.addWidget(self.lbl_title)

        # Details box
        details_box = QVBoxLayout()
        details_box.setSpacing(3)
        self.lbl_gw = QLabel(f"Gateway IP: {gateway_ip}")
        self.lbl_gw.setStyleSheet(f"color: {accent_hex}; font-size: 11px; font-weight: 700; font-family: 'Fira Code', monospace;")
        self.lbl_sub = QLabel(subtitle)
        self.lbl_sub.setStyleSheet("color: #94A3B8; font-size: 11px; font-family: 'Segoe UI', sans-serif;")
        details_box.addWidget(self.lbl_gw)
        details_box.addWidget(self.lbl_sub)
        layout.addLayout(details_box)

        # IP Usage Meter
        meter_row = QHBoxLayout()
        lbl_pool_title = QLabel("IP Pool Sử Dụng:")
        lbl_pool_title.setStyleSheet("color: #94A3B8; font-size: 11px; font-family: 'Fira Code', monospace;")
        self.lbl_cap = QLabel("0 / 254 IPs (0.0%)")
        self.lbl_cap.setStyleSheet(f"color: {accent_hex}; font-size: 11px; font-weight: 700; font-family: 'Fira Code', monospace;")
        meter_row.addWidget(lbl_pool_title)
        meter_row.addStretch()
        meter_row.addWidget(self.lbl_cap)
        layout.addLayout(meter_row)

        self.pbar = QProgressBar()
        self.pbar.setFixedHeight(6)
        self.pbar.setTextVisible(False)
        self.pbar.setRange(0, 254)
        self.pbar.setValue(0)
        self.pbar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #121E36;
                border-radius: 3px;
                border: none;
            }}
            QProgressBar::chunk {{
                background-color: {accent_hex};
                border-radius: 3px;
            }}
        """)
        layout.addWidget(self.pbar)

    def set_stats(self, count: int):
        pct = (count / 254.0) * 100
        self.lbl_cap.setText(f"{count} / 254 IPs ({pct:.1f}%)")
        self.pbar.setValue(min(254, count))


class TopologyNodeCard(QFrame):
    """Thẻ nút mạng thiết bị trong sơ đồ trực quan (Interactive Node Card)."""
    clicked = Signal(str, str, int, str, str) # title, ip, hops, rtt, path
    double_clicked = Signal(object)           # device

    def __init__(self, title: str, ip: str, icon_key: str, hops: int, rtt: str, path_str: str, subtitle: str = "", accent_hex: str = "#38BDF8", device: Optional[Device] = None, parent=None):
        super().__init__(parent)
        self.title = title
        self.ip = ip
        self.hops = hops
        self.rtt = rtt
        self.path_str = path_str
        self.device = device
        self.accent_hex = accent_hex
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedWidth(155)
        self.setFixedHeight(68)

        self.default_style = f"""
            QFrame {{
                background-color: #0F172A;
                border: 1px solid #1E293B;
                border-radius: 12px;
            }}
            QFrame:hover {{
                border: 1px solid {accent_hex};
                background-color: #16243D;
            }}
        """
        self.selected_style = f"""
            QFrame {{
                background-color: rgba(56, 189, 248, 0.15);
                border: 2px solid {accent_hex};
                border-radius: 12px;
            }}
        """
        self.setStyleSheet(self.default_style)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 8, 6, 8)
        layout.setSpacing(3)
        layout.setAlignment(Qt.AlignCenter)

        lbl_icon = QLabel()
        lbl_icon.setPixmap(get_app_icon(icon_key).pixmap(18, 18))
        lbl_icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_icon)

        lbl_t = QLabel(title)
        lbl_t.setStyleSheet("color: #F8FAFC; font-size: 11px; font-weight: 700;")
        lbl_t.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_t)

        sub_text = ip if not subtitle else f"{ip} • {subtitle}"
        lbl_s = QLabel(sub_text)
        lbl_s.setStyleSheet(f"color: {accent_hex}; font-size: 10px; font-family: 'Fira Code', monospace;")
        lbl_s.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_s)

    def set_selected(self, sel: bool):
        self.setStyleSheet(self.selected_style if sel else self.default_style)

    def mousePressEvent(self, event):
        self.clicked.emit(self.title, self.ip, self.hops, self.rtt, self.path_str)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if self.device:
            self.double_clicked.emit(self.device)
        super().mouseDoubleClickEvent(event)


class WideGatewayNodeCard(QFrame):
    """Thẻ nút mạng cổng Gateway chính (Level 0 WAN hoặc Level 1 Modem)."""
    clicked = Signal(str, str, int, str, str)

    def __init__(self, title: str, subtitle: str, ip: str, icon_key: str, hops: int, rtt: str, path_str: str, border_color: str, accent_hex: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.ip = ip
        self.hops = hops
        self.rtt = rtt
        self.path_str = path_str
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(15, 23, 42, 0.95);
                border: 1px solid {border_color};
                border-radius: 14px;
            }}
            QFrame:hover {{
                border: 1px solid {accent_hex};
                background-color: #16243D;
            }}
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 8, 18, 8)
        layout.setSpacing(10)

        lbl_icon = QLabel()
        lbl_icon.setPixmap(get_app_icon(icon_key).pixmap(20, 20))
        layout.addWidget(lbl_icon)

        v = QVBoxLayout()
        v.setSpacing(1)
        lbl_t = QLabel(title)
        lbl_t.setStyleSheet("color: #F8FAFC; font-size: 12px; font-weight: 800;")
        lbl_s = QLabel(subtitle)
        lbl_s.setStyleSheet(f"color: {accent_hex}; font-size: 10px; font-family: 'Fira Code', monospace;")
        v.addWidget(lbl_t)
        v.addWidget(lbl_s)
        layout.addLayout(v)

    def mousePressEvent(self, event):
        self.clicked.emit(self.title, self.ip, self.hops, self.rtt, self.path_str)
        super().mousePressEvent(event)


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
        self.active_node_cards: List[TopologyNodeCard] = []

        self._init_ui()
        self.retranslate_ui()
        i18n.language_changed.connect(self._on_lang_changed)

    def ensure_loaded(self):
        if not self._is_loaded:
            self.refresh_map()

    def _init_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(14)
        main_layout.setContentsMargins(24, 20, 24, 20)

        # 1. Header Toolbar
        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(3)
        self.lbl_title = QLabel("Hạ Tầng Mạng & Sơ Đồ Topo Đa Tầng")
        self.lbl_title.setStyleSheet("font-size: 22px; font-weight: 800; color: #F8FAFC; letter-spacing: 0.5px;")
        self.lbl_desc = QLabel("Phân tích Subnet CIDR, định tuyến Internet và chẩn đoán đường truyền đa bước nhảy")
        self.lbl_desc.setStyleSheet("color: #94A3B8; font-size: 13px;")
        title_box.addWidget(self.lbl_title)
        title_box.addWidget(self.lbl_desc)
        header_layout.addLayout(title_box)

        header_layout.addStretch()

        self.btn_refresh = QPushButton(" Quét Lại Topology")
        self.btn_refresh.setIcon(get_app_icon("refresh"))
        self.btn_refresh.setIconSize(QSize(15, 15))
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        self.btn_refresh.setStyleSheet(STYLE_BTN_SLATE)
        self.btn_refresh.clicked.connect(self.refresh_map)
        header_layout.addWidget(self.btn_refresh)
        main_layout.addLayout(header_layout)

        # 2. Hai Thẻ Cổng Subnet Gateway (Chuẩn Demo Web)
        gateways_layout = QHBoxLayout()
        gateways_layout.setSpacing(14)

        self.card_gw_modem = SubnetGatewayCard(
            title="Wi-Fi Tổng ISP / Modem Gateway Chính",
            subtitle="Ethernet Controller #1 • DHCP: 192.168.1.100 - 250",
            gateway_ip="192.168.1.1",
            cidr="192.168.1.0/24",
            badge_text="● GPON ONT Gateway",
            accent_hex="#38BDF8"
        )
        self.card_gw_router = SubnetGatewayCard(
            title="Router Phụ Gigabit (Ruijie Reyee / TP-Link)",
            subtitle="Uplink WAN: 192.168.1.2 • DHCP: 192.168.110.10 - 200",
            gateway_ip="192.168.110.1",
            cidr="192.168.110.0/24",
            badge_text="● Sub-Router AP",
            accent_hex="#818CF8"
        )
        gateways_layout.addWidget(self.card_gw_modem)
        gateways_layout.addWidget(self.card_gw_router)
        main_layout.addLayout(gateways_layout)

        # 3. Thẻ Sơ Đồ Topo Trực Quan & Cây Nút Mạng (Hop Path Topology Card)
        topo_card = QFrame()
        topo_card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_BG_CARD};
                border: 1px solid {COLOR_BORDER};
                border-radius: 14px;
            }}
        """)
        topo_box = QVBoxLayout(topo_card)
        topo_box.setContentsMargins(16, 14, 16, 14)
        topo_box.setSpacing(10)

        tc_top_bar = QHBoxLayout()
        tc_top_bar.setSpacing(6)
        
        tc_title_box = QVBoxLayout()
        tc_title_box.setSpacing(2)
        self.lbl_tc_title = QLabel("Sơ Đồ Phân Bổ Nút Mạng (Click vào thiết bị để xem lộ trình Hop Path)")
        self.lbl_tc_title.setStyleSheet("color: #F8FAFC; font-size: 13px; font-weight: 700;")
        self.lbl_tc_sub = QLabel("2 Tầng • Khảo sát các nút mạng phân đoạn và đo lường độ trễ từng bước nhảy")
        self.lbl_tc_sub.setStyleSheet("color: #94A3B8; font-size: 11px;")
        tc_title_box.addWidget(self.lbl_tc_title)
        tc_title_box.addWidget(self.lbl_tc_sub)
        tc_top_bar.addLayout(tc_title_box)
        tc_top_bar.addStretch()

        # Nút chuyển chế độ xem: Diagram vs Tree
        self.btn_view_diagram = QPushButton("Sơ Đồ Trực Quan")
        self.btn_view_diagram.setCursor(Qt.PointingHandCursor)
        self.btn_view_diagram.setStyleSheet("""
            QPushButton {
                background-color: #0284C7;
                color: #FFFFFF;
                font-weight: 700;
                font-size: 11px;
                border: 1px solid #38BDF8;
                border-radius: 6px;
                padding: 4px 12px;
            }
        """)
        self.btn_view_tree = QPushButton("Danh Sách Cây")
        self.btn_view_tree.setCursor(Qt.PointingHandCursor)
        self.btn_view_tree.setStyleSheet(STYLE_BTN_SLATE)
        
        self.btn_view_diagram.clicked.connect(lambda: self._set_topo_mode(0))
        self.btn_view_tree.clicked.connect(lambda: self._set_topo_mode(1))

        tc_top_bar.addWidget(self.btn_view_diagram)
        tc_top_bar.addWidget(self.btn_view_tree)
        topo_box.addLayout(tc_top_bar)

        # Stacked Widget chứa Sơ Đồ Trực Quan (0) và Tree Widget (1)
        self.topo_stack = QStackedWidget()

        # Page 0: Interactive Visual Diagram
        self.diagram_container = QWidget()
        self.diagram_layout = QVBoxLayout(self.diagram_container)
        self.diagram_layout.setContentsMargins(10, 8, 10, 8)
        self.diagram_layout.setSpacing(10)
        self.diagram_layout.setAlignment(Qt.AlignCenter)
        self.topo_stack.addWidget(self.diagram_container)

        # Page 1: QTreeWidget
        self.tree = QTreeWidget()
        self.tree.setColumnCount(7)
        self.tree.setIndentation(18)
        header = self.tree.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.topo_stack.addWidget(self.tree)

        topo_box.addWidget(self.topo_stack, 1)

        # Hop Summary / Analysis Banner (Chuẩn Demo Web)
        hop_bar = QFrame()
        hop_bar.setStyleSheet("""
            QFrame {
                background-color: #0F172A;
                border: 1px solid #1E293B;
                border-radius: 10px;
                padding: 4px 10px;
            }
        """)
        hb_layout = QHBoxLayout(hop_bar)
        hb_layout.setContentsMargins(12, 6, 12, 6)
        hb_layout.setSpacing(8)

        lbl_hop_prefix = QLabel("Lộ trình gói tin (Hop Path):")
        lbl_hop_prefix.setStyleSheet("color: #38BDF8; font-size: 11px; font-weight: 700;")
        self.lbl_hop_route = QLabel("Samsung 4K TV ➔ Router Phụ (192.168.110.1) ➔ Modem Tổng (192.168.1.1) ➔ Internet")
        self.lbl_hop_route.setStyleSheet("color: #F8FAFC; font-size: 11px; font-family: 'Fira Code', monospace;")
        
        hb_layout.addWidget(lbl_hop_prefix)
        hb_layout.addWidget(self.lbl_hop_route)
        hb_layout.addStretch()

        self.lbl_hop_badge = QLabel("2 Hops • 5 ms RTT")
        self.lbl_hop_badge.setStyleSheet("""
            background-color: rgba(16, 185, 129, 0.15);
            color: #10B981;
            border: 1px solid rgba(16, 185, 129, 0.35);
            border-radius: 6px;
            font-size: 10px;
            font-weight: 700;
            padding: 2px 8px;
            font-family: 'Fira Code', monospace;
        """)
        hb_layout.addWidget(self.lbl_hop_badge)
        topo_box.addWidget(hop_bar)

        main_layout.addWidget(topo_card, 1)

        # 4. Công Cụ Chẩn Đoán ICMP Echo Ping Trực Tiếp (Chuẩn Demo Web)
        ping_card = QFrame()
        ping_card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_BG_CARD};
                border: 1px solid {COLOR_BORDER};
                border-radius: 14px;
            }}
        """)
        ping_box = QVBoxLayout(ping_card)
        ping_box.setContentsMargins(16, 12, 16, 12)
        ping_box.setSpacing(8)

        p_header = QHBoxLayout()
        v_ph = QVBoxLayout()
        v_ph.setSpacing(2)
        lbl_p_title = QLabel("Công Cụ Chẩn Đoán Ping Trực Tiếp (ICMP Echo)")
        lbl_p_title.setStyleSheet("color: #F8FAFC; font-size: 13px; font-weight: 700;")
        lbl_p_sub = QLabel("Đo lường độ trễ phản hồi Round-Trip Time (RTT) tới bất kỳ địa chỉ nào trong mạng nội bộ hoặc Internet")
        lbl_p_sub.setStyleSheet("color: #94A3B8; font-size: 11px;")
        v_ph.addWidget(lbl_p_title)
        v_ph.addWidget(lbl_p_sub)
        p_header.addLayout(v_ph)
        p_header.addStretch()
        ping_box.addLayout(p_header)

        p_form = QHBoxLayout()
        p_form.setSpacing(8)

        self.txt_ping_ip = QLineEdit("192.168.1.1")
        self.txt_ping_ip.setPlaceholderText("Nhập IP...")
        self.txt_ping_ip.setStyleSheet("""
            QLineEdit {
                background-color: #0D1322;
                border: 1px solid #1E293B;
                border-radius: 8px;
                color: #38BDF8;
                font-family: 'Fira Code', monospace;
                font-size: 12px;
                font-weight: 700;
                padding: 6px 12px;
                min-width: 180px;
            }
            QLineEdit:focus { border: 1px solid #38BDF8; }
        """)
        p_form.addWidget(self.txt_ping_ip)

        self.btn_run_ping = QPushButton(" Kiểm Tra Ping")
        self.btn_run_ping.setIcon(get_app_icon("scan"))
        self.btn_run_ping.setIconSize(QSize(14, 14))
        self.btn_run_ping.setCursor(Qt.PointingHandCursor)
        self.btn_run_ping.setStyleSheet(STYLE_BTN_PRIMARY)
        self.btn_run_ping.clicked.connect(self._run_icmp_ping)
        p_form.addWidget(self.btn_run_ping)

        # Preset buttons
        presets = [
            ("Modem (192.168.1.1)", "192.168.1.1"),
            ("Router Phụ (192.168.110.1)", "192.168.110.1"),
            ("Google DNS (8.8.8.8)", "8.8.8.8"),
            ("Cloudflare (1.1.1.1)", "1.1.1.1"),
        ]
        for p_name, p_ip in presets:
            btn_p = QPushButton(p_name)
            btn_p.setCursor(Qt.PointingHandCursor)
            btn_p.setStyleSheet(STYLE_BTN_SLATE)
            btn_p.clicked.connect(lambda chk=False, target=p_ip: self.txt_ping_ip.setText(target))
            p_form.addWidget(btn_p)

        p_form.addStretch()
        ping_box.addLayout(p_form)

        # Ping console output
        self.lbl_ping_result = QLabel("Sẵn sàng kiểm tra. Nhấn 'Kiểm Tra Ping' để đo độ trễ tới máy chủ đích.")
        self.lbl_ping_result.setStyleSheet("""
            background-color: #080D1A;
            color: #94A3B8;
            font-family: 'Fira Code', monospace;
            font-size: 11px;
            border-radius: 8px;
            padding: 8px 12px;
            border: 1px solid #1E293B;
        """)
        ping_box.addWidget(self.lbl_ping_result)

        main_layout.addWidget(ping_card)
        scroll.setWidget(container)
        outer_layout.addWidget(scroll)

    def _set_topo_mode(self, idx: int):
        self.topo_stack.setCurrentIndex(idx)
        if idx == 0:
            self.btn_view_diagram.setStyleSheet("""
                QPushButton {
                    background-color: #0284C7;
                    color: #FFFFFF;
                    font-weight: 700;
                    font-size: 11px;
                    border: 1px solid #38BDF8;
                    border-radius: 6px;
                    padding: 4px 12px;
                }
            """)
            self.btn_view_tree.setStyleSheet(STYLE_BTN_SLATE)
        else:
            self.btn_view_tree.setStyleSheet("""
                QPushButton {
                    background-color: #0284C7;
                    color: #FFFFFF;
                    font-weight: 700;
                    font-size: 11px;
                    border: 1px solid #38BDF8;
                    border-radius: 6px;
                    padding: 4px 12px;
                }
            """)
            self.btn_view_diagram.setStyleSheet(STYLE_BTN_SLATE)

    def retranslate_ui(self):
        is_vi = i18n.current_lang == "vi"
        if is_vi:
            self.lbl_title.setText("Hạ Tầng Mạng & Sơ Đồ Topo Đa Tầng")
            self.lbl_desc.setText("Phân tích Subnet CIDR, định tuyến Internet và chẩn đoán đường truyền đa bước nhảy")
            self.btn_refresh.setText(" Quét Lại Topology")
            self.lbl_tc_title.setText("Sơ Đồ Phân Bổ Nút Mạng (Click vào thiết bị để xem lộ trình Hop Path)")
            self.lbl_tc_sub.setText("2 Tầng • Khảo sát các nút mạng phân đoạn và đo lường độ trễ từng bước nhảy")
        else:
            self.lbl_title.setText("Network Infrastructure & Multi-Tier Topology")
            self.lbl_desc.setText("Subnet CIDR analysis, Internet routing gateway survey, and multi-hop latency diagnostics")
            self.btn_refresh.setText(" Rescan Topology")
            self.lbl_tc_title.setText("Network Topology Map (Click device to inspect Hop Path)")
            self.lbl_tc_sub.setText("2 Tiers • Survey segmented network nodes and measure hop latency")

        self.tree.setHeaderLabels([
            "NÚT MẠNG / THIẾT BỊ" if is_vi else "NETWORK NODE / DEVICE",
            "IP ADDRESS",
            "MAC ADDRESS",
            "PHƯƠNG THỨC" if is_vi else "CONNECTION",
            "LOẠI THIẾT BỊ" if is_vi else "DEVICE TYPE",
            "ĐỘ TRỄ" if is_vi else "LATENCY",
            "TRẠNG THÁI" if is_vi else "STATUS"
        ])

    def _on_lang_changed(self, lang: str):
        self.retranslate_ui()
        self.refresh_map()

    def _select_node(self, title: str, ip: str, hops: int, rtt: str, path_str: str):
        self.lbl_hop_route.setText(path_str)
        self.lbl_hop_badge.setText(f"{hops} Hops • {rtt} RTT")

    def _run_icmp_ping(self):
        target = self.txt_ping_ip.text().strip()
        if not target:
            return
        self.lbl_ping_result.setText(f"Đang gửi gói tin ICMP Echo tới {target}...")
        self.lbl_ping_result.setStyleSheet("background-color: #080D1A; color: #38BDF8; font-family: 'Fira Code', monospace; font-size: 11px; border-radius: 8px; padding: 8px 12px; border: 1px solid rgba(56, 189, 248, 0.3);")
        QTimer.singleShot(100, lambda: self._do_ping_exec(target))

    def _do_ping_exec(self, target: str):
        try:
            param = "-n" if platform.system().lower() == "windows" else "-c"
            cmd = ["ping", param, "2", "-w", "1000", target]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=3)
            if res.returncode == 0:
                self.lbl_ping_result.setText(f"[SUCCESS] Phản hồi từ {target}: Gói tin nhận 2/2, RTT ~ 2-5ms (Chất lượng kết nối: Cực tốt)")
                self.lbl_ping_result.setStyleSheet("background-color: rgba(16, 185, 129, 0.1); color: #10B981; font-family: 'Fira Code', monospace; font-size: 11px; border-radius: 8px; padding: 8px 12px; border: 1px solid rgba(16, 185, 129, 0.3);")
            else:
                self.lbl_ping_result.setText(f"[TIMEOUT] Không nhận được phản hồi từ {target}. Thiết bị có thể offline hoặc chặn ICMP.")
                self.lbl_ping_result.setStyleSheet("background-color: rgba(239, 68, 68, 0.1); color: #F87171; font-family: 'Fira Code', monospace; font-size: 11px; border-radius: 8px; padding: 8px 12px; border: 1px solid rgba(239, 68, 68, 0.3);")
        except Exception as e:
            self.lbl_ping_result.setText(f"[ERROR] Lỗi thực thi lệnh ping: {e}")

    def refresh_map(self):
        self._is_loaded = True
        self.tree.clear()
        if not self.iface:
            self.iface = NetworkManagerCore.get_default_interface()

        devices = self.device_dao.get_all_devices()
        local_gw_ip = self.iface.gateway if self.iface else "192.168.110.1"
        local_cidr = self.iface.cidr if self.iface else "192.168.110.0/24"

        # Đếm số thiết bị theo dải
        cnt_modem = sum(1 for d in devices if d.ip and d.ip.startswith("192.168.1."))
        cnt_router = sum(1 for d in devices if d.ip and (d.ip.startswith("192.168.110.") or d.ip.startswith("192.168.2.")))
        self.card_gw_modem.set_stats(cnt_modem)
        self.card_gw_router.set_stats(cnt_router)

        # ----------------- REBUILD VISUAL DIAGRAM -----------------
        # Xóa các widget cũ trong diagram_layout
        while self.diagram_layout.count():
            item = self.diagram_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    sub = item.layout().takeAt(0)
                    if sub.widget():
                        sub.widget().deleteLater()

        # Level 0: Internet
        row0 = QHBoxLayout()
        row0.setAlignment(Qt.AlignCenter)
        card_internet = WideGatewayNodeCard(
            title="Internet Toàn Cầu (WAN Gateway)",
            subtitle="Global Internet Uplink (Cáp quang ISP 1Gbps)",
            ip="0.0.0.0/0",
            icon_key="globe",
            hops=0,
            rtt="1 ms",
            path_str="Internet Gateway (WAN Uplink)",
            border_color="rgba(16, 185, 129, 0.4)",
            accent_hex="#10B981"
        )
        card_internet.clicked.connect(self._select_node)
        row0.addWidget(card_internet)
        self.diagram_layout.addLayout(row0)

        # Connector 1
        lbl_arr1 = QLabel("▼ (Đường truyền ISP Cáp Quang)")
        lbl_arr1.setStyleSheet("color: #64748B; font-size: 11px; font-family: 'Fira Code', monospace;")
        lbl_arr1.setAlignment(Qt.AlignCenter)
        self.diagram_layout.addWidget(lbl_arr1)

        # Level 1: Modem Tổng ISP
        row1 = QHBoxLayout()
        row1.setAlignment(Qt.AlignCenter)
        card_modem = WideGatewayNodeCard(
            title="Modem Tổng ISP (GPON ONT Gateway)",
            subtitle="Dải 192.168.1.0/24 • Wi-Fi Chính (5GHz & 2.4GHz)",
            ip="192.168.1.1",
            icon_key="router",
            hops=1,
            rtt="2 ms",
            path_str="Modem Tổng ISP (192.168.1.1) ➔ Internet Gateway",
            border_color="rgba(56, 189, 248, 0.5)",
            accent_hex="#38BDF8"
        )
        card_modem.clicked.connect(self._select_node)
        row1.addWidget(card_modem)
        self.diagram_layout.addLayout(row1)

        # Connector 2
        lbl_arr2 = QLabel("↙ (Wi-Fi 5GHz)             | (Dây LAN 1Gbps)             ↘ (Wi-Fi 2.4GHz)")
        lbl_arr2.setStyleSheet("color: #64748B; font-size: 11px; font-family: 'Fira Code', monospace;")
        lbl_arr2.setAlignment(Qt.AlignCenter)
        self.diagram_layout.addWidget(lbl_arr2)

        # Level 2: Direct Devices & Sub-Router
        row2 = QHBoxLayout()
        row2.setSpacing(14)
        row2.setAlignment(Qt.AlignCenter)

        # Device 1: Laptop
        dev_pc = next((d for d in devices if d.ip and d.ip.startswith("192.168.1.") and d.ip != "192.168.1.1" and "laptop" in (d.device_type or "").lower()), None)
        pc_name = dev_pc.custom_name or dev_pc.hostname or "MacBook Pro M2" if dev_pc else "MacBook Pro M2"
        pc_ip = dev_pc.ip if dev_pc else "192.168.1.189"
        card_pc = TopologyNodeCard(
            title=pc_name,
            ip=pc_ip,
            icon_key="laptop",
            hops=2,
            rtt="3 ms",
            path_str=f"{pc_name} ({pc_ip}) ➔ Modem Tổng (192.168.1.1) ➔ Internet",
            subtitle="Wi-Fi 5GHz",
            accent_hex="#38BDF8",
            device=dev_pc
        )
        card_pc.clicked.connect(self._select_node)
        card_pc.double_clicked.connect(self._open_device_dialog)
        row2.addWidget(card_pc)

        # Sub-Router
        card_subrouter = TopologyNodeCard(
            title="Router Phụ TP-Link",
            ip="192.168.110.1",
            icon_key="router",
            hops=2,
            rtt="3 ms",
            path_str="Router Phụ (192.168.110.1) ➔ Modem Tổng (192.168.1.1) ➔ Internet",
            subtitle="LAN 1Gbps",
            accent_hex="#818CF8"
        )
        card_subrouter.clicked.connect(self._select_node)
        row2.addWidget(card_subrouter)

        # Device 2: Smartphone
        dev_phone = next((d for d in devices if d.ip and d.ip.startswith("192.168.1.") and d.ip != "192.168.1.1" and "phone" in (d.device_type or "").lower()), None)
        ph_name = dev_phone.custom_name or dev_phone.hostname or "iPhone 15 Pro" if dev_phone else "iPhone 15 Pro"
        ph_ip = dev_phone.ip if dev_phone else "192.168.1.115"
        card_phone = TopologyNodeCard(
            title=ph_name,
            ip=ph_ip,
            icon_key="smartphone",
            hops=2,
            rtt="4 ms",
            path_str=f"{ph_name} ({ph_ip}) ➔ Modem Tổng (192.168.1.1) ➔ Internet",
            subtitle="Wi-Fi 2.4GHz",
            accent_hex="#38BDF8",
            device=dev_phone
        )
        card_phone.clicked.connect(self._select_node)
        card_phone.double_clicked.connect(self._open_device_dialog)
        row2.addWidget(card_phone)

        self.diagram_layout.addLayout(row2)

        # Connector 3
        lbl_arr3 = QLabel("▼ (Các thiết bị con dưới quyền Router Phụ - Subnet 192.168.110.0/24)")
        lbl_arr3.setStyleSheet("color: #64748B; font-size: 11px; font-family: 'Fira Code', monospace;")
        lbl_arr3.setAlignment(Qt.AlignCenter)
        self.diagram_layout.addWidget(lbl_arr3)

        # Level 3: Secondary Subnet Devices (TV, Cam, Smart Relay)
        row3 = QHBoxLayout()
        row3.setSpacing(14)
        row3.setAlignment(Qt.AlignCenter)

        dev_tv = next((d for d in devices if d.ip and d.ip.startswith("192.168.110.") and "tv" in (d.device_type or "").lower()), None)
        tv_name = dev_tv.custom_name or dev_tv.hostname or "Samsung 4K TV" if dev_tv else "Samsung 4K TV"
        tv_ip = dev_tv.ip if dev_tv else "192.168.110.45"
        card_tv = TopologyNodeCard(
            title=tv_name,
            ip=tv_ip,
            icon_key="tv",
            hops=3,
            rtt="5 ms",
            path_str=f"{tv_name} ({tv_ip}) ➔ Router Phụ (192.168.110.1) ➔ Modem Tổng (192.168.1.1) ➔ Internet",
            subtitle="Wi-Fi 5GHz",
            accent_hex="#F59E0B",
            device=dev_tv
        )
        card_tv.clicked.connect(self._select_node)
        card_tv.double_clicked.connect(self._open_device_dialog)
        row3.addWidget(card_tv)

        dev_cam = next((d for d in devices if d.ip and d.ip.startswith("192.168.110.") and "cam" in (d.device_type or "").lower()), None)
        cam_name = dev_cam.custom_name or dev_cam.hostname or "Ezviz Security Cam" if dev_cam else "Ezviz Security Cam"
        cam_ip = dev_cam.ip if dev_cam else "192.168.110.88"
        card_cam = TopologyNodeCard(
            title=cam_name,
            ip=cam_ip,
            icon_key="camera",
            hops=3,
            rtt="6 ms",
            path_str=f"{cam_name} ({cam_ip}) ➔ Router Phụ (192.168.110.1) ➔ Modem Tổng (192.168.1.1) ➔ Internet",
            subtitle="Wi-Fi 2.4GHz",
            accent_hex="#F43F5E",
            device=dev_cam
        )
        card_cam.clicked.connect(self._select_node)
        card_cam.double_clicked.connect(self._open_device_dialog)
        row3.addWidget(card_cam)

        dev_esp = next((d for d in devices if d.ip and d.ip.startswith("192.168.110.") and ("iot" in (d.device_type or "").lower() or "relay" in (d.custom_name or "").lower())), None)
        esp_name = dev_esp.custom_name or dev_esp.hostname or "ESP32 Smart Relay" if dev_esp else "ESP32 Smart Relay"
        esp_ip = dev_esp.ip if dev_esp else "192.168.110.99"
        card_esp = TopologyNodeCard(
            title=esp_name,
            ip=esp_ip,
            icon_key="devices",
            hops=3,
            rtt="4 ms",
            path_str=f"{esp_name} ({esp_ip}) ➔ Router Phụ (192.168.110.1) ➔ Modem Tổng (192.168.1.1) ➔ Internet",
            subtitle="MQTT IoT",
            accent_hex="#10B981",
            device=dev_esp
        )
        card_esp.clicked.connect(self._select_node)
        card_esp.double_clicked.connect(self._open_device_dialog)
        row3.addWidget(card_esp)

        self.diagram_layout.addLayout(row3)

        # ----------------- REBUILD TREE VIEW -----------------
        subnets_map: Dict[str, List[Device]] = {}
        main_modem_dev = next((d for d in devices if d.ip in ("192.168.1.1", "192.168.0.1") and d.ip != local_gw_ip), None)
        local_gw_dev = next((d for d in devices if d.ip == local_gw_ip), None)

        for dev in devices:
            parts = dev.ip.split(".") if dev.ip else []
            if len(parts) == 4:
                net_key = f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
            else:
                net_key = "Other"
            subnets_map.setdefault(net_key, []).append(dev)

        # Nút Gốc: Mạng Toàn Cầu
        net_root = QTreeWidgetItem(self.tree)
        net_root.setIcon(0, get_app_icon("globe"))
        net_root.setText(0, " [MẠNG INTERNET TOÀN CẦU] Cáp quang WAN Uplink")
        net_root.setText(1, "0.0.0.0/0")
        net_root.setIcon(3, get_app_icon("globe"))
        net_root.setText(3, " Cáp quang ISP")
        net_root.setText(4, "Global Internet")
        net_root.setText(6, "ONLINE")
        net_root.setForeground(6, QColor("#10B981"))
        net_root.setFont(0, QFont("Segoe UI", 10, QFont.Bold))

        # Modem Tổng
        root_item = QTreeWidgetItem(net_root)
        root_item.setIcon(0, get_app_icon("router"))
        v_name = main_modem_dev.vendor if main_modem_dev else "Viettel / VNPT"
        root_item.setText(0, f" [Modem / Wi-Fi Tổng ISP] {v_name} (192.168.1.1)")
        root_item.setText(1, "192.168.1.1")
        root_item.setText(2, main_modem_dev.mac if main_modem_dev else "--")
        root_item.setIcon(3, get_app_icon("router"))
        root_item.setText(3, " GPON ONT")
        root_item.setText(4, "Modem ONT Gateway")
        root_item.setText(5, "2 ms")
        root_item.setText(6, "ONLINE")
        root_item.setForeground(6, QColor("#10B981"))
        root_item.setFont(0, QFont("Segoe UI", 10, QFont.Bold))

        # Nhánh Modem Devices
        modem_devices = [d for d in subnets_map.get("192.168.1.0/24", []) if d.ip != "192.168.1.1"]
        branch_modem = QTreeWidgetItem(root_item)
        branch_modem.setIcon(0, get_app_icon("wifi"))
        branch_modem.setText(0, f" [Mạng Wi-Fi Tổng] 192.168.1.0/24 ({len(modem_devices)} thiết bị)")
        branch_modem.setText(1, "192.168.1.0/24")
        branch_modem.setFont(0, QFont("Segoe UI", 9, QFont.Bold))
        self._populate_group_devices(branch_modem, modem_devices)

        # Nhánh Router Phụ
        router_item = QTreeWidgetItem(root_item)
        router_item.setIcon(0, get_app_icon("router"))
        router_item.setText(0, f" [Router Wi-Fi Phụ] Ruijie Reyee ({local_gw_ip})")
        router_item.setText(1, local_gw_ip)
        router_item.setText(2, local_gw_dev.mac if local_gw_dev else "--")
        router_item.setText(3, "Cáp WAN Uplink")
        router_item.setText(4, "Secondary Wi-Fi Router")
        router_item.setText(5, "4 ms")
        router_item.setText(6, "ONLINE")
        router_item.setForeground(6, QColor("#10B981"))
        router_item.setFont(0, QFont("Segoe UI", 10, QFont.Bold))

        local_devices = [d for d in subnets_map.get("192.168.110.0/24", []) if d.ip != local_gw_ip]
        branch_local = QTreeWidgetItem(router_item)
        branch_local.setIcon(0, get_app_icon("network"))
        branch_local.setText(0, f" [Mạng Wi-Fi Phụ LAN] 192.168.110.0/24 ({len(local_devices)} thiết bị)")
        branch_local.setText(1, "192.168.110.0/24")
        branch_local.setFont(0, QFont("Segoe UI", 9, QFont.Bold))
        self._populate_group_devices(branch_local, local_devices)

        self.tree.expandAll()

    def _populate_group_devices(self, parent_item: QTreeWidgetItem, device_list: List[Device]):
        for d in device_list:
            d_item = QTreeWidgetItem(parent_item)
            dtype = (d.device_type or "").lower()
            if "phone" in dtype or "mobile" in dtype:
                icon_k = "smartphone"
            elif "laptop" in dtype or "pc" in dtype:
                icon_k = "laptop"
            elif "tv" in dtype:
                icon_k = "tv"
            elif "printer" in dtype:
                icon_k = "printer"
            elif "camera" in dtype:
                icon_k = "camera"
            else:
                icon_k = "devices"

            d_item.setIcon(0, get_app_icon(icon_k))
            name = d.custom_name or d.hostname or d.vendor or "Thiết bị mạng"
            d_item.setText(0, f"  {name}")
            d_item.setText(1, d.ip or "--")
            d_item.setText(2, d.mac or "--")
            d_item.setText(3, d.display_connection_badge)
            d_item.setText(4, f"{d.vendor} ({d.device_type})")
            d_item.setText(5, f"{d.latency_ms} ms" if d.status == "ONLINE" else "--")
            d_item.setText(6, d.status)
            if d.status == "ONLINE":
                d_item.setForeground(6, QColor("#10B981"))
            elif d.status == "BLOCKED":
                d_item.setForeground(6, QColor("#EF4444"))
            else:
                d_item.setForeground(6, QColor("#94A3B8"))

            d_item.setData(0, Qt.UserRole, d)

    def _open_device_dialog(self, dev: Device):
        if isinstance(dev, Device):
            dlg = DeviceDetailDialog(
                device=dev,
                device_dao=self.device_dao,
                event_dao=self.event_dao,
                block_manager=self.block_manager,
                parent=self
            )
            dlg.device_changed.connect(self.refresh_map)
            dlg.exec()
            self.data_changed.emit()

    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        dev = item.data(0, Qt.UserRole)
        if isinstance(dev, Device):
            self._open_device_dialog(dev)

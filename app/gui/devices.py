"""
Màn hình Quản lý Danh sách Thiết bị (Connected Devices View) - Chuẩn Thiết kế Cyber Dark-Tech (Ảnh 2).
Song ngữ VI / EN, hỗ trợ phân đoạn Subnet, lọc trạng thái, tìm kiếm tức thì và chặn/bỏ chặn thiết bị.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, Signal, QSize
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
    COLOR_BG_CARD, COLOR_BORDER, COLOR_ACCENT_CYAN,
    COLOR_ACCENT_EMERALD, COLOR_ACCENT_ROSE, COLOR_ACCENT_AMBER,
    STYLE_BTN_PRIMARY, STYLE_BTN_SLATE, STYLE_BTN_BLOCK, STYLE_BTN_UNBLOCK
)

class DevicesView(QWidget):
    scan_requested = Signal()
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
        self.active_filter = "all"
        self.search_text = ""

        self._init_ui()
        self.retranslate_ui()
        self.load_devices()
        i18n.language_changed.connect(self._on_lang_changed)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 20, 24, 20)

        # 1. Header Toolbar (Title + Subtitle + Quét mạng ngay & Làm mới)
        top_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(3)
        self.lbl_title = QLabel("Danh Sách Thiết Bị Mạng")
        self.lbl_title.setStyleSheet("font-size: 22px; font-weight: 800; color: #F8FAFC; letter-spacing: 0.5px;")
        self.lbl_subtitle = QLabel("Quản lý trạng thái kết nối, gán nhãn nhận diện và kiểm soát truy cập thời gian thực")
        self.lbl_subtitle.setStyleSheet("color: #94A3B8; font-size: 13px;")
        title_box.addWidget(self.lbl_title)
        title_box.addWidget(self.lbl_subtitle)
        top_layout.addLayout(title_box)

        top_layout.addStretch()

        # Nút Quét mạng ngay
        self.btn_scan = QPushButton(" Quét mạng ngay")
        self.btn_scan.setIcon(get_app_icon("scan"))
        self.btn_scan.setIconSize(QSize(15, 15))
        self.btn_scan.setCursor(Qt.PointingHandCursor)
        self.btn_scan.setStyleSheet(STYLE_BTN_PRIMARY)
        self.btn_scan.clicked.connect(self.scan_requested.emit)
        top_layout.addWidget(self.btn_scan)

        # Nút Làm mới
        self.btn_refresh = QPushButton(" Làm mới")
        self.btn_refresh.setIcon(get_app_icon("refresh"))
        self.btn_refresh.setIconSize(QSize(15, 15))
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        self.btn_refresh.setStyleSheet(STYLE_BTN_SLATE)
        self.btn_refresh.clicked.connect(self.load_devices)
        top_layout.addWidget(self.btn_refresh)

        layout.addLayout(top_layout)

        # 2. Filter Bar: Subnet Pills + Search + Status Dropdown
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(8)

        self.btn_pill_all = QPushButton("Tất cả (7)")
        self.btn_pill_pri = QPushButton("192.168.1.x")
        self.btn_pill_sec = QPushButton("192.168.110.x")
        self.btn_pill_blk = QPushButton("Đang bị chặn")

        self.pill_buttons = [
            ("all", self.btn_pill_all),
            ("primary", self.btn_pill_pri),
            ("secondary", self.btn_pill_sec),
            ("blocked", self.btn_pill_blk),
        ]

        for k, btn in self.pill_buttons:
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, f_key=k: self._set_filter(f_key))
            filter_layout.addWidget(btn)

        filter_layout.addStretch()

        # Ô tìm kiếm
        self.txt_search = QLineEdit()
        self.txt_search.addAction(get_app_icon("search"), QLineEdit.LeadingPosition)
        self.txt_search.setFixedWidth(240)
        self.txt_search.setPlaceholderText("Tìm theo IP, MAC, Tên...")
        self.txt_search.setStyleSheet("""
            QLineEdit {
                background-color: #0D1322;
                border: 1px solid #1E293B;
                border-radius: 8px;
                color: #F8FAFC;
                padding: 6px 14px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #38BDF8;
            }
        """)
        self.txt_search.textChanged.connect(self._on_search_changed)
        filter_layout.addWidget(self.txt_search)

        # Dropdown trạng thái
        self.cb_status = QComboBox()
        self.cb_status.setStyleSheet("""
            QComboBox {
                background-color: #0D1322;
                border: 1px solid #1E293B;
                border-radius: 8px;
                color: #F8FAFC;
                padding: 6px 12px;
                min-width: 140px;
                font-size: 12px;
            }
            QComboBox::drop-down { border: none; }
        """)
        self.cb_status.addItems(["Tất cả trạng thái", "Chỉ Online", "Chỉ Offline", "Đang bị chặn"])
        self.cb_status.currentIndexChanged.connect(self.load_devices)
        filter_layout.addWidget(self.cb_status)

        layout.addLayout(filter_layout)
        self._update_pill_styles()

        # 3. Bảng thiết bị chuẩn 7 cột
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "THIẾT BỊ & TÊN",
            "IP & MAC",
            "NHÀ SẢN XUẤT",
            "DẢI MẠNG & KẾT NỐI",
            "ĐỘ TRỄ",
            "TRẠNG THÁI",
            "THAO TÁC"
        ])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setShowGrid(False)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)

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

    def _set_filter(self, filter_key: str):
        self.active_filter = filter_key
        self._update_pill_styles()
        self.load_devices()

    def _update_pill_styles(self):
        for k, btn in self.pill_buttons:
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
        self.load_devices()

    def _on_lang_changed(self, lang: str):
        self.retranslate_ui()
        self.load_devices()

    def retranslate_ui(self):
        is_vi = i18n.current_lang == "vi"
        if is_vi:
            self.lbl_title.setText("Danh Sách Thiết Bị Mạng")
            self.lbl_subtitle.setText("Quản lý trạng thái kết nối, gán nhãn nhận diện và kiểm soát truy cập thời gian thực")
            self.btn_scan.setText(" Quét mạng ngay")
            self.btn_refresh.setText(" Làm mới")
            self.btn_pill_pri.setText("192.168.1.x")
            self.btn_pill_sec.setText("192.168.110.x")
            self.btn_pill_blk.setText("Đang bị chặn")
            self.txt_search.setPlaceholderText("Tìm theo IP, MAC, Tên...")
            self.cb_status.setItemText(0, "Tất cả trạng thái")
            self.cb_status.setItemText(1, "Chỉ Online")
            self.cb_status.setItemText(2, "Chỉ Offline")
            self.cb_status.setItemText(3, "Đang bị chặn")
        else:
            self.lbl_title.setText("Connected Network Devices")
            self.lbl_subtitle.setText("Manage device connection states, identity tagging, and real-time hardware access control")
            self.btn_scan.setText(" Scan Network")
            self.btn_refresh.setText(" Refresh")
            self.btn_pill_pri.setText("192.168.1.x")
            self.btn_pill_sec.setText("192.168.110.x")
            self.btn_pill_blk.setText("Blocked")
            self.txt_search.setPlaceholderText("Search by IP, MAC, Name...")
            self.cb_status.setItemText(0, "All Statuses")
            self.cb_status.setItemText(1, "Online Only")
            self.cb_status.setItemText(2, "Offline Only")
            self.cb_status.setItemText(3, "Blocked Only")

        self.table.setHorizontalHeaderLabels([
            "THIẾT BỊ & TÊN" if is_vi else "DEVICE & NAME",
            "IP & MAC",
            "NHÀ SẢN XUẤT" if is_vi else "VENDOR",
            "DẢI MẠNG & KẾT NỐI" if is_vi else "NETWORK & CONN",
            "ĐỘ TRỄ" if is_vi else "LATENCY",
            "TRẠNG THÁI" if is_vi else "STATUS",
            "THAO TÁC" if is_vi else "ACTIONS"
        ])

    def load_devices(self):
        devices = self.device_dao.get_all_devices()
        total_cnt = len(devices)
        self.btn_pill_all.setText(f"Tất cả ({total_cnt})" if i18n.current_lang == "vi" else f"All ({total_cnt})")

        # Áp dụng bộ lọc
        filtered: List[Device] = []
        status_idx = self.cb_status.currentIndex()

        for d in devices:
            # 1. Subnet / Blocked Pill Filter
            if self.active_filter == "primary" and not (d.ip and d.ip.startswith("192.168.1.")):
                continue
            if self.active_filter == "secondary" and not (d.ip and (d.ip.startswith("192.168.110.") or d.ip.startswith("192.168.2."))):
                continue
            if self.active_filter == "blocked" and d.status != "BLOCKED":
                continue

            # 2. Status Dropdown
            if status_idx == 1 and d.status != "ONLINE":
                continue
            if status_idx == 2 and d.status != "OFFLINE":
                continue
            if status_idx == 3 and d.status != "BLOCKED":
                continue

            # 3. Search text
            if self.search_text:
                haystack = f"{d.custom_name or ''} {d.hostname or ''} {d.ip or ''} {d.mac or ''} {d.vendor or ''}".lower()
                if self.search_text not in haystack:
                    continue

            filtered.append(d)

        self.devices_cache = filtered
        self.table.setRowCount(len(filtered))

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

        is_vi = i18n.current_lang == "vi"

        for row, dev in enumerate(filtered):
            self.table.setRowHeight(row, 52)

            # Cột 0: THIẾT BỊ & TÊN (Icon trong khung vuông bo tròn 36x36)
            icon_key = type_icons.get(dev.device_type, "devices")
            name = dev.custom_name or dev.hostname or dev.vendor or "Thiết bị mạng"
            dev_type = dev.device_type or "PC / Laptop"

            c_dev = QWidget()
            c_dev_layout = QHBoxLayout(c_dev)
            c_dev_layout.setContentsMargins(6, 4, 6, 4)
            c_dev_layout.setSpacing(10)

            icon_box = QFrame()
            icon_box.setFixedSize(36, 36)
            icon_box.setStyleSheet("""
                QFrame {
                    background-color: #121E36;
                    border: 1px solid rgba(56, 189, 248, 0.2);
                    border-radius: 8px;
                }
            """)
            ib_layout = QVBoxLayout(icon_box)
            ib_layout.setContentsMargins(0, 0, 0, 0)
            ib_layout.setAlignment(Qt.AlignCenter)
            lbl_icon = QLabel()
            lbl_icon.setPixmap(get_app_icon(icon_key).pixmap(20, 20))
            lbl_icon.setAlignment(Qt.AlignCenter)
            ib_layout.addWidget(lbl_icon)

            text_box = QVBoxLayout()
            text_box.setSpacing(1)
            text_box.setContentsMargins(0, 0, 0, 0)
            lbl_n = QLabel(f"<b>{name}</b>")
            lbl_n.setStyleSheet("color: #F8FAFC; font-size: 12px; background: transparent;")
            lbl_t = QLabel(dev_type)
            lbl_t.setStyleSheet("color: #94A3B8; font-size: 10px; background: transparent;")
            text_box.addWidget(lbl_n)
            text_box.addWidget(lbl_t)

            c_dev_layout.addWidget(icon_box)
            c_dev_layout.addLayout(text_box)
            c_dev_layout.addStretch()
            self.table.setCellWidget(row, 0, c_dev)

            # Cột 1: IP & MAC (2 dòng: IP Cyan ở trên, MAC Slate ở dưới)
            c_ipmac = QWidget()
            c_ipmac_layout = QVBoxLayout(c_ipmac)
            c_ipmac_layout.setContentsMargins(6, 6, 6, 6)
            c_ipmac_layout.setSpacing(2)
            lbl_ip = QLabel(dev.ip or "--")
            lbl_ip.setStyleSheet("color: #38BDF8; font-size: 12px; font-weight: 700; font-family: 'Fira Code', monospace; background: transparent;")
            lbl_mac = QLabel(dev.mac or "--")
            lbl_mac.setStyleSheet("color: #94A3B8; font-size: 10px; font-family: 'Fira Code', monospace; background: transparent;")
            c_ipmac_layout.addWidget(lbl_ip)
            c_ipmac_layout.addWidget(lbl_mac)
            self.table.setCellWidget(row, 1, c_ipmac)

            # Cột 2: NHÀ SẢN XUẤT
            item_vendor = QTableWidgetItem(dev.vendor or "Unknown")
            item_vendor.setForeground(QColor("#CBD5E1"))
            self.table.setItem(row, 2, item_vendor)

            # Cột 3: DẢI MẠNG & KẾT NỐI (2 dòng: Tên dải + Phương thức Wi-Fi 5GHz/LAN)
            c_net = QWidget()
            c_net_layout = QVBoxLayout(c_net)
            c_net_layout.setContentsMargins(6, 6, 6, 6)
            c_net_layout.setSpacing(2)
            net_badge = dev.display_network_badge
            conn_badge = dev.display_connection_badge
            lbl_net_name = QLabel(net_badge)
            lbl_net_name.setStyleSheet("color: #38BDF8; font-size: 11px; font-weight: 600; background: transparent;")
            lbl_net_conn = QLabel(conn_badge)
            lbl_net_conn.setStyleSheet("color: #94A3B8; font-size: 10px; background: transparent;")
            c_net_layout.addWidget(lbl_net_name)
            c_net_layout.addWidget(lbl_net_conn)
            self.table.setCellWidget(row, 3, c_net)

            # Cột 4: ĐỘ TRỄ
            item_lat = QTableWidgetItem(f"● {dev.latency_ms} ms" if dev.status == "ONLINE" else "--")
            item_lat.setFont(QFont("Fira Code", 10, QFont.Bold))
            item_lat.setForeground(QColor("#10B981" if dev.status == "ONLINE" else "#64748B"))
            self.table.setItem(row, 4, item_lat)

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
            c_status_layout.setContentsMargins(4, 10, 4, 10)
            c_status_layout.addWidget(lbl_status)
            self.table.setCellWidget(row, 5, c_status)

            # Cột 6: THAO TÁC (Nút Chi tiết + Nút Chặn dạng Pill đỏ)
            is_blocked = dev.status == "BLOCKED"
            c_act = QWidget()
            c_act_layout = QHBoxLayout(c_act)
            c_act_layout.setContentsMargins(4, 4, 4, 4)
            c_act_layout.setSpacing(6)

            btn_detail = QPushButton("Chi tiết" if is_vi else "Details")
            btn_detail.setIcon(get_app_icon("info"))
            btn_detail.setIconSize(QSize(13, 13))
            btn_detail.setCursor(Qt.PointingHandCursor)
            btn_detail.setStyleSheet(STYLE_BTN_SLATE)
            btn_detail.clicked.connect(lambda chk=False, d=dev: self._open_detail(d))

            btn_block = QPushButton(("Bỏ chặn" if is_vi else "Unblock") if is_blocked else ("Chặn" if is_vi else "Block"))
            btn_block.setIcon(get_app_icon("shield_check" if is_blocked else "shield_block"))
            btn_block.setIconSize(QSize(13, 13))
            btn_block.setCursor(Qt.PointingHandCursor)
            btn_block.setStyleSheet(STYLE_BTN_UNBLOCK if is_blocked else STYLE_BTN_BLOCK)
            btn_block.clicked.connect(lambda chk=False, d=dev: self._toggle_block(d))

            c_act_layout.addWidget(btn_detail)
            c_act_layout.addWidget(btn_block)
            self.table.setCellWidget(row, 6, c_act)

    def _open_detail(self, dev: Device):
        dlg = DeviceDetailDialog(
            device=dev,
            device_dao=self.device_dao,
            event_dao=self.event_dao,
            block_manager=self.block_manager,
            parent=self
        )
        dlg.device_changed.connect(self.load_devices)
        dlg.exec()

    def _toggle_block(self, dev: Device):
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
                ok, msg = self.block_manager.block_device(mac=dev.mac, ip=dev.ip, reason="Chặn qua danh sách thiết bị")
                if ok:
                    QMessageBox.information(self, "Đã Chặn", f"Đã gửi lệnh chặn thiết bị {target_name} ({dev.mac}) thành công.")
                else:
                    QMessageBox.warning(self, "Thất Bại", f"Không thể chặn thiết bị: {msg}")

        self.load_devices()
        self.data_changed.emit()

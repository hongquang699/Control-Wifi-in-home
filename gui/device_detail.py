"""
Hộp thoại xem và chỉnh sửa chi tiết thiết bị (Device Detail Dialog) - Song ngữ VI / EN.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QFrame, QGroupBox, QScrollArea, QWidget
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont
from typing import Optional
from core.device import Device
from database.devices import DeviceDAO
from database.events import EventDAO
from security.blocker import BlockManager
from core.i18n import t, i18n

class DeviceDetailDialog(QDialog):
    device_changed = Signal()

    def __init__(
        self,
        device: Device,
        device_dao: DeviceDAO,
        event_dao: EventDAO,
        block_manager: BlockManager,
        parent=None
    ):
        super().__init__(parent)
        self.device = device
        self.device_dao = device_dao
        self.event_dao = event_dao
        self.block_manager = block_manager
        
        self.setWindowTitle(t("modal_title", ip=self.device.ip, mac=self.device.mac))
        self.resize(700, 660)
        self.setMinimumSize(580, 480)
        self.setStyleSheet("""
            QDialog {
                background-color: #080D1A;
                color: #F8FAFC;
            }
            QLabel {
                color: #E2E8F0;
                font-size: 13px;
                border: none;
                background: transparent;
            }
            QLineEdit, QComboBox {
                background-color: #101B33;
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 8px;
                color: #F8FAFC;
                padding: 6px 12px;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #6366F1;
                background-color: #152244;
            }
            QGroupBox {
                background-color: #0D162B;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 10px;
                margin-top: 14px;
                font-weight: 700;
                font-size: 13px;
                color: #F8FAFC;
                padding-top: 14px;
                padding-bottom: 12px;
                padding-left: 12px;
                padding-right: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 14px;
                top: 0px;
                padding: 2px 8px;
                background-color: #1E293B;
                border-radius: 4px;
                color: #38BDF8;
                font-size: 11px;
                font-weight: bold;
            }
        """)
        self._init_ui()

    def _init_ui(self):
        main_dialog_layout = QVBoxLayout(self)
        main_dialog_layout.setContentsMargins(0, 0, 0, 0)
        main_dialog_layout.setSpacing(0)

        # 0. Vùng cuộn QScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("background-color: transparent; border: none;")

        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background-color: #080D1A;")
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(12)

        # 1. Thông tin tổng quan
        self.info_box = QGroupBox(t("sec_ident"))
        info_layout = QVBoxLayout(self.info_box)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel(f"<b>{t('col_ip')}:</b> {self.device.ip}"))
        row1.addWidget(QLabel(f"<b>{t('col_mac')}:</b> {self.device.mac}"))
        info_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel(f"<b>{t('col_vendor')}:</b> {self.device.vendor}"))
        status_color = "#10B981" if self.device.status == "ONLINE" else "#94A3B8"
        status_text = t("val_online") if self.device.status == "ONLINE" else t("val_offline")
        lbl_status = QLabel(f"<b>{t('col_status')}:</b> <span style='color:{status_color}'>{status_text}</span>")
        row2.addWidget(lbl_status)
        info_layout.addLayout(row2)

        row3 = QHBoxLayout()
        row3.addWidget(QLabel(f"<b>Hostname:</b> {self.device.hostname or 'N/A'}"))
        row3.addWidget(QLabel(f"<b>{t('col_latency')}:</b> {self.device.latency_ms} ms"))
        info_layout.addLayout(row3)

        row4 = QHBoxLayout()
        row4.addWidget(QLabel(f"<b>First seen:</b> {self.device.first_seen}"))
        row4.addWidget(QLabel(f"<b>Last seen:</b> {self.device.last_seen}"))
        info_layout.addLayout(row4)

        layout.addWidget(self.info_box)

        # 1.5 Thông tin Kết nối & Lộ trình Internet
        self.route_box = QGroupBox(t("sec_network_route"))
        route_layout = QVBoxLayout(self.route_box)
        route_layout.setSpacing(10)

        from core.topology import NetworkTopologyHelper
        net_info = NetworkTopologyHelper.get_network_info(self.device.ip)

        r_row1 = QHBoxLayout()
        lbl_net = QLabel(f"<b>{t('lbl_connected_network')}</b> <span style='color:#38BDF8; font-weight:bold;'>{self.device.display_network_name}</span>")
        lbl_gw = QLabel(f"<b>{t('lbl_gateway')}</b> {net_info['gateway_ip']} ({net_info['subnet_cidr']})")
        r_row1.addWidget(lbl_net)
        r_row1.addWidget(lbl_gw)
        route_layout.addLayout(r_row1)

        r_row2 = QHBoxLayout()
        r_row2.addWidget(QLabel(f"<b>{t('lbl_conn_type')}</b>"))
        self.cb_conn_type = QComboBox()
        self.cb_conn_type.addItems(["Wi-Fi", "Ethernet", "WAN"])
        current_conn = (self.device.connection_type or "Wi-Fi").strip()
        if current_conn in ["Wi-Fi", "Ethernet", "WAN"]:
            self.cb_conn_type.setCurrentText(current_conn)
        r_row2.addWidget(self.cb_conn_type)

        status_internet_str = t("val_internet_blocked") if self.device.blocked else t("val_internet_allowed")
        lbl_net_status = QLabel(f"<b>{t('lbl_internet_status')}</b> {status_internet_str}")
        r_row2.addWidget(lbl_net_status)
        route_layout.addLayout(r_row2)

        # Sơ đồ lộ trình Internet (Visual Breadcrumb Flow)
        route_hops = NetworkTopologyHelper.get_internet_route(
            ip=self.device.ip,
            connection_type=self.device.connection_type,
            custom_name=self.device.display_name,
            blocked=self.device.blocked
        )

        flow_box = QFrame()
        flow_box.setStyleSheet("""
            QFrame {
                background-color: #0B1120;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px;
                padding: 4px;
            }
        """)
        flow_layout = QHBoxLayout(flow_box)
        flow_layout.setContentsMargins(6, 6, 6, 6)
        flow_layout.setSpacing(6)

        for i, hop in enumerate(route_hops):
            node_lbl = QLabel(f"<b>{hop['icon']} {hop['name']}</b><br><span style='font-size:11px; color:#94A3B8;'>{hop['ip']} ({hop['medium']})</span>")
            node_lbl.setAlignment(Qt.AlignCenter)
            is_blk = (hop['status'] == 'BLOCKED')
            bg_col = 'rgba(239, 68, 68, 0.15)' if is_blk else 'rgba(99, 102, 241, 0.12)'
            border_col = '#EF4444' if is_blk else 'rgba(99, 102, 241, 0.4)'
            node_lbl.setStyleSheet(f"""
                QLabel {{
                    background-color: {bg_col};
                    border: 1px solid {border_col};
                    border-radius: 6px;
                    padding: 5px 8px;
                    color: #F8FAFC;
                }}
            """)
            flow_layout.addWidget(node_lbl)

            if i < len(route_hops) - 1:
                arrow = QLabel("➔" if not is_blk else "✖")
                arrow.setAlignment(Qt.AlignCenter)
                arrow.setStyleSheet("font-size: 15px; color: #6366F1; font-weight: bold;")
                flow_layout.addWidget(arrow)

        route_layout.addWidget(QLabel(f"<b>{t('lbl_internet_route')}</b>"))
        route_layout.addWidget(flow_box)
        layout.addWidget(self.route_box)

        # 2. Chỉnh sửa tên gợi nhớ và loại thiết bị
        self.edit_box = QGroupBox(t("sec_admin"))
        edit_layout = QVBoxLayout(self.edit_box)

        alias_layout = QHBoxLayout()
        alias_layout.addWidget(QLabel(t("lbl_alias")))
        self.txt_custom_name = QLineEdit(self.device.custom_name)
        self.txt_custom_name.setPlaceholderText(t("alias_placeholder"))
        alias_layout.addWidget(self.txt_custom_name)
        edit_layout.addLayout(alias_layout)

        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel(t("lbl_device_type")))
        self.cb_device_type = QComboBox()
        self.cb_device_type.addItems(["Unknown", "PC", "Phone", "Router", "IoT", "Printer", "Server"])
        if self.device.device_type in ["Unknown", "PC", "Phone", "Router", "IoT", "Printer", "Server"]:
            self.cb_device_type.setCurrentText(self.device.device_type)
        type_layout.addWidget(self.cb_device_type)
        
        self.btn_save_alias = QPushButton(t("btn_save_changes"))
        self.btn_save_alias.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4F46E5, stop:1 #06B6D4);
                color: white;
                font-weight: 600;
                font-size: 13px;
                padding: 7px 18px;
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
        self.btn_save_alias.clicked.connect(self._save_changes)
        type_layout.addWidget(self.btn_save_alias)
        edit_layout.addLayout(type_layout)

        layout.addWidget(self.edit_box)

        # 3. Lịch sử sự kiện riêng của thiết bị
        self.hist_box = QGroupBox(t("sec_history"))
        hist_layout = QVBoxLayout(self.hist_box)
        
        self.table_history = QTableWidget()
        self.table_history.setColumnCount(3)
        self.table_history.setHorizontalHeaderLabels([t("col_time"), t("col_event_type"), t("col_desc")])
        self.table_history.setFixedHeight(120)
        self.table_history.setShowGrid(False)
        self.table_history.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table_history.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table_history.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.table_history.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table_history.setColumnWidth(0, 140)
        self.table_history.setColumnWidth(1, 110)
        self.table_history.verticalHeader().setVisible(False)
        self.table_history.setEditTriggers(QTableWidget.NoEditTriggers)
        hist_layout.addWidget(self.table_history)
        layout.addWidget(self.hist_box)
        self._load_history()

        # Kết thúc scroll area
        scroll.setWidget(scroll_widget)
        main_dialog_layout.addWidget(scroll, 1)

        # 4. Action Buttons cố định dưới đáy (Bottom Bar)
        bottom_bar = QFrame()
        bottom_bar.setStyleSheet("""
            QFrame {
                background-color: #0A1224;
                border-top: 1px solid rgba(255, 255, 255, 0.08);
            }
        """)
        action_layout = QHBoxLayout(bottom_bar)
        action_layout.setContentsMargins(18, 12, 18, 12)
        action_layout.setSpacing(12)
        
        self.btn_block = QPushButton()
        self._update_block_btn_ui()
        self.btn_block.clicked.connect(self._toggle_block)
        action_layout.addWidget(self.btn_block)

        action_layout.addStretch()

        self.btn_close = QPushButton(t("btn_close"))
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: #1E293B;
                color: #E2E8F0;
                font-weight: 600;
                padding: 8px 22px;
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            QPushButton:hover {
                background-color: #334155;
                color: #FFFFFF;
            }
        """)
        self.btn_close.clicked.connect(self.accept)
        action_layout.addWidget(self.btn_close)

        main_dialog_layout.addWidget(bottom_bar)

    def _update_block_btn_ui(self):
        if self.device.blocked:
            self.btn_block.setText(f"  {t('btn_toggle_block_no')}")
            self.btn_block.setStyleSheet("""
                QPushButton {
                    background-color: #065F46;
                    color: #A7F3D0;
                    border: 1px solid #10B981;
                    font-weight: 700;
                    padding: 8px 20px;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background-color: #047857;
                    color: #FFFFFF;
                }
            """)
        else:
            self.btn_block.setText(f"  {t('btn_toggle_block_yes')}")
            self.btn_block.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #EF4444, stop:1 #DC2626);
                    color: white;
                    font-weight: 700;
                    padding: 8px 20px;
                    border-radius: 8px;
                    border: none;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #DC2626, stop:1 #B91C1C);
                }
            """)

    def _load_history(self):
        events = self.event_dao.get_events_for_mac(self.device.mac)
        self.table_history.setRowCount(len(events))
        for r, ev in enumerate(events):
            self.table_history.setRowHeight(r, 28)
            item_ts = QTableWidgetItem(ev["timestamp"])
            item_type = QTableWidgetItem(ev["event_type"])
            item_desc = QTableWidgetItem(ev["description"])
            for it in (item_ts, item_type, item_desc):
                it.setFont(QFont("Segoe UI", 9))
            self.table_history.setItem(r, 0, item_ts)
            self.table_history.setItem(r, 1, item_type)
            self.table_history.setItem(r, 2, item_desc)

    def _save_changes(self):
        new_name = self.txt_custom_name.text().strip()
        new_type = self.cb_device_type.currentText()
        new_conn = self.cb_conn_type.currentText()
        self.device_dao.update_custom_name(self.device.mac, new_name, new_type)
        self.device_dao.update_connection_info(self.device.mac, new_conn)
        self.device.custom_name = new_name
        self.device.device_type = new_type
        self.device.connection_type = new_conn
        self.device_changed.emit()
        QMessageBox.information(self, "Success", t("save_success"))

    def _toggle_block(self):
        if self.device.blocked:
            reply = QMessageBox.question(
                self, t("confirm_unblock_title"),
                t("confirm_unblock_msg", mac=self.device.mac, ip=self.device.ip),
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                success, msg = self.block_manager.unblock_device(self.device.mac, self.device.ip)
                if success:
                    self.device.blocked = False
                    self._update_block_btn_ui()
                    self._load_history()
                    self.device_changed.emit()
                    QMessageBox.information(self, "Success", msg)
                else:
                    QMessageBox.warning(self, "Error", msg)
        else:
            reply = QMessageBox.warning(
                self, t("confirm_block_title"),
                t("confirm_block_msg", name=self.device.display_name, mac=self.device.mac, ip=self.device.ip),
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                success, msg = self.block_manager.block_device(
                    self.device.mac,
                    ip=self.device.ip,
                    reason=f"Blocked by Admin: {self.device.display_name}"
                )
                if success:
                    self.device.blocked = True
                    self._update_block_btn_ui()
                    self._load_history()
                    self.device_changed.emit()
                    QMessageBox.information(self, "Success", msg)
                else:
                    QMessageBox.warning(self, "Error", msg)

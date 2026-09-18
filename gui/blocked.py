"""
Màn hình Quản lý Thiết bị Bị chặn (Blocked Devices View) - Song ngữ VI / EN.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QGroupBox, QLineEdit
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont
from core.device import Device
from database.devices import DeviceDAO
from database.events import EventDAO
from security.blocker import BlockManager
from utils.validators import is_valid_mac, is_valid_ipv4, normalize_mac
from core.i18n import t, i18n

class BlockedView(QWidget):
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
        self._init_ui()
        self.retranslate_ui()
        self.load_blocked_devices()
        i18n.language_changed.connect(self._on_lang_changed)

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
        self.lbl_subtitle = QLabel("...")
        self.lbl_subtitle.setStyleSheet("color: #94A3B8; font-size: 13px;")
        title_box.addWidget(self.lbl_title)
        title_box.addWidget(self.lbl_subtitle)
        header_layout.addLayout(title_box)
        layout.addLayout(header_layout)

        # 2. Form Chặn thủ công bằng MAC/IP
        self.manual_box = QGroupBox()
        m_layout = QHBoxLayout(self.manual_box)
        m_layout.setContentsMargins(14, 16, 14, 14)
        m_layout.setSpacing(10)

        self.txt_manual_mac = QLineEdit()
        m_layout.addWidget(self.txt_manual_mac)

        self.txt_manual_ip = QLineEdit()
        m_layout.addWidget(self.txt_manual_ip)

        self.txt_manual_reason = QLineEdit()
        m_layout.addWidget(self.txt_manual_reason)

        self.btn_manual_block = QPushButton()
        self.btn_manual_block.setCursor(Qt.PointingHandCursor)
        self.btn_manual_block.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #E11D48, stop:1 #F43F5E);
                color: white;
                font-weight: bold;
                padding: 8px 18px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover { background-color: #BE123C; }
        """)
        self.btn_manual_block.clicked.connect(self._manual_block)
        m_layout.addWidget(self.btn_manual_block)

        layout.addWidget(self.manual_box)

        # 3. Bảng thiết bị đang bị chặn
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setShowGrid(False)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        header.setSectionResizeMode(6, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(1, 130)
        self.table.setColumnWidth(5, 140)
        self.table.setColumnWidth(6, 120)
        layout.addWidget(self.table)

    def retranslate_ui(self):
        self.lbl_title.setText(t("blk_title"))
        self.manual_box.setTitle(t("blk_manual_title"))
        self.txt_manual_mac.setPlaceholderText(t("blk_manual_mac"))
        self.txt_manual_ip.setPlaceholderText(t("blk_manual_ip"))
        self.txt_manual_reason.setPlaceholderText(t("blk_manual_reason"))
        self.btn_manual_block.setText(f"  {t('btn_add_blacklist')}")

        self.table.setHorizontalHeaderLabels([
            t("col_mac"), t("col_ip"), t("col_name"), t("col_vendor"),
            "Reason", "Last Seen", t("col_actions")
        ])

    def _on_lang_changed(self, lang: str):
        self.retranslate_ui()
        self.load_blocked_devices()

    def load_blocked_devices(self):
        blocked_devices = self.device_dao.get_all_devices(blocked_filter=True)
        self.table.setRowCount(len(blocked_devices))
        self.lbl_subtitle.setText(t("blk_subtitle", count=len(blocked_devices)))

        for row, dev in enumerate(blocked_devices):
            self.table.setRowHeight(row, 44)
            item_mac = QTableWidgetItem(dev.mac)
            item_mac.setFont(QFont("Consolas", 9, QFont.Bold))
            item_mac.setForeground(QColor("#F43F5E"))
            self.table.setItem(row, 0, item_mac)

            self.table.setItem(row, 1, QTableWidgetItem(dev.ip))
            self.table.setItem(row, 2, QTableWidgetItem(dev.display_name))
            self.table.setItem(row, 3, QTableWidgetItem(dev.vendor))
            self.table.setItem(row, 4, QTableWidgetItem(dev.block_reason or "Blocked by Admin"))
            self.table.setItem(row, 5, QTableWidgetItem(dev.last_seen))

            btn_unblock = QPushButton(f"  {t('btn_unblock')}")
            btn_unblock.setCursor(Qt.PointingHandCursor)
            btn_unblock.setStyleSheet("""
                QPushButton {
                    background-color: rgba(16, 185, 129, 0.15);
                    color: #10B981;
                    border: 1px solid rgba(16, 185, 129, 0.35);
                    font-weight: 600;
                    border-radius: 6px;
                    padding: 5px 14px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #10B981;
                    color: white;
                }
            """)
            btn_unblock.clicked.connect(lambda checked=False, d=dev: self._unblock_device(d))
            self.table.setCellWidget(row, 6, btn_unblock)

    def _manual_block(self):
        mac = self.txt_manual_mac.text().strip()
        ip = self.txt_manual_ip.text().strip()
        reason = self.txt_manual_reason.text().strip() or "Manual Block"

        if not is_valid_mac(mac):
            QMessageBox.warning(self, "Error", t("err_invalid_mac"))
            return

        if ip and not is_valid_ipv4(ip):
            QMessageBox.warning(self, "Error", t("err_invalid_ip"))
            return

        mac_norm = normalize_mac(mac)
        reply = QMessageBox.warning(
            self, t("confirm_block_title"),
            t("confirm_block_msg", name=mac_norm, mac=mac_norm, ip=ip or "N/A"),
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            existing = self.device_dao.get_device_by_mac(mac_norm)
            if not existing:
                dev = Device(ip=ip or "0.0.0.0", mac=mac_norm, blocked=True, block_reason=reason)
                self.device_dao.upsert_device(dev)

            success, msg = self.block_manager.block_device(mac_norm, ip=ip, reason=reason)
            if success:
                self.txt_manual_mac.clear()
                self.txt_manual_ip.clear()
                self.txt_manual_reason.clear()
                self.load_blocked_devices()
                self.data_changed.emit()
                QMessageBox.information(self, "Success", msg)
            else:
                QMessageBox.warning(self, "Error", msg)

    def _unblock_device(self, dev: Device):
        reply = QMessageBox.question(
            self, t("confirm_unblock_title"),
            t("confirm_unblock_msg", mac=dev.mac, ip=dev.ip),
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            success, msg = self.block_manager.unblock_device(dev.mac, dev.ip)
            if success:
                self.load_blocked_devices()
                self.data_changed.emit()
                QMessageBox.information(self, "Success", msg)
            else:
                QMessageBox.warning(self, "Error", msg)

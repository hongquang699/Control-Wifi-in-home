"""
Màn hình Cấu hình Hệ thống (Settings View) - Thiết kế Card hiện đại, hỗ trợ cuộn mượt mà & Song ngữ VI / EN.
"""

import json
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QCheckBox, QFrame, QMessageBox,
    QFileDialog, QSpinBox, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QCursor
from security.blocker import BlockManager
from core.logger import logger
from core.i18n import t, i18n
from gui.theme import (
    COLOR_BG_CARD, COLOR_BG_INPUT, COLOR_BORDER,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    COLOR_ACCENT_INDIGO, COLOR_ACCENT_CYAN, COLOR_ACCENT_EMERALD, COLOR_ACCENT_AMBER, COLOR_ACCENT_ROSE
)

STYLE_COMBOBOX = f"""
    QComboBox {{
        background-color: {COLOR_BG_INPUT};
        border: 1px solid #1E293B;
        border-radius: 8px;
        color: {COLOR_TEXT_PRIMARY};
        padding: 6px 14px;
        font-size: 13px;
        font-weight: 500;
    }}
    QComboBox:hover {{
        border: 1px solid #334155;
    }}
    QComboBox:focus {{
        border: 1px solid {COLOR_ACCENT_INDIGO};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {COLOR_BG_INPUT};
        color: {COLOR_TEXT_PRIMARY};
        border: 1px solid #1E293B;
        border-radius: 8px;
        selection-background-color: {COLOR_ACCENT_INDIGO};
        selection-color: #FFFFFF;
        padding: 6px;
        outline: none;
    }}
"""

STYLE_CHECKBOX = f"""
    QCheckBox {{
        font-size: 13px;
        font-weight: 600;
        color: {COLOR_TEXT_PRIMARY};
        spacing: 10px;
    }}
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border-radius: 4px;
        border: 1px solid #334155;
        background-color: {COLOR_BG_INPUT};
    }}
    QCheckBox::indicator:hover {{
        border: 1px solid {COLOR_ACCENT_INDIGO};
    }}
    QCheckBox::indicator:checked {{
        background-color: {COLOR_ACCENT_INDIGO};
        border: 1px solid #818CF8;
    }}
"""

STYLE_LINEEDIT = f"""
    QLineEdit {{
        background-color: {COLOR_BG_INPUT};
        border: 1px solid #1E293B;
        border-radius: 8px;
        color: {COLOR_TEXT_PRIMARY};
        padding: 7px 12px;
        font-size: 13px;
    }}
    QLineEdit:focus {{
        border: 1px solid {COLOR_ACCENT_INDIGO};
        background-color: #111C38;
    }}
    QLineEdit:disabled {{
        background-color: #0A1020;
        color: {COLOR_TEXT_MUTED};
        border: 1px solid #1E293B;
    }}
"""


class SettingsCard(QFrame):
    """Container dạng thẻ (Card) chuẩn phong cách Dark Glassmorphic với tiêu đề & phụ đề tinh tế."""
    def __init__(self, icon: str, title_key: str, sub_key: str, parent=None):
        super().__init__(parent)
        self.icon_char = icon
        self.title_key = title_key
        self.sub_key = sub_key

        self.setStyleSheet(f"""
            SettingsCard {{
                background-color: {COLOR_BG_CARD};
                border: 1px solid {COLOR_BORDER};
                border-radius: 12px;
            }}
            SettingsCard:hover {{
                border: 1px solid rgba(99, 102, 241, 0.25);
            }}
        """)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 18, 20, 20)
        self.main_layout.setSpacing(14)

        # Header của Card: Icon tròn + Tiêu đề + Phụ đề
        header_row = QHBoxLayout()
        header_row.setSpacing(12)

        self.lbl_icon = QLabel(self.icon_char)
        self.lbl_icon.setAlignment(Qt.AlignCenter)
        self.lbl_icon.setFixedSize(36, 36)
        self.lbl_icon.setStyleSheet(f"""
            background-color: rgba(99, 102, 241, 0.12);
            border: 1px solid rgba(99, 102, 241, 0.25);
            border-radius: 18px;
            font-size: 17px;
        """)
        header_row.addWidget(self.lbl_icon)

        text_vbox = QVBoxLayout()
        text_vbox.setSpacing(2)

        self.lbl_title = QLabel()
        self.lbl_title.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {COLOR_TEXT_PRIMARY};")
        self.lbl_sub = QLabel()
        self.lbl_sub.setStyleSheet(f"font-size: 12px; color: {COLOR_TEXT_MUTED};")
        self.lbl_sub.setWordWrap(True)

        text_vbox.addWidget(self.lbl_title)
        text_vbox.addWidget(self.lbl_sub)
        header_row.addLayout(text_vbox, stretch=1)

        self.main_layout.addLayout(header_row)

        # Đường kẻ chia phần nhẹ
        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background-color: rgba(255, 255, 255, 0.05);")
        self.main_layout.addWidget(divider)

        # Vùng chứa các control bên trong Card
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(12)
        self.content_layout.setContentsMargins(0, 4, 0, 0)
        self.main_layout.addLayout(self.content_layout)

    def retranslate_ui(self):
        self.lbl_title.setText(t(self.title_key))
        self.lbl_sub.setText(t(self.sub_key))


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
        app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
        # Root layout không padding để Header và Action Bar ôm sát mép
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # -------------------------------------------------------------
        # 1. TOP HEADER (Tiêu đề trang cài đặt)
        # -------------------------------------------------------------
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

        # -------------------------------------------------------------
        # 2. SCROLLABLE CONTENT AREA (Vùng chứa Card có thanh cuộn mượt)
        # -------------------------------------------------------------
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

        # CARD 1: Ngôn ngữ & Giao diện
        self._build_language_card()

        # CARD 2: Cấu hình Quét & Giám sát Mạng
        self._build_scan_card()

        # CARD 3: Cấu hình Router Quản trị
        self._build_router_card()

        # CARD 4: Bảo mật & Tường lửa Cục bộ
        self._build_security_card()

        # Giữ khoảng cách co dãn ở cuối danh sách thẻ
        self.cards_layout.addStretch()

        self.scroll_area.setWidget(scroll_content)
        root_layout.addWidget(self.scroll_area, stretch=1)

        # -------------------------------------------------------------
        # 3. BOTTOM STICKY ACTION BAR (Thanh công cụ cố định chân trang)
        # -------------------------------------------------------------
        self._build_action_bar(root_layout)

    # -----------------------------------------------------------------
    # Card Builders
    # -----------------------------------------------------------------
    def _build_language_card(self):
        self.card_lang = SettingsCard("🌐", "card_lang_title", "card_lang_sub")
        
        row = QHBoxLayout()
        row.setSpacing(16)

        self.lbl_lang_label = QLabel()
        self.lbl_lang_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #CBD5E1;")
        self.lbl_lang_label.setFixedWidth(160)

        self.cb_language = QComboBox()
        self.cb_language.addItems(["🇻🇳 Tiếng Việt", "🇬🇧 English"])
        self.cb_language.setMinimumHeight(38)
        self.cb_language.setMinimumWidth(220)
        self.cb_language.setStyleSheet(STYLE_COMBOBOX)
        self.cb_language.setCursor(Qt.PointingHandCursor)
        self.cb_language.currentIndexChanged.connect(self._on_language_selection_changed)

        row.addWidget(self.lbl_lang_label)
        row.addWidget(self.cb_language)
        row.addStretch()

        self.card_lang.content_layout.addLayout(row)
        self.cards_layout.addWidget(self.card_lang)

    def _build_scan_card(self):
        self.card_scan = SettingsCard("📡", "card_scan_title", "card_scan_sub")

        # 1. Checkbox Auto-detect
        self.chk_autodetect = QCheckBox()
        self.chk_autodetect.setCursor(Qt.PointingHandCursor)
        self.chk_autodetect.setStyleSheet(STYLE_CHECKBOX)
        self.chk_autodetect.toggled.connect(self._on_autodetect_toggle)
        self.card_scan.content_layout.addWidget(self.chk_autodetect)

        # 2. Checkbox Multi-subnet
        self.chk_multisubnet = QCheckBox()
        self.chk_multisubnet.setCursor(Qt.PointingHandCursor)
        self.chk_multisubnet.setStyleSheet(STYLE_CHECKBOX)
        self.card_scan.content_layout.addWidget(self.chk_multisubnet)

        # 3. Custom Subnets Input
        subnet_vbox = QVBoxLayout()
        subnet_vbox.setSpacing(4)
        self.lbl_custom_subnet = QLabel()
        self.lbl_custom_subnet.setStyleSheet("font-size: 13px; font-weight: 600; color: #CBD5E1;")
        self.txt_custom_subnet = QLineEdit()
        self.txt_custom_subnet.setMinimumHeight(38)
        self.txt_custom_subnet.setStyleSheet(STYLE_LINEEDIT)

        subnet_vbox.addWidget(self.lbl_custom_subnet)
        subnet_vbox.addWidget(self.txt_custom_subnet)
        self.card_scan.content_layout.addLayout(subnet_vbox)

        # 4. Timer SpinBoxes (Chu kỳ quét & Ngưỡng offline)
        timer_row = QHBoxLayout()
        timer_row.setSpacing(20)

        # Cột Chu kỳ quét
        col_interval = QVBoxLayout()
        col_interval.setSpacing(4)
        self.lbl_scan_interval = QLabel()
        self.lbl_scan_interval.setStyleSheet("font-size: 13px; font-weight: 600; color: #CBD5E1;")
        self.spin_interval = QSpinBox()
        self.spin_interval.setRange(10, 3600)
        self.spin_interval.setMinimumHeight(38)
        self.spin_interval.setStyleSheet(f"""
            QSpinBox {{
                background-color: {COLOR_BG_INPUT};
                border: 1px solid #1E293B;
                border-radius: 8px;
                color: #F8FAFC;
                padding: 6px 12px;
                font-size: 13px;
                font-weight: 600;
            }}
            QSpinBox:focus {{
                border: 1px solid {COLOR_ACCENT_INDIGO};
            }}
        """)
        self.lbl_hint_interval = QLabel()
        self.lbl_hint_interval.setStyleSheet("font-size: 11px; color: #64748B;")

        col_interval.addWidget(self.lbl_scan_interval)
        col_interval.addWidget(self.spin_interval)
        col_interval.addWidget(self.lbl_hint_interval)
        timer_row.addLayout(col_interval, stretch=1)

        # Cột Ngưỡng Offline
        col_offline = QVBoxLayout()
        col_offline.setSpacing(4)
        self.lbl_offline_thresh = QLabel()
        self.lbl_offline_thresh.setStyleSheet("font-size: 13px; font-weight: 600; color: #CBD5E1;")
        self.spin_offline_thresh = QSpinBox()
        self.spin_offline_thresh.setRange(30, 7200)
        self.spin_offline_thresh.setMinimumHeight(38)
        self.spin_offline_thresh.setStyleSheet(f"""
            QSpinBox {{
                background-color: {COLOR_BG_INPUT};
                border: 1px solid #1E293B;
                border-radius: 8px;
                color: #F8FAFC;
                padding: 6px 12px;
                font-size: 13px;
                font-weight: 600;
            }}
            QSpinBox:focus {{
                border: 1px solid {COLOR_ACCENT_INDIGO};
            }}
        """)
        self.lbl_hint_offline = QLabel()
        self.lbl_hint_offline.setStyleSheet("font-size: 11px; color: #64748B;")

        col_offline.addWidget(self.lbl_offline_thresh)
        col_offline.addWidget(self.spin_offline_thresh)
        col_offline.addWidget(self.lbl_hint_offline)
        timer_row.addLayout(col_offline, stretch=1)

        self.card_scan.content_layout.addLayout(timer_row)

        # 5. Đường dẫn Nmap kèm nút Duyệt tệp
        nmap_vbox = QVBoxLayout()
        nmap_vbox.setSpacing(4)
        self.lbl_nmap_path = QLabel()
        self.lbl_nmap_path.setStyleSheet("font-size: 13px; font-weight: 600; color: #CBD5E1;")

        nmap_row = QHBoxLayout()
        nmap_row.setSpacing(8)

        self.txt_nmap_path = QLineEdit()
        self.txt_nmap_path.setMinimumHeight(38)
        self.txt_nmap_path.setStyleSheet(STYLE_LINEEDIT)

        self.btn_browse_nmap = QPushButton()
        self.btn_browse_nmap.setMinimumHeight(38)
        self.btn_browse_nmap.setCursor(Qt.PointingHandCursor)
        self.btn_browse_nmap.setStyleSheet("""
            QPushButton {
                background-color: #1E293B;
                color: #38BDF8;
                border: 1px solid rgba(56, 189, 248, 0.35);
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
                padding: 0 16px;
            }
            QPushButton:hover {
                background-color: rgba(56, 189, 248, 0.15);
                border: 1px solid #38BDF8;
                color: #E0F2FE;
            }
            QPushButton:pressed {
                background-color: rgba(56, 189, 248, 0.25);
            }
        """)
        self.btn_browse_nmap.clicked.connect(self._browse_nmap_path)

        nmap_row.addWidget(self.txt_nmap_path, stretch=1)
        nmap_row.addWidget(self.btn_browse_nmap)

        nmap_vbox.addWidget(self.lbl_nmap_path)
        nmap_vbox.addLayout(nmap_row)
        self.card_scan.content_layout.addLayout(nmap_vbox)

        self.cards_layout.addWidget(self.card_scan)

    def _build_router_card(self):
        self.card_router = SettingsCard("🔀", "card_router_title", "card_router_sub")

        # 1. Chọn loại Router Adapter
        adapter_vbox = QVBoxLayout()
        adapter_vbox.setSpacing(4)
        self.lbl_adapter_type = QLabel()
        self.lbl_adapter_type.setStyleSheet("font-size: 13px; font-weight: 600; color: #CBD5E1;")

        self.cb_adapter = QComboBox()
        self.cb_adapter.addItems([
            "🛡️ mock - Chế độ Giả lập an toàn (Mock Adapter)",
            "🌐 tplink - TP-Link Router (Web Management)",
            "⚡ openwrt - OpenWrt Router (UCI / SSH)",
            "📡 mikrotik - MikroTik RouterOS (REST API)"
        ])
        self.cb_adapter.setMinimumHeight(38)
        self.cb_adapter.setStyleSheet(STYLE_COMBOBOX)
        self.cb_adapter.setCursor(Qt.PointingHandCursor)
        self.cb_adapter.currentIndexChanged.connect(self._on_adapter_changed)

        adapter_vbox.addWidget(self.lbl_adapter_type)
        adapter_vbox.addWidget(self.cb_adapter)
        self.card_router.content_layout.addLayout(adapter_vbox)

        # 2. Hộp thông tin Mock Mode Tip Banner
        self.frame_mock_tip = QFrame()
        self.frame_mock_tip.setStyleSheet("""
            QFrame {
                background-color: rgba(6, 182, 212, 0.08);
                border: 1px solid rgba(6, 182, 212, 0.25);
                border-radius: 8px;
            }
        """)
        mock_tip_layout = QHBoxLayout(self.frame_mock_tip)
        mock_tip_layout.setContentsMargins(14, 10, 14, 10)
        mock_tip_layout.setSpacing(10)

        self.lbl_mock_tip_icon = QLabel("💡")
        self.lbl_mock_tip_icon.setStyleSheet("font-size: 16px; border: none; background: transparent;")
        self.lbl_mock_tip = QLabel()
        self.lbl_mock_tip.setStyleSheet("color: #7DD3FC; font-size: 12px; border: none; background: transparent;")
        self.lbl_mock_tip.setWordWrap(True)

        mock_tip_layout.addWidget(self.lbl_mock_tip_icon)
        mock_tip_layout.addWidget(self.lbl_mock_tip, stretch=1)
        self.card_router.content_layout.addWidget(self.frame_mock_tip)

        # 3. Router Host & Port (Hàng 2 cột)
        host_port_row = QHBoxLayout()
        host_port_row.setSpacing(16)

        col_host = QVBoxLayout()
        col_host.setSpacing(4)
        self.lbl_router_host = QLabel()
        self.lbl_router_host.setStyleSheet("font-size: 13px; font-weight: 600; color: #CBD5E1;")
        self.txt_router_host = QLineEdit()
        self.txt_router_host.setMinimumHeight(38)
        self.txt_router_host.setStyleSheet(STYLE_LINEEDIT)
        self.txt_router_host.setPlaceholderText("192.168.1.1")
        col_host.addWidget(self.lbl_router_host)
        col_host.addWidget(self.txt_router_host)
        host_port_row.addLayout(col_host, stretch=3)

        col_port = QVBoxLayout()
        col_port.setSpacing(4)
        self.lbl_router_port = QLabel()
        self.lbl_router_port.setStyleSheet("font-size: 13px; font-weight: 600; color: #CBD5E1;")
        self.txt_router_port = QLineEdit()
        self.txt_router_port.setMinimumHeight(38)
        self.txt_router_port.setStyleSheet(STYLE_LINEEDIT)
        self.txt_router_port.setPlaceholderText("80")
        col_port.addWidget(self.lbl_router_port)
        col_port.addWidget(self.txt_router_port)
        host_port_row.addLayout(col_port, stretch=1)

        self.card_router.content_layout.addLayout(host_port_row)

        # 4. Router Username & Password (kèm nút ẩn/hiện mắt xem mật khẩu)
        user_pass_row = QHBoxLayout()
        user_pass_row.setSpacing(16)

        col_user = QVBoxLayout()
        col_user.setSpacing(4)
        self.lbl_router_user = QLabel()
        self.lbl_router_user.setStyleSheet("font-size: 13px; font-weight: 600; color: #CBD5E1;")
        self.txt_router_user = QLineEdit()
        self.txt_router_user.setMinimumHeight(38)
        self.txt_router_user.setStyleSheet(STYLE_LINEEDIT)
        self.txt_router_user.setPlaceholderText("admin")
        col_user.addWidget(self.lbl_router_user)
        col_user.addWidget(self.txt_router_user)
        user_pass_row.addLayout(col_user, stretch=1)

        col_pass = QVBoxLayout()
        col_pass.setSpacing(4)
        self.lbl_router_pass = QLabel()
        self.lbl_router_pass.setStyleSheet("font-size: 13px; font-weight: 600; color: #CBD5E1;")

        pass_inner_row = QHBoxLayout()
        pass_inner_row.setSpacing(6)

        self.txt_router_pass = QLineEdit()
        self.txt_router_pass.setMinimumHeight(38)
        self.txt_router_pass.setStyleSheet(STYLE_LINEEDIT)
        self.txt_router_pass.setEchoMode(QLineEdit.Password)

        self.btn_toggle_pass = QPushButton("👁️")
        self.btn_toggle_pass.setFixedSize(38, 38)
        self.btn_toggle_pass.setCursor(Qt.PointingHandCursor)
        self.btn_toggle_pass.setStyleSheet("""
            QPushButton {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #334155;
                border: 1px solid #475569;
            }
        """)
        self.btn_toggle_pass.clicked.connect(self._toggle_password_visibility)

        pass_inner_row.addWidget(self.txt_router_pass, stretch=1)
        pass_inner_row.addWidget(self.btn_toggle_pass)

        col_pass.addWidget(self.lbl_router_pass)
        col_pass.addLayout(pass_inner_row)
        user_pass_row.addLayout(col_pass, stretch=1)

        self.card_router.content_layout.addLayout(user_pass_row)

        # 5. Nút Kiểm tra Kết nối và Badge trạng thái phản hồi
        conn_row = QHBoxLayout()
        conn_row.setSpacing(14)

        self.btn_test_router = QPushButton()
        self.btn_test_router.setMinimumHeight(38)
        self.btn_test_router.setCursor(Qt.PointingHandCursor)
        self.btn_test_router.setStyleSheet("""
            QPushButton {
                background-color: #1E293B;
                color: #38BDF8;
                border: 1px solid rgba(56, 189, 248, 0.4);
                font-weight: 600;
                font-size: 13px;
                padding: 0 20px;
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

        self.lbl_conn_status = QLabel()
        self.lbl_conn_status.setStyleSheet("font-size: 13px; font-weight: 600;")
        self.lbl_conn_status.setVisible(False)

        conn_row.addWidget(self.btn_test_router)
        conn_row.addWidget(self.lbl_conn_status)
        conn_row.addStretch()

        self.card_router.content_layout.addLayout(conn_row)
        self.cards_layout.addWidget(self.card_router)

    def _build_security_card(self):
        self.card_sec = SettingsCard("🛡️", "card_sec_title", "card_sec_sub")

        # 1. Checkbox Firewall + Hint
        fw_vbox = QVBoxLayout()
        fw_vbox.setSpacing(2)
        self.chk_firewall = QCheckBox()
        self.chk_firewall.setCursor(Qt.PointingHandCursor)
        self.chk_firewall.setStyleSheet(STYLE_CHECKBOX)
        self.lbl_hint_firewall = QLabel()
        self.lbl_hint_firewall.setStyleSheet("font-size: 11px; color: #64748B; margin-left: 28px;")
        fw_vbox.addWidget(self.chk_firewall)
        fw_vbox.addWidget(self.lbl_hint_firewall)
        self.card_sec.content_layout.addLayout(fw_vbox)

        # 2. Checkbox Confirm + Hint
        cf_vbox = QVBoxLayout()
        cf_vbox.setSpacing(2)
        self.chk_confirm = QCheckBox()
        self.chk_confirm.setCursor(Qt.PointingHandCursor)
        self.chk_confirm.setStyleSheet(STYLE_CHECKBOX)
        self.lbl_hint_confirm = QLabel()
        self.lbl_hint_confirm.setStyleSheet("font-size: 11px; color: #64748B; margin-left: 28px;")
        cf_vbox.addWidget(self.chk_confirm)
        cf_vbox.addWidget(self.lbl_hint_confirm)
        self.card_sec.content_layout.addLayout(cf_vbox)

        self.cards_layout.addWidget(self.card_sec)

    def _build_action_bar(self, root_layout: QVBoxLayout):
        self.action_bar = QFrame()
        self.action_bar.setStyleSheet("""
            QFrame {
                background-color: #0B1326;
                border-top: 1px solid rgba(255, 255, 255, 0.08);
            }
        """)
        bar_layout = QHBoxLayout(self.action_bar)
        bar_layout.setContentsMargins(28, 14, 28, 14)
        bar_layout.setSpacing(14)

        # Trạng thái bên trái
        self.lbl_action_status = QLabel()
        self.lbl_action_status.setStyleSheet("color: #64748B; font-size: 12px; font-weight: 500;")
        bar_layout.addWidget(self.lbl_action_status)
        bar_layout.addStretch()

        # Nút Khôi phục mặc định
        self.btn_reset = QPushButton()
        self.btn_reset.setMinimumHeight(42)
        self.btn_reset.setCursor(Qt.PointingHandCursor)
        self.btn_reset.setStyleSheet("""
            QPushButton {
                background-color: #1E293B;
                color: #94A3B8;
                border: 1px solid rgba(148, 163, 184, 0.2);
                border-radius: 8px;
                font-weight: 600;
                font-size: 13px;
                padding: 0 18px;
            }
            QPushButton:hover {
                background-color: #334155;
                color: #F8FAFC;
                border: 1px solid rgba(148, 163, 184, 0.4);
            }
            QPushButton:pressed {
                background-color: #0F172A;
            }
        """)
        self.btn_reset.clicked.connect(self._reset_defaults)
        bar_layout.addWidget(self.btn_reset)

        # Nút Lưu Cấu hình
        self.btn_save = QPushButton()
        self.btn_save.setMinimumHeight(42)
        self.btn_save.setMinimumWidth(160)
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4F46E5, stop:1 #06B6D4);
                color: #FFFFFF;
                font-weight: 700;
                font-size: 13px;
                padding: 0 24px;
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
        bar_layout.addWidget(self.btn_save)

        root_layout.addWidget(self.action_bar)

    # -----------------------------------------------------------------
    # Retranslate UI (Đa ngôn ngữ VI / EN)
    # -----------------------------------------------------------------
    def retranslate_ui(self):
        self.lbl_main_title.setText(f"⚙️ {t('set_title')}")
        self.lbl_main_desc.setText(t("set_desc"))

        # Retranslate Cards
        self.card_lang.retranslate_ui()
        self.lbl_lang_label.setText(t("lbl_language"))

        self.card_scan.retranslate_ui()
        self.chk_autodetect.setText(t("chk_autodetect").replace("&", "&&"))
        self.chk_multisubnet.setText(t("chk_multisubnet").replace("&", "&&"))
        self.lbl_custom_subnet.setText(t("lbl_custom_subnet"))
        self.txt_custom_subnet.setPlaceholderText(t("custom_subnets_placeholder"))
        self.lbl_scan_interval.setText(t("lbl_scan_interval"))
        self.spin_interval.setSuffix(f" {t('sec_unit')}")
        self.lbl_hint_interval.setText(t("hint_scan_interval"))
        self.lbl_offline_thresh.setText(t("lbl_offline_thresh"))
        self.spin_offline_thresh.setSuffix(f" {t('sec_unit')}")
        self.lbl_hint_offline.setText(t("hint_offline_thresh"))
        self.lbl_nmap_path.setText(t("lbl_nmap_path"))
        self.btn_browse_nmap.setText(t("btn_browse"))

        self.card_router.retranslate_ui()
        self.lbl_adapter_type.setText(t("lbl_adapter_type"))
        self.lbl_mock_tip.setText(t("router_mock_tip"))
        self.lbl_router_host.setText(t("lbl_router_host"))
        self.lbl_router_port.setText(t("lbl_router_port"))
        self.lbl_router_user.setText(t("lbl_router_user"))
        self.lbl_router_pass.setText(t("lbl_router_pass"))
        self.btn_test_router.setText(f"⚡ {t('btn_test_conn')}")
        self.btn_toggle_pass.setToolTip(t("hide_pass") if self.password_visible else t("show_pass"))

        self.card_sec.retranslate_ui()
        self.chk_firewall.setText(t("chk_firewall").replace("&", "&&"))
        self.lbl_hint_firewall.setText(t("card_sec_firewall_hint"))
        self.chk_confirm.setText(t("chk_confirm").replace("&", "&&"))
        self.lbl_hint_confirm.setText(t("card_sec_confirm_hint"))

        self.lbl_action_status.setText(f"💡 {t('settings_synced')}")
        self.btn_reset.setText(f"🔄 {t('btn_reset_defaults')}")
        self.btn_save.setText(f"💾 {t('btn_save_settings')}")

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

        # Ẩn hoặc hiện hộp lưu ý Mock Mode
        self.frame_mock_tip.setVisible(adapter_key == "mock")
        self.lbl_conn_status.setVisible(False)

    def _toggle_password_visibility(self):
        self.password_visible = not self.password_visible
        if self.password_visible:
            self.txt_router_pass.setEchoMode(QLineEdit.Normal)
            self.btn_toggle_pass.setText("🙈")
            self.btn_toggle_pass.setToolTip(t("hide_pass"))
        else:
            self.txt_router_pass.setEchoMode(QLineEdit.Password)
            self.btn_toggle_pass.setText("👁️")
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

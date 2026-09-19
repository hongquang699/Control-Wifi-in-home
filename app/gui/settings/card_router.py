"""
Thẻ cấu hình Router Adapter & Quản lý kết nối (Router Settings Card).
"""

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QFrame
)
from PySide6.QtCore import Qt
from core.i18n import t
from gui.theme import COLOR_ACCENT_EMERALD, COLOR_ACCENT_ROSE
from gui.settings.card_base import SettingsCard, STYLE_COMBOBOX, STYLE_LINEEDIT

class RouterSettingsCard(SettingsCard):
    def __init__(self, parent=None):
        super().__init__("🔀", "card_router_title", "card_router_sub", parent)
        self.password_visible = False

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

        adapter_vbox.addWidget(self.lbl_adapter_type)
        adapter_vbox.addWidget(self.cb_adapter)
        self.content_layout.addLayout(adapter_vbox)

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
        self.content_layout.addWidget(self.frame_mock_tip)

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

        self.content_layout.addLayout(host_port_row)

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

        pass_inner_row.addWidget(self.txt_router_pass, stretch=1)
        pass_inner_row.addWidget(self.btn_toggle_pass)

        col_pass.addWidget(self.lbl_router_pass)
        col_pass.addLayout(pass_inner_row)
        user_pass_row.addLayout(col_pass, stretch=1)

        self.content_layout.addLayout(user_pass_row)

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

        self.lbl_conn_status = QLabel()
        self.lbl_conn_status.setStyleSheet("font-size: 13px; font-weight: 600;")
        self.lbl_conn_status.setVisible(False)

        conn_row.addWidget(self.btn_test_router)
        conn_row.addWidget(self.lbl_conn_status)
        conn_row.addStretch()

        self.content_layout.addLayout(conn_row)

    def retranslate_ui(self):
        super().retranslate_ui()
        self.lbl_adapter_type.setText(t("lbl_adapter_type"))
        self.lbl_mock_tip.setText(t("router_mock_tip"))
        self.lbl_router_host.setText(t("lbl_router_host"))
        self.lbl_router_port.setText(t("lbl_router_port"))
        self.lbl_router_user.setText(t("lbl_router_user"))
        self.lbl_router_pass.setText(t("lbl_router_pass"))
        self.btn_test_router.setText(f"⚡ {t('btn_test_conn')}")
        self.btn_toggle_pass.setToolTip(t("hide_pass") if self.password_visible else t("show_pass"))

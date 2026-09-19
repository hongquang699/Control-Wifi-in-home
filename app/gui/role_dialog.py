"""
Hộp thoại Quản lý Phân quyền & Vai trò người dùng (RBAC Role Dialog)
Hỗ trợ chuyển đổi vai trò: ADMIN (Toàn quyền), OPERATOR (Quản trị viên), VIEWER (Chỉ xem).
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QRadioButton, QButtonGroup, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor
from gui.theme import (
    COLOR_BG_CARD, COLOR_BORDER, COLOR_ACCENT_CYAN,
    COLOR_ACCENT_AMBER, COLOR_ACCENT_EMERALD, COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED, STYLE_BTN_PRIMARY, STYLE_BTN_SLATE
)
from gui.icons import get_app_icon

class CurrentRoleManager:
    """Quản lý singleton lưu vai trò hiện tại trong phiên làm việc."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.current_role = "ADMIN"
            cls._instance.subscribers = []
        return cls._instance

    def set_role(self, role: str):
        self.current_role = role
        for cb in self.subscribers:
            try:
                cb(role)
            except Exception:
                pass

    def subscribe(self, callback):
        if callback not in self.subscribers:
            self.subscribers.append(callback)

role_manager = CurrentRoleManager()


class RoleDialog(QDialog):
    role_updated = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Xác Thực & Phân Quyền Vai Trò (RBAC)")
        self.setFixedSize(480, 400)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: #060D1D;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
            }}
        """)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(16)

        # Header
        header = QLabel("Chuyển Đổi Quyền Hạn Hệ Thống")
        header.setStyleSheet(f"font-size: 16px; font-weight: 800; color: {COLOR_TEXT_PRIMARY};")
        layout.addWidget(header)

        desc = QLabel("Lựa chọn cấp độ quyền hạn để kiểm thử cơ chế phòng vệ RBAC đa lớp trên giao diện:")
        desc.setStyleSheet(f"font-size: 12px; color: {COLOR_TEXT_MUTED};")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Role Options Container
        opt_box = QFrame()
        opt_box.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_BG_CARD};
                border: 1px solid {COLOR_BORDER};
                border-radius: 10px;
                padding: 10px;
            }}
        """)
        opt_layout = QVBoxLayout(opt_box)
        opt_layout.setSpacing(10)

        self.btn_group = QButtonGroup(self)

        roles = [
            ("ADMIN", "Quản Trị Viên Toàn Quyền (ADMIN)", "Toàn quyền cấu hình router, quét mạng, chặn/bỏ chặn và đọc Audit Logs nhạy cảm.", "#F59E0B"),
            ("OPERATOR", "Kỹ Thuật Viên Vận Hành (OPERATOR)", "Được phép quét mạng, xem băng thông, chặn thiết bị. Không được xem Audit Logs.", "#38BDF8"),
            ("VIEWER", "Người Quan Sát (VIEWER / GUEST)", "Chế độ chỉ đọc an toàn. Vô hiệu hóa tính năng can thiệp phần cứng và chặn thiết bị.", "#94A3B8")
        ]

        self.radios = {}
        for role_key, role_title, role_sub, accent_hex in roles:
            item_frame = QFrame()
            item_frame.setStyleSheet("""
                QFrame:hover { background-color: rgba(255, 255, 255, 0.03); border-radius: 6px; }
            """)
            i_layout = QVBoxLayout(item_frame)
            i_layout.setContentsMargins(8, 6, 8, 6)
            i_layout.setSpacing(2)

            rb = QRadioButton(role_title)
            rb.setStyleSheet(f"""
                QRadioButton {{
                    font-size: 13px;
                    font-weight: 700;
                    color: {accent_hex};
                    spacing: 8px;
                }}
            """)
            if role_manager.current_role == role_key:
                rb.setChecked(True)
            self.btn_group.addButton(rb)
            self.radios[role_key] = rb

            lbl_sub = QLabel(role_sub)
            lbl_sub.setStyleSheet(f"font-size: 11px; color: {COLOR_TEXT_MUTED}; margin-left: 24px;")
            lbl_sub.setWordWrap(True)

            i_layout.addWidget(rb)
            i_layout.addWidget(lbl_sub)
            opt_layout.addWidget(item_frame)

        layout.addWidget(opt_box)

        # Buttons Row
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self.btn_cancel = QPushButton("Hủy bỏ")
        self.btn_cancel.setStyleSheet(STYLE_BTN_SLATE)
        self.btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(self.btn_cancel)

        self.btn_apply = QPushButton("Áp Dụng Quyền")
        self.btn_apply.setStyleSheet(STYLE_BTN_PRIMARY)
        self.btn_apply.clicked.connect(self._on_apply)
        btn_row.addWidget(self.btn_apply)

        layout.addLayout(btn_row)

    def _on_apply(self):
        selected_role = "ADMIN"
        for role_key, rb in self.radios.items():
            if rb.isChecked():
                selected_role = role_key
                break
        
        role_manager.set_role(selected_role)
        self.role_updated.emit(selected_role)
        self.accept()

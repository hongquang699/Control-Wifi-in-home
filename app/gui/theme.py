"""
Hệ sinh thái Giao diện & Bảng màu Hiện đại (Modern Dark Glassmorphism Theme).
Cung cấp QSS toàn cục, bảng màu và các thành phần UI cao cấp tái sử dụng.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QPushButton
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor
from core.i18n import t

# 1. Bảng màu cao cấp (Modern Luxury Dark Palette)
COLOR_BG_MAIN = "#0B0F19"         # Nền chính không gian sâu (Dark Tech Canvas)
COLOR_BG_SIDEBAR = "#0D1322"      # Nền sidebar sắc nét
COLOR_BG_CARD = "#0D1322"         # Nền thẻ container (Glass Card)
COLOR_BG_CARD_HOVER = "#131C31"   # Thẻ khi hover
COLOR_BG_INPUT = "#0D1322"        # Nền ô nhập liệu / combobox

COLOR_BORDER = "#1E293B"
COLOR_BORDER_LIGHT = "rgba(255, 255, 255, 0.12)"
COLOR_BORDER_FOCUS = "#38BDF8"    # Cyan sáng khi focus

COLOR_TEXT_PRIMARY = "#F8FAFC"    # Chữ sáng chính
COLOR_TEXT_SECONDARY = "#94A3B8"  # Chữ phụ
COLOR_TEXT_MUTED = "#64748B"      # Chữ làm mờ

COLOR_ACCENT_INDIGO = "#6366F1"   # Indigo chủ đạo
COLOR_ACCENT_CYAN = "#38BDF8"     # Xanh Cyan công nghệ
COLOR_ACCENT_PURPLE = "#A855F7"   # Tím sóng / Uplink
COLOR_ACCENT_EMERALD = "#10B981"  # Xanh ngọc trực tuyến / thành công
COLOR_ACCENT_AMBER = "#F59E0B"    # Hổ phách / Cảnh báo
COLOR_ACCENT_ROSE = "#EF4444"     # Đỏ hồng / Chặn

# Bộ định kiểu nút bấm chuẩn Cyber Dark-Tech
STYLE_PILL_ACTIVE = """
    QPushButton {
        background-color: #0284C7;
        color: #FFFFFF;
        border: 1px solid #38BDF8;
        border-radius: 8px;
        font-weight: 700;
        font-size: 12px;
        padding: 6px 14px;
    }
"""

STYLE_PILL_INACTIVE = """
    QPushButton {
        background-color: #0A1224;
        color: #94A3B8;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        font-weight: 600;
        font-size: 12px;
        padding: 6px 14px;
    }
    QPushButton:hover {
        background-color: #121E36;
        color: #F8FAFC;
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
"""

STYLE_BTN_BLOCK = """
    QPushButton {
        background-color: rgba(239, 68, 68, 0.12);
        color: #F87171;
        border: 1px solid rgba(239, 68, 68, 0.45);
        border-radius: 6px;
        font-weight: 700;
        font-size: 12px;
        padding: 5px 14px;
    }
    QPushButton:hover {
        background-color: #DC2626;
        color: #FFFFFF;
        border: 1px solid #EF4444;
    }
"""

STYLE_BTN_UNBLOCK = """
    QPushButton {
        background-color: rgba(16, 185, 129, 0.12);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.45);
        border-radius: 6px;
        font-weight: 700;
        font-size: 12px;
        padding: 5px 14px;
    }
    QPushButton:hover {
        background-color: #059669;
        color: #FFFFFF;
        border: 1px solid #10B981;
    }
"""

STYLE_BTN_SLATE = """
    QPushButton {
        background-color: #1E293B;
        color: #CBD5E1;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 6px;
        font-weight: 600;
        font-size: 12px;
        padding: 5px 12px;
    }
    QPushButton:hover {
        background-color: #334155;
        color: #FFFFFF;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
"""

STYLE_BTN_PRIMARY = """
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284C7, stop:1 #2563EB);
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
        font-weight: 700;
        font-size: 12px;
        padding: 7px 18px;
    }
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0EA5E9, stop:1 #3B82F6);
    }
"""

STYLE_BTN_AMBER = """
    QPushButton {
        background-color: rgba(245, 158, 11, 0.15);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.45);
        border-radius: 8px;
        font-weight: 700;
        font-size: 12px;
        padding: 7px 16px;
    }
    QPushButton:hover {
        background-color: #D97706;
        color: #FFFFFF;
        border: 1px solid #F59E0B;
    }
"""

STYLE_BTN_EMERALD = """
    QPushButton {
        background-color: rgba(16, 185, 129, 0.15);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.45);
        border-radius: 8px;
        font-weight: 700;
        font-size: 12px;
        padding: 7px 16px;
    }
    QPushButton:hover {
        background-color: #059669;
        color: #FFFFFF;
        border: 1px solid #10B981;
    }
"""

# 2. QSS Toàn cục (Global StyleSheet)
GLOBAL_QSS = """
/* Cửa sổ & Nền */
QMainWindow, QDialog {
    background-color: #0B0F19;
    color: #F8FAFC;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
}

QLabel, QPushButton, QLineEdit, QComboBox, QTableWidget, QTreeWidget, QHeaderView, QGroupBox {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
}

QLabel {
    border: none;
    background: transparent;
}

/* Thanh trạng thái Status Bar */
QStatusBar {
    background-color: #0D1322;
    color: #64748B;
    border-top: 1px solid #1E293B;
    padding: 6px 14px;
    font-size: 11px;
    font-weight: 500;
}

/* Thanh cuộn siêu mỏng hiện đại */
QScrollBar:vertical {
    background: transparent;
    width: 6px;
    margin: 0px;
    border-radius: 3px;
}
QScrollBar::handle:vertical {
    background: #1E293B;
    min-height: 28px;
    border-radius: 3px;
}
QScrollBar::handle:vertical:hover {
    background: #334155;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar:horizontal {
    background: transparent;
    height: 6px;
    margin: 0px;
    border-radius: 3px;
}
QScrollBar::handle:horizontal {
    background: #1E293B;
    min-width: 28px;
    border-radius: 3px;
}
QScrollBar::handle:horizontal:hover {
    background: #334155;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Ô nhập liệu hiện đại */
QLineEdit {
    background-color: #0D1322;
    border: 1px solid #1E293B;
    border-radius: 10px;
    color: #F8FAFC;
    padding: 7px 14px;
    font-size: 12px;
    selection-background-color: #0284C7;
}
QLineEdit:focus {
    border: 1px solid #0EA5E9;
    background-color: #121A2D;
}
QLineEdit:disabled {
    background-color: #0B0F19;
    color: #64748B;
    border: 1px solid #1E293B;
}

/* Hộp chọn ComboBox */
QComboBox {
    background-color: #0D1322;
    border: 1px solid #1E293B;
    border-radius: 10px;
    color: #F8FAFC;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: 500;
}
QComboBox:hover {
    border: 1px solid #334155;
    background-color: #121A2D;
}
QComboBox:focus {
    border: 1px solid #0EA5E9;
}
QComboBox::drop-down {
    border: none;
    width: 22px;
}
QComboBox QAbstractItemView {
    background-color: #0D1322;
    color: #F8FAFC;
    border: 1px solid #1E293B;
    border-radius: 10px;
    selection-background-color: #0284C7;
    selection-color: #FFFFFF;
    outline: none;
    padding: 4px;
}

/* Bảng dữ liệu không viền thừa */
QTableWidget {
    background-color: #0D1322;
    border: 1px solid #1E293B;
    border-radius: 14px;
    color: #F8FAFC;
    gridline-color: transparent;
    selection-background-color: rgba(56, 189, 248, 0.12);
    selection-color: #FFFFFF;
    outline: none;
}
QTableWidget::item {
    padding: 8px 10px;
    border: none;
    border-bottom: 1px solid #1E293B;
    background-color: transparent;
}
QTableWidget::item:selected {
    background-color: rgba(56, 189, 248, 0.12);
}
QTableWidget::item:hover {
    background-color: #131C31;
}
QHeaderView::section {
    background-color: #0F172A;
    color: #94A3B8;
    padding: 10px 10px;
    font-weight: 700;
    font-size: 11px;
    text-transform: uppercase;
    border: none;
    border-bottom: 1px solid #1E293B;
}

/* Cây phân tầng QTreeWidget */
QTreeWidget {
    background-color: #0D1322;
    border: 1px solid #1E293B;
    border-radius: 14px;
    color: #F8FAFC;
    outline: none;
    padding: 8px;
}
QTreeWidget::item {
    padding: 8px 6px;
    border-radius: 8px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}
QTreeWidget::item:hover {
    background-color: #131C31;
}
QTreeWidget::item:selected {
    background-color: rgba(14, 165, 233, 0.18);
    color: #FFFFFF;
}

/* Tooltip */
QToolTip {
    background-color: #091022;
    color: #F8FAFC;
    border: 1px solid #1E293B;
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 12px;
}

/* Nhóm GroupBox */
QGroupBox {
    background-color: #0B1326;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    margin-top: 14px;
    padding-top: 16px;
    padding-bottom: 14px;
    padding-left: 14px;
    padding-right: 14px;
    font-weight: bold;
    font-size: 13px;
    color: #F8FAFC;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 16px;
    top: 0px;
    padding: 2px 10px;
    background-color: #1E293B;
    border-radius: 6px;
    color: #38BDF8;
    font-size: 11px;
    font-weight: bold;
}
"""

class StatusPill(QFrame):
    """Huy hiệu trạng thái bo tròn dạng viên thuốc có chấm màu phát sáng."""
    def __init__(self, status: str, parent=None):
        super().__init__(parent)
        self.setFixedHeight(24)
        self.setMinimumWidth(85)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 0, 6, 0)
        layout.setSpacing(5)
        layout.setAlignment(Qt.AlignCenter)
        
        self.lbl_dot = QLabel("●")
        self.lbl_text = QLabel()
        self.lbl_text.setFont(QFont("Segoe UI", 9, QFont.Bold))
        
        layout.addWidget(self.lbl_dot)
        layout.addWidget(self.lbl_text)
        
        self.set_status(status)

    def set_status(self, status: str):
        status_upper = str(status).upper()
        if status_upper in ("ONLINE", "TRỰC TUYẾN"):
            bg_color = "rgba(16, 185, 129, 0.15)"
            border_color = "rgba(16, 185, 129, 0.35)"
            text_color = "#10B981"
            display_text = "ONLINE"
        elif status_upper in ("BLOCKED", "BỊ CHẶN", "ĐÃ CHẶN"):
            bg_color = "rgba(244, 63, 94, 0.15)"
            border_color = "rgba(244, 63, 94, 0.35)"
            text_color = "#F43F5E"
            display_text = "BLOCKED"
        else:
            bg_color = "rgba(100, 116, 139, 0.15)"
            border_color = "rgba(100, 116, 139, 0.25)"
            text_color = "#94A3B8"
            display_text = "OFFLINE"

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 12px;
            }}
            QLabel {{
                border: none;
                background: transparent;
            }}
        """)
        self.lbl_dot.setStyleSheet(f"color: {text_color}; font-size: 8px; border: none; background: transparent;")
        self.lbl_text.setStyleSheet(f"color: {text_color}; border: none; background: transparent;")
        self.lbl_text.setText(display_text)


class SubnetTabButton(QPushButton):
    """Nút lọc dải mạng phân đoạn (Segmented Pill Button) kèm huy hiệu số lượng."""
    def __init__(self, key: str, count: int = 0, parent=None):
        super().__init__(parent)
        self.key = key
        self.count = count
        self.setCheckable(True)
        self.setAutoExclusive(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(34)
        self.setFont(QFont("Segoe UI", 9, QFont.DemiBold))
        self._update_style()

    def set_count(self, count: int):
        self.count = count
        self.retranslate_ui()

    def _update_style(self):
        self.setStyleSheet("""
            SubnetTabButton {
                background-color: #101B33;
                color: #94A3B8;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px;
                padding: 4px 14px;
            }
            SubnetTabButton:hover {
                background-color: #152445;
                color: #F8FAFC;
            }
            SubnetTabButton:checked {
                background-color: #6366F1;
                color: white;
                font-weight: bold;
                border: 1px solid #818CF8;
            }
        """)

    def retranslate_ui(self):
        label = t(self.key) if self.key.startswith("subtab_") else self.key
        self.setText(f"{label} ({self.count})")


class MetricCard(QFrame):
    """Thẻ số liệu Hero cao cấp với biểu tượng tròn, số liệu 30px và hiệu ứng viền phát sáng."""
    def __init__(self, icon_str: str, title_key: str, value: str = "0", accent_hex: str = "#6366F1", parent=None):
        super().__init__(parent)
        self.icon_str = icon_str
        self.title_key = title_key
        self.accent_hex = accent_hex
        self.setFrameShape(QFrame.StyledPanel)
        
        self.setStyleSheet(f"""
            MetricCard {{
                background-color: {COLOR_BG_CARD};
                border: 1px solid {COLOR_BORDER};
                border-radius: 12px;
            }}
            MetricCard:hover {{
                border: 1px solid {accent_hex};
                background-color: {COLOR_BG_CARD_HOVER};
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)

        # Header hàng 1: Icon tròn + Tiêu đề nhỏ
        top_row = QHBoxLayout()
        top_row.setSpacing(8)
        
        self.lbl_icon = QLabel()
        self.lbl_icon.setAlignment(Qt.AlignCenter)
        self.lbl_icon.setFixedSize(28, 28)
        self.lbl_icon.setStyleSheet(f"""
            background-color: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 14px;
            font-size: 13px;
        """)
        try:
            from gui.icons import get_app_icon
            app_icon = get_app_icon(self.icon_str)
            if not app_icon.isNull():
                self.lbl_icon.setPixmap(app_icon.pixmap(18, 18))
            else:
                self.lbl_icon.setText(self.icon_str)
        except Exception:
            self.lbl_icon.setText(self.icon_str)
        top_row.addWidget(self.lbl_icon)

        self.lbl_title = QLabel(t(self.title_key))
        self.lbl_title.setStyleSheet("color: #94A3B8; font-size: 11px; font-weight: 700; text-transform: uppercase;")
        top_row.addWidget(self.lbl_title)
        top_row.addStretch()

        layout.addLayout(top_row)

        # Hàng 2: Giá trị số liệu lớn
        self.lbl_val = QLabel(value)
        self.lbl_val.setStyleSheet(f"color: {accent_hex}; font-size: 26px; font-weight: 800; margin-top: 2px;")
        layout.addWidget(self.lbl_val)

    def set_value(self, val: int | str):
        self.lbl_val.setText(str(val))

    def retranslate_ui(self):
        self.lbl_title.setText(t(self.title_key))

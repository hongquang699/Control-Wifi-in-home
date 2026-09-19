"""
Màn hình Cảnh Báo An Ninh Mạng (Security Alerts View) - Chuẩn Thiết Kế Cyber Dark-Tech (Ảnh 5).
Bao gồm:
- Header với nút 'Mô phỏng sự cố mới' (Amber) & 'Đánh dấu đã đọc'
- Bộ lọc dạng viên thuốc (Tất cả, Critical, Warning, Success, Info)
- Danh sách thẻ cảnh báo dạng Glass Alert Card với nút 'Chặn Kẻ Tấn Công' và 'Bỏ qua'
"""

import time
from typing import List, Dict, Any, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QColor, QFont

from core.i18n import t, i18n
from gui.icons import get_app_icon
from gui.theme import (
    COLOR_BG_CARD, COLOR_BORDER, COLOR_ACCENT_CYAN,
    COLOR_ACCENT_EMERALD, COLOR_ACCENT_AMBER, COLOR_ACCENT_ROSE,
    STYLE_BTN_AMBER, STYLE_BTN_PRIMARY, STYLE_BTN_SLATE,
    STYLE_BTN_BLOCK, STYLE_BTN_UNBLOCK
)

class AlertCard(QFrame):
    block_requested = Signal(dict)
    dismiss_requested = Signal(dict)

    def __init__(self, data: dict, parent=None):
        super().__init__(parent)
        self.data = data
        lvl = data.get("level", "INFO")

        border_color = "rgba(255, 255, 255, 0.08)"
        if lvl == "CRITICAL":
            border_color = "rgba(244, 63, 94, 0.35)"
        elif lvl == "WARNING":
            border_color = "rgba(245, 158, 11, 0.35)"
        elif lvl == "SUCCESS":
            border_color = "rgba(16, 185, 129, 0.35)"

        self.setStyleSheet(f"""
            AlertCard {{
                background-color: {COLOR_BG_CARD};
                border: 1px solid {border_color};
                border-radius: 14px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        # Top row: Level Badge + Time + Source
        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        badge_cfg = {
            "CRITICAL": ("CRITICAL", "#F43F5E", "rgba(244, 63, 94, 0.15)", "rgba(244, 63, 94, 0.35)", "shield_block"),
            "WARNING": ("WARNING", "#F59E0B", "rgba(245, 158, 11, 0.15)", "rgba(245, 158, 11, 0.35)", "warning"),
            "SUCCESS": ("SUCCESS", "#10B981", "rgba(16, 185, 129, 0.15)", "rgba(16, 185, 129, 0.35)", "check"),
            "INFO": ("INFO", "#38BDF8", "rgba(56, 189, 248, 0.15)", "rgba(56, 189, 248, 0.35)", "info"),
        }
        b_txt, b_color, b_bg, b_bd, b_ico = badge_cfg.get(lvl, badge_cfg["INFO"])

        lbl_badge = QLabel(f" {b_txt}")
        lbl_badge.setStyleSheet(f"""
            background-color: {b_bg};
            color: {b_color};
            border: 1px solid {b_bd};
            border-radius: 5px;
            font-size: 10px;
            font-weight: 800;
            padding: 3px 8px;
        """)
        top_row.addWidget(lbl_badge)

        lbl_time = QLabel(data.get("time", ""))
        lbl_time.setStyleSheet("color: #64748B; font-size: 11px; font-family: 'Fira Code', monospace;")
        top_row.addWidget(lbl_time)

        top_row.addStretch()

        source_txt = data.get("source", "Nguồn: WAF Engine / IDS")
        lbl_source = QLabel(source_txt)
        lbl_source.setStyleSheet("color: #94A3B8; font-size: 11px;")
        top_row.addWidget(lbl_source)
        layout.addLayout(top_row)

        # Title
        is_vi = i18n.current_lang == "vi"
        title_txt = data.get("title", "") if is_vi else data.get("title_en", data.get("title", ""))
        lbl_title = QLabel(title_txt)
        lbl_title.setStyleSheet("color: #F8FAFC; font-size: 14px; font-weight: 700;")
        layout.addWidget(lbl_title)

        # Desc
        desc_txt = data.get("desc", "") if is_vi else data.get("desc_en", data.get("desc", ""))
        lbl_desc = QLabel(desc_txt)
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("color: #94A3B8; font-size: 12px; line-height: 1.4;")
        layout.addWidget(lbl_desc)

        # Meta bar (target & attacker)
        meta_txt = data.get("meta", "")
        if meta_txt:
            lbl_meta = QLabel(meta_txt)
            lbl_meta.setStyleSheet("""
                background-color: #0D162B;
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 6px;
                color: #38BDF8;
                font-family: 'Fira Code', monospace;
                font-size: 11px;
                padding: 6px 10px;
            """)
            layout.addWidget(lbl_meta)

        # Action buttons
        act_row = QHBoxLayout()
        act_row.setSpacing(10)

        if lvl in ("CRITICAL", "WARNING") and data.get("attacker_mac"):
            btn_block = QPushButton(" Chặn Kẻ Tấn Công")
            btn_block.setIcon(get_app_icon("shield_block"))
            btn_block.setIconSize(QSize(14, 14))
            btn_block.setCursor(Qt.PointingHandCursor)
            btn_block.setStyleSheet(STYLE_BTN_BLOCK)
            btn_block.clicked.connect(lambda: self.block_requested.emit(self.data))
            act_row.addWidget(btn_block)

            btn_dismiss = QPushButton("Bỏ qua")
            btn_dismiss.setCursor(Qt.PointingHandCursor)
            btn_dismiss.setStyleSheet(STYLE_BTN_SLATE)
            btn_dismiss.clicked.connect(lambda: self.dismiss_requested.emit(self.data))
            act_row.addWidget(btn_dismiss)
        else:
            btn_detail = QPushButton("Chi tiết sự cố")
            btn_detail.setCursor(Qt.PointingHandCursor)
            btn_detail.setStyleSheet(STYLE_BTN_SLATE)
            btn_detail.clicked.connect(lambda: self.dismiss_requested.emit(self.data))
            act_row.addWidget(btn_detail)

        act_row.addStretch()
        layout.addLayout(act_row)


class AlertsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_filter = "all"
        self.alerts_data: List[Dict[str, Any]] = [
            {
                "id": "alt-101",
                "level": "CRITICAL",
                "title": "Phát hiện nghi vấn tấn công ARP Spoofing / Cắt mạng",
                "title_en": "Suspicious ARP Spoofing / Network Cut Off Attack Detected",
                "desc": "Thiết bị lạ tại MAC 00:1A:2B:3C:4D:5E đang liên tục phát tán các gói tin ARP Reply giả mạo nhằm chiếm quyền điều khiển gateway 192.168.1.1 và nghe lén dữ liệu nội bộ.",
                "desc_en": "Rogue device at MAC 00:1A:2B:3C:4D:5E is continuously broadcasting gratuitous ARP replies attempting to impersonate gateway 192.168.1.1.",
                "meta": "Mục tiêu: 192.168.1.1 (Modem Tổng) • Kẻ tấn công: 192.168.1.188 (MAC: 00:1A:2B:3C:4D:5E)",
                "attacker_mac": "00:1A:2B:3C:4D:5E",
                "attacker_ip": "192.168.1.188",
                "time": "10:45:12 • 19/09/2026",
                "source": "Nguồn: WAF Engine / ARP Inspector"
            },
            {
                "id": "alt-102",
                "level": "WARNING",
                "title": "Cảnh báo thiết bị mới gia nhập mạng chưa được gán nhãn",
                "title_en": "Unrecognized Rogue Device Joined Network",
                "desc": "Phát hiện thiết bị IP 192.168.1.115 (iPhone 15 Pro Max) vừa kết nối thành công vào dải Wi-Fi Tổng 192.168.1.0/24.",
                "desc_en": "New device at IP 192.168.1.115 (iPhone 15 Pro Max) joined Primary Wi-Fi subnet 192.168.1.0/24.",
                "meta": "Vị trí: Wi-Fi Tổng (5GHz) • MAC: F8:FF:C2:11:22:33",
                "attacker_mac": "F8:FF:C2:11:22:33",
                "attacker_ip": "192.168.1.115",
                "time": "09:30:18 • 19/09/2026",
                "source": "Nguồn: Network Discovery Service"
            },
            {
                "id": "alt-103",
                "level": "SUCCESS",
                "title": "Tường lửa đồng bộ an toàn quy tắc Inbound/Outbound",
                "title_en": "Firewall Rules Synchronized Successfully",
                "desc": "Đã tự động xác minh tính toàn vẹn danh sách đen MAC phần cứng router và cập nhật quy tắc phòng vệ 2 chiều của Windows Firewall.",
                "desc_en": "Successfully verified hardware router MAC blacklist integrity and synchronized Windows Firewall inbound/outbound rules.",
                "meta": "Trạng thái: 0 quy tắc lỗi • Thời gian đáp ứng: 120ms",
                "attacker_mac": None,
                "attacker_ip": None,
                "time": "08:30:00 • 19/09/2026",
                "source": "Nguồn: Security Shield Module"
            },
            {
                "id": "alt-104",
                "level": "INFO",
                "title": "Quét mạng định kỳ hoàn tất trên 2 dải Subnet",
                "title_en": "Scheduled Subnet Survey Completed",
                "desc": "Khảo sát hoàn tất 508 địa chỉ IP trên 192.168.1.0/24 & 192.168.110.0/24. Phát hiện 7 thiết bị hoạt động bình thường, không phát hiện xung đột IP.",
                "desc_en": "Surveyed 508 IPs across 192.168.1.0/24 and 192.168.110.0/24. 7 active devices identified with zero IP conflicts.",
                "meta": "Tổng thiết bị: 7 trực tuyến • Độ trễ RTT: 5ms",
                "attacker_mac": None,
                "attacker_ip": None,
                "time": "08:00:15 • 19/09/2026",
                "source": "Nguồn: Scan Scheduler Worker"
            }
        ]

        self._init_ui()
        self.retranslate_ui()
        self.load_alerts()
        i18n.language_changed.connect(self._on_lang_changed)

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(14)
        main_layout.setContentsMargins(24, 20, 24, 20)

        # 1. Header Toolbar
        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(3)
        self.lbl_title = QLabel("Cảnh Báo An Ninh Mạng")
        self.lbl_title.setStyleSheet("font-size: 22px; font-weight: 800; color: #F8FAFC; letter-spacing: 0.5px;")
        self.lbl_subtitle = QLabel("Hệ thống phát hiện xâm nhập thời gian thực (IDS), phân tích bất thường và phản hồi tức thì")
        self.lbl_subtitle.setStyleSheet("color: #94A3B8; font-size: 13px;")
        title_box.addWidget(self.lbl_title)
        title_box.addWidget(self.lbl_subtitle)
        header_layout.addLayout(title_box)

        header_layout.addStretch()

        # Nút Mô phỏng sự cố mới (Amber)
        self.btn_simulate = QPushButton(" Mô phỏng sự cố mới")
        self.btn_simulate.setIcon(get_app_icon("warning"))
        self.btn_simulate.setIconSize(QSize(15, 15))
        self.btn_simulate.setCursor(Qt.PointingHandCursor)
        self.btn_simulate.setStyleSheet(STYLE_BTN_AMBER)
        self.btn_simulate.clicked.connect(self._simulate_new_alert)
        header_layout.addWidget(self.btn_simulate)

        # Nút Đánh dấu đã đọc (Slate)
        self.btn_mark_read = QPushButton(" Đánh dấu đã đọc")
        self.btn_mark_read.setIcon(get_app_icon("check"))
        self.btn_mark_read.setIconSize(QSize(15, 15))
        self.btn_mark_read.setCursor(Qt.PointingHandCursor)
        self.btn_mark_read.setStyleSheet(STYLE_BTN_SLATE)
        self.btn_mark_read.clicked.connect(self._mark_all_read)
        header_layout.addWidget(self.btn_mark_read)

        main_layout.addLayout(header_layout)

        # 2. Filter Pills: Tất cả, Critical, Warning, Success, Info
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(8)

        self.btn_f_all = QPushButton("Tất cả (4)")
        self.btn_f_crit = QPushButton("Critical (1)")
        self.btn_f_warn = QPushButton("Warning (1)")
        self.btn_f_succ = QPushButton("Success (1)")
        self.btn_f_info = QPushButton("Info (1)")

        self.filter_buttons = [
            ("all", self.btn_f_all),
            ("CRITICAL", self.btn_f_crit),
            ("WARNING", self.btn_f_warn),
            ("SUCCESS", self.btn_f_succ),
            ("INFO", self.btn_f_info),
        ]

        for f_key, btn in self.filter_buttons:
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda chk=False, k=f_key: self._set_filter(k))
            filter_layout.addWidget(btn)

        filter_layout.addStretch()
        main_layout.addLayout(filter_layout)
        self._update_filter_styles()

        # 3. Danh sách Alert Cards cuộn được
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")

        self.cards_container = QWidget()
        self.cards_container.setStyleSheet("background: transparent;")
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(12)

        scroll.setWidget(self.cards_container)
        main_layout.addWidget(scroll, 1)

    def _set_filter(self, filter_key: str):
        self.active_filter = filter_key
        self._update_filter_styles()
        self.load_alerts()

    def _update_filter_styles(self):
        for k, btn in self.filter_buttons:
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

    def load_alerts(self):
        # Clear existing cards
        while self.cards_layout.count():
            child = self.cards_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        filtered = [
            a for a in self.alerts_data
            if self.active_filter == "all" or a["level"] == self.active_filter
        ]

        for alert in filtered:
            card = AlertCard(alert, parent=self.cards_container)
            card.block_requested.connect(self._on_block_attacker)
            card.dismiss_requested.connect(self._on_dismiss_alert)
            self.cards_layout.addWidget(card)

        self.cards_layout.addStretch()

    def _simulate_new_alert(self):
        new_id = f"alt-{len(self.alerts_data) + 101}"
        cur_time = time.strftime("%H:%M:%S • %d/%m/%Y")
        item = {
            "id": new_id,
            "level": "WARNING",
            "title": "Phát hiện lưu lượng quét cổng TCP Port Scan bất thường",
            "title_en": "Abnormal TCP Port Scanning Traffic Detected",
            "desc": "Thiết bị IP 192.168.1.199 đang cố gắng thăm dò hàng loạt cổng dịch vụ (21, 22, 80, 443, 8080) trong mạng nội bộ.",
            "desc_en": "Device at IP 192.168.1.199 is aggressively probing internal service ports (21, 22, 80, 443, 8080).",
            "meta": "Mục tiêu: Toàn bộ subnet • Kẻ tấn công: 192.168.1.199 (MAC: 1C:2B:3C:4D:5E:6F)",
            "attacker_mac": "1C:2B:3C:4D:5E:6F",
            "attacker_ip": "192.168.1.199",
            "time": cur_time,
            "source": "Nguồn: WAF Port-Scan Analyzer"
        }
        self.alerts_data.insert(0, item)
        self.load_alerts()
        QMessageBox.information(self, "Mô Phỏng Cảnh Báo", "Đã tạo sự cố mô phỏng mới thành công trên hệ thống IDS.")

    def _mark_all_read(self):
        QMessageBox.information(self, "Thông Báo", "Đã đánh dấu tất cả cảnh báo là đã đọc.")

    def _on_block_attacker(self, data: dict):
        mac = data.get("attacker_mac")
        ip = data.get("attacker_ip")
        QMessageBox.information(self, "Đã Chặn", f"Đã kích hoạt tường lửa ngăn chặn kẻ tấn công {ip} ({mac}) thành công!")

    def _on_dismiss_alert(self, data: dict):
        if data in self.alerts_data:
            self.alerts_data.remove(data)
            self.load_alerts()

    def _on_lang_changed(self, lang: str):
        self.retranslate_ui()
        self.load_alerts()

    def retranslate_ui(self):
        is_vi = i18n.current_lang == "vi"
        if is_vi:
            self.lbl_title.setText("Cảnh Báo An Ninh Mạng")
            self.lbl_subtitle.setText("Hệ thống phát hiện xâm nhập thời gian thực (IDS), phân tích bất thường và phản hồi tức thì")
            self.btn_simulate.setText(" Mô phỏng sự cố mới")
            self.btn_mark_read.setText(" Đánh dấu đã đọc")
        else:
            self.lbl_title.setText("Security Alerts & Incidents")
            self.lbl_subtitle.setText("Real-time intrusion detection system (IDS), anomaly analysis, and instant defense")
            self.btn_simulate.setText(" Simulate Alert")
            self.btn_mark_read.setText(" Mark All as Read")

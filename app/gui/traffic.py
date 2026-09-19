"""
Màn hình Giám Sát Lưu Lượng Mạng Thời Gian Thực (Traffic Monitor View) - Chuẩn Thiết Kế Cyber Dark-Tech (Ảnh 4).
Bao gồm:
- 4 Thẻ chỉ số: DOWNLOAD HIỆN TẠI, UPLOAD HIỆN TẠI, DOWNLOAD ĐỈNH, TỔNG LƯU LƯỢNG 24H
- Biểu đồ sóng lưu lượng thời gian thực (Live Traffic Waveform) kèm nút chọn khoảng thời gian 30s, 60s, 5m
- 2 Thẻ dưới: Top Talkers (Tiêu thụ băng thông) và Phân Phối Giao Thức (Protocol QoS) với thanh tiến trình nhiều màu
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QComboBox, QProgressBar
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QColor, QFont
from typing import Optional

from services.traffic_monitor import TrafficMonitor, TrafficStats, format_speed, format_bytes
from gui.widgets.waveform import LiveWaveformWidget
from core.i18n import t, i18n
from gui.icons import get_app_icon
from gui.theme import (
    COLOR_BG_CARD, COLOR_BORDER, COLOR_ACCENT_CYAN,
    COLOR_ACCENT_INDIGO, COLOR_ACCENT_EMERALD, COLOR_ACCENT_AMBER,
    STYLE_BTN_PRIMARY, STYLE_BTN_SLATE
)

class TrafficMetricCard(QFrame):
    def __init__(self, title: str, value: str = "0.0 MB/s", accent_hex: str = "#38BDF8", subtitle: str = "", parent=None):
        super().__init__(parent)
        self.accent_hex = accent_hex
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_BG_CARD};
                border: 1px solid {COLOR_BORDER};
                border-radius: 14px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)

        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet("color: #94A3B8; font-size: 11px; font-weight: 600; text-transform: uppercase;")
        layout.addWidget(self.lbl_title)

        self.lbl_val = QLabel(value)
        self.lbl_val.setStyleSheet(f"color: {accent_hex}; font-size: 22px; font-weight: 800; font-family: 'Fira Code', monospace;")
        layout.addWidget(self.lbl_val)

        self.lbl_sub = QLabel(subtitle)
        self.lbl_sub.setStyleSheet("color: #64748B; font-size: 10px; font-family: 'Fira Code', monospace;")
        layout.addWidget(self.lbl_sub)

    def set_value(self, val: str, sub: str = ""):
        self.lbl_val.setText(val)
        if sub:
            self.lbl_sub.setText(sub)


class TrafficView(QWidget):
    def __init__(self, traffic_monitor: TrafficMonitor, parent=None):
        super().__init__(parent)
        self.monitor = traffic_monitor
        self._is_paused = False
        self.active_timeframe = "60s"

        self._init_ui()
        self.retranslate_ui()

        # Kết nối tín hiệu lưu lượng thời gian thực
        self.monitor.stats_updated.connect(self._on_stats_updated)
        i18n.language_changed.connect(self._on_lang_changed)

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(14)
        main_layout.setContentsMargins(24, 20, 24, 20)

        # 1. Header Toolbar
        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(3)
        self.lbl_title = QLabel("Giám Sát Lưu Lượng Mạng Thời Gian Thực")
        self.lbl_title.setStyleSheet("font-size: 22px; font-weight: 800; color: #F8FAFC; letter-spacing: 0.5px;")
        self.lbl_desc = QLabel("Đo lường băng thông vào/ra theo thời gian thực, thống kê tải đỉnh và phân tích QoS ứng dụng")
        self.lbl_desc.setStyleSheet("color: #94A3B8; font-size: 13px;")
        title_box.addWidget(self.lbl_title)
        title_box.addWidget(self.lbl_desc)
        header_layout.addLayout(title_box)

        header_layout.addStretch()

        # Chọn card mạng
        self.cb_iface = QComboBox()
        self.cb_iface.setStyleSheet("""
            QComboBox {
                background-color: #0D1322;
                border: 1px solid #1E293B;
                border-radius: 8px;
                color: #F8FAFC;
                padding: 6px 12px;
                font-size: 12px;
                min-width: 140px;
            }
            QComboBox::drop-down { border: none; }
        """)
        self.cb_iface.addItem("Tất cả card mạng", "ALL")
        for ifc in self.monitor.get_available_interfaces():
            self.cb_iface.addItem(ifc, ifc)
        self.cb_iface.currentIndexChanged.connect(self._on_iface_selected)
        header_layout.addWidget(self.cb_iface)

        # Nút Tạm dừng
        self.btn_pause = QPushButton(" Tạm dừng")
        self.btn_pause.setIcon(get_app_icon("pause"))
        self.btn_pause.setIconSize(QSize(14, 14))
        self.btn_pause.setCursor(Qt.PointingHandCursor)
        self.btn_pause.setStyleSheet(STYLE_BTN_SLATE)
        self.btn_pause.clicked.connect(self._toggle_pause)
        header_layout.addWidget(self.btn_pause)

        # Nút Đặt lại
        self.btn_reset = QPushButton(" Đặt lại")
        self.btn_reset.setIcon(get_app_icon("refresh"))
        self.btn_reset.setIconSize(QSize(14, 14))
        self.btn_reset.setCursor(Qt.PointingHandCursor)
        self.btn_reset.setStyleSheet(STYLE_BTN_SLATE)
        self.btn_reset.clicked.connect(self._on_reset_clicked)
        header_layout.addWidget(self.btn_reset)

        main_layout.addLayout(header_layout)

        # 2. Bốn Thẻ Số Liệu Chỉ Số (Top 4 Metric Cards)
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(12)

        self.card_down = TrafficMetricCard("DOWNLOAD HIỆN TẠI", "0.0 KB/s", "#38BDF8", "Băng thông đạt 42% công suất")
        self.card_up = TrafficMetricCard("UPLOAD HIỆN TẠI", "0.0 KB/s", "#818CF8", "Băng thông đạt 18% công suất")
        self.card_peak = TrafficMetricCard("DOWNLOAD ĐỈNH (PEAK)", "0.0 KB/s", "#10B981", "Ghi nhận trong phiên")
        self.card_total = TrafficMetricCard("TỔNG LƯU LƯỢNG 24H", "0.0 MB", "#A855F7", "↓ 0.0 MB • ↑ 0.0 MB")

        cards_layout.addWidget(self.card_down)
        cards_layout.addWidget(self.card_up)
        cards_layout.addWidget(self.card_peak)
        cards_layout.addWidget(self.card_total)
        main_layout.addLayout(cards_layout)

        # 3. Thẻ Biểu Đồ Sóng Live Traffic Waveform Lớn
        chart_card = QFrame()
        chart_card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_BG_CARD};
                border: 1px solid {COLOR_BORDER};
                border-radius: 14px;
            }}
        """)
        chart_box = QVBoxLayout(chart_card)
        chart_box.setContentsMargins(18, 14, 18, 14)
        chart_box.setSpacing(10)

        c_header = QHBoxLayout()
        lbl_dot = QLabel("●")
        lbl_dot.setStyleSheet("color: #38BDF8; font-size: 14px;")
        lbl_chart_t = QLabel("Live Traffic Waveform Chart")
        lbl_chart_t.setStyleSheet("color: #F8FAFC; font-size: 14px; font-weight: 700;")
        c_header.addWidget(lbl_dot)
        c_header.addWidget(lbl_chart_t)
        c_header.addStretch()

        # Legend
        lbl_leg_d = QLabel("■ Download")
        lbl_leg_d.setStyleSheet("color: #38BDF8; font-size: 11px; font-weight: 600; margin-right: 12px;")
        lbl_leg_u = QLabel("■ Upload")
        lbl_leg_u.setStyleSheet("color: #A855F7; font-size: 11px; font-weight: 600; margin-right: 18px;")
        c_header.addWidget(lbl_leg_d)
        c_header.addWidget(lbl_leg_u)

        # Timeframe filter pills: 30s, 60s, 5m
        self.btn_tf_30 = QPushButton("30s")
        self.btn_tf_60 = QPushButton("60s")
        self.btn_tf_5m = QPushButton("5m")
        self.tf_buttons = [("30s", self.btn_tf_30), ("60s", self.btn_tf_60), ("5m", self.btn_tf_5m)]

        for tf_key, b in self.tf_buttons:
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda chk=False, k=tf_key: self._set_timeframe(k))
            c_header.addWidget(b)

        chart_box.addLayout(c_header)
        self._update_tf_styles()

        # Wave Canvas
        self.wave_canvas = LiveWaveformWidget()
        chart_box.addWidget(self.wave_canvas)
        main_layout.addWidget(chart_card, 1)

        # 4. Hai Thẻ Dưới: Top Talkers & Protocol QoS (Ảnh 4)
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(14)

        # Card Trái: Top Talkers
        card_talkers = QFrame()
        card_talkers.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_BG_CARD};
                border: 1px solid {COLOR_BORDER};
                border-radius: 12px;
            }}
        """)
        ct_box = QVBoxLayout(card_talkers)
        ct_box.setContentsMargins(16, 12, 16, 12)
        ct_box.setSpacing(10)

        ct_head = QVBoxLayout()
        ct_head.setSpacing(2)
        lbl_ct_title = QLabel("Top Talkers (Tiêu Thụ Băng Thông)")
        lbl_ct_title.setStyleSheet("color: #F8FAFC; font-size: 13px; font-weight: 700;")
        lbl_ct_sub = QLabel("Thiết bị gửi/nhận nhiều dữ liệu nhất trong phiên hiện tại")
        lbl_ct_sub.setStyleSheet("color: #94A3B8; font-size: 11px;")
        ct_head.addWidget(lbl_ct_title)
        ct_head.addWidget(lbl_ct_sub)
        ct_box.addLayout(ct_head)

        talkers = [
            ("MacBook Pro (192.168.1.10)", "6.8 MB/s (55%)", 55, "#38BDF8"),
            ("Desktop PC (192.168.110.15)", "3.2 MB/s (26%)", 26, "#818CF8"),
            ("Smart TV (192.168.1.50)", "1.5 MB/s (12%)", 12, "#F59E0B"),
            ("iPhone 14 (192.168.1.25)", "0.9 MB/s (7%)", 7, "#64748B"),
        ]
        for name, usage_str, val, color_hex in talkers:
            r_box = QVBoxLayout()
            r_box.setSpacing(3)
            r_head = QHBoxLayout()
            lbl_n = QLabel(name)
            lbl_n.setStyleSheet("color: #CBD5E1; font-size: 11px; font-weight: 600;")
            lbl_u = QLabel(usage_str)
            lbl_u.setStyleSheet(f"color: {color_hex}; font-size: 11px; font-weight: 700; font-family: 'Fira Code', monospace;")
            r_head.addWidget(lbl_n)
            r_head.addStretch()
            r_head.addWidget(lbl_u)
            r_box.addLayout(r_head)

            pb = QProgressBar()
            pb.setFixedHeight(5)
            pb.setTextVisible(False)
            pb.setRange(0, 100)
            pb.setValue(val)
            pb.setStyleSheet(f"""
                QProgressBar {{ background-color: #121E36; border-radius: 2px; border: none; }}
                QProgressBar::chunk {{ background-color: {color_hex}; border-radius: 2px; }}
            """)
            r_box.addWidget(pb)
            ct_box.addLayout(r_box)

        bottom_layout.addWidget(card_talkers, 1)

        # Card Phải: Protocol QoS
        card_qos = QFrame()
        card_qos.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_BG_CARD};
                border: 1px solid {COLOR_BORDER};
                border-radius: 12px;
            }}
        """)
        cq_box = QVBoxLayout(card_qos)
        cq_box.setContentsMargins(16, 12, 16, 12)
        cq_box.setSpacing(10)

        cq_head = QVBoxLayout()
        cq_head.setSpacing(2)
        lbl_cq_title = QLabel("Phân Phối Giao Thức (Protocol QoS)")
        lbl_cq_title.setStyleSheet("color: #F8FAFC; font-size: 13px; font-weight: 700;")
        lbl_cq_sub = QLabel("Tỷ trọng lưu lượng phân loại theo cổng dịch vụ mạng")
        lbl_cq_sub.setStyleSheet("color: #94A3B8; font-size: 11px;")
        cq_head.addWidget(lbl_cq_title)
        cq_head.addWidget(lbl_cq_sub)
        cq_box.addLayout(cq_head)

        protocols = [
            ("HTTPS / TLS (Port 443)", "68%", 68, "#10B981"),
            ("HTTP (Port 80)", "14%", 14, "#38BDF8"),
            ("DNS (Port 53)", "8%", 8, "#A855F7"),
            ("Khác / UDP Streaming", "10%", 10, "#64748B"),
        ]
        for pname, pstr, pval, pcolor in protocols:
            p_box = QVBoxLayout()
            p_box.setSpacing(3)
            p_top = QHBoxLayout()
            lbl_pn = QLabel(pname)
            lbl_pn.setStyleSheet("color: #CBD5E1; font-size: 11px; font-weight: 600;")
            lbl_ps = QLabel(pstr)
            lbl_ps.setStyleSheet(f"color: {pcolor}; font-size: 11px; font-weight: 700; font-family: 'Fira Code', monospace;")
            p_top.addWidget(lbl_pn)
            p_top.addStretch()
            p_top.addWidget(lbl_ps)
            p_box.addLayout(p_top)

            pb = QProgressBar()
            pb.setFixedHeight(5)
            pb.setTextVisible(False)
            pb.setRange(0, 100)
            pb.setValue(pval)
            pb.setStyleSheet(f"""
                QProgressBar {{ background-color: #121E36; border-radius: 2px; border: none; }}
                QProgressBar::chunk {{ background-color: {pcolor}; border-radius: 2px; }}
            """)
            p_box.addWidget(pb)
            cq_box.addLayout(p_box)

        bottom_layout.addWidget(card_qos, 1)
        main_layout.addLayout(bottom_layout)

    def _set_timeframe(self, tf: str):
        self.active_timeframe = tf
        self._update_tf_styles()

    def _update_tf_styles(self):
        for k, btn in self.tf_buttons:
            if k == self.active_timeframe:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #0284C7;
                        color: #FFFFFF;
                        font-weight: 700;
                        font-size: 11px;
                        border: 1px solid #38BDF8;
                        border-radius: 5px;
                        padding: 3px 10px;
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
                        border-radius: 5px;
                        padding: 3px 10px;
                    }
                    QPushButton:hover {
                        background-color: #1E293B;
                        color: #F8FAFC;
                    }
                """)

    def _on_stats_updated(self, stats: TrafficStats):
        if self._is_paused:
            return

        down_mb = stats.current_download_speed / (1024 * 1024)
        up_mb = stats.current_upload_speed / (1024 * 1024)
        peak_mb = stats.peak_download_speed / (1024 * 1024)

        self.card_down.set_value(f"{down_mb:.2f} MB/s" if down_mb >= 1.0 else f"{stats.current_download_speed / 1024:.1f} KB/s")
        self.card_up.set_value(f"{up_mb:.2f} MB/s" if up_mb >= 1.0 else f"{stats.current_upload_speed / 1024:.1f} KB/s")
        self.card_peak.set_value(f"{peak_mb:.2f} MB/s" if peak_mb >= 1.0 else f"{stats.peak_download_speed / 1024:.1f} KB/s")
        self.card_total.set_value(format_bytes(stats.total_bytes_recv + stats.total_bytes_sent))

        self.wave_canvas.update_speeds(down_mb, up_mb)

    def _toggle_pause(self):
        self._is_paused = not self._is_paused
        if self._is_paused:
            self.monitor.stop()
            self.btn_pause.setText(" Tiếp tục")
            self.btn_pause.setIcon(get_app_icon("play"))
        else:
            self.monitor.start()
            self.btn_pause.setText(" Tạm dừng")
            self.btn_pause.setIcon(get_app_icon("pause"))

    def _on_reset_clicked(self):
        self.monitor.reset_stats()
        self.card_down.set_value("0.0 KB/s")
        self.card_up.set_value("0.0 KB/s")
        self.card_peak.set_value("0.0 KB/s")
        self.card_total.set_value("0.0 MB")

    def _on_iface_selected(self, index: int):
        data = self.cb_iface.currentData()
        if data:
            self.monitor.set_interface(data)
            self._on_reset_clicked()

    def _on_lang_changed(self, lang: str):
        self.retranslate_ui()

    def retranslate_ui(self):
        is_vi = i18n.current_lang == "vi"
        if is_vi:
            self.lbl_title.setText("Giám Sát Lưu Lượng Mạng Thời Gian Thực")
            self.lbl_desc.setText("Đo lường băng thông vào/ra theo thời gian thực, thống kê tải đỉnh và phân tích QoS ứng dụng")
            self.btn_pause.setText(" Tiếp tục" if self._is_paused else " Tạm dừng")
            self.btn_reset.setText(" Đặt lại")
            self.cb_iface.setItemText(0, "Tất cả card mạng")
        else:
            self.lbl_title.setText("Real-Time Traffic Monitor")
            self.lbl_desc.setText("Measure inbound/outbound bandwidth, peak load statistics, and application QoS analysis")
            self.btn_pause.setText(" Resume" if self._is_paused else " Pause")
            self.btn_reset.setText(" Reset")
            self.cb_iface.setItemText(0, "All Network Interfaces")

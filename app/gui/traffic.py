"""
Màn hình chuyên sâu: Biểu đồ mức sử dụng mạng & Phân tích băng thông (Song ngữ VI / EN).
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QComboBox, QGridLayout, QGroupBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor
from typing import Optional

from services.traffic_monitor import TrafficMonitor, TrafficStats, format_speed, format_bytes
from gui.traffic_chart import TrafficChart
from core.i18n import t, i18n
from gui.theme import (
    MetricCard, COLOR_BG_CARD, COLOR_BORDER, COLOR_ACCENT_INDIGO,
    COLOR_ACCENT_CYAN, COLOR_ACCENT_EMERALD, COLOR_ACCENT_AMBER
)


class TrafficStatCard(MetricCard):
    """Thẻ số liệu lưu lượng kế thừa từ MetricCard hiện đại."""
    def __init__(self, title_key: str, value: str = "0 B/s", color_hex: str = "#10B981", parent=None):
        icon = "📊"
        if "down" in title_key and "total" in title_key:
            icon = "📥"
        elif "up" in title_key and "total" in title_key:
            icon = "📤"
        elif "down" in title_key:
            icon = "⬇️"
        elif "up" in title_key:
            icon = "⬆️"
        super().__init__(icon_str=icon, title_key=title_key, value=value, accent_hex=color_hex, parent=parent)


class TrafficView(QWidget):
    def __init__(self, traffic_monitor: TrafficMonitor, parent=None):
        super().__init__(parent)
        self.monitor = traffic_monitor
        self._is_paused = False
        
        self._init_ui()
        self.retranslate_ui()
        
        # Kết nối tín hiệu từ TrafficMonitor
        self.monitor.stats_updated.connect(self._on_stats_updated)
        i18n.language_changed.connect(self._on_lang_changed)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 20, 24, 20)

        # 1. Header Toolbar
        header_layout = QHBoxLayout()

        title_box = QVBoxLayout()
        title_box.setSpacing(3)
        self.lbl_title = QLabel()
        self.lbl_title.setStyleSheet("font-size: 22px; font-weight: 800; color: #F8FAFC; letter-spacing: 0.5px;")
        self.lbl_desc = QLabel()
        self.lbl_desc.setStyleSheet("color: #94A3B8; font-size: 13px;")
        title_box.addWidget(self.lbl_title)
        title_box.addWidget(self.lbl_desc)
        header_layout.addLayout(title_box)

        header_layout.addStretch()

        # Chọn card mạng
        self.lbl_iface_title = QLabel()
        self.lbl_iface_title.setStyleSheet("color: #CBD5E1; font-size: 13px; font-weight: 500;")
        header_layout.addWidget(self.lbl_iface_title)

        self.cb_iface = QComboBox()
        self.cb_iface.addItem(t("traffic_all_ifaces"), "ALL")
        for iface in self.monitor.get_available_interfaces():
            self.cb_iface.addItem(iface, iface)
        self.cb_iface.currentIndexChanged.connect(self._on_iface_selected)
        header_layout.addWidget(self.cb_iface)

        # Nút Tạm dừng / Tiếp tục
        self.btn_pause = QPushButton()
        self.btn_pause.setCursor(Qt.PointingHandCursor)
        self.btn_pause.setStyleSheet("""
            QPushButton {
                background-color: #1E293B;
                color: #F8FAFC;
                font-size: 13px;
                font-weight: 600;
                padding: 8px 16px;
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            QPushButton:hover { background-color: #334155; border: 1px solid #6366F1; }
        """)
        self.btn_pause.clicked.connect(self._toggle_pause)
        header_layout.addWidget(self.btn_pause)

        # Nút Đặt lại số liệu
        self.btn_reset = QPushButton()
        self.btn_reset.setCursor(Qt.PointingHandCursor)
        self.btn_reset.setStyleSheet("""
            QPushButton {
                background-color: #101B33;
                color: #94A3B8;
                font-size: 13px;
                padding: 8px 16px;
                border-radius: 8px;
                border: 1px solid #1E293B;
            }
            QPushButton:hover {
                background-color: #1E293B;
                color: #F8FAFC;
            }
        """)
        self.btn_reset.clicked.connect(self._on_reset_clicked)
        header_layout.addWidget(self.btn_reset)

        layout.addLayout(header_layout)

        # 2. Bốn thẻ số liệu thống kê (Hero MetricCards)
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(14)

        self.card_down = TrafficStatCard("traffic_down_cur", "0 B/s", "#10B981")
        self.card_up = TrafficStatCard("traffic_up_cur", "0 B/s", "#8B5CF6")
        self.card_total_down = TrafficStatCard("traffic_total_down", "0 B", "#06B6D4")
        self.card_total_up = TrafficStatCard("traffic_total_up", "0 B", "#F59E0B")

        cards_layout.addWidget(self.card_down)
        cards_layout.addWidget(self.card_up)
        cards_layout.addWidget(self.card_total_down)
        cards_layout.addWidget(self.card_total_up)
        layout.addLayout(cards_layout)

        # 3. Biểu đồ lưu lượng lớn (Chart)
        self.chart = TrafficChart(max_samples=60, compact=False)
        layout.addWidget(self.chart, 1)

        # 4. Chi tiết bổ sung (Đỉnh tốc độ & Thống kê gói tin)
        bottom_frame = QFrame()
        bottom_frame.setStyleSheet(f"""
            background-color: {COLOR_BG_CARD};
            border: 1px solid {COLOR_BORDER};
            border-radius: 12px;
            padding: 14px;
        """)
        bottom_layout = QHBoxLayout(bottom_frame)
        bottom_layout.setContentsMargins(16, 10, 16, 10)

        # Cột trái: Đỉnh tốc độ
        left_box = QVBoxLayout()
        self.lbl_peak_down = QLabel("• Đỉnh tải về: 0 B/s")
        self.lbl_peak_up = QLabel("• Đỉnh tải lên: 0 B/s")
        self.lbl_status_badge = QLabel("• Trạng thái: Đang theo dõi")
        for lbl in (self.lbl_peak_down, self.lbl_peak_up, self.lbl_status_badge):
            lbl.setStyleSheet("color: #CBD5E1; font-size: 12px; margin: 2px 0;")
            left_box.addWidget(lbl)
        bottom_layout.addLayout(left_box)

        bottom_layout.addStretch()

        # Cột phải: Gói tin
        right_box = QVBoxLayout()
        self.lbl_pkts_recv = QLabel("• Gói tin nhận: 0")
        self.lbl_pkts_sent = QLabel("• Gói tin gửi: 0")
        self.lbl_pkts_err = QLabel("• Lỗi / Drop: 0 / 0")
        for lbl in (self.lbl_pkts_recv, self.lbl_pkts_sent, self.lbl_pkts_err):
            lbl.setStyleSheet("color: #94A3B8; font-size: 12px; margin: 2px 0;")
            right_box.addWidget(lbl)
        bottom_layout.addLayout(right_box)

        layout.addWidget(bottom_frame)

    def retranslate_ui(self):
        self.lbl_title.setText(t("traffic_title"))
        self.lbl_desc.setText(t("traffic_desc"))
        self.lbl_iface_title.setText(t("traffic_iface_select"))
        self.cb_iface.setItemText(0, t("traffic_all_ifaces"))
        self.btn_reset.setText(f"  {t('traffic_btn_reset')}")
        self._update_pause_button_text()

        for card in (self.card_down, self.card_up, self.card_total_down, self.card_total_up):
            card.retranslate_ui()

        self.chart.update()

    def _update_pause_button_text(self):
        if self._is_paused:
            self.btn_pause.setText(f"▶  {t('traffic_btn_resume')}")
            self.lbl_status_badge.setText(f"• {t('traffic_paused_badge')}")
            self.lbl_status_badge.setStyleSheet("color: #F59E0B; font-weight: bold; font-size: 12px;")
        else:
            self.btn_pause.setText(f"⏸  {t('traffic_btn_pause')}")
            self.lbl_status_badge.setText(f"• {t('traffic_live_badge')}")
            self.lbl_status_badge.setStyleSheet("color: #10B981; font-weight: bold; font-size: 12px;")

    def _on_lang_changed(self, lang: str):
        self.retranslate_ui()

    def _toggle_pause(self):
        self._is_paused = not self._is_paused
        if self._is_paused:
            self.monitor.stop()
        else:
            self.monitor.start()
        self._update_pause_button_text()

    def _on_reset_clicked(self):
        self.monitor.reset_stats()
        self.chart.update_data([], 0.0, 0.0, 0.0, 0.0)
        self.card_down.set_value("0 B/s")
        self.card_up.set_value("0 B/s")
        self.card_total_down.set_value("0 B")
        self.card_total_up.set_value("0 B")
        self.lbl_peak_down.setText(f"• {t('traffic_down_peak')}: 0 B/s")
        self.lbl_peak_up.setText(f"• {t('traffic_up_peak')}: 0 B/s")
        self.lbl_pkts_recv.setText(f"• {t('traffic_pkt_recv')}: 0")
        self.lbl_pkts_sent.setText(f"• {t('traffic_pkt_sent')}: 0")
        self.lbl_pkts_err.setText(f"• {t('traffic_pkt_err')}: 0 / 0")

    def _on_iface_selected(self, index: int):
        data = self.cb_iface.currentData()
        if data:
            self.monitor.set_interface(data)
            self._on_reset_clicked()

    def _on_stats_updated(self, stats: TrafficStats):
        if self._is_paused:
            return

        # Cập nhật các thẻ
        self.card_down.set_value(format_speed(stats.current_download_speed))
        self.card_up.set_value(format_speed(stats.current_upload_speed))
        self.card_total_down.set_value(format_bytes(stats.total_bytes_recv))
        self.card_total_up.set_value(format_bytes(stats.total_bytes_sent))

        # Cập nhật biểu đồ
        self.chart.update_data(
            history=stats.history,
            current_down=stats.current_download_speed,
            current_up=stats.current_upload_speed,
            peak_down=stats.peak_download_speed,
            peak_up=stats.peak_upload_speed
        )

        # Cập nhật chi tiết
        self.lbl_peak_down.setText(f"• {t('traffic_down_peak')}: {format_speed(stats.peak_download_speed)}")
        self.lbl_peak_up.setText(f"• {t('traffic_up_peak')}: {format_speed(stats.peak_upload_speed)}")
        self.lbl_pkts_recv.setText(f"• {t('traffic_pkt_recv')}: {stats.packets_recv:,}")
        self.lbl_pkts_sent.setText(f"• {t('traffic_pkt_sent')}: {stats.packets_sent:,}")
        self.lbl_pkts_err.setText(f"• {t('traffic_pkt_err')}: {stats.errin + stats.errout} | Drop: {stats.dropin + stats.dropout}")

"""
Widget biểu đồ lưu lượng mạng thời gian thực (Real-time Network Traffic Chart).
Vẽ bằng QPainter khử răng cưa với hiệu ứng Dark-mode Glowing Curves.
"""

from PySide6.QtWidgets import QWidget, QToolTip
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QPainterPath,
    QLinearGradient, QMouseEvent
)
from typing import List, Optional
from services.traffic_monitor import TrafficSample, format_speed
from core.i18n import t


class TrafficChart(QWidget):
    def __init__(self, max_samples: int = 60, compact: bool = False, parent=None):
        super().__init__(parent)
        self.max_samples = max_samples
        self.compact = compact
        
        self.history: List[TrafficSample] = []
        self.current_download: float = 0.0
        self.current_upload: float = 0.0
        self.peak_download: float = 0.0
        self.peak_upload: float = 0.0
        
        self.hover_index: Optional[int] = None
        self.hover_pos: Optional[QPointF] = None
        
        self.setMouseTracking(True)
        self.setMinimumHeight(115 if compact else 250)
        self.setStyleSheet("background-color: transparent;")

    def update_data(self, history: List[TrafficSample], current_down: float, current_up: float, peak_down: float, peak_up: float):
        self.history = history
        self.current_download = current_down
        self.current_upload = current_up
        self.peak_download = peak_down
        self.peak_upload = peak_up
        self.update()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.compact or not self.history:
            super().mouseMoveEvent(event)
            return

        margin_left = 65
        margin_right = 20
        chart_w = self.width() - margin_left - margin_right
        if chart_w <= 0:
            return

        mouse_x = event.position().x()
        if margin_left <= mouse_x <= self.width() - margin_right:
            ratio = (mouse_x - margin_left) / chart_w
            idx = int(ratio * (len(self.history) - 1))
            idx = max(0, min(len(self.history) - 1, idx))
            self.hover_index = idx
            self.hover_pos = event.position()
            
            sample = self.history[idx]
            tip_text = (
                f"Tải về: {format_speed(sample.download_speed)}\n"
                f"Tải lên: {format_speed(sample.upload_speed)}"
            )
            QToolTip.showText(event.globalPosition().toPoint(), tip_text, self)
        else:
            self.hover_index = None
            self.hover_pos = None
            QToolTip.hideText()

        self.update()

    def leaveEvent(self, event):
        self.hover_index = None
        self.hover_pos = None
        QToolTip.hideText()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)

        w = self.width()
        h = self.height()

        # 1. Vẽ khung nền thẻ
        bg_rect = QRectF(0, 0, w, h)
        painter.setPen(QPen(QColor("#1E293B"), 1))
        painter.setBrush(QBrush(QColor("#0F172A")))
        painter.drawRoundedRect(bg_rect, 10, 10)

        # 2. Thiết lập biên vùng vẽ đồ thị
        margin_left = 35 if self.compact else 65
        margin_right = 15 if self.compact else 20
        margin_top = 28 if self.compact else 45
        margin_bottom = 20 if self.compact else 32

        plot_w = w - margin_left - margin_right
        plot_h = h - margin_top - margin_bottom

        if plot_w <= 10 or plot_h <= 10:
            return

        # 3. Vẽ Legend / Tiêu đề nhỏ phía trên
        font_header = QFont("Segoe UI", 9 if self.compact else 10, QFont.Bold)
        painter.setFont(font_header)

        # Legend Download (Xanh ngọc #10B981)
        down_text = f"⬇ {t('traffic_down_cur')}: {format_speed(self.current_download)}"
        painter.setPen(QColor("#10B981"))
        if self.compact:
            painter.drawText(QRectF(margin_left, 4, 220, 20), Qt.AlignLeft | Qt.AlignVCenter, down_text)
        else:
            painter.drawText(margin_left, 28, down_text)

        # Legend Upload (Tím lam #8B5CF6)
        up_text = f"⬆ {t('traffic_up_cur')}: {format_speed(self.current_upload)}"
        painter.setPen(QColor("#8B5CF6"))
        if self.compact:
            painter.drawText(QRectF(w - margin_right - 220, 4, 220, 20), Qt.AlignRight | Qt.AlignVCenter, up_text)
        else:
            painter.drawText(margin_left + 250, 28, up_text)

        if not self.compact:
            # Đỉnh tốc độ
            painter.setFont(QFont("Segoe UI", 8))
            painter.setPen(QColor("#64748B"))
            peak_text = f"{t('traffic_down_peak')}: {format_speed(self.peak_download)} | {t('traffic_up_peak')}: {format_speed(self.peak_upload)}"
            painter.drawText(w - margin_right - 260, 28, peak_text)

        # 4. Xác định thang đo Y (Max Speed)
        max_speed = 1024 * 10  # Tối thiểu 10 KB/s để biểu đồ không bị bẹt
        if self.history:
            for s in self.history:
                max_speed = max(max_speed, s.download_speed, s.upload_speed)
        max_speed *= 1.25  # Thêm 25% trần để không chạm nóc

        # 5. Vẽ lưới ngang (Horizontal Grid lines)
        num_y_ticks = 3 if self.compact else 4
        painter.setFont(QFont("Segoe UI", 8))
        for i in range(num_y_ticks + 1):
            y_val = (max_speed / num_y_ticks) * i
            y_coord = margin_top + plot_h - (i / num_y_ticks) * plot_h

            # Đường lưới
            pen_grid = QPen(QColor("#1E293B" if i > 0 else "#334155"), 1, Qt.DashLine if i > 0 else Qt.SolidLine)
            painter.setPen(pen_grid)
            painter.drawLine(QPointF(margin_left, y_coord), QPointF(margin_left + plot_w, y_coord))

            # Nhãn trục Y
            if not self.compact:
                painter.setPen(QColor("#64748B"))
                y_label = format_speed(y_val)
                painter.drawText(QRectF(5, y_coord - 9, margin_left - 10, 18), Qt.AlignRight | Qt.AlignVCenter, y_label)

        # 6. Vẽ trục thời gian X (Thời gian lùi dần từ -60s về Hiện tại)
        if not self.compact:
            painter.setPen(QColor("#64748B"))
            time_labels = ["-60s", "-45s", "-30s", "-15s", t("traffic_now")]
            for idx, label in enumerate(time_labels):
                x_pos = margin_left + (idx / 4.0) * plot_w
                # Vạch khấc nhỏ
                painter.drawLine(QPointF(x_pos, margin_top + plot_h), QPointF(x_pos, margin_top + plot_h + 4))
                # Chữ
                rect_lbl = QRectF(x_pos - 25, margin_top + plot_h + 6, 50, 16)
                align = Qt.AlignCenter
                if idx == 0:
                    align = Qt.AlignLeft
                    rect_lbl.setLeft(x_pos)
                elif idx == 4:
                    align = Qt.AlignRight
                    rect_lbl.setRight(x_pos)
                painter.drawText(rect_lbl, align, label)

        # 7. Nếu chưa có dữ liệu
        if len(self.history) < 2:
            painter.setFont(QFont("Segoe UI", 10))
            painter.setPen(QColor("#475569"))
            painter.drawText(QRectF(margin_left, margin_top, plot_w, plot_h), Qt.AlignCenter, t("traffic_waiting"))
            return

        # 8. Tính toán các điểm tọa độ
        samples = self.history
        n = len(samples)
        dx = plot_w / float(self.max_samples - 1)
        x_offset = margin_left + (self.max_samples - n) * dx

        pts_down: List[QPointF] = []
        pts_up: List[QPointF] = []

        for i, s in enumerate(samples):
            x = x_offset + i * dx
            yd = margin_top + plot_h - (s.download_speed / max_speed) * plot_h
            yu = margin_top + plot_h - (s.upload_speed / max_speed) * plot_h
            yd = max(margin_top, min(margin_top + plot_h, yd))
            yu = max(margin_top, min(margin_top + plot_h, yu))
            pts_down.append(QPointF(x, yd))
            pts_up.append(QPointF(x, yu))

        # 9. Vẽ vùng Gradient Fill và Đường viền Download (Xanh ngọc)
        if pts_down:
            path_down_fill = QPainterPath()
            path_down_fill.moveTo(pts_down[0].x(), margin_top + plot_h)
            for p in pts_down:
                path_down_fill.lineTo(p)
            path_down_fill.lineTo(pts_down[-1].x(), margin_top + plot_h)
            path_down_fill.closeSubpath()

            grad_down = QLinearGradient(0, margin_top, 0, margin_top + plot_h)
            grad_down.setColorAt(0.0, QColor(16, 185, 129, 85))
            grad_down.setColorAt(1.0, QColor(16, 185, 129, 5))
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(grad_down))
            painter.drawPath(path_down_fill)

            # Vẽ đường nét phát sáng
            path_down_line = QPainterPath()
            path_down_line.moveTo(pts_down[0])
            for p in pts_down[1:]:
                path_down_line.lineTo(p)
            painter.setPen(QPen(QColor("#10B981"), 2.2))
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(path_down_line)

        # 10. Vẽ vùng Gradient Fill và Đường viền Upload (Tím lam)
        if pts_up:
            path_up_fill = QPainterPath()
            path_up_fill.moveTo(pts_up[0].x(), margin_top + plot_h)
            for p in pts_up:
                path_up_fill.lineTo(p)
            path_up_fill.lineTo(pts_up[-1].x(), margin_top + plot_h)
            path_up_fill.closeSubpath()

            grad_up = QLinearGradient(0, margin_top, 0, margin_top + plot_h)
            grad_up.setColorAt(0.0, QColor(139, 92, 246, 75))
            grad_up.setColorAt(1.0, QColor(139, 92, 246, 5))
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(grad_up))
            painter.drawPath(path_up_fill)

            # Vẽ đường nét phát sáng
            path_up_line = QPainterPath()
            path_up_line.moveTo(pts_up[0])
            for p in pts_up[1:]:
                path_up_line.lineTo(p)
            painter.setPen(QPen(QColor("#8B5CF6"), 1.8))
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(path_up_line)

        # 11. Vẽ chấm sáng ở điểm mới nhất (Current Point Glow)
        if pts_down:
            last_p_d = pts_down[-1]
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(16, 185, 129, 120))
            painter.drawEllipse(last_p_d, 6, 6)
            painter.setBrush(QColor("#10B981"))
            painter.drawEllipse(last_p_d, 3.5, 3.5)

        if pts_up:
            last_p_u = pts_up[-1]
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(139, 92, 246, 120))
            painter.drawEllipse(last_p_u, 5, 5)
            painter.setBrush(QColor("#8B5CF6"))
            painter.drawEllipse(last_p_u, 3, 3)

        # 12. Vẽ đường gióng hover khi người dùng rê chuột
        if not self.compact and self.hover_pos and pts_down:
            hx = self.hover_pos.x()
            painter.setPen(QPen(QColor("#E2E8F0"), 1, Qt.DotLine))
            painter.drawLine(QPointF(hx, margin_top), QPointF(hx, margin_top + plot_h))

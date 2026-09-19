"""
Biểu đồ sóng động (Live Waveform Canvas Widget) theo thời gian thực.
"""

import math
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QPainterPath, QLinearGradient

class LiveWaveformWidget(QWidget):
    """Vẽ biểu đồ sóng động (Waveform) khử răng cưa phát sáng theo thời gian thực."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.step = 0
        self.current_download_mbps = 24.5
        self.current_upload_mbps = 8.2
        self.setFixedHeight(120)
        self.setMinimumWidth(300)

        # Timer hoạt họa 30fps
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate_step)
        self.timer.start(33)

    def _animate_step(self):
        self.step += 1
        self.update()

    def update_speeds(self, down_mbps: float, up_mbps: float):
        self.current_download_mbps = down_mbps
        self.current_upload_mbps = up_mbps

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = float(self.width())
        h = float(self.height())
        mid_y = h / 2.0

        # Nền tối tinh tế khớp giao diện
        painter.setPen(QPen(QColor(255, 255, 255, 15), 1))
        painter.setBrush(QColor("#070E1E"))
        painter.drawRoundedRect(QRectF(0, 0, w, h), 10, 10)

        # 1. Đường sóng Download (Cyan #38BDF8)
        down_path = QPainterPath()
        down_path.moveTo(0, mid_y)
        for x in range(0, int(w) + 1, 3):
            rad = (x + self.step * 1.8) * 0.035
            rad2 = (x + self.step * 0.9) * 0.018
            amp = 18.0 + min(12.0, self.current_download_mbps * 0.3)
            y = mid_y + math.sin(rad) * amp + math.sin(rad2) * 8.0
            down_path.lineTo(x, y)

        down_fill = QPainterPath(down_path)
        down_fill.lineTo(w, h)
        down_fill.lineTo(0, h)
        down_fill.closeSubpath()

        grad_cyan = QLinearGradient(0, 0, 0, h)
        grad_cyan.setColorAt(0, QColor(56, 189, 248, 45))
        grad_cyan.setColorAt(1, QColor(56, 189, 248, 0))
        painter.fillPath(down_fill, grad_cyan)

        pen_cyan = QPen(QColor("#38BDF8"), 2.2)
        painter.strokePath(down_path, pen_cyan)

        # 2. Đường sóng Upload (Purple #A855F7)
        up_path = QPainterPath()
        up_path.moveTo(0, mid_y)
        for x in range(0, int(w) + 1, 3):
            rad = (x + self.step * 1.2) * 0.028
            rad2 = (x - self.step * 0.7) * 0.015
            amp = 14.0 + min(8.0, self.current_upload_mbps * 0.2)
            y = mid_y + math.cos(rad) * amp + math.sin(rad2) * 6.0
            up_path.lineTo(x, y)

        pen_purple = QPen(QColor("#A855F7"), 2.0)
        painter.strokePath(up_path, pen_purple)

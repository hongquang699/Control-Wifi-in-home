"""
Dịch vụ theo dõi và phân tích lưu lượng mạng thời gian thực (Real-time Network Traffic Monitor).
Sử dụng psutil để thu thập số liệu I/O mạng và phát tín hiệu định kỳ cho giao diện người dùng.
"""

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from collections import deque
from PySide6.QtCore import QObject, QTimer, Signal

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


@dataclass
class TrafficSample:
    timestamp: float
    bytes_recv: int
    bytes_sent: int
    download_speed: float  # bytes/sec
    upload_speed: float    # bytes/sec


@dataclass
class TrafficStats:
    interface: str
    current_download_speed: float  # bytes/sec
    current_upload_speed: float    # bytes/sec
    peak_download_speed: float     # bytes/sec
    peak_upload_speed: float       # bytes/sec
    total_bytes_recv: int          # bytes
    total_bytes_sent: int          # bytes
    packets_recv: int
    packets_sent: int
    errin: int
    errout: int
    dropin: int
    dropout: int
    history: List[TrafficSample] = field(default_factory=list)


def format_speed(bytes_per_sec: float) -> str:
    """Chuyển đổi tốc độ bytes/s sang chuỗi dễ đọc (B/s, KB/s, MB/s, GB/s)."""
    if bytes_per_sec < 1024:
        return f"{bytes_per_sec:.0f} B/s"
    elif bytes_per_sec < 1024 * 1024:
        return f"{bytes_per_sec / 1024:.1f} KB/s"
    elif bytes_per_sec < 1024 * 1024 * 1024:
        return f"{bytes_per_sec / (1024 * 1024):.2f} MB/s"
    else:
        return f"{bytes_per_sec / (1024 * 1024 * 1024):.2f} GB/s"


def format_bytes(total_bytes: int) -> str:
    """Chuyển đổi tổng dung lượng byte sang chuỗi dễ đọc (B, KB, MB, GB)."""
    if total_bytes < 1024:
        return f"{total_bytes} B"
    elif total_bytes < 1024 * 1024:
        return f"{total_bytes / 1024:.1f} KB"
    elif total_bytes < 1024 * 1024 * 1024:
        return f"{total_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{total_bytes / (1024 * 1024 * 1024):.2f} GB"


class TrafficMonitor(QObject):
    """
    Theo dõi lưu lượng mạng định kỳ mỗi giây bằng QTimer.
    Phát tín hiệu stats_updated(TrafficStats) cho UI hiển thị biểu đồ.
    """
    stats_updated = Signal(object)  # Emits TrafficStats

    def __init__(self, max_history_seconds: int = 60, parent=None):
        super().__init__(parent)
        self.max_history = max_history_seconds
        self.selected_interface: str = "ALL"  # "ALL" hoặc tên card mạng cụ thể
        
        self._history: deque[TrafficSample] = deque(maxlen=self.max_history)
        self._last_time: Optional[float] = None
        self._last_bytes_recv: Optional[int] = None
        self._last_bytes_sent: Optional[int] = None
        
        # Thống kê tích lũy phiên làm việc
        self._session_start_recv: Optional[int] = None
        self._session_start_sent: Optional[int] = None
        self._peak_download: float = 0.0
        self._peak_upload: float = 0.0
        
        self.timer = QTimer(self)
        self.timer.setInterval(1000)  # 1 giây
        self.timer.timeout.connect(self._poll_traffic)

    @staticmethod
    def get_available_interfaces() -> List[str]:
        """Lấy danh sách các card mạng có thể theo dõi trên hệ thống."""
        if not PSUTIL_AVAILABLE:
            return []
        try:
            return sorted(list(psutil.net_io_counters(pernic=True).keys()))
        except Exception:
            return []

    def set_interface(self, iface_name: str):
        """Chuyển đổi card mạng cần theo dõi ("ALL" hoặc tên card)."""
        if self.selected_interface != iface_name:
            self.selected_interface = iface_name
            self.reset_stats()

    def reset_stats(self):
        """Đặt lại số liệu thống kê khi đổi card mạng hoặc người dùng yêu cầu."""
        self._history.clear()
        self._last_time = None
        self._last_bytes_recv = None
        self._last_bytes_sent = None
        self._session_start_recv = None
        self._session_start_sent = None
        self._peak_download = 0.0
        self._peak_upload = 0.0

    def start(self):
        """Bắt đầu thu thập dữ liệu."""
        if not self.timer.isActive():
            self._poll_traffic()  # Lấy mẫu ban đầu
            self.timer.start()

    def stop(self):
        """Tạm dừng thu thập."""
        if self.timer.isActive():
            self.timer.stop()

    def is_running(self) -> bool:
        return self.timer.isActive()

    def _get_raw_counters(self) -> Optional[Tuple[int, int, int, int, int, int, int, int]]:
        """Lấy (bytes_recv, bytes_sent, packets_recv, packets_sent, errin, errout, dropin, dropout)."""
        if not PSUTIL_AVAILABLE:
            return None

        try:
            if self.selected_interface == "ALL":
                counters = psutil.net_io_counters(pernic=False)
                return (
                    counters.bytes_recv, counters.bytes_sent,
                    counters.packets_recv, counters.packets_sent,
                    counters.errin, counters.errout,
                    counters.dropin, counters.dropout
                )
            else:
                pernic = psutil.net_io_counters(pernic=True)
                if self.selected_interface in pernic:
                    counters = pernic[self.selected_interface]
                    return (
                        counters.bytes_recv, counters.bytes_sent,
                        counters.packets_recv, counters.packets_sent,
                        counters.errin, counters.errout,
                        counters.dropin, counters.dropout
                    )
        except Exception:
            pass
        return None

    def _poll_traffic(self):
        raw = self._get_raw_counters()
        if not raw:
            return

        now = time.time()
        (b_recv, b_sent, p_recv, p_sent, errin, errout, dropin, dropout) = raw

        if self._session_start_recv is None:
            self._session_start_recv = b_recv
            self._session_start_sent = b_sent

        if self._last_time is None:
            self._last_time = now
            self._last_bytes_recv = b_recv
            self._last_bytes_sent = b_sent
            return

        dt = now - self._last_time
        if dt <= 0:
            return

        delta_recv = max(0, b_recv - self._last_bytes_recv)
        delta_sent = max(0, b_sent - self._last_bytes_sent)

        down_speed = delta_recv / dt
        up_speed = delta_sent / dt

        if down_speed > self._peak_download:
            self._peak_download = down_speed
        if up_speed > self._peak_upload:
            self._peak_upload = up_speed

        sample = TrafficSample(
            timestamp=now,
            bytes_recv=b_recv,
            bytes_sent=b_sent,
            download_speed=down_speed,
            upload_speed=up_speed
        )
        self._history.append(sample)

        self._last_time = now
        self._last_bytes_recv = b_recv
        self._last_bytes_sent = b_sent

        total_session_recv = max(0, b_recv - self._session_start_recv)
        total_session_sent = max(0, b_sent - self._session_start_sent)

        stats = TrafficStats(
            interface=self.selected_interface,
            current_download_speed=down_speed,
            current_upload_speed=up_speed,
            peak_download_speed=self._peak_download,
            peak_upload_speed=self._peak_upload,
            total_bytes_recv=total_session_recv,
            total_bytes_sent=total_session_sent,
            packets_recv=p_recv,
            packets_sent=p_sent,
            errin=errin,
            errout=errout,
            dropin=dropin,
            dropout=dropout,
            history=list(self._history)
        )

        self.stats_updated.emit(stats)

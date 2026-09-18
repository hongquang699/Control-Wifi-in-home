"""
Luồng quét định kỳ chạy ngầm (Background Scheduler & Worker) bằng QThread.
"""

import time
from typing import Optional
from PySide6.QtCore import QThread, Signal, QObject
from services.discovery import NetworkDiscoveryService
from core.device import Device
from core.logger import logger

class ScanWorker(QThread):
    # Các tín hiệu Qt giao tiếp với GUI
    scan_started = Signal()
    progress_updated = Signal(int, str)  # percent, message
    scan_finished = Signal(list)         # List[Device]
    new_device_detected = Signal(object) # Device
    status_changed = Signal(object, str) # Device, status
    error_occurred = Signal(str)

    def __init__(
        self,
        discovery_service: Optional[NetworkDiscoveryService] = None,
        subnet: Optional[str] = None,
        parent: Optional[QObject] = None
    ):
        super().__init__(parent)
        self.discovery_service = discovery_service or NetworkDiscoveryService()
        self.subnet = subnet
        self._is_running = True

    def set_subnet(self, subnet: Optional[str]):
        self.subnet = subnet

    def run(self):
        self.scan_started.emit()
        try:
            def on_progress(percent: int, msg: str):
                self.progress_updated.emit(percent, msg)

            def on_new(dev: Device):
                self.new_device_detected.emit(dev)

            def on_change(dev: Device, status: str):
                self.status_changed.emit(dev, status)

            devices = self.discovery_service.run_discovery(
                subnet=self.subnet,
                progress_callback=on_progress,
                on_new_device=on_new,
                on_status_change=on_change
            )
            self.scan_finished.emit(devices)
        except Exception as e:
            logger.error(f"Lỗi trong quá trình quét mạng: {e}")
            self.error_occurred.emit(str(e))

class PeriodicScheduler(QThread):
    """Quản lý kích hoạt quét tự động định kỳ theo khoảng thời gian."""
    trigger_scan = Signal()

    def __init__(self, interval_seconds: int = 60, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.interval_seconds = interval_seconds
        self._active = True

    def set_interval(self, seconds: int):
        self.interval_seconds = max(10, seconds)

    def stop(self):
        self._active = False

    def run(self):
        while self._active:
            # Ngủ theo từng giây để có thể dừng ngay lập tức khi tắt app
            for _ in range(self.interval_seconds):
                if not self._active:
                    return
                time.sleep(1)
            if self._active:
                self.trigger_scan.emit()

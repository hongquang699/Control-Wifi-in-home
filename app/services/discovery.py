"""
Dịch vụ khám phá mạng cục bộ (Network Discovery Service).
"""

from typing import List, Dict, Optional, Callable
from core.device import Device
from core.scanner import NetworkScanner
from core.monitor import NetworkMonitor
from database.devices import DeviceDAO
from database.events import EventDAO
from core.logger import logger

class NetworkDiscoveryService:
    def __init__(
        self,
        scanner: Optional[NetworkScanner] = None,
        monitor: Optional[NetworkMonitor] = None,
        device_dao: Optional[DeviceDAO] = None,
        event_dao: Optional[EventDAO] = None
    ):
        self.device_dao = device_dao or DeviceDAO()
        self.event_dao = event_dao or EventDAO()
        self.scanner = scanner or NetworkScanner()
        self.monitor = monitor or NetworkMonitor(self.device_dao, self.event_dao)

    def run_discovery(
        self,
        subnet: Optional[str] = None,
        progress_callback: Optional[Callable[[int, str], None]] = None,
        on_new_device: Optional[Callable[[Device], None]] = None,
        on_status_change: Optional[Callable[[Device, str], None]] = None
    ) -> List[Device]:
        """
        Thực hiện một chu kỳ quét đầy đủ và đồng bộ database:
        1. Quét dải subnet bằng Nmap/ARP.
        2. Đối chiếu cơ sở dữ liệu SQLite qua NetworkMonitor.
        3. Cập nhật trạng thái và trả về danh sách tất cả thiết bị online.
        """
        self.event_dao.log_event(
            event_type="SCAN_STARTED",
            description=f"Khởi động chu trình quét mạng dải: {subnet or 'Auto'}"
        )

        scanned = self.scanner.scan_subnet(subnet=subnet, progress_callback=progress_callback)
        
        # Đồng bộ trạng thái với DB
        self.monitor.process_scan_results(
            scanned,
            on_new_device=on_new_device,
            on_status_change=on_status_change
        )

        self.event_dao.log_event(
            event_type="SCAN_COMPLETED",
            description=f"Quét hoàn tất: phát hiện {len(scanned)} thiết bị trực tuyến."
        )

        return self.device_dao.get_all_devices()

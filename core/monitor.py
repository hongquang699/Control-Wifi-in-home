"""
Module theo dõi thiết bị, phát hiện thay đổi online/offline và đối chiếu database.
"""

from typing import List, Dict, Callable, Optional
from core.device import Device
from database.devices import DeviceDAO
from database.events import EventDAO
from core.logger import logger

class NetworkMonitor:
    def __init__(
        self,
        device_dao: Optional[DeviceDAO] = None,
        event_dao: Optional[EventDAO] = None,
        offline_threshold_seconds: int = 300
    ):
        self.device_dao = device_dao or DeviceDAO()
        self.event_dao = event_dao or EventDAO()
        self.offline_threshold_seconds = offline_threshold_seconds

    def process_scan_results(
        self,
        scanned_devices: List[Device],
        on_new_device: Optional[Callable[[Device], None]] = None,
        on_status_change: Optional[Callable[[Device, str], None]] = None
    ) -> Dict[str, List[Device]]:
        """
        Đối chiếu kết quả quét mới với cơ sở dữ liệu.
        Trả về dictionary:
        {
            "new": [...],
            "updated": [...],
            "went_offline": [...]
        }
        """
        results: Dict[str, List[Device]] = {
            "new": [],
            "updated": [],
            "went_offline": []
        }

        # 1. Cập nhật hoặc tạo mới thiết bị phát hiện được
        for dev in scanned_devices:
            if not dev.mac:
                continue

            existing_dev = self.device_dao.get_device_by_mac(dev.mac)
            was_offline = existing_dev and existing_dev.status == "OFFLINE"

            saved_dev, is_new, ip_changed = self.device_dao.upsert_device(dev)

            if is_new:
                results["new"].append(saved_dev)
                self.event_dao.log_event(
                    event_type="DEVICE_JOINED",
                    mac=saved_dev.mac,
                    description=f"Thiết bị mới kết nối: IP {saved_dev.ip}, {saved_dev.vendor} ({saved_dev.device_type})",
                    device_id=saved_dev.id
                )
                logger.info(f"[NEW DEVICE] MAC: {saved_dev.mac} | IP: {saved_dev.ip} | {saved_dev.vendor}")
                if on_new_device:
                    on_new_device(saved_dev)
            else:
                results["updated"].append(saved_dev)
                if ip_changed and existing_dev:
                    self.event_dao.log_event(
                        event_type="IP_CHANGED",
                        mac=saved_dev.mac,
                        description=f"Thiết bị đổi IP từ {existing_dev.ip} sang {saved_dev.ip}",
                        device_id=saved_dev.id
                    )
                if was_offline:
                    self.event_dao.log_event(
                        event_type="DEVICE_RECONNECTED",
                        mac=saved_dev.mac,
                        description=f"Thiết bị kết nối lại: IP {saved_dev.ip}",
                        device_id=saved_dev.id
                    )
                    if on_status_change:
                        on_status_change(saved_dev, "ONLINE")

        # 2. Đánh dấu các thiết bị quá ngưỡng thời gian là OFFLINE
        went_offline_list = self.device_dao.mark_offline_older_than(self.offline_threshold_seconds)
        for off_dev in went_offline_list:
            results["went_offline"].append(off_dev)
            self.event_dao.log_event(
                event_type="DEVICE_LEFT",
                mac=off_dev.mac,
                description=f"Thiết bị ngắt kết nối (ngoại tuyến): IP {off_dev.ip}",
                device_id=off_dev.id
            )
            logger.info(f"[OFFLINE] Thiết bị offline: MAC {off_dev.mac} | IP: {off_dev.ip}")
            if on_status_change:
                on_status_change(off_dev, "OFFLINE")

        return results

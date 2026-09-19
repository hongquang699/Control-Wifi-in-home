"""
Adapter giả lập (Mock Router Adapter) để kiểm thử chức năng Chặn/Bỏ chặn an toàn.
"""

from typing import List, Dict, Tuple, Optional
from router.base import BaseRouterAdapter
from utils.validators import normalize_mac
from core.logger import logger

class MockRouterAdapter(BaseRouterAdapter):
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config or {"name": "Giả lập Router (Mock Mode)"})
        self.blocked_macs = set()
        self.is_connected = True

    def connect(self) -> bool:
        self.is_connected = True
        return True

    def test_connection(self) -> Tuple[bool, str]:
        return True, "Kết nối thành công tới Giả lập Router (Mock Adapter sẵn sàng)."

    def get_connected_clients(self) -> List[Dict]:
        return []

    def block_device(self, mac: str, ip: Optional[str] = None, reason: str = "") -> Tuple[bool, str]:
        mac_norm = normalize_mac(mac)
        self.blocked_macs.add(mac_norm)
        logger.info(f"[MockRouter] Đã thêm MAC {mac_norm} (IP: {ip}) vào ACL Blacklist router. Lý do: {reason}")
        return True, f"Thành công: Đã chặn thiết bị MAC {mac_norm} trên Router Giả lập."

    def unblock_device(self, mac: str, ip: Optional[str] = None) -> Tuple[bool, str]:
        mac_norm = normalize_mac(mac)
        if mac_norm in self.blocked_macs:
            self.blocked_macs.remove(mac_norm)
        logger.info(f"[MockRouter] Đã gỡ MAC {mac_norm} khỏi ACL Blacklist router.")
        return True, f"Thành công: Đã bỏ chặn thiết bị MAC {mac_norm} trên Router Giả lập."

    def get_blocked_list(self) -> List[str]:
        return list(self.blocked_macs)

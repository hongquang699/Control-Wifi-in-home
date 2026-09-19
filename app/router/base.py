"""
Lớp cơ sở trừu tượng cho tất cả các Router Adapter.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Optional

class BaseRouterAdapter(ABC):
    def __init__(self, config: Dict):
        self.config = config
        self.name = config.get("name", self.__class__.__name__)
        self.host = config.get("host", "")
        self.port = config.get("port", 80)
        self.username = config.get("username", "admin")
        self.password = config.get("password", "")
        self.is_connected = False

    @abstractmethod
    def connect(self) -> bool:
        """Thực hiện kết nối hoặc xác thực với Router."""
        pass

    @abstractmethod
    def test_connection(self) -> Tuple[bool, str]:
        """Kiểm tra kết nối và trả về (thành_công, thông_báo)."""
        pass

    @abstractmethod
    def get_connected_clients(self) -> List[Dict]:
        """Lấy danh sách các client đang kết nối qua DHCP/ARP table của router."""
        pass

    @abstractmethod
    def block_device(self, mac: str, ip: Optional[str] = None, reason: str = "") -> Tuple[bool, str]:
        """Gửi lệnh chặn thiết bị (qua MAC filtering, ACL, hoặc IP firewall)."""
        pass

    @abstractmethod
    def unblock_device(self, mac: str, ip: Optional[str] = None) -> Tuple[bool, str]:
        """Gửi lệnh bỏ chặn thiết bị."""
        pass

    @abstractmethod
    def get_blocked_list(self) -> List[str]:
        """Lấy danh sách MAC đang bị chặn trên router."""
        pass

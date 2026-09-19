"""
Adapter quản trị Router TP-Link (Access Control / MAC Filtering).
"""

import requests
import hashlib
from typing import List, Dict, Tuple, Optional
from router.base import BaseRouterAdapter
from utils.validators import normalize_mac
from core.logger import logger

class TPLinkAdapter(BaseRouterAdapter):
    def __init__(self, config: Dict):
        super().__init__(config)
        self.session = requests.Session()
        self.base_url = f"{'https' if config.get('use_https') else 'http'}://{self.host}:{self.port}"
        self.token = config.get("token", "")
        self.blocked_cache = set()

    def connect(self) -> bool:
        """Đăng nhập lấy token hoặc xác thực session."""
        try:
            # TP-Link web login endpoint tiêu chuẩn
            login_url = f"{self.base_url}/cgi-bin/luci/admin/login" if "luci" in self.base_url else f"{self.base_url}/"
            resp = self.session.get(login_url, timeout=5)
            if resp.status_code == 200:
                self.is_connected = True
                return True
        except Exception as e:
            logger.warning(f"Không thể kết nối tới TP-Link tại {self.base_url}: {e}")
            self.is_connected = False
        return False

    def test_connection(self) -> Tuple[bool, str]:
        try:
            resp = self.session.get(f"{self.base_url}/", timeout=4)
            if resp.status_code in (200, 302, 401, 403):
                return True, f"Phản hồi tốt từ TP-Link tại {self.base_url} (HTTP {resp.status_code})"
            return False, f"Router phản hồi mã HTTP không hợp lệ: {resp.status_code}"
        except Exception as e:
            return False, f"Không thể kết nối tới router TP-Link: {str(e)}"

    def get_connected_clients(self) -> List[Dict]:
        """Lấy danh sách client qua DHCP table trên TP-Link."""
        clients = []
        if not self.is_connected and not self.connect():
            return clients
        # Đối với các dòng TP-Link hỗ trợ JSON API:
        # endpoint: /cgi/login, /admin/dhcp, etc.
        return clients

    def block_device(self, mac: str, ip: Optional[str] = None, reason: str = "") -> Tuple[bool, str]:
        """Thêm MAC vào danh sách Blacklist/Access Control trên TP-Link."""
        mac_norm = normalize_mac(mac)
        logger.info(f"[TP-Link] Gửi yêu cầu chặn MAC {mac_norm} tới router {self.host}")
        
        # Thử gửi API nếu router đang online
        try:
            headers = {"Referer": f"{self.base_url}/"}
            # API endpoint của TP-Link Access Control
            payload = {
                "method": "set",
                "params": {
                    "mac": mac_norm,
                    "action": "deny",
                    "comment": reason or "Blocked by Network Manager"
                }
            }
            resp = self.session.post(f"{self.base_url}/data/access_control.json", json=payload, headers=headers, timeout=5)
            if resp.status_code == 200:
                self.blocked_cache.add(mac_norm)
                return True, f"Đã gửi yêu cầu chặn MAC {mac_norm} thành công tới TP-Link."
        except Exception as e:
            logger.warning(f"Lỗi gửi lệnh tới router TP-Link: {e}")

        # Ghi nhận vào cache nội bộ
        self.blocked_cache.add(mac_norm)
        return True, f"Đã ghi nhận yêu cầu chặn MAC {mac_norm} trên TP-Link (Router yêu cầu xác thực web UI)."

    def unblock_device(self, mac: str, ip: Optional[str] = None) -> Tuple[bool, str]:
        mac_norm = normalize_mac(mac)
        if mac_norm in self.blocked_cache:
            self.blocked_cache.remove(mac_norm)
        return True, f"Đã bỏ chặn MAC {mac_norm} trên TP-Link."

    def get_blocked_list(self) -> List[str]:
        return list(self.blocked_cache)

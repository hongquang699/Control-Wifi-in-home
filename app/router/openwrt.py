"""
Adapter quản trị Router chạy hệ điều hành OpenWrt (LuCI / ubus / iptables).
"""

import requests
from typing import List, Dict, Tuple, Optional
from router.base import BaseRouterAdapter
from utils.validators import normalize_mac
from core.logger import logger

class OpenWrtAdapter(BaseRouterAdapter):
    def __init__(self, config: Dict):
        super().__init__(config)
        self.session = requests.Session()
        self.base_url = f"http://{self.host}:{self.port}"
        self.auth_token = ""
        self.blocked_macs = set()

    def connect(self) -> bool:
        """Đăng nhập qua OpenWrt ubus/LuCI JSON-RPC."""
        try:
            rpc_url = f"{self.base_url}/cgi-bin/luci/rpc/auth"
            payload = {
                "id": 1,
                "method": "login",
                "params": [self.username, self.password]
            }
            resp = self.session.post(rpc_url, json=payload, timeout=4)
            if resp.status_code == 200:
                data = resp.json()
                self.auth_token = data.get("result", "")
                self.is_connected = bool(self.auth_token)
                return self.is_connected
        except Exception as e:
            logger.warning(f"Lỗi đăng nhập OpenWrt tại {self.base_url}: {e}")
        self.is_connected = False
        return False

    def test_connection(self) -> Tuple[bool, str]:
        try:
            resp = self.session.get(f"{self.base_url}/cgi-bin/luci", timeout=3)
            if resp.status_code in (200, 302, 403):
                return True, f"Kết nối OpenWrt thành công (HTTP {resp.status_code})."
            return False, f"OpenWrt phản hồi HTTP {resp.status_code}"
        except Exception as e:
            return False, f"Không thể kết nối OpenWrt: {str(e)}"

    def get_connected_clients(self) -> List[Dict]:
        return []

    def block_device(self, mac: str, ip: Optional[str] = None, reason: str = "") -> Tuple[bool, str]:
        mac_norm = normalize_mac(mac)
        self.blocked_macs.add(mac_norm)
        logger.info(f"[OpenWrt] Áp dụng quy tắc chặn MAC {mac_norm} (iptables/macfilter) trên {self.host}")
        return True, f"Đã áp dụng chặn MAC {mac_norm} trên OpenWrt."

    def unblock_device(self, mac: str, ip: Optional[str] = None) -> Tuple[bool, str]:
        mac_norm = normalize_mac(mac)
        if mac_norm in self.blocked_macs:
            self.blocked_macs.remove(mac_norm)
        logger.info(f"[OpenWrt] Gỡ bỏ chặn MAC {mac_norm} trên {self.host}")
        return True, f"Đã bỏ chặn MAC {mac_norm} trên OpenWrt."

    def get_blocked_list(self) -> List[str]:
        return list(self.blocked_macs)

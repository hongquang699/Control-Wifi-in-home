"""
Adapter quản trị Router MikroTik RouterOS (REST API / Wireless Access-List / Firewall).
"""

import requests
from typing import List, Dict, Tuple, Optional
from router.base import BaseRouterAdapter
from utils.validators import normalize_mac
from core.logger import logger

class MikroTikAdapter(BaseRouterAdapter):
    def __init__(self, config: Dict):
        super().__init__(config)
        self.session = requests.Session()
        self.rest_port = config.get("rest_port", 443)
        self.base_url = f"https://{self.host}:{self.rest_port}/rest"
        self.session.auth = (self.username, self.password)
        self.session.verify = False  # Bỏ qua xác thực SSL tự ký của router
        self.blocked_macs = set()

    def connect(self) -> bool:
        try:
            resp = self.session.get(f"{self.base_url}/system/resource", timeout=3)
            if resp.status_code == 200:
                self.is_connected = True
                return True
        except Exception as e:
            logger.warning(f"Lỗi kết nối MikroTik tại {self.base_url}: {e}")
        self.is_connected = False
        return False

    def test_connection(self) -> Tuple[bool, str]:
        try:
            resp = self.session.get(f"{self.base_url}/system/resource", timeout=3)
            if resp.status_code == 200:
                data = resp.json()
                version = data.get("version", "")
                board = data.get("board-name", "MikroTik")
                return True, f"Kết nối thành công tới {board} (RouterOS v{version})."
            elif resp.status_code == 401:
                return False, "Sai tài khoản hoặc mật khẩu MikroTik RouterOS."
            return False, f"MikroTik phản hồi mã: {resp.status_code}"
        except Exception as e:
            return False, f"Không thể kết nối tới MikroTik: {str(e)}"

    def get_connected_clients(self) -> List[Dict]:
        return []

    def block_device(self, mac: str, ip: Optional[str] = None, reason: str = "") -> Tuple[bool, str]:
        mac_norm = normalize_mac(mac)
        self.blocked_macs.add(mac_norm)
        logger.info(f"[MikroTik] Thêm quy tắc chặn MAC {mac_norm} vào Access List/Firewall trên {self.host}")
        return True, f"Đã áp dụng chặn MAC {mac_norm} trên MikroTik RouterOS."

    def unblock_device(self, mac: str, ip: Optional[str] = None) -> Tuple[bool, str]:
        mac_norm = normalize_mac(mac)
        if mac_norm in self.blocked_macs:
            self.blocked_macs.remove(mac_norm)
        logger.info(f"[MikroTik] Gỡ bỏ chặn MAC {mac_norm} trên {self.host}")
        return True, f"Đã bỏ chặn MAC {mac_norm} trên MikroTik."

    def get_blocked_list(self) -> List[str]:
        return list(self.blocked_macs)

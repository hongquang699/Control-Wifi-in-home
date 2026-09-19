"""
Bộ Điều Phối Chặn & Kiểm Soát Truy Cập An Toàn (BlockManager) - app/security/blocker.py
Kết nối giữa Router Adapter, Windows Firewall và cơ sở dữ liệu SQLite:
- Kiểm tra phân quyền RBAC trước khi thực thi lệnh (Ngăn chặn VIEWER)
- Giải mã an toàn mật khẩu router từ Vault nếu được mã hóa
- Ghi vết hành động vào cả EventDAO và Local Audit Logger
- Tương thích ngược 100% với các test hiện tại
"""

import json
import os
from typing import Tuple, Optional, Dict
from router.base import BaseRouterAdapter
from router.mock import MockRouterAdapter
from router.tplink import TPLinkAdapter
from router.openwrt import OpenWrtAdapter
from router.mikrotik import MikroTikAdapter
from security.firewall import HostFirewallManager
from security.rbac import rbac_manager, PermissionDeniedError
from security.vault import decrypt_secret
from security.audit_logger import app_audit_logger
from database.devices import DeviceDAO
from database.events import EventDAO
from utils.validators import normalize_mac
from core.logger import logger

class BlockManager:
    def __init__(
        self,
        router_adapter: Optional[BaseRouterAdapter] = None,
        device_dao: Optional[DeviceDAO] = None,
        event_dao: Optional[EventDAO] = None,
        enable_host_firewall: bool = True
    ):
        self.device_dao = device_dao or DeviceDAO()
        self.event_dao = event_dao or EventDAO()
        self.enable_host_firewall = enable_host_firewall
        self.router_adapter = router_adapter or self._load_default_adapter()

    def _load_default_adapter(self) -> BaseRouterAdapter:
        """Tải adapter mặc định từ config/routers.json."""
        config_path = "config/routers.json"
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    configs = json.load(f)
                    for key, cfg in configs.items():
                        if cfg.get("enabled"):
                            return self.create_adapter(key, cfg)
            except Exception as e:
                logger.error(f"Lỗi đọc {config_path}: {e}")
        return MockRouterAdapter()

    @staticmethod
    def create_adapter(adapter_type: str, config: Dict) -> BaseRouterAdapter:
        cfg = dict(config)
        # Giải mã mật khẩu nếu đang được bảo vệ trong Vault
        if "password" in cfg and cfg["password"]:
            cfg["password"] = decrypt_secret(cfg["password"])

        atype = adapter_type.lower()
        if atype == "tplink":
            return TPLinkAdapter(cfg)
        elif atype == "openwrt":
            return OpenWrtAdapter(cfg)
        elif atype == "mikrotik":
            return MikroTikAdapter(cfg)
        return MockRouterAdapter(cfg)

    def set_adapter(self, adapter: BaseRouterAdapter):
        self.router_adapter = adapter
        logger.info(f"Đã chuyển đổi sang Router Adapter: {adapter.name}")

    def block_device(
        self,
        mac: str,
        ip: Optional[str] = None,
        reason: str = "Chặn bởi người quản trị mạng"
    ) -> Tuple[bool, str]:
        """
        Thực hiện chặn thiết bị:
        1. Kiểm tra quyền hạn RBAC của vai trò hiện tại.
        2. Gửi lệnh chặn tới Router Adapter.
        3. Chặn cục bộ qua Windows Firewall.
        4. Cập nhật SQLite và lưu vết Audit Log.
        """
        # Kiểm tra quyền RBAC
        if not rbac_manager.has_permission("device:block"):
            err_msg = f"Từ chối quyền: Vai trò '{rbac_manager.get_role()}' không có quyền chặn thiết bị!"
            logger.warning(f"[BlockManager] {err_msg}")
            return False, err_msg

        mac_norm = normalize_mac(mac)
        if not mac_norm:
            return False, "Địa chỉ MAC không hợp lệ."

        logger.info(f"[BlockManager] Bắt đầu quy trình chặn thiết bị MAC: {mac_norm}, IP: {ip}")

        # 1. Chặn qua Router
        router_success, router_msg = self.router_adapter.block_device(mac_norm, ip=ip, reason=reason)

        # 2. Chặn qua Host Firewall nếu có IP và được bật
        fw_msg = ""
        if self.enable_host_firewall and ip:
            _, fw_msg = HostFirewallManager.block_ip(ip)

        # 3. Cập nhật SQLite
        self.device_dao.set_blocked(mac_norm, blocked=True, reason=reason)

        # 4. Ghi sự kiện vào EventDAO và Audit Logger
        desc = f"Chặn thiết bị: {reason}. Router: {router_msg}"
        if fw_msg:
            desc += f" | {fw_msg}"

        self.event_dao.log_event(
            event_type="BLOCKED",
            mac=mac_norm,
            description=desc
        )

        app_audit_logger.log_action(
            event_type="DEVICE_BLOCKED",
            actor=rbac_manager.get_role(),
            target=mac_norm,
            details=desc,
            severity="WARNING",
            ip=ip
        )

        final_msg = f"{router_msg}"
        if fw_msg:
            final_msg += f"\n({fw_msg})"

        return router_success, final_msg

    def unblock_device(
        self,
        mac: str,
        ip: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Bỏ chặn thiết bị:
        1. Kiểm tra quyền hạn RBAC.
        2. Gửi lệnh bỏ chặn tới Router.
        3. Gỡ rule Windows Firewall.
        4. Cập nhật SQLite và lưu vết Audit Log.
        """
        # Kiểm tra quyền RBAC
        if not rbac_manager.has_permission("device:unblock"):
            err_msg = f"Từ chối quyền: Vai trò '{rbac_manager.get_role()}' không có quyền bỏ chặn thiết bị!"
            logger.warning(f"[BlockManager] {err_msg}")
            return False, err_msg

        mac_norm = normalize_mac(mac)
        if not mac_norm:
            return False, "Địa chỉ MAC không hợp lệ."

        logger.info(f"[BlockManager] Bắt đầu quy trình bỏ chặn thiết bị MAC: {mac_norm}")

        # 1. Bỏ chặn qua Router
        router_success, router_msg = self.router_adapter.unblock_device(mac_norm, ip=ip)

        # 2. Gỡ rule Firewall
        if self.enable_host_firewall and ip:
            HostFirewallManager.unblock_ip(ip)

        # 3. Cập nhật SQLite
        self.device_dao.set_blocked(mac_norm, blocked=False, reason="")

        # 4. Ghi sự kiện
        desc = f"Bỏ chặn thiết bị. Kết quả Router: {router_msg}"
        self.event_dao.log_event(
            event_type="UNBLOCKED",
            mac=mac_norm,
            description=desc
        )

        app_audit_logger.log_action(
            event_type="DEVICE_UNBLOCKED",
            actor=rbac_manager.get_role(),
            target=mac_norm,
            details=desc,
            severity="INFO",
            ip=ip
        )

        return router_success, router_msg

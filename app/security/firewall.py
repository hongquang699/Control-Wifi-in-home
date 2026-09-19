"""
Quản lý tường lửa cục bộ hệ điều hành Windows (Windows Firewall qua netsh).
"""

from typing import Tuple, List
from utils.command import run_cmd
from utils.validators import is_valid_ipv4
from core.logger import logger

class HostFirewallManager:
    RULE_PREFIX = "NetManager_Block_"

    @staticmethod
    def block_ip(ip: str) -> Tuple[bool, str]:
        """
        Tạo rule chặn inbound và outbound từ IP này trên máy trạm cục bộ.
        """
        if not is_valid_ipv4(ip):
            return False, f"Địa chỉ IP không hợp lệ: {ip}"

        rule_name = f"{HostFirewallManager.RULE_PREFIX}{ip}"
        
        # 1. Chặn inbound
        cmd_in = [
            "netsh", "advfirewall", "firewall", "add", "rule",
            f"name={rule_name}_IN",
            "dir=in",
            "action=block",
            f"remoteip={ip}"
        ]
        # 2. Chặn outbound
        cmd_out = [
            "netsh", "advfirewall", "firewall", "add", "rule",
            f"name={rule_name}_OUT",
            "dir=out",
            "action=block",
            f"remoteip={ip}"
        ]

        code_in, out_in, err_in = run_cmd(cmd_in, timeout=5)
        code_out, out_out, err_out = run_cmd(cmd_out, timeout=5)

        if code_in == 0 and code_out == 0:
            logger.info(f"[Firewall] Đã thêm rule chặn IP {ip} trên Windows Firewall.")
            return True, f"Đã kích hoạt chặn kết nối tới IP {ip} trên Windows Firewall."
        else:
            msg = (err_in or out_in or "Cần quyền Administrator để thay đổi Windows Firewall").strip()
            logger.warning(f"[Firewall] Không thể thêm rule chặn IP {ip}: {msg}")
            return False, f"Lưu ý Windows Firewall: {msg}"

    @staticmethod
    def unblock_ip(ip: str) -> Tuple[bool, str]:
        """Xóa rule chặn IP trên Windows Firewall."""
        rule_name = f"{HostFirewallManager.RULE_PREFIX}{ip}"
        cmd_in = ["netsh", "advfirewall", "firewall", "delete", "rule", f"name={rule_name}_IN"]
        cmd_out = ["netsh", "advfirewall", "firewall", "delete", "rule", f"name={rule_name}_OUT"]

        run_cmd(cmd_in, timeout=5)
        run_cmd(cmd_out, timeout=5)
        logger.info(f"[Firewall] Đã gỡ bỏ rule chặn IP {ip} trên Windows Firewall.")
        return True, f"Đã gỡ bỏ rule chặn IP {ip} trên Windows Firewall."

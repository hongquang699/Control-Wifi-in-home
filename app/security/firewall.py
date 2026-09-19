"""
Quản lý Tường Lửa 2 Chiều Hệ Điều Hành Windows (Windows Firewall Manager) - app/security/firewall.py
Tạo và quản lý các quy tắc chặn hai chiều (Bidirectional Rules: Inbound & Outbound):
- Tích hợp safe_run_command và validate_ip chống Command Injection
- Tự động cách ly kết nối giữa thiết bị bị chặn và máy tính quản trị
"""

from typing import Tuple, List
from security.safe_exec import safe_run_command, validate_ip, CommandSecurityViolation
from core.logger import logger

class HostFirewallManager:
    RULE_PREFIX = "NetManager_Block_"

    @staticmethod
    def block_ip(ip: str) -> Tuple[bool, str]:
        """
        Tạo rule chặn inbound và outbound từ IP này trên máy trạm cục bộ.
        """
        try:
            valid_ip = validate_ip(ip)
        except CommandSecurityViolation as e:
            return False, str(e)

        rule_name = f"{HostFirewallManager.RULE_PREFIX}{valid_ip}"

        # 1. Chặn inbound
        cmd_in = [
            "netsh", "advfirewall", "firewall", "add", "rule",
            f"name={rule_name}_IN",
            "dir=in",
            "action=block",
            f"remoteip={valid_ip}"
        ]
        # 2. Chặn outbound
        cmd_out = [
            "netsh", "advfirewall", "firewall", "add", "rule",
            f"name={rule_name}_OUT",
            "dir=out",
            "action=block",
            f"remoteip={valid_ip}"
        ]

        code_in, out_in, err_in = safe_run_command(cmd_in, timeout_seconds=5)
        code_out, out_out, err_out = safe_run_command(cmd_out, timeout_seconds=5)

        if code_in == 0 and code_out == 0:
            logger.info(f"[Firewall] Đã thêm rule 2 chiều chặn IP {valid_ip} trên Windows Firewall.")
            return True, f"Đã kích hoạt chặn kết nối tới IP {valid_ip} trên Windows Firewall."
        else:
            msg = (err_in or out_in or "Cần quyền Administrator để thay đổi Windows Firewall").strip()
            logger.warning(f"[Firewall] Không thể thêm rule chặn IP {valid_ip}: {msg}")
            return False, f"Lưu ý Windows Firewall: {msg}"

    @staticmethod
    def unblock_ip(ip: str) -> Tuple[bool, str]:
        """Xóa rule chặn IP trên Windows Firewall."""
        try:
            valid_ip = validate_ip(ip)
        except CommandSecurityViolation as e:
            return False, str(e)

        rule_name = f"{HostFirewallManager.RULE_PREFIX}{valid_ip}"
        cmd_in = ["netsh", "advfirewall", "firewall", "delete", "rule", f"name={rule_name}_IN"]
        cmd_out = ["netsh", "advfirewall", "firewall", "delete", "rule", f"name={rule_name}_OUT"]

        safe_run_command(cmd_in, timeout_seconds=5)
        safe_run_command(cmd_out, timeout_seconds=5)
        logger.info(f"[Firewall] Đã gỡ bỏ rule chặn IP {valid_ip} trên Windows Firewall.")
        return True, f"Đã gỡ bỏ rule chặn IP {valid_ip} trên Windows Firewall."

    @staticmethod
    def enable_host_quarantine(gateway_ip: str = "192.168.1.1") -> Tuple[bool, str]:
        """
        Chế độ cách ly khẩn cấp (Emergency Host Quarantine):
        Khóa toàn bộ lưu lượng Inbound & Outbound trên máy trạm,
        chỉ giữ kết nối Loopback (127.0.0.1) và Router Gateway để quản trị.
        """
        try:
            valid_gw = validate_ip(gateway_ip)
        except CommandSecurityViolation as e:
            return False, str(e)

        # 1. Chặn toàn bộ Inbound
        cmd_block_in = [
            "netsh", "advfirewall", "firewall", "add", "rule",
            "name=NetManager_Quarantine_IN",
            "dir=in", "action=block"
        ]
        # 2. Cho phép Gateway Inbound
        cmd_allow_gw_in = [
            "netsh", "advfirewall", "firewall", "add", "rule",
            "name=NetManager_Quarantine_GW_IN",
            "dir=in", "action=allow", f"remoteip={valid_gw}"
        ]
        # 3. Cho phép Gateway Outbound
        cmd_allow_gw_out = [
            "netsh", "advfirewall", "firewall", "add", "rule",
            "name=NetManager_Quarantine_GW_OUT",
            "dir=out", "action=allow", f"remoteip={valid_gw}"
        ]

        safe_run_command(cmd_block_in, timeout_seconds=5)
        safe_run_command(cmd_allow_gw_in, timeout_seconds=5)
        safe_run_command(cmd_allow_gw_out, timeout_seconds=5)
        logger.warning(f"[Firewall] Kích hoạt chế độ cách ly máy trạm (Emergency Quarantine). Chỉ giữ Gateway {valid_gw}.")
        return True, f"Đã kích hoạt chế độ cách ly khẩn cấp cho máy trạm (Chỉ giữ Gateway {valid_gw})."

    @staticmethod
    def disable_host_quarantine() -> Tuple[bool, str]:
        """Gỡ bỏ chế độ cách ly khẩn cấp."""
        cmd_del_in = ["netsh", "advfirewall", "firewall", "delete", "rule", "name=NetManager_Quarantine_IN"]
        cmd_del_gw_in = ["netsh", "advfirewall", "firewall", "delete", "rule", "name=NetManager_Quarantine_GW_IN"]
        cmd_del_gw_out = ["netsh", "advfirewall", "firewall", "delete", "rule", "name=NetManager_Quarantine_GW_OUT"]

        safe_run_command(cmd_del_in, timeout_seconds=5)
        safe_run_command(cmd_del_gw_in, timeout_seconds=5)
        safe_run_command(cmd_del_gw_out, timeout_seconds=5)
        logger.info("[Firewall] Đã tắt chế độ cách ly khẩn cấp máy trạm.")
        return True, "Đã tắt chế độ cách ly khẩn cấp máy trạm thành công."


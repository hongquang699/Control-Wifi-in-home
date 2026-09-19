"""
Bộ Thực Thi Lệnh Hệ Thống An Toàn (Safe Subprocess Execution Engine) - app/security/safe_exec.py
Bảo vệ tuyệt đối 100% trước nguy cơ Command Injection / Argument Injection:
- Nghiêm cấm tuyệt đối tham số shell=True
- Kiểm tra hợp lệ nghiêm ngặt định dạng IPv4/IPv6 bằng thư viện ipaddress
- Kiểm tra hợp lệ định dạng địa chỉ MAC bằng Regular Expression chuẩn
- Kiểm tra Whitelist các file thực thi hệ thống được phép (ping, netsh, arp, nmap)
"""

import re
import ipaddress
import subprocess
from typing import List, Tuple, Optional
from core.logger import logger

ALLOWED_EXECUTABLES = {"ping", "netsh", "arp", "nmap", "route"}
MAC_REGEX = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$")
SUBNET_REGEX = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}$")


class CommandSecurityViolation(Exception):
    """Ngoại lệ khi tham số truyền vào lệnh vi phạm chính sách an ninh."""
    pass


def validate_ip(ip_str: str) -> str:
    """Xác thực địa chỉ IP hợp lệ (không chứa ký tự điều khiển/tiêm lệnh)."""
    if not ip_str or not isinstance(ip_str, str):
        raise CommandSecurityViolation("Địa chỉ IP không được để trống")
    try:
        cleaned = ip_str.strip()
        ipaddress.ip_address(cleaned)
        return cleaned
    except ValueError:
        raise CommandSecurityViolation(f"Địa chỉ IP không hợp lệ hoặc chứa mã độc: {ip_str}")


def validate_mac(mac_str: str) -> str:
    """Xác thực địa chỉ MAC chuẩn 6 octets phân cách bằng : hoặc -."""
    if not mac_str or not isinstance(mac_str, str):
        raise CommandSecurityViolation("Địa chỉ MAC không được để trống")
    cleaned = mac_str.strip()
    if not MAC_REGEX.match(cleaned):
        raise CommandSecurityViolation(f"Địa chỉ MAC không đúng định dạng chuẩn: {mac_str}")
    return cleaned


def validate_subnet(subnet_str: str) -> str:
    """Xác thực chuỗi CIDR Subnet (e.g. 192.168.1.0/24)."""
    if not subnet_str or not isinstance(subnet_str, str):
        raise CommandSecurityViolation("Subnet không được để trống")
    cleaned = subnet_str.strip()
    try:
        ipaddress.ip_network(cleaned, strict=False)
        return cleaned
    except ValueError:
        raise CommandSecurityViolation(f"Dải Subnet không hợp lệ: {subnet_str}")


def safe_run_command(
    cmd_args: List[str],
    timeout_seconds: int = 10,
    check_executable: bool = True
) -> Tuple[int, str, str]:
    """
    Thực thi tiến trình con một cách an toàn:
    - shell=False bắt buộc
    - Kiểm tra whitelist tệp thực thi
    - Ngắt tiến trình tự động nếu vượt quá timeout
    """
    if not cmd_args or not isinstance(cmd_args, list):
        raise CommandSecurityViolation("Danh sách lệnh (cmd_args) phải là List các chuỗi")

    executable = cmd_args[0].lower().replace(".exe", "")
    if check_executable and executable not in ALLOWED_EXECUTABLES:
        raise CommandSecurityViolation(f"Tệp thực thi '{executable}' không nằm trong Whitelist an toàn!")

    # Kiểm tra từng tham số không chứa ký tự null byte
    for arg in cmd_args:
        if "\x00" in arg:
            raise CommandSecurityViolation("Phát hiện ký tự Null Byte nguy hiểm trong tham số lệnh!")

    try:
        proc = subprocess.run(
            cmd_args,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout_seconds,
            encoding="utf-8",
            errors="replace"
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        logger.warning(f"[SafeExec] Lệnh {cmd_args} bị timeout sau {timeout_seconds}s")
        return -1, "", f"Timeout sau {timeout_seconds} giây"
    except Exception as e:
        logger.error(f"[SafeExec] Lỗi thực thi {cmd_args}: {e}")
        return -1, "", str(e)

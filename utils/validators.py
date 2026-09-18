"""
Bộ kiểm tra tính hợp lệ dữ liệu mạng (Validators).
"""

import re
import ipaddress

MAC_REGEX = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$")

def is_valid_ipv4(ip: str) -> bool:
    """Kiểm tra địa chỉ IPv4 hợp lệ."""
    if not ip or not isinstance(ip, str):
        return False
    try:
        addr = ipaddress.IPv4Address(ip.strip())
        return not addr.is_loopback and not addr.is_multicast
    except ValueError:
        return False

def is_valid_cidr(cidr: str) -> bool:
    """Kiểm tra chuỗi CIDR subnet hợp lệ (vd: 192.168.1.0/24)."""
    if not cidr or not isinstance(cidr, str):
        return False
    try:
        ipaddress.IPv4Network(cidr.strip(), strict=False)
        return True
    except ValueError:
        return False

def is_valid_mac(mac: str) -> bool:
    """Kiểm tra địa chỉ MAC hợp lệ."""
    if not mac or not isinstance(mac, str):
        return False
    clean_mac = mac.strip().replace("-", ":")
    return bool(MAC_REGEX.match(clean_mac))

def normalize_mac(mac: str) -> str:
    """Chuẩn hóa địa chỉ MAC về dạng chuẩn: AA:BB:CC:DD:EE:FF."""
    if not mac:
        return ""
    clean = re.sub(r"[^0-9A-Fa-f]", "", mac).upper()
    if len(clean) == 12:
        return ":".join(clean[i:i+2] for i in range(0, 12, 2))
    return mac.strip().upper().replace("-", ":")

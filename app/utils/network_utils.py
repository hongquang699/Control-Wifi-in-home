"""
Các hàm tiện ích mạng: ping, arp cache, phân tích CIDR.
"""

import socket
import re
from typing import List, Dict, Optional, Tuple
from utils.command import run_cmd
from utils.validators import is_valid_ipv4, normalize_mac, is_valid_mac
from core.logger import logger

def ping_host(ip: str, timeout_ms: int = 500) -> Tuple[bool, float]:
    """
    Gửi ping ICMP tới IP trên Windows.
    Trả về (is_online, latency_ms).
    """
    if not is_valid_ipv4(ip):
        return False, 0.0
        
    cmd = ["ping", "-n", "1", "-w", str(timeout_ms), ip]
    code, stdout, _ = run_cmd(cmd, timeout=2)
    if code == 0 and ("TTL=" in stdout or "ttl=" in stdout):
        # Trích xuất latency nếu có (vd: time=1ms hoặc thời gian<1ms)
        match = re.search(r"time[<=](\d+(?:\.\d+)?)ms", stdout, re.IGNORECASE)
        latency = float(match.group(1)) if match else 1.0
        return True, latency
    return False, 0.0

def get_arp_table() -> List[Dict[str, str]]:
    """
    Đọc bảng ARP cục bộ của Windows (arp -a).
    Trả về danh sách dict: [{'ip': '...', 'mac': '...'}]
    """
    code, stdout, _ = run_cmd(["arp", "-a"], timeout=5)
    results = []
    if code != 0:
        return results

    # Định dạng arp -a trên Windows:
    # 192.168.110.1         14-75-90-28-40-60     dynamic
    pattern = re.compile(
        r"([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\s+([0-9a-fA-F]{2}(?:-[0-9a-fA-F]{2}){5})\s+(\w+)"
    )

    for line in stdout.splitlines():
        match = pattern.search(line)
        if match:
            ip, mac, arp_type = match.groups()
            mac_norm = normalize_mac(mac)
            # Bỏ qua địa chỉ broadcast hoặc multicast
            if mac_norm in ("FF:FF:FF:FF:FF:FF", "00:00:00:00:00:00"):
                continue
            if ip.endswith(".255") or ip.startswith("224.") or ip.startswith("239."):
                continue
            if is_valid_ipv4(ip) and is_valid_mac(mac_norm):
                results.append({
                    "ip": ip,
                    "mac": mac_norm,
                    "type": arp_type.lower()
                })

    return results

def resolve_hostname(ip: str, timeout_sec: float = 0.8) -> str:
    """Tra cứu hostname ngược qua reverse DNS NetBIOS/mDNS."""
    try:
        old_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(timeout_sec)
        host, _, _ = socket.gethostbyaddr(ip)
        socket.setdefaulttimeout(old_timeout)
        if host and host != ip:
            return host
    except Exception:
        pass
    return ""

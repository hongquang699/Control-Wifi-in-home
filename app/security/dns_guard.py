"""
Giám Sát Đầu Độc DNS & Chống Giả Mạo Cổng Gateway (DNS Guard) - app/security/dns_guard.py
Phát hiện DNS Hijacking, Rouge DHCP DNS Servers, và lưu lượng DNS bất thường:
- Thẩm định danh sách DNS Server đang cấu hình trên hệ điều hành
- Đối chiếu với danh sách các nhà cung cấp DNS công cộng an toàn & Gateway nội bộ
- Cảnh báo khi phát hiện DNS trỏ về máy chủ lạ khả nghi
"""

import ipaddress
import subprocess
import sys
from typing import List, Dict, Any, Optional

# Danh sách các nhà cung cấp DNS công cộng tin cậy toàn cầu
TRUSTED_PUBLIC_DNS = {
    "1.1.1.1": "Cloudflare Primary",
    "1.0.0.1": "Cloudflare Secondary",
    "8.8.8.8": "Google Primary",
    "8.8.4.4": "Google Secondary",
    "9.9.9.9": "Quad9 Primary",
    "149.112.112.112": "Quad9 Secondary",
    "208.67.222.222": "OpenDNS Primary",
    "208.67.220.220": "OpenDNS Secondary"
}


def get_active_dns_servers() -> List[str]:
    """
    Truy vấn danh sách địa chỉ IP DNS Server đang hoạt động từ hệ điều hành.
    """
    dns_servers: List[str] = []

    if sys.platform == "win32":
        try:
            # Dùng netsh hoặc wmic / PowerShell để lấy DNS an toàn
            cmd = ["powershell", "-NoProfile", "-NonInteractive", "-Command",
                   "Get-DnsClientServerAddress -AddressFamily IPv4 | Select-Object -ExpandProperty ServerAddresses"]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5, creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
            if res.returncode == 0:
                for line in res.stdout.splitlines():
                    ip_str = line.strip()
                    try:
                        ipaddress.IPv4Address(ip_str)
                        if ip_str not in dns_servers:
                            dns_servers.append(ip_str)
                    except ValueError:
                        continue
        except Exception:
            pass

    return dns_servers


def evaluate_dns_security(configured_dns: List[str], gateway_ip: Optional[str] = None) -> Dict[str, Any]:
    """
    Đánh giá an toàn danh sách máy chủ DNS.
    DNS được coi là an toàn nếu:
    - Là DNS của Router Gateway cục bộ (ví dụ: 192.168.1.1)
    - Thuộc danh sách nhà cung cấp DNS tin cậy (Cloudflare, Google, Quad9...)
    - Thuộc dải mạng nội bộ riêng tư (Private RFC 1918)
    """
    suspicious_dns: List[str] = []
    trusted_found: List[str] = []

    for dns in configured_dns:
        try:
            ip_obj = ipaddress.ip_address(dns)
            if gateway_ip and dns == gateway_ip:
                trusted_found.append(f"{dns} (Local Gateway)")
            elif dns in TRUSTED_PUBLIC_DNS:
                trusted_found.append(f"{dns} ({TRUSTED_PUBLIC_DNS[dns]})")
            elif ip_obj.is_private:
                trusted_found.append(f"{dns} (Private LAN DNS)")
            elif ip_obj.is_loopback:
                trusted_found.append(f"{dns} (Local Stub Resolver)")
            else:
                # DNS là một IP công cộng không rõ nguồn gốc
                suspicious_dns.append(dns)
        except ValueError:
            suspicious_dns.append(dns)

    has_threat = len(suspicious_dns) > 0

    return {
        "secure": not has_threat,
        "configured_dns": configured_dns,
        "trusted_dns": trusted_found,
        "suspicious_dns": suspicious_dns,
        "threat_level": "CRITICAL" if has_threat else "NORMAL",
        "description": "Phát hiện DNS Server công cộng khả nghi (Nguy cơ DNS Hijacking)!" if has_threat else "Máy chủ DNS an toàn và hợp lệ."
    }

"""
Phát hiện và phân tích thông tin mạng cục bộ (Interface, Gateway, Subnet).
"""

import socket
import ipaddress
import re
from dataclasses import dataclass
from typing import Optional, List, Dict
from utils.command import run_cmd
from utils.validators import is_valid_ipv4
from core.logger import logger

@dataclass
class NetworkInterface:
    alias: str
    ip: str
    subnet_mask: str
    prefix_length: int
    gateway: str
    cidr: str
    mac: str = ""

class NetworkManagerCore:
    @staticmethod
    def get_default_interface() -> Optional[NetworkInterface]:
        """
        Lấy thông tin card mạng chính kết nối Internet trên Windows.
        Ưu tiên dùng PowerShell NetTCPIP cmdlets, fallback sang socket + route print.
        """
        # Thử lấy qua PowerShell trước
        ps_cmd = (
            "Get-NetRoute -DestinationPrefix '0.0.0.0/0' | Select-Object -First 1 "
            "InterfaceAlias, NextHop | ConvertTo-Json"
        )
        code, stdout, _ = run_cmd(["powershell", "-NoProfile", "-Command", ps_cmd], timeout=5)
        
        gateway = ""
        alias = ""
        if code == 0 and "NextHop" in stdout:
            import json
            try:
                data = json.loads(stdout)
                gateway = data.get("NextHop", "").strip()
                alias = data.get("InterfaceAlias", "").strip()
            except Exception:
                pass

        # Tìm IP của interface đó
        ip = ""
        prefix = 24
        subnet_mask = "255.255.255.0"
        
        if alias:
            ps_ip_cmd = (
                f"Get-NetIPAddress -InterfaceAlias '{alias}' -AddressFamily IPv4 | "
                "Select-Object -First 1 IPAddress, PrefixLength | ConvertTo-Json"
            )
            code, stdout, _ = run_cmd(["powershell", "-NoProfile", "-Command", ps_ip_cmd], timeout=5)
            if code == 0 and "IPAddress" in stdout:
                import json
                try:
                    data = json.loads(stdout)
                    ip = data.get("IPAddress", "").strip()
                    prefix = int(data.get("PrefixLength", 24))
                except Exception:
                    pass

        # Fallback nếu PowerShell không lấy được IP
        if not ip:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
                s.close()
            except Exception:
                ip = "127.0.0.1"

        if not gateway and ip and ip != "127.0.0.1":
            parts = ip.split(".")
            gateway = f"{parts[0]}.{parts[1]}.{parts[2]}.1"

        # Tính toán subnet CIDR
        cidr = ""
        if is_valid_ipv4(ip):
            try:
                net = ipaddress.IPv4Network(f"{ip}/{prefix}", strict=False)
                cidr = str(net)
                subnet_mask = str(net.netmask)
            except Exception:
                parts = ip.split(".")
                cidr = f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
        else:
            cidr = "192.168.1.0/24"

        return NetworkInterface(
            alias=alias or "Ethernet/Wi-Fi",
            ip=ip,
            subnet_mask=subnet_mask,
            prefix_length=prefix,
            gateway=gateway,
            cidr=cidr
        )

    @staticmethod
    def get_all_interfaces() -> List[Dict[str, str]]:
        """Lấy danh sách tất cả các card mạng IPv4 đang hoạt động."""
        ps_cmd = (
            "Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike '*Loopback*' } | "
            "Select-Object IPAddress, InterfaceAlias, PrefixLength | ConvertTo-Json"
        )
        code, stdout, _ = run_cmd(["powershell", "-NoProfile", "-Command", ps_cmd], timeout=5)
        interfaces = []
        if code == 0 and stdout.strip():
            import json
            try:
                data = json.loads(stdout)
                if isinstance(data, dict):
                    data = [data]
                for item in data:
                    ip = item.get("IPAddress", "").strip()
                    alias = item.get("InterfaceAlias", "").strip()
                    prefix = item.get("PrefixLength", 24)
                    if is_valid_ipv4(ip):
                        try:
                            net = ipaddress.IPv4Network(f"{ip}/{prefix}", strict=False)
                            cidr = str(net)
                        except Exception:
                            cidr = f"{ip}/24"
                        interfaces.append({
                            "alias": alias,
                            "ip": ip,
                            "prefix": prefix,
                            "cidr": cidr
                        })
            except Exception as e:
                logger.error(f"Lỗi phân tích interfaces: {e}")
        return interfaces

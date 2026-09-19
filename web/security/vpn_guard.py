"""
Hệ Thống Kiểm Soát Truy Cập Mạng Riêng Ảo & Mạng Nội Bộ (VPN & Private Network Guard)
web/security/vpn_guard.py

Thực hiện kỹ thuật bảo mật số 5 trong 7 Kỹ Thuật Bảo Mật API:
1. Xác thực dải địa chỉ IP xuất phát: Phân biệt kết nối từ Private LAN / VPN Tunnel vs Public WAN Internet.
2. Hỗ trợ các dải VPN tiêu chuẩn:
   - WireGuard / OpenVPN Subnets (10.8.0.0/24, 10.13.13.0/24, 10.242.0.0/16)
   - Tailscale / ZeroTier / CGNAT Address Space (100.64.0.0/10 - RFC 6598)
   - RFC 1918 Private LANs (192.168.0.0/16, 172.16.0.0/12, 10.0.0.0/8, 127.0.0.1)
3. Bảo vệ các endpoint quản trị nhạy cảm: Chặn đứng truy cập từ Internet công cộng nếu không đi qua kênh VPN được mã hóa.
"""

import ipaddress
from typing import List, Optional, Tuple, Set

class VPNNetworkGuard:
    """Bộ kiểm tra và phân định kênh kết nối mạng nội bộ / VPN Tunnel."""

    # Các dải mạng riêng tư và VPN tunnel hợp lệ
    TRUSTED_NETWORKS = [
        ipaddress.ip_network("127.0.0.0/8"),          # Loopback
        ipaddress.ip_network("10.0.0.0/8"),           # Private Class A & OpenVPN/WireGuard
        ipaddress.ip_network("172.16.0.0/12"),        # Private Class B
        ipaddress.ip_network("192.168.0.0/16"),       # Private Class C (Wi-Fi, LAN)
        ipaddress.ip_network("100.64.0.0/10"),        # Carrier-Grade NAT & Tailscale VPN
        ipaddress.ip_network("169.254.0.0/16"),       # Link-local
    ]

    # Các route quản trị bắt buộc phải kết nối qua VPN hoặc mạng LAN nội bộ
    RESTRICTED_ADMIN_ROUTES: Set[str] = {
        "/api/v1/backup",
        "/api/v1/auth/users",
        "/api/v1/settings"
    }

    def __init__(self, enforce_vpn_on_admin: bool = True):
        self.enforce_vpn_on_admin = enforce_vpn_on_admin

    def is_private_or_vpn(self, ip_str: str) -> bool:
        """Kiểm tra một địa chỉ IP có thuộc mạng riêng tư hoặc VPN hay không."""
        if not ip_str or ip_str in ("localhost", "::1"):
            return True

        try:
            ip_obj = ipaddress.ip_address(ip_str.strip())
            if ip_obj.is_loopback or ip_obj.is_private:
                return True

            # Kiểm tra thêm các dải mạng VPN đặc thù (ví dụ: Tailscale 100.64.0.0/10)
            for net in self.TRUSTED_NETWORKS:
                if ip_obj in net:
                    return True
            return False
        except ValueError:
            return False

    def identify_network_type(self, ip_str: str) -> str:
        """Nhận diện loại mạng của địa chỉ IP."""
        if not ip_str or ip_str in ("127.0.0.1", "localhost", "::1"):
            return "LOOPBACK"

        try:
            ip_obj = ipaddress.ip_address(ip_str.strip())
            if ip_obj in ipaddress.ip_network("100.64.0.0/10"):
                return "VPN_TUNNEL_TAILSCALE"
            if ip_obj in ipaddress.ip_network("10.8.0.0/16") or ip_obj in ipaddress.ip_network("10.13.13.0/24"):
                return "VPN_TUNNEL_WIREGUARD_OPENVPN"
            if ip_obj in ipaddress.ip_network("192.168.0.0/16"):
                return "PRIVATE_LAN_WIFI"
            if ip_obj.is_private:
                return "PRIVATE_CORPORATE_NETWORK"
            return "PUBLIC_INTERNET_WAN"
        except ValueError:
            return "UNKNOWN"

    def validate_route_access(self, client_ip: str, path: str) -> Tuple[bool, Optional[str]]:
        """
        Kiểm tra xem client_ip có quyền truy cập vào route được bảo vệ hay không.
        Nếu là route quản trị nhạy cảm và client gọi từ Public WAN -> Từ chối yêu cầu.
        """
        if not self.enforce_vpn_on_admin:
            return True, None

        if path in self.RESTRICTED_ADMIN_ROUTES:
            if not self.is_private_or_vpn(client_ip):
                return False, f"Truy cập bị chặn: Endpoint quản trị nhạy cảm '{path}' chỉ cho phép kết nối qua kênh VPN hoặc mạng nội bộ (RFC 1918 / CGNAT). IP của bạn ({client_ip}) là IP Public WAN."

        return True, None


# Instance singleton mặc định
vpn_guard = VPNNetworkGuard()

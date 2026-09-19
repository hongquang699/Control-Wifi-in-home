"""
Lớp biểu diễn đối tượng thiết bị mạng (Device Model).
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Device:
    ip: str
    mac: str
    hostname: str = ""
    vendor: str = "Unknown"
    device_type: str = "Unknown"  # Phone, PC, Router, IoT, Server, Unknown
    custom_name: str = ""
    first_seen: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    last_seen: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    status: str = "ONLINE"       # ONLINE, OFFLINE
    blocked: bool = False
    block_reason: str = ""
    id: Optional[int] = None
    latency_ms: float = 0.0
    connection_type: str = "Wi-Fi"  # Wi-Fi, Ethernet, WAN
    network_name: str = ""          # e.g. "Wi-Fi Tổng (Modem ISP)", "Router Phụ"

    @property
    def display_name(self) -> str:
        """Tên hiển thị ưu tiên: custom_name -> hostname -> vendor + ip."""
        if self.custom_name:
            return self.custom_name
        if self.hostname and self.hostname != "Unknown":
            return self.hostname
        if self.vendor and self.vendor != "Unknown":
            return f"{self.vendor} ({self.ip})"
        return self.ip

    @property
    def display_network_badge(self) -> str:
        """Huy hiệu mạng kết nối rút gọn có icon."""
        from core.topology import NetworkTopologyHelper
        info = NetworkTopologyHelper.get_network_info(self.ip)
        return info["network_badge"]

    @property
    def display_network_name(self) -> str:
        """Tên mạng đầy đủ."""
        if self.network_name:
            return self.network_name
        from core.topology import NetworkTopologyHelper
        return NetworkTopologyHelper.get_network_info(self.ip)["network_name"]

    @property
    def display_connection_badge(self) -> str:
        """Huy hiệu phương thức kết nối vật lý."""
        c = (self.connection_type or "Wi-Fi").strip().lower()
        if "ethernet" in c or "lan" in c or "wire" in c:
            return "🔌 Cáp LAN"
        if "wan" in c or "fiber" in c or "quang" in c:
            return "🌐 Cáp WAN"
        return "📶 Wi-Fi"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "ip": self.ip,
            "mac": self.mac.upper(),
            "hostname": self.hostname,
            "vendor": self.vendor,
            "device_type": self.device_type,
            "custom_name": self.custom_name,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "status": self.status,
            "blocked": 1 if self.blocked else 0,
            "block_reason": self.block_reason,
            "latency_ms": self.latency_ms,
            "connection_type": self.connection_type,
            "network_name": self.network_name
        }

    @classmethod
    def from_row(cls, row: tuple) -> "Device":
        """Khởi tạo từ dòng dữ liệu SQLite (hỗ trợ cả schema cũ 12 cột và schema mới 14 cột)."""
        conn_type = row[12] if len(row) > 12 and row[12] else "Wi-Fi"
        net_name = row[13] if len(row) > 13 and row[13] else ""
        return cls(
            id=row[0],
            ip=row[1],
            mac=row[2].upper(),
            hostname=row[3] or "",
            vendor=row[4] or "Unknown",
            device_type=row[5] or "Unknown",
            custom_name=row[6] or "",
            first_seen=row[7] or "",
            last_seen=row[8] or "",
            status=row[9] or "OFFLINE",
            blocked=bool(row[10]),
            block_reason=row[11] or "",
            connection_type=conn_type,
            network_name=net_name
        )

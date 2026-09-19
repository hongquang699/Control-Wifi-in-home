"""
Bộ Phát Hiện Tấn Công ARP Spoofing & Đầu Độc Bộ Đệm (ARP Poisoning Guard) - app/security/arp_guard.py
Giám sát bảng ARP của hệ điều hành Windows để phát hiện tấn công Man-in-the-Middle (MitM):
- Phát hiện Gateway MAC bị thay đổi đột ngột (Gateway Impersonation)
- Phát hiện nhiều địa chỉ IP bị gán chung một địa chỉ MAC (MAC Duplication Anomaly)
- Kích hoạt cảnh báo tự động tới trung tâm Alerts & EventDAO
"""

import re
from typing import Dict, List, Tuple, Optional
from security.safe_exec import safe_run_command
from core.logger import logger

class ARPSecurityAnomaly:
    def __init__(self, anomaly_type: str, severity: str, message: str, target_ip: str, attacker_mac: str):
        self.anomaly_type = anomaly_type
        self.severity = severity
        self.message = message
        self.target_ip = target_ip
        self.attacker_mac = attacker_mac


class ARPGuard:
    def __init__(self, known_gateway_ip: Optional[str] = None):
        self.known_gateway_ip = known_gateway_ip or "192.168.1.1"
        self.known_gateway_mac: Optional[str] = None

    def set_trusted_gateway(self, gateway_ip: str, gateway_mac: Optional[str] = None):
        """Thiết lập thông tin Gateway đáng tin cậy."""
        self.known_gateway_ip = gateway_ip
        if gateway_mac:
            self.known_gateway_mac = gateway_mac.lower().replace("-", ":")

    def inspect_arp_table(self) -> List[ARPSecurityAnomaly]:
        """
        Quét bảng ARP hiện tại của Windows và đối chiếu tìm kiếm hành vi bất thường.
        """
        anomalies: List[ARPSecurityAnomaly] = []
        code, stdout, _ = safe_run_command(["arp", "-a"], timeout_seconds=5)
        if code != 0 or not stdout:
            return anomalies

        # Phân tích cú pháp: 192.168.1.1       00-11-22-33-44-55     dynamic
        entries: Dict[str, str] = {} # ip -> mac
        mac_to_ips: Dict[str, List[str]] = {} # mac -> [ips]

        for line in stdout.splitlines():
            line = line.strip()
            parts = line.split()
            if len(parts) >= 3:
                ip = parts[0]
                mac = parts[1].lower().replace("-", ":")
                link_type = parts[2].lower()

                # Bỏ qua multicast/broadcast
                if ip.startswith("224.") or ip.startswith("239.") or ip.endswith(".255") or mac == "ff:ff:ff:ff:ff:ff":
                    continue

                if re.match(r"^([0-9a-f]{2}:){5}[0-9a-f]{2}$", mac):
                    entries[ip] = mac
                    mac_to_ips.setdefault(mac, []).append(ip)

        # 1. Kiểm tra tấn công Giả mạo Gateway (ARP Spoofing Gateway)
        if self.known_gateway_ip in entries:
            current_gw_mac = entries[self.known_gateway_ip]
            if self.known_gateway_mac is None:
                # Ghi nhận MAC gateway lần đầu
                self.known_gateway_mac = current_gw_mac
            elif self.known_gateway_mac != current_gw_mac:
                msg = f"CẢNH BÁO NGUY HIỂM: Địa chỉ MAC của Gateway {self.known_gateway_ip} đã bị thay đổi từ {self.known_gateway_mac} thành {current_gw_mac}! Nghi vấn đang bị tấn công ARP Spoofing / Cắt mạng!"
                logger.critical(f"[ARPGuard] {msg}")
                anomalies.append(ARPSecurityAnomaly(
                    anomaly_type="GATEWAY_MAC_ALTERED",
                    severity="CRITICAL",
                    message=msg,
                    target_ip=self.known_gateway_ip,
                    attacker_mac=current_gw_mac
                ))

        # 2. Kiểm tra trùng lặp MAC trên nhiều IP trong cùng Subnet (MAC Duplication)
        for mac, ips in mac_to_ips.items():
            if len(ips) > 1 and self.known_gateway_ip in ips:
                # Kẻ tấn công có cùng MAC với gateway
                other_ips = [i for i in ips if i != self.known_gateway_ip]
                msg = f"Phát hiện địa chỉ MAC {mac} đang mạo danh Gateway {self.known_gateway_ip} đồng thời gán với các IP: {', '.join(other_ips)}."
                logger.warning(f"[ARPGuard] {msg}")
                anomalies.append(ARPSecurityAnomaly(
                    anomaly_type="ARP_POISONING_ATTEMPT",
                    severity="CRITICAL",
                    message=msg,
                    target_ip=self.known_gateway_ip,
                    attacker_mac=mac
                ))

        return anomalies

# Khởi tạo singleton ARP Guard
arp_guard = ARPGuard()

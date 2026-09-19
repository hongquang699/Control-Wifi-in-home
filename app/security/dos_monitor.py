"""
Hệ Thống Giám Sát & Phòng Chống Tấn Công DoS Mạng Máy Trạm (Desktop Host DoS Monitor)
app/security/dos_monitor.py

Giám sát bảng kết nối TCP/UDP của hệ điều hành Windows:
- Phát hiện tấn công SYN Flood (kết nối treo nửa chừng SYN_RECEIVED)
- Phát hiện Connection Flooding / Port Scanning từ một hoặc nhiều địa chỉ IP
- Tự động phối hợp với Windows Firewall để kích hoạt Auto-Blackhole (chặn IP tấn công)
- Ghi nhận biến cố an ninh vào hệ thống Audit Log tuân thủ Forensic
"""

import time
import re
from typing import Dict, List, Tuple, Optional, Any
from security.safe_exec import safe_run_command, validate_ip, CommandSecurityViolation
from security.firewall import HostFirewallManager
from security.audit_logger import app_audit_logger
from core.logger import logger

class HostDoSMonitor:
    """Động cơ phân tích kết nối mạng và phát hiện tấn công DoS/Flood vào máy trạm."""

    def __init__(
        self,
        syn_flood_threshold: int = 15,
        ip_flood_threshold: int = 30,
        auto_block: bool = True,
        block_duration_seconds: float = 600.0
    ):
        self.syn_flood_threshold = syn_flood_threshold
        self.ip_flood_threshold = ip_flood_threshold
        self.auto_block = auto_block
        self.block_duration = block_duration_seconds

        # IP -> Thời điểm hết hạn chặn
        self._blacklisted_ips: Dict[str, float] = {}

    def parse_netstat_output(self, netstat_text: str) -> List[Dict[str, str]]:
        """Phân tích đầu ra của lệnh netstat thành danh sách kết nối có cấu trúc."""
        connections: List[Dict[str, str]] = []
        if not netstat_text:
            return connections

        for line in netstat_text.strip().splitlines():
            parts = line.strip().split()
            # Ví dụ: TCP    192.168.1.15:54321    192.168.1.50:80    ESTABLISHED    1234
            if len(parts) >= 4 and parts[0].upper() in ("TCP", "UDP"):
                proto = parts[0].upper()
                local_addr = parts[1]
                foreign_addr = parts[2]
                state = parts[3].upper() if proto == "TCP" else "STATELESS"

                # Tách IP và Port của địa chỉ nguồn/đích
                remote_ip = foreign_addr.rsplit(":", 1)[0] if ":" in foreign_addr else foreign_addr
                connections.append({
                    "proto": proto,
                    "local_addr": local_addr,
                    "remote_addr": foreign_addr,
                    "remote_ip": remote_ip,
                    "state": state
                })

        return connections

    def scan_active_connections(self) -> List[Dict[str, str]]:
        """Lấy danh sách kết nối mạng hiện tại từ Windows qua safe_run_command."""
        code, stdout, _ = safe_run_command(["netstat", "-n", "-p", "tcp"], timeout_seconds=5)
        if code == 0:
            return self.parse_netstat_output(stdout)
        return []

    def analyze_connections(self, connections: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Phân tích danh sách kết nối để phát hiện các dấu hiệu tấn công DoS:
        - Đếm số kết nối SYN_RECEIVED (SYN Flood)
        - Đếm số lượng kết nối đồng thời từ mỗi remote IP
        """
        now = time.time()
        ip_connection_counts: Dict[str, int] = {}
        syn_received_by_ip: Dict[str, int] = {}
        threats_detected: List[Dict[str, Any]] = []

        for conn in connections:
            remote_ip = conn.get("remote_ip", "").strip()
            state = conn.get("state", "").upper()

            # Bỏ qua địa chỉ loopback hoặc wildcard
            if not remote_ip or remote_ip in ("127.0.0.1", "0.0.0.0", "*", "[::]", "localhost"):
                continue

            # Đếm tổng kết nối theo IP
            ip_connection_counts[remote_ip] = ip_connection_counts.get(remote_ip, 0) + 1

            # Đếm kết nối nửa mở SYN_RECEIVED
            if "SYN" in state:
                syn_received_by_ip[remote_ip] = syn_received_by_ip.get(remote_ip, 0) + 1

        # 1. Kiểm tra tấn công SYN Flood
        for ip, syn_count in syn_received_by_ip.items():
            if syn_count >= self.syn_flood_threshold:
                threats_detected.append({
                    "type": "SYN_FLOOD",
                    "ip": ip,
                    "count": syn_count,
                    "threshold": self.syn_flood_threshold,
                    "description": f"Phát hiện tấn công SYN Flood ({syn_count} kết nối nửa mở) từ IP {ip}"
                })

        # 2. Kiểm tra tấn công Connection Flood
        for ip, count in ip_connection_counts.items():
            if count >= self.ip_flood_threshold:
                threats_detected.append({
                    "type": "CONNECTION_FLOOD",
                    "ip": ip,
                    "count": count,
                    "threshold": self.ip_flood_threshold,
                    "description": f"Phát hiện tấn công Connection Flood ({count} kết nối đồng thời) từ IP {ip}"
                })

        return {
            "timestamp": now,
            "total_connections": len(connections),
            "threats_count": len(threats_detected),
            "threats": threats_detected,
            "ip_stats": ip_connection_counts,
            "syn_stats": syn_received_by_ip
        }

    def check_and_mitigate(self, connections: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Chạy toàn bộ quy trình: Quét -> Phân tích -> Tự động cô lập IP (Auto-Blackhole) -> Ghi log.
        """
        now = time.time()
        self.cleanup_expired_blocks()

        if connections is None:
            connections = self.scan_active_connections()

        analysis = self.analyze_connections(connections)
        blocked_this_round: List[str] = []

        for threat in analysis.get("threats", []):
            ip = threat["ip"]
            # Kiểm tra định dạng IP hợp lệ trước khi thao tác tường lửa
            try:
                valid_ip = validate_ip(ip)
            except CommandSecurityViolation:
                continue

            if valid_ip not in self._blacklisted_ips:
                self._blacklisted_ips[valid_ip] = now + self.block_duration

                if self.auto_block:
                    ok, msg = HostFirewallManager.block_ip(valid_ip)
                    if ok:
                        blocked_this_round.append(valid_ip)
                        logger.warning(f"[DoSMonitor] TỰ ĐỘNG CHẶN IP TẤN CÔNG {valid_ip}: {threat['description']}")

                app_audit_logger.log_action(
                    event_type="HOST_DOS_ATTACK_DETECTED",
                    actor="network_monitor",
                    target=valid_ip,
                    details=threat["description"],
                    severity="CRITICAL",
                    ip=valid_ip
                )

        analysis["blocked_ips"] = blocked_this_round
        analysis["active_blacklists"] = self.get_blacklist()
        return analysis

    def cleanup_expired_blocks(self):
        """Tự động dọn dẹp các rule đã hết hạn cách ly."""
        now = time.time()
        expired = [ip for ip, exp in self._blacklisted_ips.items() if exp <= now]
        for ip in expired:
            HostFirewallManager.unblock_ip(ip)
            del self._blacklisted_ips[ip]
            logger.info(f"[DoSMonitor] Hết hạn cách ly DoS, đã mở khóa cho IP {ip}")

    def get_blacklist(self) -> Dict[str, float]:
        """Lấy danh sách các IP đang bị khóa cùng thời gian hết hạn."""
        now = time.time()
        return {ip: round(exp - now, 1) for ip, exp in self._blacklisted_ips.items() if exp > now}

    def reset(self):
        """Khởi tạo lại trạng thái giám sát."""
        self._blacklisted_ips.clear()

# Khởi tạo singleton HostDoSMonitor
host_dos_monitor = HostDoSMonitor()

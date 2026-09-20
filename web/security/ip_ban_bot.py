"""
Bot Tự Động Khóa IP Khi Phát Hiện Tấn Công Dồn Dập (Automated IP Ban Bot)
web/security/ip_ban_bot.py

Chức năng:
- Giám sát hành vi và tần suất request của các địa chỉ IP trên toàn hệ thống.
- Tự động kích hoạt cấm (Ban) khi một địa chỉ IP vượt quá ngưỡng 1,000 requests.
- Lưu trữ bền vững danh sách đen IP (banned_ips.json) kèm dấu vết thời gian và lý do.
- Tích hợp gọi Windows Host Firewall (netsh advfirewall) chặn ở tầng mạng OS nếu khả dụng.
- Tích hợp ghi nhật ký Forensic Audit Log (Chained-Hash).
- An toàn đa luồng (Thread-safe) với threading.RLock.
"""

import os
import json
import time
import subprocess
import threading
from typing import Dict, Any, Optional, Tuple, List

try:
    from .audit import audit_logger
except ImportError:
    try:
        from web.security.audit import audit_logger
    except ImportError:
        audit_logger = None

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
BANNED_FILE = os.path.join(DATA_DIR, "banned_ips.json")


class IPBanBot:
    """
    Bot an ninh tự động quản lý và cưỡng chế cấm IP độc hại khi vượt ngưỡng 1000 requests.
    """

    DEFAULT_THRESHOLD = 1000
    DEFAULT_BAN_DURATION = 86400 * 30  # 30 ngày (coi như vĩnh viễn)

    def __init__(
        self,
        ban_threshold: int = DEFAULT_THRESHOLD,
        ban_duration_seconds: int = DEFAULT_BAN_DURATION,
        storage_file: str = BANNED_FILE,
        enable_host_firewall: bool = True
    ):
        self.ban_threshold = ban_threshold
        self.ban_duration_seconds = ban_duration_seconds
        self.storage_file = storage_file
        self.enable_host_firewall = enable_host_firewall
        self._lock = threading.RLock()
        self._last_loaded_mtime: float = 0.0

        # IP -> Dict metadata {banned_at, expires_at, reason, request_count, incident_id}
        self._banned_ips: Dict[str, Dict[str, Any]] = {}
        self._load_from_storage()

    def _ensure_data_dir(self):
        folder = os.path.dirname(self.storage_file)
        if folder and not os.path.exists(folder):
            try:
                os.makedirs(folder, exist_ok=True)
            except Exception:
                pass

    def _load_from_storage(self):
        """Nạp danh sách IP bị cấm từ tệp JSON."""
        if not os.path.exists(self.storage_file):
            return
        try:
            mtime = os.path.getmtime(self.storage_file)
            with open(self.storage_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    now = time.time()
                    with self._lock:
                        self._last_loaded_mtime = mtime
                        # Chỉ giữ lại các IP chưa hết hạn
                        self._banned_ips = {
                            ip: meta for ip, meta in data.items()
                            if meta.get("expires_at", 0) > now
                        }
        except Exception:
            pass

    def _save_to_storage(self):
        """Lưu danh sách IP bị cấm vào tệp JSON."""
        try:
            self._ensure_data_dir()
            with open(self.storage_file, "w", encoding="utf-8") as f:
                json.dump(self._banned_ips, f, ensure_ascii=False, indent=2)
            if os.path.exists(self.storage_file):
                self._last_loaded_mtime = os.path.getmtime(self.storage_file)
        except Exception:
            pass

    def is_banned(self, ip: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Kiểm tra xem địa chỉ IP có đang bị Bot cấm hay không.
        Trả về: (is_banned: bool, ban_info: Optional[dict])
        """
        # Miễn trừ hoàn toàn cho Loopback nội bộ
        if ip in ("127.0.0.1", "::1", "localhost"):
            return False, None

        # Tự động nạp lại nếu file storage bị thay đổi từ bên ngoài
        if os.path.exists(self.storage_file):
            try:
                if os.path.getmtime(self.storage_file) > self._last_loaded_mtime:
                    self._load_from_storage()
            except Exception:
                pass

        now = time.time()
        with self._lock:
            if ip in self._banned_ips:
                meta = self._banned_ips[ip]
                if now < meta.get("expires_at", 0):
                    return True, meta
                else:
                    # Đã hết hạn -> xóa khỏi danh sách
                    del self._banned_ips[ip]
                    self._save_to_storage()

        return False, None

    def ban_ip(
        self,
        ip: str,
        reason: str = "Vượt quá ngưỡng 1000 requests liên tiếp (Bot Ban Kích Hoạt)",
        request_count: int = 1000,
        duration_seconds: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Kích hoạt cấm địa chỉ IP bởi Bot.
        Thực hiện lưu trữ danh sách đen, tạo rule Windows Firewall và ghi nhật ký kiểm toán.
        """
        if ip in ("127.0.0.1", "::1", "localhost"):
            return {"success": False, "message": "Không thể cấm địa chỉ loopback cục bộ."}

        now = time.time()
        duration = duration_seconds or self.ban_duration_seconds
        expires_at = now + duration

        import hashlib
        incident_id = f"BOT-{hashlib.md5(f'{ip}:{now}'.encode()).hexdigest()[:8].upper()}"

        ban_info = {
            "ip": ip,
            "incident_id": incident_id,
            "reason": reason,
            "request_count": request_count,
            "banned_at": now,
            "banned_at_iso": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now)),
            "expires_at": expires_at,
            "expires_at_iso": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(expires_at)),
            "duration_seconds": duration,
            "banned_by": "IPBanBot_v2.0"
        }

        with self._lock:
            self._banned_ips[ip] = ban_info
            self._save_to_storage()

        # 1. Tích hợp gọi Windows Firewall ở tầng mạng
        if self.enable_host_firewall and os.name == "nt":
            self._apply_windows_firewall_rule(ip)

        # 2. Ghi nhật ký Forensic Audit Log
        if audit_logger:
            try:
                audit_logger.log_security_event(
                    event_type="BOT_IP_BANNED",
                    actor="IPBanBot",
                    ip_address=ip,
                    details=f"Incident: {incident_id} | Requests: {request_count} | Reason: {reason}",
                    severity="CRITICAL"
                )
            except Exception:
                pass

        return ban_info

    def unban_ip(self, ip: str) -> bool:
        """Gỡ bỏ lệnh cấm cho địa chỉ IP."""
        with self._lock:
            if ip in self._banned_ips:
                del self._banned_ips[ip]
                self._save_to_storage()
                if self.enable_host_firewall and os.name == "nt":
                    self._remove_windows_firewall_rule(ip)
                if audit_logger:
                    try:
                        audit_logger.log_security_event(
                            event_type="BOT_IP_UNBANNED",
                            actor="admin",
                            ip_address=ip,
                            details="IP đã được mở khóa thủ công",
                            severity="MEDIUM"
                        )
                    except Exception:
                        pass
                return True
        return False

    def get_banned_ips(self) -> Dict[str, Dict[str, Any]]:
        """Lấy danh sách toàn bộ các IP đang bị cấm."""
        now = time.time()
        with self._lock:
            return {
                ip: meta for ip, meta in self._banned_ips.items()
                if meta.get("expires_at", 0) > now
            }

    def reset(self):
        """Khởi tạo lại bộ nhớ bot ban (dùng trong test)."""
        with self._lock:
            self._banned_ips.clear()
            if os.path.exists(self.storage_file):
                try:
                    os.remove(self.storage_file)
                except Exception:
                    pass

    def _apply_windows_firewall_rule(self, ip: str):
        """Thêm rule chặn IP vào Windows Advanced Firewall qua netsh."""
        try:
            rule_name = f"NetManager_BotBan_{ip.replace(':', '_')}"
            # Thêm rule inbound
            cmd_in = f'netsh advfirewall firewall add rule name="{rule_name}_IN" dir=in action=block remoteip={ip}'
            subprocess.run(cmd_in, shell=True, capture_output=True, timeout=3)
        except Exception:
            pass

    def _remove_windows_firewall_rule(self, ip: str):
        """Gỡ rule chặn IP trên Windows Firewall."""
        try:
            rule_name = f"NetManager_BotBan_{ip.replace(':', '_')}"
            cmd_del = f'netsh advfirewall firewall delete rule name="{rule_name}_IN"'
            subprocess.run(cmd_del, shell=True, capture_output=True, timeout=3)
        except Exception:
            pass


# Khởi tạo singleton Bot Ban IP
ip_ban_bot = IPBanBot()

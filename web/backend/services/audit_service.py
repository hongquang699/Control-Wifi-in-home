"""
Lớp 9: Security Audit Logging Module
Ghi nhận toàn bộ các sự kiện bảo mật quan trọng:
- LOGIN_SUCCESS, LOGIN_FAILED, LOGOUT
- DEVICE_BLOCKED, DEVICE_UNBLOCKED, CONFIG_CHANGED
- FILE_DOWNLOADED
- WAF_BLOCKED, RATE_LIMIT_HIT, ADMIN_ACTION

Nguyên tắc bảo mật cốt lõi:
Tuyệt đối không ghi password, token, key hay dữ liệu bí mật vào log.
"""

import os
import time
import json
import threading
from typing import Dict, Any, List, Optional

SENSITIVE_KEYS = {"password", "pass", "token", "secret", "authorization", "cookie", "api_key"}

class AuditLogger:
    def __init__(self, log_dir: Optional[str] = None):
        self._lock = threading.Lock()
        if log_dir is None:
            # web/logs/audit
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.log_dir = os.path.join(base_dir, "logs", "audit")
        else:
            self.log_dir = log_dir

        self.log_file = os.path.join(self.log_dir, "audit.log")
        self._ensure_dir()
        self._memory_cache: List[Dict[str, Any]] = []

    def _ensure_dir(self):
        try:
            if not os.path.exists(self.log_dir):
                os.makedirs(self.log_dir, exist_ok=True)
        except Exception:
            pass

    def _sanitize_details(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Loại bỏ triệt để các trường nhạy cảm trước khi ghi log."""
        sanitized = {}
        for k, v in details.items():
            if any(sensitive in k.lower() for sensitive in SENSITIVE_KEYS):
                sanitized[k] = "[REDACTED]"
            elif isinstance(v, dict):
                sanitized[k] = self._sanitize_details(v)
            else:
                sanitized[k] = v
        return sanitized

    def log_event(
        self,
        event_type: str,
        actor: str = "anonymous",
        ip: str = "127.0.0.1",
        status: str = "SUCCESS",
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ghi một sự kiện kiểm toán bảo mật chuẩn JSON Lines.
        """
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        cleaned_details = self._sanitize_details(details or {})

        event = {
            "timestamp": now,
            "event_type": event_type,
            "actor": actor,
            "client_ip": ip,
            "status": status,
            "details": cleaned_details
        }

        with self._lock:
            # 1. Lưu vào bộ nhớ đệm phục vụ xem nhanh qua giao diện Admin
            self._memory_cache.insert(0, event)
            if len(self._memory_cache) > 500:
                self._memory_cache.pop()

            # 2. Ghi ra tệp tin audit.log
            try:
                self._ensure_dir()
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(event, ensure_ascii=False) + "\n")
            except Exception:
                pass

        return event

    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Lấy danh sách các sự kiện kiểm toán gần nhất."""
        with self._lock:
            return list(self._memory_cache[:limit])

# Singleton AuditLogger instance
audit_logger = AuditLogger()

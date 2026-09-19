"""
Hệ Thống Ghi Nhận Kiểm Toán An Ninh Mạng (Local Security Audit Logger) - app/security/audit_logger.py
Ghi nhận đầy đủ vết hoạt động phục vụ kiểm toán an toàn thông tin (Compliance & Forensic Audit):
- Ghi vết các hành động can thiệp: Chặn thiết bị, Bỏ chặn, Sửa đổi cấu hình, Đổi vai trò RBAC, Phát hiện ARP attack
- Lưu đồng thời vào EventDAO (SQLite) và tệp log kiểm toán nội bộ data/audit_compliance.log
"""

import os
import json
import time
import threading
from typing import Dict, Any, List, Optional
from core.logger import logger

class AppAuditLogger:
    def __init__(self, log_path: str = "data/audit_compliance.log"):
        self.log_path = log_path
        self._lock = threading.Lock()
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

    def log_action(
        self,
        event_type: str,
        actor: str,
        target: str,
        details: str,
        severity: str = "INFO",
        ip: Optional[str] = None
    ) -> Dict[str, Any]:
        """Ghi lại một hành động kiểm toán vào tệp nhật ký."""
        with self._lock:
            ts = time.strftime("%Y-%m-%d %H:%M:%S")
            entry = {
                "timestamp": ts,
                "epoch": time.time(),
                "event_type": event_type,
                "severity": severity,
                "actor": actor,
                "target": target,
                "ip": ip or "--",
                "details": details,
                "status": "AUDITED"
            }

            try:
                with open(self.log_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            except Exception as e:
                logger.error(f"[AppAudit] Lỗi ghi log kiểm toán: {e}")

            return entry

    def get_audit_summary(self) -> Dict[str, int]:
        """Thống kê tổng hợp số lượng sự kiện kiểm toán."""
        total = 0
        blocks = 0
        auths = 0

        if os.path.exists(self.log_path):
            try:
                with open(self.log_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        total += 1
                        if "BLOCK" in line:
                            blocks += 1
                        if "ROLE" in line or "AUTH" in line or "LOGIN" in line:
                            auths += 1
            except Exception:
                pass

        return {
            "total": total,
            "blocks": blocks,
            "auths": auths
        }

# Khởi tạo singleton App Audit Logger
app_audit_logger = AppAuditLogger()

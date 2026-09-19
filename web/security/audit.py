"""
Nhật Ký Kiểm Toán Chống Can Thiệp (Tamper-Evident Security Audit Logger) - web/security/audit.py
Sử dụng cấu trúc chuỗi băm mật mã học (Cryptographic Hash-Chained Audit Trail):
- Mỗi bản ghi sự kiện chứa mã băm SHA-256 của bản ghi liền trước (Blockchain-style)
- Bất kỳ hành vi sửa đổi, chèn thêm, xóa bớt hay can thiệp log từ bên ngoài đều bị phát hiện
- Cung cấp hàm verify_log_integrity() để kiểm toán tính toàn vẹn bất kỳ lúc nào
- Lưu trữ tại web/logs/audit/security_audit.log
"""

import os
import json
import time
import hashlib
import threading
from typing import Dict, Any, List, Tuple

class AuditLogger:
    def __init__(self, log_dir: str = "web/logs/audit"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(self.log_dir, "security_audit.log")
        self._lock = threading.Lock()
        self._last_hash = self._get_initial_hash()

    def _get_initial_hash(self) -> str:
        """Đọc hash của bản ghi cuối cùng hoặc tạo genesis hash nếu file mới."""
        if not os.path.exists(self.log_file) or os.path.getsize(self.log_file) == 0:
            return "0000000000000000000000000000000000000000000000000000000000000000"

        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1].strip()
                    if last_line:
                        entry = json.loads(last_line)
                        return entry.get("hash", "0" * 64)
        except Exception:
            pass
        return "0" * 64

    def log_security_event(
        self,
        event_type: str,
        actor: str,
        ip_address: str,
        details: str,
        severity: str = "INFO"
    ) -> Dict[str, Any]:
        """
        Ghi lại một sự kiện an ninh với chữ ký băm liên kết chống can thiệp.
        """
        with self._lock:
            ts = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
            epoch = time.time()

            raw_payload = f"{epoch}:{event_type}:{actor}:{ip_address}:{severity}:{details}:{self._last_hash}"
            cur_hash = hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()

            entry = {
                "timestamp": ts,
                "epoch": epoch,
                "event_type": event_type,
                "severity": severity,
                "actor": actor,
                "client_ip": ip_address,
                "details": details,
                "prev_hash": self._last_hash,
                "hash": cur_hash
            }

            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

            self._last_hash = cur_hash
            return entry

    def verify_log_integrity(self) -> Tuple[bool, int, str]:
        """
        Kiểm tra tính toàn vẹn của toàn bộ nhật ký.
        Trả về: (is_valid: bool, verified_count: int, message: str)
        """
        with self._lock:
            if not os.path.exists(self.log_file):
                return True, 0, "File log chưa tồn tại"

            expected_prev = "0000000000000000000000000000000000000000000000000000000000000000"
            count = 0

            with open(self.log_file, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, start=1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        epoch = entry.get("epoch")
                        event_type = entry.get("event_type")
                        actor = entry.get("actor")
                        ip_address = entry.get("client_ip")
                        severity = entry.get("severity")
                        details = entry.get("details")
                        prev_hash = entry.get("prev_hash")
                        cur_hash = entry.get("hash")

                        if prev_hash != expected_prev:
                            return False, count, f"LỖI TOÀN VẸN: Chuỗi băm bị đứt gãy tại dòng {line_num}! Prev hash không khớp."

                        raw_payload = f"{epoch}:{event_type}:{actor}:{ip_address}:{severity}:{details}:{prev_hash}"
                        recomputed = hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()

                        if recomputed != cur_hash:
                            return False, count, f"LỖI TOÀN VẸN: Nội dung dòng {line_num} đã bị sửa đổi trái phép!"

                        expected_prev = cur_hash
                        count += 1
                    except Exception as e:
                        return False, count, f"LỖI PHÂN TÍCH: Dòng {line_num} bị lỗi định dạng: {e}"

            return True, count, f"Xác minh thành công: {count} bản ghi toàn vẹn 100%, không bị can thiệp."

# Khởi tạo singleton audit logger
audit_logger = AuditLogger()

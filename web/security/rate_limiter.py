"""
Hệ Thống Giới Hạn Tần Suất & Tự Động Khóa IP (Rate Limiter & Auto-Jail) - web/security/rate_limiter.py
Sử dụng thuật toán Sliding-Window Log kết hợp cơ chế Auto-Jail (Fail2Ban-style):
- Giới hạn request trên mỗi địa chỉ IP (mặc định 60 req/phút cho API, 10 req/phút cho đăng nhập)
- Tự động cách ly (Jail/Ban) các địa chỉ IP cố tình gửi request spam hoặc bị WAF đánh dấu
- Hỗ trợ thời gian phạt lũy tiến (Exponential Backoff Ban Duration)
- An toàn đa luồng (Thread-safe) với threading.Lock
"""

import time
import threading
from typing import Dict, List, Tuple, Optional

class RateLimiter:
    """Bộ điều tiết lưu lượng và bảo vệ từ chối dịch vụ (DoS Protection)."""

    def __init__(
        self,
        default_limit_per_minute: int = 60,
        auth_limit_per_minute: int = 10,
        jail_violation_threshold: int = 5,
        default_jail_duration_seconds: int = 300
    ):
        self.default_limit = default_limit_per_minute
        self.auth_limit = auth_limit_per_minute
        self.jail_threshold = jail_violation_threshold
        self.default_jail_duration = default_jail_duration_seconds

        self._lock = threading.Lock()
        # IP -> List[timestamps]
        self._request_logs: Dict[str, List[float]] = {}
        # IP -> int (số lần vi phạm)
        self._violations: Dict[str, int] = {}
        # IP -> float (thời điểm hết hạn ban)
        self._jailed_ips: Dict[str, float] = {}

    def is_allowed(self, client_ip: str, endpoint: str = "") -> Tuple[bool, int, Optional[str]]:
        """
        Kiểm tra xem request từ client_ip có được phép hay không.
        Trả về: (allowed: bool, retry_after_seconds: int, reason: Optional[str])
        """
        now = time.time()

        with self._lock:
            # 1. Kiểm tra xem IP có đang bị Jail/Khóa hay không
            if client_ip in self._jailed_ips:
                unban_time = self._jailed_ips[client_ip]
                if now < unban_time:
                    remaining = int(unban_time - now) + 1
                    return False, remaining, f"IP bị tạm khóa do vi phạm an ninh liên tiếp. Thử lại sau {remaining} giây."
                else:
                    # Hết hạn khóa -> mở unjail
                    del self._jailed_ips[client_ip]

            # 2. Xác định giới hạn của endpoint
            limit = self.default_limit
            if any(k in endpoint.lower() for k in ["/login", "/auth", "/token", "/admin"]):
                limit = self.auth_limit

            # 3. Lọc lịch sử trong cửa sổ 60 giây qua
            window_start = now - 60.0
            logs = self._request_logs.get(client_ip, [])
            valid_logs = [ts for ts in logs if ts > window_start]
            self._request_logs[client_ip] = valid_logs

            # 4. Kiểm tra vượt ngưỡng
            if len(valid_logs) >= limit:
                # Ghi nhận vi phạm
                violations = self._violations.get(client_ip, 0) + 1
                self._violations[client_ip] = violations

                # Nếu vi phạm nhiều lần liên tiếp -> đưa vào Jail
                if violations >= self.jail_threshold:
                    ban_duration = self.default_jail_duration * min(10, violations - self.jail_threshold + 1)
                    self._jailed_ips[client_ip] = now + ban_duration
                    return False, ban_duration, f"Phát hiện hành vi tấn công từ chối dịch vụ. IP đã bị đưa vào danh sách cách ly {ban_duration}s."

                oldest_ts = valid_logs[0]
                retry_after = int(60.0 - (now - oldest_ts)) + 1
                return False, retry_after, f"Vượt quá tần suất cho phép ({limit} req/phút). Vui lòng thử lại sau {retry_after}s."

            # Hợp lệ -> lưu timestamp
            valid_logs.append(now)
            self._request_logs[client_ip] = valid_logs
            return True, 0, None

    def record_security_violation(self, client_ip: str, weight: int = 2):
        """Ghi nhận trực tiếp một vi phạm an ninh (ví dụ: bị WAF chặn) để tăng tốc độ cách ly IP."""
        now = time.time()
        with self._lock:
            violations = self._violations.get(client_ip, 0) + weight
            self._violations[client_ip] = violations
            if violations >= self.jail_threshold:
                ban_duration = self.default_jail_duration * min(10, violations - self.jail_threshold + 1)
                self._jailed_ips[client_ip] = now + ban_duration

    def unjail_ip(self, client_ip: str):
        """Mở khóa thủ công cho một IP."""
        with self._lock:
            self._jailed_ips.pop(client_ip, None)
            self._violations.pop(client_ip, None)

    def get_jailed_ips(self) -> Dict[str, float]:
        """Lấy danh sách các IP đang bị cách ly cùng thời gian hết hạn."""
        now = time.time()
        with self._lock:
            return {ip: t_exp for ip, t_exp in self._jailed_ips.items() if t_exp > now}

# Khởi tạo singleton Rate Limiter
rate_limiter = RateLimiter()

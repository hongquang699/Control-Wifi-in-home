"""
Lớp 2: Rate Limiting Middleware (Chống Brute-force & HTTP Flood)
Sử dụng thuật toán Sliding-Window Counter theo địa chỉ IP máy khách.
"""

import time
import threading
from typing import Dict, List, Tuple

class RateLimiter:
    def __init__(self):
        self._lock = threading.Lock()
        # Lưu trữ lịch sử timestamp theo (ip, zone): [t1, t2, ...]
        self._records: Dict[Tuple[str, str], List[float]] = {}
        # Danh sách IP bị tạm khóa do vi phạm lặp lại: ip -> unlock_timestamp
        self._banned_ips: Dict[str, float] = {}

    def is_rate_limited(self, ip: str, zone: str = "api", max_requests: int = 100, window_seconds: int = 60) -> Tuple[bool, int]:
        """
        Kiểm tra xem request từ IP này có vượt ngưỡng không.
        Trả về (is_blocked, retry_after_seconds).
        """
        now = time.time()
        key = (ip, zone)

        with self._lock:
            # 1. Kiểm tra xem IP có đang bị tạm khóa không
            if ip in self._banned_ips:
                unlock_time = self._banned_ips[ip]
                if now < unlock_time:
                    return True, int(unlock_time - now)
                else:
                    del self._banned_ips[ip]

            # 2. Làm sạch các timestamp cũ ngoài khung thời gian sliding window
            if key not in self._records:
                self._records[key] = []

            cutoff = now - window_seconds
            self._records[key] = [t for t in self._records[key] if t > cutoff]

            # 3. Kiểm tra số lượng request trong window
            if len(self._records[key]) >= max_requests:
                # Nếu vi phạm zone nhạy cảm như "login", phạt khóa 15 phút (900s)
                if zone == "login":
                    self._banned_ips[ip] = now + 900
                    return True, 900
                
                earliest = self._records[key][0]
                retry_after = max(1, int(window_seconds - (now - earliest)))
                return True, retry_after

            # 4. Ghi nhận request hợp lệ
            self._records[key].append(now)
            return False, 0

    def cleanup(self):
        """Dọn dẹp các bản ghi cũ để giải phóng bộ nhớ."""
        now = time.time()
        with self._lock:
            for key in list(self._records.keys()):
                self._records[key] = [t for t in self._records[key] if t > (now - 300)]
                if not self._records[key]:
                    del self._records[key]
            for ip in list(self._banned_ips.keys()):
                if now >= self._banned_ips[ip]:
                    del self._banned_ips[ip]

# Singleton RateLimiter instance
rate_limiter = RateLimiter()

"""
Bảo Vệ Tài Khoản Khỏi Brute-Force & Credential Stuffing (Account Lockout) - web/security/account_lockout.py
Theo dõi số lần đăng nhập thất bại theo username, độc lập với IP:
- Ngăn chặn mạng botnet phân tán xoay IP (IP Rotation) để dò mật khẩu
- Khóa tài khoản tạm thời khi vượt quá số lần thử tối đa (mặc định 5 lần)
- Tự động mở khóa sau khoảng thời gian cấu hình (mặc định 15 phút)
"""

import time
import threading
from typing import Dict, Tuple, Optional

class AccountLockoutManager:
    """Quản lý trạng thái khóa tài khoản khi có hành vi dò mật khẩu."""

    def __init__(self, max_attempts: int = 5, lockout_seconds: int = 900):
        self.max_attempts = max_attempts
        self.lockout_seconds = lockout_seconds
        self._lock = threading.Lock()
        # username -> {"failed_attempts": int, "locked_until": float, "last_attempt": float}
        self._accounts: Dict[str, Dict[str, float]] = {}

    def is_locked(self, username: str) -> Tuple[bool, int]:
        """
        Kiểm tra xem tài khoản có đang bị khóa hay không.
        Trả về: (is_locked: bool, remaining_seconds: int)
        """
        user_key = username.strip().lower()
        now = time.time()

        with self._lock:
            record = self._accounts.get(user_key)
            if not record:
                return False, 0

            locked_until = record.get("locked_until", 0)
            if locked_until > now:
                remaining = int(locked_until - now)
                return True, max(1, remaining)
            elif locked_until > 0:
                # Đã hết thời gian phạt -> xóa trạng thái khóa
                record["locked_until"] = 0
                record["failed_attempts"] = 0
                return False, 0

            return False, 0

    def record_failure(self, username: str) -> Tuple[bool, int]:
        """
        Ghi nhận một lần đăng nhập thất bại.
        Trả về: (just_locked: bool, remaining_attempts_or_lockout_seconds: int)
        """
        user_key = username.strip().lower()
        now = time.time()

        with self._lock:
            if user_key not in self._accounts:
                self._accounts[user_key] = {
                    "failed_attempts": 0,
                    "locked_until": 0,
                    "last_attempt": now
                }

            record = self._accounts[user_key]
            # Nếu lần thất bại trước cách xa hơn 1 giờ, reset bộ đếm
            if now - record["last_attempt"] > 3600:
                record["failed_attempts"] = 0

            record["failed_attempts"] += 1
            record["last_attempt"] = now

            if record["failed_attempts"] >= self.max_attempts:
                record["locked_until"] = now + self.lockout_seconds
                return True, self.lockout_seconds

            remaining_attempts = self.max_attempts - record["failed_attempts"]
            return False, remaining_attempts

    def record_success(self, username: str) -> None:
        """Đăng nhập thành công -> xóa bỏ toàn bộ lịch sử vi phạm của username."""
        user_key = username.strip().lower()
        with self._lock:
            if user_key in self._accounts:
                del self._accounts[user_key]

    def reset(self) -> None:
        """Xóa toàn bộ bộ nhớ cache (dùng cho testing)."""
        with self._lock:
            self._accounts.clear()

# Singleton instance
account_lockout_manager = AccountLockoutManager()

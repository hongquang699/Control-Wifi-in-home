"""
Lớp 3 & Lớp 4: Session Management & RBAC (Role-Based Access Control)
Hỗ trợ 3 vai trò:
- ADMIN: Toàn quyền (quản trị người dùng, audit log, cấu hình, sao lưu database)
- OPERATOR: Quản lý thiết bị, quét mạng, chặn/bỏ chặn MAC
- USER: Khách / người dùng cơ bản, chỉ xem Dashboard và tải xuống
"""

import time
import secrets
import threading
from enum import Enum
from typing import Dict, Optional, Any, List, Tuple
from .password import hash_password, verify_password

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    OPERATOR = "OPERATOR"
    USER = "USER"

    @classmethod
    def can_access(cls, user_role: "UserRole", required_role: "UserRole") -> bool:
        hierarchy = {
            cls.ADMIN: 3,
            cls.OPERATOR: 2,
            cls.USER: 1
        }
        return hierarchy.get(user_role, 0) >= hierarchy.get(required_role, 0)

class User:
    def __init__(self, username: str, password_hash: str, role: UserRole, full_name: str):
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.full_name = full_name
        self.failed_login_attempts = 0
        self.locked_until = 0.0

    def is_locked(self) -> bool:
        return time.time() < self.locked_until

class Session:
    def __init__(self, token: str, username: str, role: UserRole, ip: str, ttl_seconds: int = 7200):
        self.token = token
        self.username = username
        self.role = role
        self.ip = ip
        self.created_at = time.time()
        self.expires_at = self.created_at + ttl_seconds

    def is_expired(self) -> bool:
        return time.time() > self.expires_at

    def touch(self, extend_seconds: int = 3600):
        self.expires_at = time.time() + extend_seconds

class SessionManager:
    def __init__(self):
        self._lock = threading.Lock()
        self._sessions: Dict[str, Session] = {}
        self._users: Dict[str, User] = {}
        self._init_default_users()

    def _init_default_users(self):
        """Khởi tạo các tài khoản mẫu với mật khẩu đã băm PBKDF2."""
        self._users["admin"] = User(
            username="admin",
            password_hash=hash_password("Admin@Security2026"),
            role=UserRole.ADMIN,
            full_name="Quản Trị Viên Hệ Thống"
        )
        self._users["operator"] = User(
            username="operator",
            password_hash=hash_password("Operator@Network2026"),
            role=UserRole.OPERATOR,
            full_name="Kỹ Thuật Viên Vận Hành"
        )
        self._users["viewer"] = User(
            username="viewer",
            password_hash=hash_password("Viewer@Guest2026"),
            role=UserRole.USER,
            full_name="Khách Xem Hệ Thống"
        )

    def authenticate(self, username: str, password: str, client_ip: str) -> Tuple[Optional[Session], str]:
        """
        Xác thực thông tin đăng nhập, tạo session token nếu đúng.
        Trả về (Session, error_message).
        """
        with self._lock:
            user = self._users.get(username.lower())
            if not user:
                return None, "Tài khoản hoặc mật khẩu không chính xác"

            # Kiểm tra tài khoản có đang bị khóa do nhập sai nhiều lần
            if user.is_locked():
                remain = int(user.locked_until - time.time())
                return None, f"Tài khoản đang bị tạm khóa. Vui lòng thử lại sau {remain} giây"

            # Xác thực mật khẩu
            if not verify_password(password, user.password_hash):
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= 5:
                    user.locked_until = time.time() + 900  # Khóa 15 phút
                    user.failed_login_attempts = 0
                    return None, "Nhập sai mật khẩu 5 lần liên tiếp. Tài khoản đã bị khóa 15 phút."
                remaining_attempts = 5 - user.failed_login_attempts
                return None, f"Mật khẩu không đúng. Còn {remaining_attempts} lần thử."

            # Đăng nhập thành công -> reset số lần sai
            user.failed_login_attempts = 0
            user.locked_until = 0.0

            # Tạo cryptographically secure token
            token = secrets.token_hex(32)
            session = Session(token, user.username, user.role, client_ip)
            self._sessions[token] = session
            return session, ""

    def get_session(self, token: Optional[str]) -> Optional[Session]:
        """Lấy phiên làm việc hợp lệ từ token."""
        if not token:
            return None
        with self._lock:
            session = self._sessions.get(token)
            if not session:
                return None
            if session.is_expired():
                del self._sessions[token]
                return None
            session.touch()  # Gia hạn phiên
            return session

    def revoke_session(self, token: str) -> bool:
        """Thu hồi token khi đăng xuất."""
        with self._lock:
            if token in self._sessions:
                del self._sessions[token]
                return True
            return False

    def list_users(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [
                {
                    "username": u.username,
                    "full_name": u.full_name,
                    "role": u.role.value,
                    "is_locked": u.is_locked()
                }
                for u in self._users.values()
            ]

# Singleton SessionManager instance
session_manager = SessionManager()

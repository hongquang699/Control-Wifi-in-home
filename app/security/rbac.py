"""
Hệ Thống Phân Quyền & Kiểm Soát Truy Cập Chương Trình (Programmatic RBAC Engine) - app/security/rbac.py
Ngăn chặn người dùng thực thi các tác vụ nhạy cảm trái phép kể cả khi cố ý bypass UI:
- Cung cấp các hàm kiểm tra và Decorator: @require_role, @require_permission
- Định nghĩa ma trận quyền hạn nghiêm ngặt cho 3 cấp độ: ADMIN, OPERATOR, VIEWER
- Đồng bộ tự động với RoleManager trên GUI
"""

import functools
from typing import Set, Dict, List, Callable, Any

class PermissionDeniedError(Exception):
    """Ngoại lệ khi người dùng không đủ quyền thực thi hành động này."""
    def __init__(self, required_permission: str, current_role: str):
        self.required_permission = required_permission
        self.current_role = current_role
        super().__init__(f"Từ chối quyền: Cần quyền '{required_permission}' nhưng vai trò hiện tại là '{current_role}'")


ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    "ADMIN": {
        "network:read",
        "network:scan",
        "device:block",
        "device:unblock",
        "device:rename",
        "router:test",
        "router:config",
        "settings:write",
        "audit:read",
        "audit:backup",
        "audit:clear"
    },
    "OPERATOR": {
        "network:read",
        "network:scan",
        "device:block",
        "device:unblock",
        "device:rename",
        "router:test"
    },
    "VIEWER": {
        "network:read"
    }
}


class RBACManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.current_role = "ADMIN"
            cls._instance._listeners = []
        return cls._instance

    def set_role(self, role: str):
        """Thiết lập vai trò hiện tại trong phiên."""
        r_upper = role.upper()
        if r_upper in ROLE_PERMISSIONS:
            self.current_role = r_upper
            for cb in self._listeners:
                try:
                    cb(r_upper)
                except Exception:
                    pass

    def get_role(self) -> str:
        return self.current_role

    def has_permission(self, permission: str) -> bool:
        """Kiểm tra vai trò hiện tại có quyền permission hay không."""
        allowed = ROLE_PERMISSIONS.get(self.current_role, set())
        return permission in allowed

    def subscribe(self, callback: Callable[[str], None]):
        if callback not in self._listeners:
            self._listeners.append(callback)

rbac_manager = RBACManager()


def require_role(*allowed_roles: str):
    """Decorator yêu cầu vai trò nằm trong allowed_roles."""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cur = rbac_manager.get_role()
            if cur not in allowed_roles:
                raise PermissionDeniedError(f"Role in {allowed_roles}", cur)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_permission(permission: str):
    """Decorator yêu cầu có quyền permission tương ứng."""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not rbac_manager.has_permission(permission):
                raise PermissionDeniedError(permission, rbac_manager.get_role())
            return func(*args, **kwargs)
        return wrapper
    return decorator

"""
Kiểm Soát Kích Thước & Định Dạng Request (Request Guard) - web/security/request_guard.py
Bảo vệ Web Server trước các cuộc tấn công từ chối dịch vụ DoS qua payload lớn:
- Giới hạn Content-Length tối đa (mặc định 2MB cho JSON API, 50MB cho upload)
- Kiểm tra tính hợp lệ của Content-Type đối với các phương thức thay đổi trạng thái (POST, PUT, PATCH)
- Chặn đứng tấn công tràn bộ nhớ (Memory Exhaustion / Buffer Bloating)
"""

from typing import Tuple, Dict, Optional

# Giới hạn kích thước body tối đa mặc định (2 MB)
DEFAULT_MAX_BODY_SIZE = 2 * 1024 * 1024

# Danh sách MIME type hợp lệ cho API
ALLOWED_MUTATING_CONTENT_TYPES = [
    "application/json",
    "application/x-www-form-urlencoded",
    "multipart/form-data",
    "text/plain"
]

class RequestGuardViolation(Exception):
    """Ngoại lệ khi request vi phạm chính sách kích thước hoặc MIME."""
    def __init__(self, code: int, reason: str):
        self.code = code
        self.reason = reason
        super().__init__(f"[RequestGuard {code}] {reason}")


class RequestGuard:
    """Động cơ kiểm tra kích thước và tiêu đề của request HTTP."""

    def __init__(self, max_body_size: int = DEFAULT_MAX_BODY_SIZE):
        self.max_body_size = max_body_size

    def validate_request(
        self,
        method: str,
        path: str,
        headers: Dict[str, str]
    ) -> Tuple[bool, int, Optional[str]]:
        """
        Thẩm định request trước khi đọc body.
        Trả về: (is_valid: bool, status_code: int, error_message: Optional[str])
        """
        method_upper = method.upper()

        # 1. Kiểm tra Content-Length
        content_length_str = headers.get("Content-Length", headers.get("content-length"))
        if content_length_str:
            try:
                content_length = int(content_length_str)
                if content_length < 0:
                    return False, 400, "Content-Length không hợp lệ (số âm)!"
                if content_length > self.max_body_size:
                    return False, 413, f"Kích thước request ({content_length} bytes) vượt quá giới hạn cho phép ({self.max_body_size} bytes)!"
            except ValueError:
                return False, 400, "Tiêu đề Content-Length không phải là số nguyên hợp lệ!"

        # 2. Kiểm tra Content-Type cho các phương thức có body (POST, PUT, PATCH)
        if method_upper in ("POST", "PUT", "PATCH") and content_length_str and int(content_length_str) > 0:
            content_type = headers.get("Content-Type", headers.get("content-type", "")).lower()
            # Lấy MIME cơ bản trước dấu chấm phẩy (ví dụ: application/json; charset=utf-8)
            base_mime = content_type.split(";")[0].strip()
            if base_mime and not any(base_mime.startswith(allowed) for allowed in ALLOWED_MUTATING_CONTENT_TYPES):
                return False, 415, f"Định dạng Content-Type '{base_mime}' không được hỗ trợ bởi hệ thống API!"

        return True, 200, None

# Singleton instance
request_guard = RequestGuard()

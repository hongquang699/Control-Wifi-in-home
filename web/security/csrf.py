"""
Hệ Thống Phòng Vệ Tấn Công Giả Mạo Yêu Cầu (Anti-CSRF Protection) - web/security/csrf.py
Bảo vệ các tác vụ thay đổi trạng thái (POST, PUT, DELETE) trước tấn công Cross-Site Request Forgery:
- Sinh token mật mã học ngẫu nhiên gắn kèm phiên làm việc hoặc cookie
- Kiểm tra tính hợp lệ bằng phép so sánh an toàn constant-time (hmac.compare_digest)
- Tự động miễn trừ các phương thức HTTP an toàn chỉ đọc (GET, HEAD, OPTIONS)
"""

import time
import secrets
import hmac
from typing import Dict, Optional, Tuple

class CSRFProtector:
    def __init__(self, token_ttl_seconds: int = 3600):
        self.token_ttl = token_ttl_seconds
        # session_id/ip -> (token, expiry_timestamp)
        self._tokens: Dict[str, Tuple[str, float]] = {}

    def generate_token(self, session_key: str) -> str:
        """Sinh một mã CSRF Token mới cho phiên làm việc."""
        token = secrets.token_urlsafe(32)
        expiry = time.time() + self.token_ttl
        self._tokens[session_key] = (token, expiry)
        return token

    def validate_request(
        self,
        method: str,
        session_key: str,
        submitted_token: Optional[str]
    ) -> Tuple[bool, Optional[str]]:
        """
        Xác minh tính hợp lệ của token CSRF đối với các phương thức thay đổi dữ liệu.
        """
        # GET, HEAD, OPTIONS là các phương thức chỉ đọc, được miễn trừ theo chuẩn RFC 7231
        if method.upper() in ("GET", "HEAD", "OPTIONS"):
            return True, None

        if not session_key:
            return False, "Thiếu khóa định danh phiên làm việc (Session Key)"

        record = self._tokens.get(session_key)
        if not record:
            return False, "Không tìm thấy phiên làm việc hoặc CSRF Token chưa được khởi tạo"

        expected_token, expiry = record
        now = time.time()
        if now > expiry:
            del self._tokens[session_key]
            return False, "CSRF Token đã hết hạn, vui lòng tải lại trang"

        if not submitted_token:
            return False, "Thiếu tiêu đề 'X-CSRF-Token' hoặc trường 'csrf_token' trong yêu cầu"

        # So sánh constant-time
        if not hmac.compare_digest(submitted_token.encode("utf-8"), expected_token.encode("utf-8")):
            return False, "Mã CSRF Token không hợp lệ hoặc đã bị giả mạo"

        return True, None

# Khởi tạo singleton CSRF Protector
csrf_protector = CSRFProtector()

"""
Hệ Thống Kiểm Soát Chia Sẻ Tài Nguyên Gốc (Cross-Origin Resource Sharing - CORS)
web/security/cors.py

Thực hiện kỹ thuật bảo mật số 2 trong 7 Kỹ Thuật Bảo Mật API:
1. Whitelist kiểm soát nghiêm ngặt các Origin được phép gọi API (tránh tấn công Cross-Origin Data Theft).
2. Xử lý yêu cầu Preflight (OPTIONS request) chuẩn RFC 6454 / W3C CORS Spec.
3. Chống rò rỉ thông tin xác thực (Không bao giờ kết hợp Wildcard '*' với Access-Control-Allow-Credentials: true).
4. Thiết lập Access-Control-Max-Age tối ưu hóa hiệu năng preflight caching.
"""

import re
import urllib.parse
from typing import Set, List, Optional, Tuple

class CORSManager:
    """Bộ điều phối chính sách CORS an toàn cho REST API."""

    def __init__(
        self,
        allowed_origins: Optional[List[str]] = None,
        allow_credentials: bool = True,
        max_age: int = 86400
    ):
        self.allowed_origins: Set[str] = set(allowed_origins or [
            "http://localhost:8080",
            "http://127.0.0.1:8080",
            "http://localhost:3000",
            "http://127.0.0.1:3000"
        ])
        self.allow_credentials = allow_credentials
        self.max_age = max_age
        self.allowed_methods = "GET, POST, PUT, DELETE, OPTIONS"
        self.allowed_headers = "Content-Type, Authorization, X-CSRF-Token, X-Requested-With, Accept, Origin"

        # Regex cho phép các dải IP mạng nội bộ và VPN cục bộ
        self._private_origin_regex = re.compile(
            r"^https?://(localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2[0-9]|3[0-1])\.\d{1,3}\.\d{1,3}|100\.(6[4-9]|[7-9][0-9]|1[0-1][0-9]|12[0-7])\.\d{1,3}\.\d{1,3})(:\d+)?$",
            re.IGNORECASE
        )

    def is_origin_allowed(self, origin: Optional[str]) -> bool:
        """Kiểm tra một Origin có nằm trong danh sách an toàn hay không."""
        if not origin:
            # Same-Origin request không gửi header Origin -> luôn cho phép
            return True

        origin_clean = origin.strip().rstrip("/")
        if origin_clean in self.allowed_origins:
            return True

        # Cho phép các nguồn gốc từ IP riêng tư / VPN LAN
        if self._private_origin_regex.match(origin_clean):
            return True

        return False

    def handle_preflight(self, handler, origin: Optional[str]) -> bool:
        """
        Xử lý yêu cầu HTTP OPTIONS Preflight.
        Trả về True nếu preflight được chấp thuận và response được gửi đi.
        """
        if not self.is_origin_allowed(origin):
            handler.send_response(403)
            handler.send_header("Content-Type", "application/json; charset=utf-8")
            handler.end_headers()
            handler.wfile.write(b'{"error": "CORS policy: Nguon goc (Origin) bi tu choi boi chinh sach bao mat."}')
            return False

        handler.send_response(204) # No Content cho Preflight thành công
        if origin:
            handler.send_header("Access-Control-Allow-Origin", origin)
            if self.allow_credentials:
                handler.send_header("Access-Control-Allow-Credentials", "true")
        else:
            handler.send_header("Access-Control-Allow-Origin", "*")

        handler.send_header("Access-Control-Allow-Methods", self.allowed_methods)
        handler.send_header("Access-Control-Allow-Headers", self.allowed_headers)
        handler.send_header("Access-Control-Max-Age", str(self.max_age))
        handler.end_headers()
        return True

    def apply_cors_headers(self, handler, origin: Optional[str]):
        """Gắn tiêu đề CORS vào các response GET/POST thông thường."""
        if not origin:
            return

        if self.is_origin_allowed(origin):
            handler.send_header("Access-Control-Allow-Origin", origin)
            if self.allow_credentials:
                handler.send_header("Access-Control-Allow-Credentials", "true")
            handler.send_header("Vary", "Origin")


# Instance singleton mặc định
cors_manager = CORSManager()

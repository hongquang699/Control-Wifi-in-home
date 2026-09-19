"""
Bộ Tiêu Đề An Ninh Chuẩn Quân Sự (Security Headers Engine) - web/security/headers.py
Bảo vệ trình duyệt máy khách trước các cuộc tấn công Clickjacking, MIME-confusion,
XSS Injection, Data Exfiltration, và Buộc sử dụng kết nối mã hóa an toàn.
"""

from typing import Dict

# Bộ tiêu đề an ninh mặc định cấp cao nhất
DEFAULT_SECURITY_HEADERS = {
    # 1. Chống Clickjacking
    "X-Frame-Options": "DENY",

    # 2. Ngăn chặn trình duyệt đoán định dạng tệp (MIME Sniffing)
    "X-Content-Type-Options": "nosniff",

    # 3. Kích hoạt bộ lọc XSS tích hợp của trình duyệt cũ
    "X-XSS-Protection": "1; mode=block",

    # 4. Kiểm soát nguồn tham chiếu (Referrer Leaks)
    "Referrer-Policy": "strict-origin-when-cross-origin",

    # 5. Vô hiệu hóa các API phần cứng nhạy cảm
    "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=(), usb=()",

    # 6. Ép buộc kênh truyền mã hóa HTTPS an toàn (HSTS)
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",

    # 7. Cô lập tiến trình duyệt web (Cross-Origin Protections)
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Resource-Policy": "same-origin",
    "Cross-Origin-Embedder-Policy": "credentialless",
    "X-Permitted-Cross-Domain-Policies": "none",

    # 8. Chính sách bảo mật nội dung tối ưu (Content-Security-Policy)
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn-uicons.flaticon.com https://fonts.googleapis.com; "
        "font-src 'self' https://cdn-uicons.flaticon.com https://fonts.gstatic.com data:; "
        "img-src 'self' data: https:; "
        "connect-src 'self' ws: wss:; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "frame-ancestors 'none'; "
        "form-action 'self';"
    )
}

API_CACHE_CONTROL_HEADERS = {
    "Cache-Control": "no-store, no-cache, must-revalidate, private, max-age=0",
    "Pragma": "no-cache",
    "Expires": "0"
}


def apply_security_headers(handler, is_api_response: bool = False):
    """
    Gắn toàn bộ các tiêu đề an ninh vào đối tượng phản hồi HTTP của máy chủ.
    """
    for header, value in DEFAULT_SECURITY_HEADERS.items():
        handler.send_header(header, value)

    if is_api_response:
        for header, value in API_CACHE_CONTROL_HEADERS.items():
            handler.send_header(header, value)

"""
Lớp 1 & Lớp 8: Security Headers Middleware
Cung cấp và gắn các HTTP Security Headers chuẩn bảo vệ trình duyệt.
"""

from typing import Dict, Any

SECURITY_HEADERS: Dict[str, str] = {
    # 1. Content-Security-Policy (CSP) - Giới hạn nguồn tài nguyên được tải
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
          "https://cdn.tailwindcss.com "
          "https://cdnjs.cloudflare.com "
          "https://cdn.jsdelivr.net "
          "https://www.googletagmanager.com "
          "https://www.google-analytics.com; "
        "style-src 'self' 'unsafe-inline' "
          "https://fonts.googleapis.com "
          "https://cdnjs.cloudflare.com "
          "https://cdn-uicons.flaticon.com "
          "https://cdn.jsdelivr.net; "
        "font-src 'self' "
          "https://fonts.gstatic.com "
          "https://cdnjs.cloudflare.com "
          "https://cdn-uicons.flaticon.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self' https://www.google-analytics.com; "
        "frame-ancestors 'self'; "
        "base-uri 'self'; "
        "form-action 'self';"
    ),
    # 2. Strict-Transport-Security (HSTS) - Bắt buộc HTTPS 1 năm
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
    # 3. X-Content-Type-Options - Chống MIME-sniffing
    "X-Content-Type-Options": "nosniff",
    # 4. X-Frame-Options - Chống Clickjacking
    "X-Frame-Options": "SAMEORIGIN",
    # 5. Referrer-Policy - Kiểm soát rò rỉ URL trong Referer header
    "Referrer-Policy": "strict-origin-when-cross-origin",
    # 6. Permissions-Policy - Vô hiệu hóa các API trình duyệt nguy hiểm
    "Permissions-Policy": "geolocation=(), microphone=(), camera=(), payment=(), usb=()",
    # 7. Cross-Origin-Opener-Policy & Resource-Policy
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Resource-Policy": "same-origin",
    # 8. Server header masking (Ẩn thông tin công nghệ backend)
    "Server": "NetworkManager-SecurityCore/1.2"
}

def apply_security_headers(handler: Any):
    """
    Gắn toàn bộ các security headers vào HTTP response.
    """
    for header_name, header_value in SECURITY_HEADERS.items():
        handler.send_header(header_name, header_value)

"""
Gói Bảo Mật Chuyên Biệt Dành Cho Web (Web Enterprise Security Suite) - web/security/__init__.py
Cung cấp toàn bộ các công cụ phòng vệ đa lớp theo chuẩn OWASP Top 10:
- waf_engine: Tường lửa ứng dụng lọc SQLi, XSS, Path Traversal, RCE, Bad User-Agents
- rate_limiter: Bộ điều tiết tần suất request Sliding-Window kết hợp Auto-Jail IP
- apply_security_headers: Gắn bộ tiêu đề an ninh chuẩn quân sự (CSP, HSTS, X-Frame DENY...)
- csrf_protector: Phòng vệ tấn công giả mạo yêu cầu Anti-CSRF
- hash_password / verify_password: Động cơ mật mã PBKDF2-HMAC-SHA256 (600,000 vòng lặp)
- sanitize_input / sanitize_string: Làm sạch đệ quy dữ liệu đầu vào JSON và form
- audit_logger: Nhật ký kiểm toán chuỗi băm chống can thiệp (Chained Hash Log)
"""

from .crypto import (
    hash_password,
    verify_password,
    generate_secure_token,
    sign_data,
    verify_signed_data,
    constant_time_compare
)

from .waf import (
    WAFEngine,
    WAFSecurityException,
    waf_engine
)

from .rate_limiter import (
    RateLimiter,
    rate_limiter
)

from .headers import (
    DEFAULT_SECURITY_HEADERS,
    API_CACHE_CONTROL_HEADERS,
    apply_security_headers
)

from .csrf import (
    CSRFProtector,
    csrf_protector
)

from .sanitizer import (
    sanitize_input,
    sanitize_string
)

from .audit import (
    AuditLogger,
    audit_logger
)

from .cors import (
    CORSManager,
    cors_manager
)

from .vpn_guard import (
    VPNNetworkGuard,
    vpn_guard
)

from .account_lockout import (
    AccountLockoutManager,
    account_lockout_manager
)

from .request_guard import (
    RequestGuard,
    RequestGuardViolation,
    request_guard
)

from .data_masker import (
    mask_sensitive_data,
    is_sensitive_key
)

from .dos_guard import (
    DoSProtectionManager,
    dos_manager
)

__all__ = [
    "hash_password",
    "verify_password",
    "generate_secure_token",
    "sign_data",
    "verify_signed_data",
    "constant_time_compare",
    "WAFEngine",
    "WAFSecurityException",
    "waf_engine",
    "RateLimiter",
    "rate_limiter",
    "DEFAULT_SECURITY_HEADERS",
    "API_CACHE_CONTROL_HEADERS",
    "apply_security_headers",
    "CSRFProtector",
    "csrf_protector",
    "sanitize_input",
    "sanitize_string",
    "AuditLogger",
    "audit_logger",
    "CORSManager",
    "cors_manager",
    "VPNNetworkGuard",
    "vpn_guard",
    "AccountLockoutManager",
    "account_lockout_manager",
    "RequestGuard",
    "RequestGuardViolation",
    "request_guard",
    "mask_sensitive_data",
    "is_sensitive_key",
    "DoSProtectionManager",
    "dos_manager"
]


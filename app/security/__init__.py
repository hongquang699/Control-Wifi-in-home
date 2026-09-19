"""
Gói An Ninh Mạng Cốt Lõi (App Security Suite) - app/security/__init__.py
Tập hợp toàn bộ các phân hệ phòng vệ an ninh máy trạm và mạng nội bộ:
- blocker: Quản lý quy trình chặn/bỏ chặn đa tầng (Router + Firewall + Audit)
- firewall: Tường lửa Windows hai chiều Inbound & Outbound
- safe_exec: Thực thi lệnh hệ thống an toàn, chống 100% Command Injection
- vault: Két sắt mã hóa mật khẩu Router liên kết phần cứng máy trạm
- rbac: Động cơ phân quyền lập trình cấp độ ADMIN / OPERATOR / VIEWER
- integrity: Giám sát toàn vẹn HMAC-SHA256 cho Database & Config
- arp_guard: Phát hiện tấn công ARP Spoofing & Đầu độc bộ đệm Gateway
- audit_logger: Nhật ký kiểm toán an ninh nội bộ chuẩn Forensic
"""

from .blocker import BlockManager
from .firewall import HostFirewallManager
from .rules import BlockRule
from .safe_exec import (
    safe_run_command,
    validate_ip,
    validate_mac,
    validate_subnet,
    CommandSecurityViolation
)
from .vault import (
    encrypt_secret,
    decrypt_secret,
    decrypt_secret_secure
)
from .zeroize import (
    zeroize_memory,
    SecureBuffer
)
from .process_guard import (
    is_debugger_present,
    detect_suspicious_modules,
    verify_process_security
)
from .dns_guard import (
    get_active_dns_servers,
    evaluate_dns_security
)
from .rbac import (
    rbac_manager,
    require_role,
    require_permission,
    PermissionDeniedError
)
from .integrity import (
    calculate_file_hmac,
    verify_file_integrity,
    verify_all_system_files,
    save_baseline_signatures
)
from .arp_guard import (
    ARPGuard,
    ARPSecurityAnomaly,
    arp_guard
)
from .audit_logger import (
    AppAuditLogger,
    app_audit_logger
)

__all__ = [
    "BlockManager",
    "HostFirewallManager",
    "BlockRule",
    "safe_run_command",
    "validate_ip",
    "validate_mac",
    "validate_subnet",
    "CommandSecurityViolation",
    "encrypt_secret",
    "decrypt_secret",
    "decrypt_secret_secure",
    "zeroize_memory",
    "SecureBuffer",
    "is_debugger_present",
    "detect_suspicious_modules",
    "verify_process_security",
    "get_active_dns_servers",
    "evaluate_dns_security",
    "rbac_manager",
    "require_role",
    "require_permission",
    "PermissionDeniedError",
    "calculate_file_hmac",
    "verify_file_integrity",
    "verify_all_system_files",
    "save_baseline_signatures",
    "ARPGuard",
    "ARPSecurityAnomaly",
    "arp_guard",
    "AppAuditLogger",
    "app_audit_logger"
]


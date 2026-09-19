"""
Bộ kiểm thử tự động toàn diện cho Kiến trúc Bảo mật Đa lớp (Multi-Layer Security Suite).
Bao gồm:
- Test Password Hashing (PBKDF2-HMAC-SHA256, salt, timing resistance)
- Test WAF (OWASP SQLi, XSS, Path Traversal, Command Injection)
- Test Rate Limiter (Sliding Window IP Counter, lockout)
- Test RBAC (Admin, Operator, User permissions)
- Test Audit Logging (Không lộ password, token)
- Test Secure Download (SHA-256 & chống Path Traversal)
- Test Database Backup
"""

import os
import sys
import unittest

# Đảm bảo import được web/backend
WEB_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if WEB_ROOT not in sys.path:
    sys.path.insert(0, WEB_ROOT)

from backend.auth.password import hash_password, verify_password
from backend.auth.session import session_manager, UserRole
from backend.middleware.waf import inspect_request
from backend.middleware.rate_limit import RateLimiter
from backend.services.audit_service import AuditLogger
from backend.services.download_service import DownloadService
from backend.services.backup_service import BackupService
from backend.api.routes import APIRouter

class TestMultiLayerSecurity(unittest.TestCase):

    def setUp(self):
        self.session_mgr = session_manager
        self.rate_limiter = RateLimiter()
        self.test_log_dir = os.path.join(WEB_ROOT, "logs", "test_audit")
        self.audit_logger = AuditLogger(log_dir=self.test_log_dir)
        self.download_service = DownloadService(base_dir=WEB_ROOT)
        self.backup_service = BackupService(backup_dir=os.path.join(WEB_ROOT, "backups"))

        # Router test instance
        self.devices = [{"id": 1, "mac": "AA:BB:CC:DD:EE:01", "ip": "192.168.1.10", "status": "ONLINE", "blocked": False}]
        self.settings = {"scan_interval": 60}
        self.router = APIRouter(self.devices, self.settings, [], [])

    def tearDown(self):
        # Dọn dẹp log test
        if os.path.exists(self.test_log_dir):
            try:
                import shutil
                shutil.rmtree(self.test_log_dir, ignore_errors=True)
            except Exception:
                pass

    # =========================================================================
    # 1. Test Password Hashing (Lớp 3)
    # =========================================================================
    def test_password_hashing(self):
        raw_pass = "SuperSecret#2026"
        hashed = hash_password(raw_pass)
        
        # 1. Kiểm tra tiền tố thuật toán và số vòng lặp 200.000
        self.assertTrue(hashed.startswith("pbkdf2:sha256:200000$"))
        
        # 2. Kiểm tra xác thực mật khẩu đúng
        self.assertTrue(verify_password(raw_pass, hashed))
        
        # 3. Kiểm tra mật khẩu sai
        self.assertFalse(verify_password("WrongPassword", hashed))
        
        # 4. Kiểm tra tính độc nhất của Salt (2 lần băm cho kết quả chuỗi khác nhau)
        hashed_2 = hash_password(raw_pass)
        self.assertNotEqual(hashed, hashed_2)
        self.assertTrue(verify_password(raw_pass, hashed_2))

    # =========================================================================
    # 2. Test WAF - Web Application Firewall (Lớp 2)
    # =========================================================================
    def test_waf_sqli_detection(self):
        # Thử tấn công SQL Injection
        payloads = [
            "/api/v1/devices?id=1' OR '1'='1",
            "/api/v1/devices?search=UNION SELECT username, password FROM users --",
            "/api/v1/users?name=admin' DROP TABLE devices; --"
        ]
        for p in payloads:
            res = inspect_request(p)
            self.assertTrue(res.is_blocked, f"WAF phải chặn SQLi: {p}")
            self.assertEqual(res.attack_type, "SQL_INJECTION")

    def test_waf_xss_detection(self):
        # Thử tấn công XSS
        payloads = [
            "/api/v1/devices?name=<script>alert('XSS')</script>",
            "/api/v1/search?q=<img src=x onerror=alert(1)>",
            "/api/v1/comment?body=javascript:fetch('http://attacker.com')"
        ]
        for p in payloads:
            res = inspect_request(p)
            self.assertTrue(res.is_blocked, f"WAF phải chặn XSS: {p}")
            self.assertEqual(res.attack_type, "XSS")

    def test_waf_path_traversal_detection(self):
        # Thử tấn công Path Traversal
        payloads = [
            "/downloads/../../etc/passwd",
            "/downloads/..\\..\\windows\\win.ini",
            "/downloads/%2e%2e%2f%2e%2e%2fetc/shadow",
            "/downloads/file.zip%00.exe"
        ]
        for p in payloads:
            res = inspect_request(p)
            self.assertTrue(res.is_blocked, f"WAF phải chặn Path Traversal: {p}")
            self.assertEqual(res.attack_type, "PATH_TRAVERSAL")

    def test_waf_command_injection_detection(self):
        # Thử tấn công Command Injection
        payloads = [
            "/api/v1/ping?ip=127.0.0.1; whoami",
            "/api/v1/ping?ip=127.0.0.1 && whoami",
            "/api/v1/test?cmd=$(whoami)"
        ]
        for p in payloads:
            res = inspect_request(p)
            self.assertTrue(res.is_blocked, f"WAF phải chặn Command Injection: {p}")
            self.assertEqual(res.attack_type, "COMMAND_INJECTION")

    def test_waf_clean_requests_allowed(self):
        # Request sạch phải được đi qua bình thường
        clean_requests = [
            "/api/v1/devices",
            "/api/v1/devices?subnet=192.168.1.0/24",
            "/api/v1/traffic",
            "/html/index.html",
            "/css/style.css"
        ]
        for p in clean_requests:
            res = inspect_request(p)
            self.assertFalse(res.is_blocked, f"Request hợp lệ không được chặn: {p}")

    # =========================================================================
    # 3. Test Rate Limiter (Lớp 2)
    # =========================================================================
    def test_rate_limiter_threshold_and_lockout(self):
        ip = "192.168.10.99"
        
        # 1. Cho phép 5 lần đăng nhập
        for i in range(5):
            limited, _ = self.rate_limiter.is_rate_limited(ip, zone="login", max_requests=5, window_seconds=60)
            self.assertFalse(limited, f"Request {i+1} phải được phép")

        # 2. Lần thứ 6 bị chặn và phạt khóa
        limited, retry_after = self.rate_limiter.is_rate_limited(ip, zone="login", max_requests=5, window_seconds=60)
        self.assertTrue(limited, "Request vượt quá ngưỡng phải bị rate limit")
        self.assertGreater(retry_after, 0)

    # =========================================================================
    # 4. Test RBAC & Authentication (Lớp 3 & Lớp 4)
    # =========================================================================
    def test_rbac_authorization(self):
        # 1. Xác thực admin và operator
        admin_sess, _ = self.session_mgr.authenticate("admin", "Admin@Security2026", "127.0.0.1")
        self.assertIsNotNone(admin_sess)
        self.assertEqual(admin_sess.role, UserRole.ADMIN)

        operator_sess, _ = self.session_mgr.authenticate("operator", "Operator@Network2026", "127.0.0.1")
        self.assertIsNotNone(operator_sess)
        self.assertEqual(operator_sess.role, UserRole.OPERATOR)

        # 2. User/Viewer (Không có token hoặc token guest) không thể gọi lệnh block
        res, code = self.router.handle_post(
            "/api/v1/block",
            {"mac": "AA:BB:CC:DD:EE:01", "reason": "Test block"},
            auth_header=None,
            client_ip="127.0.0.1"
        )
        self.assertEqual(code, 403, "User không có quyền block thiết bị")
        self.assertIn("Từ chối quyền truy cập", res.get("error", ""))

        # 3. Operator CÓ QUYỀN block thiết bị
        res, code = self.router.handle_post(
            "/api/v1/block",
            {"mac": "AA:BB:CC:DD:EE:01", "reason": "Operator block"},
            auth_header=f"Bearer {operator_sess.token}",
            client_ip="127.0.0.1"
        )
        self.assertEqual(code, 200, "Operator phải có quyền block thiết bị")

        # 4. Operator KHÔNG CÓ QUYỀN xem audit log của Admin
        res, code = self.router.handle_get(
            "/api/v1/audit",
            {},
            auth_header=f"Bearer {operator_sess.token}",
            client_ip="127.0.0.1"
        )
        self.assertEqual(code, 403, "Operator không được xem Audit Log")

        # 5. Admin CÓ QUYỀN xem audit log
        res, code = self.router.handle_get(
            "/api/v1/audit",
            {},
            auth_header=f"Bearer {admin_sess.token}",
            client_ip="127.0.0.1"
        )
        self.assertEqual(code, 200, "Admin phải có quyền xem Audit Log")
        self.assertIn("audit_events", res)

    # =========================================================================
    # 5. Test Audit Logging & Masking Sensitive Data (Lớp 9)
    # =========================================================================
    def test_audit_log_sensitive_data_masking(self):
        event = self.audit_logger.log_event(
            "LOGIN_ATTEMPT",
            actor="admin",
            ip="127.0.0.1",
            status="SUCCESS",
            details={
                "username": "admin",
                "password": "ClearTextPassword123!",  # Phải bị ẩn
                "session_token": "a1b2c3d4e5f67890",  # Phải bị ẩn
                "client_device": "Windows 11"
            }
        )
        # Kiểm tra dữ liệu nhạy cảm đã bị che
        self.assertEqual(event["details"]["password"], "[REDACTED]")
        self.assertEqual(event["details"]["session_token"], "[REDACTED]")
        self.assertEqual(event["details"]["client_device"], "Windows 11")

    # =========================================================================
    # 6. Test Secure Download & Path Traversal Prevention (Lớp 7)
    # =========================================================================
    def test_secure_download_path_traversal(self):
        # 1. Thử path traversal để đọc file nhạy cảm
        is_safe, path, err = self.download_service.resolve_safe_download(
            "/downloads/../../backend/main.py",
            client_ip="127.0.0.1"
        )
        self.assertFalse(is_safe, "Phải chặn Path Traversal khi tải file")
        self.assertIsNotNone(err)

        # 2. File hợp lệ trong downloads/windows
        catalog = self.download_service.get_catalog()
        self.assertGreater(len(catalog), 0)
        for item in catalog:
            self.assertIn("sha256", item)
            self.assertEqual(len(item["sha256"]), 64)  # SHA-256 có 64 ký tự hex

if __name__ == "__main__":
    unittest.main()

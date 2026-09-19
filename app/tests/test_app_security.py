"""
Bộ Kiểm Thử Toàn Diện Module Bảo Mật Desktop App (App Security Test Suite)
Kiểm thử SafeExec, Vault, RBAC, Integrity Guard, ARP Poisoning Guard, BlockManager.
"""

import unittest
import os
import sys
import tempfile
import json

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(APP_DIR)

for p in [PROJECT_DIR, APP_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from security.safe_exec import (
    validate_ip, validate_mac, validate_subnet, safe_run_command,
    CommandSecurityViolation
)
from security.vault import encrypt_secret, decrypt_secret, decrypt_secret_secure
from security.zeroize import zeroize_memory, SecureBuffer
from security.process_guard import is_debugger_present, detect_suspicious_modules, verify_process_security
from security.dns_guard import evaluate_dns_security, get_active_dns_servers
from security.firewall import HostFirewallManager
from security.rbac import (
    rbac_manager, require_role, require_permission,
    PermissionDeniedError
)
from security.integrity import (
    calculate_file_hmac, verify_file_integrity, save_baseline_signatures
)
from security.arp_guard import ARPGuard
from security.audit_logger import AppAuditLogger
from security.blocker import BlockManager
from database.database import Database
from database.devices import DeviceDAO
from database.events import EventDAO
from router.mock import MockRouterAdapter

class TestAppSecuritySuite(unittest.TestCase):

    def test_01_safe_exec_validators(self):
        # Valid IPs
        self.assertEqual(validate_ip("192.168.1.1"), "192.168.1.1")
        self.assertEqual(validate_ip("10.0.0.1"), "10.0.0.1")

        # Invalid / Injection IPs
        with self.assertRaises(CommandSecurityViolation):
            validate_ip("192.168.1.1; calc.exe")
        with self.assertRaises(CommandSecurityViolation):
            validate_ip("192.168.1.1 & dir")
        with self.assertRaises(CommandSecurityViolation):
            validate_ip("")

        # Valid MACs
        self.assertEqual(validate_mac("AA:BB:CC:DD:EE:FF"), "AA:BB:CC:DD:EE:FF")
        self.assertEqual(validate_mac("aa-bb-cc-dd-ee-ff"), "aa-bb-cc-dd-ee-ff")

        # Invalid MACs
        with self.assertRaises(CommandSecurityViolation):
            validate_mac("AA:BB:CC:DD:EE:GG")
        with self.assertRaises(CommandSecurityViolation):
            validate_mac("AA:BB:CC:DD:EE:FF|whoami")

        # Valid Subnets
        self.assertEqual(validate_subnet("192.168.1.0/24"), "192.168.1.0/24")
        with self.assertRaises(CommandSecurityViolation):
            validate_subnet("192.168.1.0/35")

    def test_02_safe_run_command_whitelist(self):
        # Ping hợp lệ
        code, out, err = safe_run_command(["ping", "-n", "1", "127.0.0.1"], timeout_seconds=4)
        self.assertEqual(code, 0)

        # Non-whitelisted binary
        with self.assertRaises(CommandSecurityViolation):
            safe_run_command(["powershell", "Get-Process"])
        with self.assertRaises(CommandSecurityViolation):
            safe_run_command(["cmd.exe", "/c", "dir"])

    def test_03_vault_encryption_roundtrip(self):
        secret = "MyVeryStrongRouterPass_2026!#$%"
        encrypted = encrypt_secret(secret)
        self.assertTrue(encrypted.startswith("vault_v1$"))
        self.assertNotEqual(secret, encrypted)

        decrypted = decrypt_secret(encrypted)
        self.assertEqual(secret, decrypted)

        # Plaintext fallback
        self.assertEqual(decrypt_secret("plain_text"), "plain_text")

    def test_04_rbac_enforcement(self):
        # Thiết lập vai trò ADMIN
        rbac_manager.set_role("ADMIN")
        self.assertEqual(rbac_manager.get_role(), "ADMIN")
        self.assertTrue(rbac_manager.has_permission("device:block"))
        self.assertTrue(rbac_manager.has_permission("audit:read"))

        @require_role("ADMIN")
        def admin_only_func():
            return "ok_admin"

        @require_permission("audit:read")
        def audit_read_func():
            return "ok_audit"

        self.assertEqual(admin_only_func(), "ok_admin")
        self.assertEqual(audit_read_func(), "ok_audit")

        # Chuyển sang vai trò VIEWER
        rbac_manager.set_role("VIEWER")
        self.assertEqual(rbac_manager.get_role(), "VIEWER")
        self.assertFalse(rbac_manager.has_permission("device:block"))
        self.assertFalse(rbac_manager.has_permission("audit:read"))
        self.assertTrue(rbac_manager.has_permission("network:read"))

        with self.assertRaises(PermissionDeniedError):
            admin_only_func()

        with self.assertRaises(PermissionDeniedError):
            audit_read_func()

        # Khôi phục ADMIN
        rbac_manager.set_role("ADMIN")

    def test_05_file_integrity_checker(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
            tmp.write(b"Initial pristine configuration data")
            tmp_path = tmp.name

        try:
            # Lưu baseline
            sig = calculate_file_hmac(tmp_path)
            self.assertTrue(len(sig) > 0)

            # Sửa file
            with open(tmp_path, "wb") as f:
                f.write(b"Tampered hacked configuration data!")

            sig_tampered = calculate_file_hmac(tmp_path)
            self.assertNotEqual(sig, sig_tampered)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_06_arp_guard_anomaly_detection(self):
        guard = ARPGuard(known_gateway_ip="192.168.1.1")
        guard.set_trusted_gateway("192.168.1.1", "00:11:22:33:44:55")
        self.assertEqual(guard.known_gateway_mac, "00:11:22:33:44:55")

    def test_07_block_manager_rbac_integration(self):
        test_db = os.path.join(APP_DIR, "data", "test_sec_rbac.db")
        if os.path.exists(test_db):
            try:
                os.remove(test_db)
            except Exception:
                pass
        db = Database(db_path=test_db)
        dev_dao = DeviceDAO(db)
        evt_dao = EventDAO(db)
        router = MockRouterAdapter()
        bm = BlockManager(router_adapter=router, device_dao=dev_dao, event_dao=evt_dao, enable_host_firewall=False)

        try:
            # Thêm thiết bị mẫu
            from core.device import Device
            dev = Device(ip="192.168.1.50", mac="11:22:33:44:55:66", hostname="TestPC", status="ONLINE")
            dev_dao.upsert_device(dev)

            # Khi là VIEWER -> Chặn bị từ chối
            rbac_manager.set_role("VIEWER")
            success, msg = bm.block_device(mac="11:22:33:44:55:66")
            self.assertFalse(success)
            self.assertIn("Từ chối quyền", msg)

            # Khi là ADMIN -> Chặn thành công
            rbac_manager.set_role("ADMIN")
            success, msg = bm.block_device(mac="11:22:33:44:55:66")
            self.assertTrue(success)
            d = dev_dao.get_device_by_mac("11:22:33:44:55:66")
            self.assertTrue(d.blocked)

            # Bỏ chặn
            success, msg = bm.unblock_device(mac="11:22:33:44:55:66")
            self.assertTrue(success)
            d = dev_dao.get_device_by_mac("11:22:33:44:55:66")
            self.assertFalse(d.blocked)
        finally:
            import gc
            gc.collect()
            for suffix in ["", "-wal", "-shm"]:
                p = test_db + suffix
                if os.path.exists(p):
                    try:
                        os.remove(p)
                    except Exception:
                        pass

    def test_08_memory_zeroization(self):
        # 1. Kiểm tra zeroize_memory với bytearray
        b = bytearray(b"SecretPassword123!")
        self.assertNotEqual(b, bytearray(len(b)))
        zeroize_memory(b)
        self.assertEqual(b, bytearray(len(b)))

        # 2. Kiểm tra SecureBuffer context manager
        with SecureBuffer("SensitiveTokenXYZ") as buf:
            self.assertEqual(buf.get_string(), "SensitiveTokenXYZ")
            self.assertFalse(buf.is_wiped)

        # Sau khi ra khỏi context -> buffer phải được wipe sạch
        self.assertTrue(buf.is_wiped)
        with self.assertRaises(ValueError):
            buf.get_string()

        # 3. Kiểm tra decrypt_secret_secure
        enc = encrypt_secret("RouterAdminSuperPass2026")
        with decrypt_secret_secure(enc) as sec_buf:
            self.assertEqual(sec_buf.get_string(), "RouterAdminSuperPass2026")
        self.assertTrue(sec_buf.is_wiped)

    def test_09_process_guard_integrity(self):
        status = verify_process_security()
        self.assertIn("secure", status)
        self.assertIn("debugger_detected", status)
        self.assertIn("suspicious_modules", status)
        self.assertIsInstance(status["suspicious_modules"], list)
        self.assertIsInstance(is_debugger_present(), bool)
        self.assertIsInstance(detect_suspicious_modules(), list)

    def test_10_dns_guard_evaluation(self):
        # 1. DNS an toàn (Cloudflare + Google + Gateway)
        safe_eval = evaluate_dns_security(["1.1.1.1", "8.8.8.8", "192.168.1.1"], gateway_ip="192.168.1.1")
        self.assertTrue(safe_eval["secure"])
        self.assertEqual(safe_eval["threat_level"], "NORMAL")
        self.assertEqual(len(safe_eval["suspicious_dns"]), 0)

        # 2. DNS chứa IP lạ khả nghi
        malicious_ip = "123.45.67.89"
        threat_eval = evaluate_dns_security(["1.1.1.1", malicious_ip], gateway_ip="192.168.1.1")
        self.assertFalse(threat_eval["secure"])
        self.assertEqual(threat_eval["threat_level"], "CRITICAL")
        self.assertIn(malicious_ip, threat_eval["suspicious_dns"])

    def test_11_host_quarantine_validation(self):
        # Validate IP từ chối IP chứa ký tự độc hại
        res_bad, msg_bad = HostFirewallManager.enable_host_quarantine("192.168.1.1; whoami")
        self.assertFalse(res_bad)
        self.assertTrue(len(msg_bad) > 0)

        # Gọi với IP hợp lệ
        res, msg = HostFirewallManager.enable_host_quarantine("192.168.1.1")
        self.assertIsInstance(res, bool)
        self.assertTrue(len(msg) > 0)

        # Tắt cách ly
        res_off, msg_off = HostFirewallManager.disable_host_quarantine()
        self.assertIsInstance(res_off, bool)
        self.assertTrue(len(msg_off) > 0)

if __name__ == "__main__":
    unittest.main()


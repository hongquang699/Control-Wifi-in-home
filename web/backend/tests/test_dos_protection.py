"""
Bộ Kiểm Thử Độc Lập Hệ Thống Phòng Chống Tấn Công DoS/DDoS (Anti-DoS Protection Test Suite)
web/backend/tests/test_dos_protection.py
"""

import unittest
import hashlib
import time
from web.security.dos_guard import DoSProtectionManager

class TestDoSProtection(unittest.TestCase):
    def setUp(self):
        # Khởi tạo instance kiểm thử độc lập với tham số nhỏ để test nhanh
        self.mgr = DoSProtectionManager(
            max_conns_per_ip=3,
            max_global_conns=5,
            socket_timeout=2.0,
            microburst_window_seconds=1.0,
            microburst_limit=5,
            under_attack_threshold_rps=10.0,
            under_attack_cooldown_seconds=2.0,
            pow_difficulty=2  # Độ khó nhỏ để giải nghiệm nhanh trong unit test (bắt đầu bằng "00")
        )

    def test_connection_limit_per_ip(self):
        """Kiểm tra giới hạn kết nối đồng thời từ 1 IP."""
        client_ip = "192.168.10.50"
        # Mở 3 kết nối hợp lệ
        self.assertTrue(self.mgr.register_connection(client_ip)[0])
        self.assertTrue(self.mgr.register_connection(client_ip)[0])
        self.assertTrue(self.mgr.register_connection(client_ip)[0])

        # Kết nối thứ 4 phải bị từ chối
        ok, reason = self.mgr.register_connection(client_ip)
        self.assertFalse(ok)
        self.assertEqual(reason, "IP_CONCURRENCY_LIMIT_EXCEEDED")

        # Giải phóng 1 kết nối -> mở lại thành công
        self.mgr.release_connection(client_ip)
        ok2, _ = self.mgr.register_connection(client_ip)
        self.assertTrue(ok2)

    def test_global_connection_limit(self):
        """Kiểm tra giới hạn tổng kết nối toàn server (max_global_conns=5)."""
        ips = [f"10.0.0.{i}" for i in range(1, 6)]
        for ip in ips:
            ok, _ = self.mgr.register_connection(ip)
            self.assertTrue(ok)

        # Kết nối thứ 6 từ IP mới phải bị từ chối do quá tải server
        ok6, reason = self.mgr.register_connection("10.0.0.99")
        self.assertFalse(ok6)
        self.assertEqual(reason, "GLOBAL_CONCURRENCY_EXHAUSTED")

    def test_loopback_exemption(self):
        """Địa chỉ loopback (127.0.0.1) được miễn trừ giới hạn per-IP."""
        for _ in range(10):
            ok, _ = self.mgr.register_connection("127.0.0.1")
            self.assertTrue(ok)

    def test_microburst_rate_limiting(self):
        """Kiểm tra chặn đợt bùng nổ request dồn dập (Micro-burst)."""
        client_ip = "172.16.0.88"
        # Gửi 5 request trong ngưỡng
        for _ in range(5):
            ok, code, _ = self.mgr.check_request(client_ip, "/api/v1/devices")
            self.assertTrue(ok)
            self.assertEqual(code, 200)

        # Request thứ 6 vượt ngưỡng 5 req/s -> Chặn 429
        ok6, code6, err6 = self.mgr.check_request(client_ip, "/api/v1/devices")
        self.assertFalse(ok6)
        self.assertEqual(code6, 429)
        self.assertIn("Micro-burst", err6)

    def test_adaptive_under_attack_mode(self):
        """Kiểm tra tự động kích hoạt Under Attack Mode khi RPS toàn hệ thống tăng vọt."""
        self.assertFalse(self.mgr.is_under_attack_mode())

        # Bắn 12 request từ nhiều IP để vượt ngưỡng RPS 10.0
        for i in range(12):
            self.mgr.check_request(f"192.168.2.{i}")

        self.assertTrue(self.mgr.is_under_attack_mode())
        metrics = self.mgr.get_metrics()
        self.assertTrue(metrics["under_attack_mode"])
        self.assertGreater(metrics["under_attack_remaining_seconds"], 0)

    def test_pow_challenge_and_verification(self):
        """Kiểm tra sinh và xác thực bài toán Proof-of-Work (PoW)."""
        client_ip = "192.168.1.99"
        challenge_info = self.mgr.generate_pow_challenge(client_ip)

        self.assertEqual(challenge_info["algorithm"], "SHA-256")
        self.assertEqual(challenge_info["difficulty"], 2)
        challenge = challenge_info["challenge"]
        token = challenge_info["token"]

        # Giải bài toán băm bằng brute-force proof ngắn
        proof_found = None
        for i in range(10000):
            candidate = f"{challenge}:{i}".encode("utf-8")
            if hashlib.sha256(candidate).hexdigest().startswith("00"):
                proof_found = str(i)
                break

        self.assertIsNotNone(proof_found, "Phải tìm được nghiệm PoW hợp lệ")

        # Xác thực nghiệm đúng
        self.assertTrue(self.mgr.verify_pow_solution(client_ip, challenge, token, proof_found))

        # Nghiệm sai phải bị từ chối
        self.assertFalse(self.mgr.verify_pow_solution(client_ip, challenge, token, "invalid_proof_99999"))

        # Token giả mạo phải bị từ chối
        self.assertFalse(self.mgr.verify_pow_solution(client_ip, challenge, "tampered_token", proof_found))

        # Sai client_ip phải bị từ chối
        self.assertFalse(self.mgr.verify_pow_solution("1.2.3.4", challenge, token, proof_found))

    def test_blackhole_management(self):
        """Kiểm tra đưa IP vào Blackhole và gỡ Blackhole."""
        ip = "203.0.113.50"
        self.mgr.blackhole_ip(ip, duration_seconds=60.0)

        # Khi đang bị Blackhole, kết nối bị từ chối ngay lập tức
        ok, reason = self.mgr.register_connection(ip)
        self.assertFalse(ok)
        self.assertIn("Blackhole", reason)

        # Gỡ Blackhole
        self.mgr.unblackhole_ip(ip)
        ok2, _ = self.mgr.register_connection(ip)
        self.assertTrue(ok2)

if __name__ == "__main__":
    unittest.main()

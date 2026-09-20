"""
Unit tests cho Hệ Thống Tường Lửa Giới Hạn 100 Req & Bot Tự Động Ban IP Trên 1000 Req
web/backend/tests/test_ip_ban_bot.py
"""

import os
import unittest
import tempfile
import time
from web.security.ip_ban_bot import IPBanBot
from web.security.rate_limiter import RateLimiter


class TestIPBanBotAndFirewall(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.banned_file = os.path.join(self.temp_dir.name, "test_banned_ips.json")
        self.bot = IPBanBot(
            ban_threshold=1000,
            ban_duration_seconds=3600,
            storage_file=self.banned_file,
            enable_host_firewall=False  # Không gọi netsh trong unit test
        )
        self.rate_limiter = RateLimiter(
            default_limit_per_minute=100,
            bot_ban_threshold=1000
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_01_rate_limit_100_requests(self):
        """Kiểm tra giới hạn đúng 100 requests, request 101 bị chặn với cảnh báo."""
        ip = "192.168.1.150"
        limiter = RateLimiter(default_limit_per_minute=100, bot_ban_threshold=1000)

        # 100 requests đầu tiên thành công
        for _ in range(100):
            allowed, _, _ = limiter.is_allowed(ip)
            self.assertTrue(allowed)

        # Request thứ 101 vượt ngưỡng 100
        allowed, retry_after, reason = limiter.is_allowed(ip)
        self.assertFalse(allowed)
        self.assertGreater(retry_after, 0)
        self.assertIn("Bạn bấm quá nhanh", reason)

    def test_02_bot_ban_trigger_at_threshold(self):
        """Kiểm tra khi đạt ngưỡng quy định, Bot Ban IP tự động kích hoạt."""
        ip = "192.168.1.199"
        # Khởi tạo limiter với threshold nhỏ (ví dụ 10) để kiểm tra logic kích hoạt
        mini_limiter = RateLimiter(default_limit_per_minute=5, bot_ban_threshold=10)

        for i in range(9):
            mini_limiter.is_allowed(ip)

        # Request thứ 10 chạm ngưỡng bot ban
        allowed, retry_after, reason = mini_limiter.is_allowed(ip)
        self.assertFalse(allowed)
        self.assertIn("BOT_BANNED", reason)

    def test_03_bot_ban_storage_persistence(self):
        """Kiểm tra lưu trữ và tải danh sách cấm từ file JSON."""
        ip = "10.0.0.88"
        ban_info = self.bot.ban_ip(ip, reason="Spam 1000 reqs test", request_count=1005)
        self.assertTrue(ban_info["incident_id"].startswith("BOT-"))

        # Kiểm tra trạng thái cấm
        is_banned, meta = self.bot.is_banned(ip)
        self.assertTrue(is_banned)
        self.assertEqual(meta["ip"], ip)

        # Khởi tạo instance mới đọc lại từ file
        bot2 = IPBanBot(storage_file=self.banned_file, enable_host_firewall=False)
        is_banned2, meta2 = bot2.is_banned(ip)
        self.assertTrue(is_banned2)
        self.assertEqual(meta2["incident_id"], ban_info["incident_id"])

    def test_04_bot_unban(self):
        """Kiểm tra chức năng mở khóa Unban IP."""
        ip = "10.0.0.77"
        self.bot.ban_ip(ip)
        self.assertTrue(self.bot.is_banned(ip)[0])

        unbanned = self.bot.unban_ip(ip)
        self.assertTrue(unbanned)
        self.assertFalse(self.bot.is_banned(ip)[0])

    def test_05_loopback_exemption(self):
        """Loopback (127.0.0.1, ::1) không bao giờ bị Bot khóa vĩnh viễn."""
        res = self.bot.ban_ip("127.0.0.1")
        self.assertFalse(res.get("success", True))
        self.assertFalse(self.bot.is_banned("127.0.0.1")[0])

    def test_06_html_pages_exist(self):
        """Kiểm tra sự tồn tại của tệp 429.html và banned.html trong web/html/."""
        html_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "html")
        page_429 = os.path.join(html_dir, "429.html")
        page_banned = os.path.join(html_dir, "banned.html")

        self.assertTrue(os.path.exists(page_429), "Thiếu tệp web/html/429.html")
        self.assertTrue(os.path.exists(page_banned), "Thiếu tệp web/html/banned.html")

        with open(page_429, "r", encoding="utf-8") as f:
            content_429 = f.read()
            self.assertIn("Bạn Bấm Quá Nhanh", content_429)
            self.assertIn("100 requests", content_429)

        with open(page_banned, "r", encoding="utf-8") as f:
            content_banned = f.read()
            self.assertIn("403 BANNED", content_banned)
            self.assertIn("1,000 requests", content_banned)


if __name__ == "__main__":
    unittest.main()

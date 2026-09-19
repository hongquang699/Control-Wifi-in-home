"""
Bộ Kiểm Thử Độc Lập Giám Sát Tấn Công DoS Mạng Máy Trạm (Desktop Host DoS Test Suite)
app/tests/test_app_dos_monitor.py
"""

import unittest
import time
import os
import sys

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(APP_DIR)
for p in [PROJECT_DIR, APP_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from security.dos_monitor import HostDoSMonitor

class TestAppDoSMonitor(unittest.TestCase):
    def setUp(self):
        # Khởi tạo instance test với threshold nhỏ và tắt auto_block thật để tránh đụng chạm firewall OS
        self.monitor = HostDoSMonitor(
            syn_flood_threshold=5,
            ip_flood_threshold=10,
            auto_block=False,
            block_duration_seconds=1.0
        )

    def test_parse_netstat_output(self):
        """Kiểm tra phân tích cú pháp đầu ra netstat chuẩn Windows."""
        sample_output = """
Active Connections

  Proto  Local Address          Foreign Address        State           PID
  TCP    192.168.1.50:50123     192.168.1.1:80         ESTABLISHED     1234
  TCP    192.168.1.50:50124     10.0.0.5:443           SYN_RECEIVED    5678
  UDP    0.0.0.0:5353           *:*                                    9999
"""
        parsed = self.monitor.parse_netstat_output(sample_output)
        self.assertEqual(len(parsed), 3)
        self.assertEqual(parsed[0]["proto"], "TCP")
        self.assertEqual(parsed[0]["remote_ip"], "192.168.1.1")
        self.assertEqual(parsed[0]["state"], "ESTABLISHED")
        self.assertEqual(parsed[1]["remote_ip"], "10.0.0.5")
        self.assertEqual(parsed[1]["state"], "SYN_RECEIVED")

    def test_detect_syn_flood(self):
        """Phát hiện tấn công SYN Flood khi số kết nối nửa mở vượt ngưỡng."""
        attacker_ip = "192.168.1.200"
        connections = [
            {"proto": "TCP", "remote_ip": attacker_ip, "state": "SYN_RECEIVED"}
            for _ in range(6)  # threshold là 5
        ]

        analysis = self.monitor.analyze_connections(connections)
        self.assertGreaterEqual(analysis["threats_count"], 1)
        threat = analysis["threats"][0]
        self.assertEqual(threat["type"], "SYN_FLOOD")
        self.assertEqual(threat["ip"], attacker_ip)
        self.assertEqual(threat["count"], 6)

    def test_detect_connection_flood(self):
        """Phát hiện tấn công Connection Flood khi số kết nối đồng thời từ 1 IP vượt ngưỡng."""
        attacker_ip = "192.168.1.201"
        connections = [
            {"proto": "TCP", "remote_ip": attacker_ip, "state": "ESTABLISHED"}
            for _ in range(12)  # threshold là 10
        ]

        analysis = self.monitor.analyze_connections(connections)
        self.assertGreaterEqual(analysis["threats_count"], 1)
        threat = analysis["threats"][0]
        self.assertEqual(threat["type"], "CONNECTION_FLOOD")
        self.assertEqual(threat["ip"], attacker_ip)
        self.assertEqual(threat["count"], 12)

    def test_ignore_loopback(self):
        """Bỏ qua địa chỉ loopback 127.0.0.1 và wildcard."""
        connections = [
            {"proto": "TCP", "remote_ip": "127.0.0.1", "state": "SYN_RECEIVED"}
            for _ in range(20)
        ]
        analysis = self.monitor.analyze_connections(connections)
        self.assertEqual(analysis["threats_count"], 0)

    def test_check_and_mitigate(self):
        """Kiểm tra quy trình check_and_mitigate tự động ghi nhận blacklist."""
        attacker_ip = "192.168.1.222"
        connections = [
            {"proto": "TCP", "remote_ip": attacker_ip, "state": "SYN_RECEIVED"}
            for _ in range(6)
        ]

        res = self.monitor.check_and_mitigate(connections)
        self.assertEqual(res["threats_count"], 1)
        self.assertIn(attacker_ip, self.monitor.get_blacklist())

    def test_cleanup_expired_blocks(self):
        """Kiểm tra tự động gỡ bỏ IP khỏi blacklist khi hết hạn cách ly."""
        attacker_ip = "192.168.1.223"
        self.monitor._blacklisted_ips[attacker_ip] = time.time() - 1.0  # Đã quá hạn 1 giây

        self.monitor.cleanup_expired_blocks()
        self.assertNotIn(attacker_ip, self.monitor.get_blacklist())

if __name__ == "__main__":
    unittest.main()

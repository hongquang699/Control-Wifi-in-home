"""
Bộ kiểm thử tự động toàn diện cho Network Manager.
"""

import os
import sys

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import unittest
from core.device import Device
from core.network import NetworkManagerCore
from services.identification import DeviceIdentifier
from database.database import Database
from database.devices import DeviceDAO
from database.events import EventDAO
from router.mock import MockRouterAdapter
from security.blocker import BlockManager
from utils.validators import is_valid_ipv4, is_valid_mac, normalize_mac, is_valid_cidr

class TestNetworkManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_db_path = "data/test_network.db"
        if os.path.exists(cls.test_db_path):
            try:
                os.remove(cls.test_db_path)
            except Exception:
                pass
        cls.db = Database(cls.test_db_path)
        cls.device_dao = DeviceDAO(cls.db)
        cls.event_dao = EventDAO(cls.db)
        cls.mock_router = MockRouterAdapter()
        cls.block_manager = BlockManager(
            router_adapter=cls.mock_router,
            device_dao=cls.device_dao,
            event_dao=cls.event_dao,
            enable_host_firewall=False  # Không đụng vào firewall hệ thống khi test
        )

    @classmethod
    def tearDownClass(cls):
        import gc
        del cls.block_manager
        del cls.event_dao
        del cls.device_dao
        del cls.db
        gc.collect()
        if os.path.exists(cls.test_db_path):
            try:
                os.remove(cls.test_db_path)
            except Exception:
                pass

    def test_01_validators(self):
        """Kiểm tra tính hợp lệ của IP, MAC và CIDR."""
        self.assertTrue(is_valid_ipv4("192.168.1.1"))
        self.assertFalse(is_valid_ipv4("999.999.1.1"))
        self.assertTrue(is_valid_mac("00:15:5D:5D:B1:C2"))
        self.assertTrue(is_valid_mac("00-15-5D-5D-B1-C2"))
        self.assertEqual(normalize_mac("00-15-5d-5d-b1-c2"), "00:15:5D:5D:B1:C2")
        self.assertTrue(is_valid_cidr("192.168.110.0/24"))
        self.assertFalse(is_valid_cidr("invalid_cidr"))

    def test_02_identification(self):
        """Kiểm tra OUI Vendor và phân loại thiết bị."""
        vendor = DeviceIdentifier.identify_vendor("00:03:93:12:34:56")
        self.assertEqual(vendor, "Apple")
        
        vendor_tp = DeviceIdentifier.identify_vendor("14:75:90:28:40:60")
        self.assertEqual(vendor_tp, "TP-Link")

        _, dev_type = DeviceIdentifier.classify_device(
            ip="192.168.1.1",
            mac="14:75:90:28:40:60",
            hostname="tplinkwifi.net",
            vendor="TP-Link",
            is_gateway=True
        )
        self.assertEqual(dev_type, "Router")

        _, phone_type = DeviceIdentifier.classify_device(
            ip="192.168.1.100",
            mac="00:03:93:00:00:01",
            hostname="iPhone-cua-Nam",
            vendor="Apple"
        )
        self.assertEqual(phone_type, "Phone")

    def test_03_database_and_events(self):
        """Kiểm tra thao tác CRUD SQLite và bảng events."""
        dev = Device(
            ip="192.168.1.55",
            mac="AA:BB:CC:DD:EE:FF",
            hostname="test-host",
            vendor="TestVendor",
            device_type="PC"
        )
        saved, is_new, ip_changed = self.device_dao.upsert_device(dev)
        self.assertTrue(is_new)
        self.assertIsNotNone(saved.id)

        # Kiểm tra ghi event
        ev_id = self.event_dao.log_event("DEVICE_JOINED", saved.mac, "Test device joined", saved.id)
        self.assertGreater(ev_id, 0)

        events = self.event_dao.get_recent_events(limit=5)
        self.assertGreaterEqual(len(events), 1)

        # Cập nhật alias
        self.device_dao.update_custom_name(saved.mac, "Máy tính kiểm thử", "PC")
        re_query = self.device_dao.get_device_by_mac(saved.mac)
        self.assertEqual(re_query.custom_name, "Máy tính kiểm thử")

    def test_04_block_unblock(self):
        """Kiểm tra quy trình Block và Unblock qua BlockManager."""
        test_mac = "AA:BB:CC:DD:EE:FF"
        
        # Thực hiện Block
        success, msg = self.block_manager.block_device(test_mac, ip="192.168.1.55", reason="Vi phạm nội quy")
        self.assertTrue(success)
        self.assertIn(test_mac, self.mock_router.get_blocked_list())

        # Kiểm tra trạng thái trong DB
        dev = self.device_dao.get_device_by_mac(test_mac)
        self.assertTrue(dev.blocked)
        self.assertEqual(dev.block_reason, "Vi phạm nội quy")

        # Thực hiện Unblock
        success_un, msg_un = self.block_manager.unblock_device(test_mac, ip="192.168.1.55")
        self.assertTrue(success_un)
        self.assertNotIn(test_mac, self.mock_router.get_blocked_list())

        dev_after = self.device_dao.get_device_by_mac(test_mac)
        self.assertFalse(dev_after.blocked)

    def test_05_gui_components_initialization(self):
        """Kiểm tra khởi tạo các thành phần GUI PySide6."""
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance() or QApplication(sys.argv)
        
        from gui.app import MainWindow
        win = MainWindow(auto_scan_on_startup=False)
        self.assertIsNotNone(win)
        self.assertEqual(win.stack.count(), 6)
        
        # Test chuyển ngôn ngữ trên MainWindow
        from core.i18n import i18n
        i18n.set_language("en")
        self.assertEqual(i18n.current_lang, "en")
        i18n.set_language("vi")
        self.assertEqual(i18n.current_lang, "vi")
        
        win.scheduler.stop()
        if hasattr(win, "traffic_monitor"):
            win.traffic_monitor.stop()
        if win.scan_worker.isRunning():
            win.scan_worker.terminate()
            win.scan_worker.wait(2000)
        win.close()
        app.processEvents()

    def test_06_i18n_translations(self):
        """Kiểm tra tính toàn vẹn của từ điển song ngữ vi và en."""
        from core.i18n import TRANSLATIONS, t, i18n
        self.assertIn("vi", TRANSLATIONS)
        self.assertIn("en", TRANSLATIONS)
        
        vi_keys = set(TRANSLATIONS["vi"].keys())
        en_keys = set(TRANSLATIONS["en"].keys())
        
        missing_in_en = vi_keys - en_keys
        missing_in_vi = en_keys - vi_keys
        
        self.assertEqual(len(missing_in_en), 0, f"Các key thiếu trong tiếng Anh: {missing_in_en}")
        self.assertEqual(len(missing_in_vi), 0, f"Các key thiếu trong tiếng Việt: {missing_in_vi}")
        
        i18n.set_language("en")
        self.assertEqual(t("nav_dashboard"), "Dashboard")
        self.assertEqual(t("nav_traffic"), "Network Usage")
        
        i18n.set_language("vi")
        self.assertEqual(t("nav_dashboard"), "Tổng quan")
        self.assertEqual(t("nav_traffic"), "Mức sử dụng mạng")

    def test_07_traffic_monitor_and_chart(self):
        """Kiểm tra dịch vụ TrafficMonitor và định dạng tốc độ lưu lượng mạng."""
        from services.traffic_monitor import TrafficMonitor, format_speed, format_bytes
        from gui.traffic_chart import TrafficChart
        from gui.traffic import TrafficView
        
        # 1. Test formatters
        self.assertEqual(format_speed(500), "500 B/s")
        self.assertEqual(format_speed(1536), "1.5 KB/s")
        self.assertEqual(format_speed(5 * 1024 * 1024), "5.00 MB/s")
        self.assertEqual(format_bytes(1024), "1.0 KB")
        self.assertEqual(format_bytes(10 * 1024 * 1024), "10.00 MB")
        
        # 2. Test TrafficMonitor
        monitor = TrafficMonitor(max_history_seconds=30)
        self.assertEqual(monitor.selected_interface, "ALL")
        ifaces = monitor.get_available_interfaces()
        self.assertIsInstance(ifaces, list)
        
        monitor.set_interface("ALL")
        monitor.reset_stats()
        self.assertEqual(len(monitor._history), 0)
        
        # 3. Test Widgets
        chart = TrafficChart(max_samples=60, compact=False)
        self.assertIsNotNone(chart)
        chart_mini = TrafficChart(max_samples=60, compact=True)
        self.assertIsNotNone(chart_mini)
        
        view = TrafficView(monitor)
        self.assertIsNotNone(view)
        view.close()

    def test_08_topology_and_internet_route(self):
        """Kiểm tra nhận diện dải mạng, phương thức kết nối và lộ trình Internet."""
        from core.topology import NetworkTopologyHelper
        
        # 1. Kiểm tra nhận diện mạng
        pri_info = NetworkTopologyHelper.get_network_info("192.168.1.150")
        self.assertTrue(pri_info["is_primary"])
        self.assertIn("Wi-Fi Tổng", pri_info["network_name"])
        self.assertEqual(pri_info["gateway_ip"], "192.168.1.1")

        sec_info = NetworkTopologyHelper.get_network_info("192.168.110.45")
        self.assertTrue(sec_info["is_secondary"])
        self.assertIn("Router Phụ", sec_info["network_name"])
        self.assertEqual(sec_info["gateway_ip"], "192.168.110.1")

        # 2. Kiểm tra phân loại phương thức kết nối
        phone_conn = NetworkTopologyHelper.infer_connection_type("192.168.110.20", device_type="Phone")
        self.assertEqual(phone_conn, "Wi-Fi")

        server_conn = NetworkTopologyHelper.infer_connection_type("192.168.110.2", device_type="Server")
        self.assertEqual(server_conn, "Ethernet")

        gw_conn = NetworkTopologyHelper.infer_connection_type("192.168.110.1", device_type="Router")
        self.assertEqual(gw_conn, "WAN")

        # 3. Kiểm tra lộ trình Internet (Hop path)
        hops = NetworkTopologyHelper.get_internet_route("192.168.110.55", connection_type="Wi-Fi", blocked=False)
        self.assertGreaterEqual(len(hops), 3)
        self.assertEqual(hops[-1]["name"], "Internet Toàn Cầu")

        blocked_hops = NetworkTopologyHelper.get_internet_route("192.168.110.55", connection_type="Wi-Fi", blocked=True)
        self.assertEqual(blocked_hops[-1]["status"], "BLOCKED")

        # 4. Kiểm tra DeviceDAO update connection & network distribution
        dev = Device(ip="192.168.110.88", mac="12:34:56:78:9A:BC", connection_type="Wi-Fi")
        self.device_dao.upsert_device(dev)
        ok = self.device_dao.update_connection_info(dev.mac, "Ethernet", "Router Phụ Test")
        self.assertTrue(ok)

        fetched = self.device_dao.get_device_by_mac(dev.mac)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.connection_type, "Ethernet")
        self.assertEqual(fetched.network_name, "Router Phụ Test")

        dist = self.device_dao.get_network_distribution()
        self.assertIn("wifi", dist)
        self.assertIn("ethernet", dist)
        self.assertIn("primary_net", dist)
        self.assertIn("secondary_net", dist)

if __name__ == "__main__":
    result = unittest.main(exit=False)
    sys.exit(0 if result.result.wasSuccessful() else 1)

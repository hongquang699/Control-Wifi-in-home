"""
Unit tests cho dịch vụ kiểm tra cập nhật (Auto-Updater Service).
"""

import unittest
from unittest.mock import patch, MagicMock
from services.updater import UpdateChecker, UpdateInfo, parse_version, CURRENT_VERSION


class TestUpdater(unittest.TestCase):

    def test_parse_version(self):
        self.assertEqual(parse_version("v2.0.0"), (2, 0, 0))
        self.assertEqual(parse_version("2.1.5"), (2, 1, 5))
        self.assertEqual(parse_version("v3.0.0-rc1"), (3, 0, 0))
        self.assertEqual(parse_version("invalid"), (0, 0, 0))
        self.assertEqual(parse_version(""), (0, 0, 0))

    def test_version_comparison_logic(self):
        v1 = parse_version("1.2.0")
        v2 = parse_version("2.0.0")
        v3 = parse_version("2.1.0")
        self.assertTrue(v2 > v1)
        self.assertTrue(v3 > v2)
        self.assertFalse(v1 > v2)

    @patch("urllib.request.urlopen")
    def test_check_for_updates_available(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = b'''{
            "tag_name": "v2.5.0",
            "name": "Network Manager v2.5.0",
            "body": "Nang cap WAF va Anti-DoS",
            "html_url": "https://github.com/hongquang699/Control-Wifi-in-home/releases/tag/v2.5.0",
            "published_at": "2026-09-20T00:00:00Z"
        }'''
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        checker = UpdateChecker(current_version="2.0.0")
        info = checker.check_for_updates()

        self.assertTrue(info.is_update_available)
        self.assertEqual(info.latest_version, "2.5.0")
        self.assertIn("v2.5.0", info.download_url)
        self.assertIsNone(info.error_message)

    @patch("urllib.request.urlopen")
    def test_check_for_updates_already_latest(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = b'''{
            "tag_name": "v2.0.0",
            "name": "Network Manager v2.0.0 Cyberpunk",
            "body": "Ban moi nhat",
            "html_url": "https://github.com/hongquang699/Control-Wifi-in-home/releases/tag/v2.0.0",
            "published_at": "2026-09-20T00:00:00Z"
        }'''
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        checker = UpdateChecker(current_version="2.0.0")
        info = checker.check_for_updates()

        self.assertFalse(info.is_update_available)
        self.assertEqual(info.latest_version, "2.0.0")

    @patch("urllib.request.urlopen")
    def test_check_for_updates_offline_fallback(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("Connection timed out")

        checker = UpdateChecker(current_version="2.0.0")
        info = checker.check_for_updates()

        self.assertFalse(info.is_update_available)
        self.assertEqual(info.current_version, "2.0.0")
        self.assertIsNotNone(info.error_message)


if __name__ == "__main__":
    unittest.main()

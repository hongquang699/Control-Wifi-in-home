"""
Network Manager - Unified Backend REST API & Web Server
Provides endpoints for system stats, devices catalog, access control blocking,
traffic monitor, security alerts, and downloads verification.
"""

import http.server
import socketserver
import json
import os
import sys
import time
import math
import hashlib
import urllib.parse
from pathlib import Path
from typing import Dict, Any, List, Optional

PORT = int(os.environ.get("PORT", 8080))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MOCK_LOGS = [
    {
        "id": 1,
        "event_type": "DEVICE_JOINED",
        "device_mac": "38:B1:DB:54:A8:12",
        "device_ip": "192.168.1.102",
        "device_name": "Dell XPS 15 (Workstation)",
        "message": "Thiết bị kết nối vào mạng qua Wi-Fi Tổng",
        "timestamp": "2026-09-19 09:15:20"
    },
    {
        "id": 2,
        "event_type": "SCAN_COMPLETED",
        "device_mac": "--",
        "device_ip": "192.168.1.0/24",
        "device_name": "System Scanner",
        "message": "Hoàn thành quét mạng định kỳ. Tìm thấy 7 thiết bị trực tuyến.",
        "timestamp": "2026-09-19 09:10:00"
    },
    {
        "id": 3,
        "event_type": "DEVICE_BLOCKED",
        "device_mac": "BC:D1:D3:45:90:E2",
        "device_ip": "192.168.1.115",
        "device_name": "iPhone 15 Pro Max",
        "message": "Đã gửi quy tắc chặn tới Router TP-Link ACL và Windows Firewall",
        "timestamp": "2026-09-19 08:50:11"
    },
    {
        "id": 4,
        "event_type": "DEVICE_UNBLOCKED",
        "device_mac": "BC:D1:D3:45:90:E2",
        "device_ip": "192.168.1.115",
        "device_name": "iPhone 15 Pro Max",
        "message": "Đã gỡ bỏ quy tắc chặn thiết bị thành công",
        "timestamp": "2026-09-19 08:55:00"
    },
    {
        "id": 5,
        "event_type": "DEVICE_OFFLINE",
        "device_mac": "3C:06:30:19:67:BC",
        "device_ip": "192.168.1.189",
        "device_name": "MacBook Pro M2 (Nam)",
        "message": "Thiết bị ngắt kết nối mạng",
        "timestamp": "2026-09-18 22:30:00"
    }
]

MOCK_SETTINGS = {
    "network": {
        "scan_interval_seconds": 60,
        "custom_subnets": ["192.168.1.0/24", "192.168.110.0/24"],
        "nmap_arguments": "-sn -PR --min-rate 100",
        "timeout_seconds": 3
    },
    "router": {
        "adapter_type": "mock",
        "host": "192.168.1.1",
        "port": 80,
        "username": "admin",
        "ssl_verify": False
    },
    "ui": {
        "language": "vi",
        "theme": "dark_cyber",
        "refresh_rate_ms": 1000
    }
}

# In-memory storage / Mock Database
MOCK_DEVICES = [
    {
        "id": 1,
        "ip": "192.168.1.102",
        "mac": "38:B1:DB:54:A8:12",
        "hostname": "DESKTOP-DELL-XPS",
        "alias": "Dell XPS 15 (Workstation)",
        "vendor": "Dell Inc.",
        "device_type": "PC / Laptop",
        "network_zone": "Wi-Fi Tổng (192.168.1.x)",
        "subnet": "primary",
        "medium": "Wi-Fi",
        "latency_ms": 2,
        "status": "ONLINE",
        "first_seen": "2026-09-01T08:00:00Z",
        "last_seen": "2026-09-19T09:00:00Z"
    },
    {
        "id": 2,
        "ip": "192.168.1.115",
        "mac": "BC:D1:D3:45:90:E2",
        "hostname": "iPhone-15-Pro",
        "alias": "iPhone 15 Pro Max",
        "vendor": "Apple, Inc.",
        "device_type": "Smartphone / Tablet",
        "network_zone": "Wi-Fi Tổng (192.168.1.x)",
        "subnet": "primary",
        "medium": "Wi-Fi",
        "latency_ms": 14,
        "status": "ONLINE",
        "first_seen": "2026-09-10T14:20:00Z",
        "last_seen": "2026-09-19T09:02:00Z"
    },
    {
        "id": 3,
        "ip": "192.168.110.45",
        "mac": "64:1C:67:8A:23:4F",
        "hostname": "Samsung-SmartTV",
        "alias": "Samsung Neo QLED 4K TV",
        "vendor": "Samsung Electronics",
        "device_type": "IoT Smart Device",
        "network_zone": "Router Phụ (192.168.110.x)",
        "subnet": "secondary",
        "medium": "LAN",
        "latency_ms": 5,
        "status": "ONLINE",
        "first_seen": "2026-09-05T10:00:00Z",
        "last_seen": "2026-09-19T09:01:00Z"
    },
    {
        "id": 4,
        "ip": "192.168.110.88",
        "mac": "AC:BC:32:89:12:34",
        "hostname": "Ezviz-C6N-Cam",
        "alias": "Ezviz C6N Security Cam",
        "vendor": "Hangzhou Hikvision",
        "device_type": "IoT Smart Device",
        "network_zone": "Router Phụ (192.168.110.x)",
        "subnet": "secondary",
        "medium": "Wi-Fi",
        "latency_ms": 18,
        "status": "ONLINE",
        "first_seen": "2026-09-12T07:15:00Z",
        "last_seen": "2026-09-19T08:59:00Z"
    },
    {
        "id": 5,
        "ip": "192.168.110.99",
        "mac": "24:6F:28:FE:19:6A",
        "hostname": "ESP32-Relay-01",
        "alias": "ESP32 Smart Home Relay",
        "vendor": "Espressif Inc.",
        "device_type": "IoT Smart Device",
        "network_zone": "Router Phụ (192.168.110.x)",
        "subnet": "secondary",
        "medium": "Wi-Fi",
        "latency_ms": 9,
        "status": "ONLINE",
        "first_seen": "2026-09-15T19:00:00Z",
        "last_seen": "2026-09-19T09:00:00Z"
    },
    {
        "id": 6,
        "ip": "192.168.1.2",
        "mac": "50:D4:F7:2C:19:A1",
        "hostname": "Archer-AX55",
        "alias": "TP-Link Archer AX55 (Sub-Router)",
        "vendor": "TP-Link Corporation",
        "device_type": "Router / Gateway",
        "network_zone": "Wi-Fi Tổng (192.168.1.x)",
        "subnet": "primary",
        "medium": "LAN",
        "latency_ms": 1,
        "status": "ONLINE",
        "first_seen": "2026-08-20T00:00:00Z",
        "last_seen": "2026-09-19T09:03:00Z"
    },
    {
        "id": 7,
        "ip": "192.168.1.189",
        "mac": "3C:06:30:19:67:BC",
        "hostname": "MacBook-Pro-Nam",
        "alias": "MacBook Pro M2 (Nam)",
        "vendor": "Apple, Inc.",
        "device_type": "PC / Laptop",
        "network_zone": "Wi-Fi Tổng (192.168.1.x)",
        "subnet": "primary",
        "medium": "Wi-Fi",
        "latency_ms": 0,
        "status": "OFFLINE",
        "first_seen": "2026-09-18T16:00:00Z",
        "last_seen": "2026-09-18T22:30:00Z"
    }
]

MOCK_ALERTS = [
    {
        "id": "alt-101",
        "level": "INFO",
        "title": "Hoàn tất quét mạng định kỳ",
        "description": "Đã quét thành công 2 dải subnet 192.168.1.0/24 và 192.168.110.0/24 trong 0.82s.",
        "timestamp": "2026-09-19T09:00:00Z"
    },
    {
        "id": "alt-102",
        "level": "WARNING",
        "title": "Phát hiện thiết bị mới kết nối",
        "description": "Thiết bị mới IP: 192.168.1.134, MAC: 7C:49:EB:11:8A:92 (Xiaomi) vừa kết nối Wi-Fi.",
        "timestamp": "2026-09-19T08:45:12Z"
    },
    {
        "id": "alt-103",
        "level": "SUCCESS",
        "title": "Đồng bộ Tường lửa Windows",
        "description": "Các quy tắc chặn 2 chiều Inbound/Outbound đã đồng bộ an toàn.",
        "timestamp": "2026-09-19T08:30:00Z"
    }
]

def calculate_file_hash(filepath: str) -> str:
    if not os.path.exists(filepath):
        return "sha256_mock_sample"
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

class NetworkManagerHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """Handles both REST API endpoints and static web assets."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def end_headers(self):
        # Enable CORS and disable aggressive caching for API
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def send_json(self, data: Any, status: int = 200):
        body = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")
        query = urllib.parse.parse_qs(parsed.query)

        # 1. API: Healthcheck
        if path == "/api/v1/health":
            self.send_json({
                "status": "healthy",
                "service": "Network Manager REST API",
                "version": "1.0.0",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            })
            return

        # 2. API: System & Network Stats
        if path == "/api/v1/stats":
            total = len(MOCK_DEVICES)
            online = sum(1 for d in MOCK_DEVICES if d["status"] == "ONLINE")
            offline = sum(1 for d in MOCK_DEVICES if d["status"] == "OFFLINE")
            blocked = sum(1 for d in MOCK_DEVICES if d["status"] == "BLOCKED")
            self.send_json({
                "total_devices": total,
                "online_devices": online,
                "offline_devices": offline,
                "blocked_devices": blocked,
                "traffic": {
                    "download_speed_mbps": 24.5,
                    "upload_speed_mbps": 8.2
                },
                "system": {
                    "cpu_percent": 14.2,
                    "ram_percent": 32.5,
                    "uptime_display": "14d 6h 0m",
                    "uptime_seconds": 1231200
                }
            })
            return

        # 3. API: Devices Catalog
        if path == "/api/v1/devices":
            devices = list(MOCK_DEVICES)
            if "subnet" in query:
                s = query["subnet"][0]
                devices = [d for d in devices if d["subnet"] == s]
            if "status" in query:
                st = query["status"][0].upper()
                devices = [d for d in devices if d["status"] == st]
            if "search" in query:
                q = query["search"][0].lower()
                devices = [d for d in devices if q in d["name"].lower() or q in d["ip"].lower() or q in d["mac"].lower() or q in d["vendor"].lower()]
            self.send_json(devices)
            return

        # 4. API: Security Alerts
        if path == "/api/v1/alerts":
            self.send_json(MOCK_ALERTS)
            return

        # 5. API: Networks & Subnets Discovery
        if path == "/api/v1/networks":
            networks_data = {
                "active_interface": {
                    "name": "Wi-Fi 6 (Intel AX211)",
                    "ip": "192.168.1.102",
                    "mac": "38:B1:DB:54:A8:12",
                    "gateway": "192.168.1.1",
                    "netmask": "255.255.255.0",
                    "dns": ["8.8.8.8", "1.1.1.1"]
                },
                "subnets": [
                    {
                        "id": "primary",
                        "cidr": "192.168.1.0/24",
                        "label": "Wi-Fi Tổng (Modem ISP)",
                        "gateway": "192.168.1.1",
                        "total_devices": sum(1 for d in MOCK_DEVICES if d.get("subnet") == "primary"),
                        "router_model": "VNPT / Viettel GPON Gateway"
                    },
                    {
                        "id": "secondary",
                        "cidr": "192.168.110.0/24",
                        "label": "Router Phụ (Phòng Ngủ / IoT)",
                        "gateway": "192.168.110.1",
                        "total_devices": sum(1 for d in MOCK_DEVICES if d.get("subnet") == "secondary"),
                        "router_model": "TP-Link Archer AX55 (AP Mode)"
                    }
                ],
                "topology_summary": {
                    "tiers": 3,
                    "internet_accessible": True,
                    "hop_route": [
                        "192.168.1.102 (Local Station)",
                        "192.168.1.1 (Gateway ISP)",
                        "203.113.131.1 (WAN Uplink)",
                        "8.8.8.8 (Global Internet)"
                    ]
                }
            }
            self.send_json(networks_data)
            return

        # 6. API: Real-time Traffic Waveform & Bandwidth
        if path == "/api/v1/traffic":
            cur_down = 24.5
            cur_up = 8.2
            samples = []
            for i in range(60):
                t_val = i * 0.15
                d = round(20 + 8 * math.sin(t_val) + 3 * math.sin(t_val * 2.1), 2)
                u = round(7 + 3 * math.cos(t_val * 1.3), 2)
                samples.append({"step": i, "download_mbps": max(0.5, d), "upload_mbps": max(0.2, u)})
            self.send_json({
                "current_download_mbps": cur_down,
                "current_upload_mbps": cur_up,
                "peak_download_mbps": 78.4,
                "peak_upload_mbps": 22.1,
                "unit": "MB/s",
                "samples_count": 60,
                "history": samples
            })
            return

        # 7. API: Audit Event Logs
        if path == "/api/v1/logs":
            limit = int(query.get("limit", [50])[0])
            self.send_json(MOCK_LOGS[:limit])
            return

        # 8. API: System Settings
        if path == "/api/v1/settings":
            self.send_json(MOCK_SETTINGS)
            return

        # 9. API: Single Device Detail by MAC
        path_parts = parsed.path.strip("/").split("/")
        if len(path_parts) == 4 and path_parts[0] == "api" and path_parts[1] == "v1" and path_parts[2] == "devices":
            mac = urllib.parse.unquote(path_parts[3])
            device = next((d for d in MOCK_DEVICES if d["mac"].upper() == mac.upper()), None)
            if device:
                self.send_json(device)
            else:
                self.send_json({"error": f"Device with MAC {mac} not found"}, status=404)
            return

        # 10. API: Downloads Catalog with SHA-256
        if path == "/api/v1/downloads":
            win_path = os.path.join(BASE_DIR, "downloads", "windows", "NetworkManager-v1.0.0-windows-x64.zip")
            linux_path = os.path.join(BASE_DIR, "downloads", "linux", "NetworkManager-v1.0.0-linux-x64.tar.gz")
            macos_path = os.path.join(BASE_DIR, "downloads", "macos", "NetworkManager-v1.0.0-darwin-arm64.dmg")
            
            downloads = [
                {
                    "platform": "windows",
                    "title": "Windows x64",
                    "filename": "NetworkManager-v1.0.0-windows-x64.zip",
                    "size_display": "45.2 MB",
                    "release_date": "19/09/2026",
                    "version": "1.0.0",
                    "sha256": calculate_file_hash(win_path),
                    "url": "/downloads/windows/NetworkManager-v1.0.0-windows-x64.zip"
                },
                {
                    "platform": "linux",
                    "title": "Linux x64",
                    "filename": "NetworkManager-v1.0.0-linux-x64.tar.gz",
                    "size_display": "38.6 MB",
                    "release_date": "19/09/2026",
                    "version": "1.0.0",
                    "sha256": calculate_file_hash(linux_path),
                    "url": "/downloads/linux/NetworkManager-v1.0.0-linux-x64.tar.gz"
                },
                {
                    "platform": "macos",
                    "title": "macOS Apple Silicon",
                    "filename": "NetworkManager-v1.0.0-darwin-arm64.dmg",
                    "size_display": "42.1 MB",
                    "release_date": "19/09/2026",
                    "version": "1.0.0",
                    "sha256": calculate_file_hash(macos_path),
                    "url": "/downloads/macos/NetworkManager-v1.0.0-darwin-arm64.dmg"
                }
            ]
            self.send_json(downloads)
            return

        # HTML Page Routing: Route root and direct HTML page URLs to html/ folder
        clean_path = parsed.path
        if clean_path in ("/", "/index.html", ""):
            self.path = "/html/index.html"
        elif clean_path in ("/404.html", "/thank-you.html", "/privacy-policy.html"):
            self.path = f"/html{clean_path}"

        # Default: Fallback to static file server
        super().do_GET()

    def send_error(self, code, message=None, explain=None):
        if code == 404:
            custom_404 = os.path.join(BASE_DIR, "html", "404.html")
            if os.path.exists(custom_404):
                with open(custom_404, "rb") as f:
                    content = f.read()
                self.send_response(404)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return
        super().send_error(code, message, explain)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")
        path_parts = path.strip("/").split("/")

        # POST /api/v1/scan
        if path == "/api/v1/scan":
            self.send_json({
                "success": True,
                "message": "Quá trình quét mạng ARP & Ping đa luồng đã hoàn tất.",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "total_scanned_subnets": 2,
                "duration_seconds": 1.15,
                "found_devices_count": len(MOCK_DEVICES)
            })
            return

        # POST /api/v1/settings
        if path == "/api/v1/settings":
            content_len = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_len) if content_len > 0 else b"{}"
            try:
                data = json.loads(post_data.decode("utf-8"))
                for k, v in data.items():
                    if isinstance(v, dict) and k in MOCK_SETTINGS:
                        MOCK_SETTINGS[k].update(v)
                    else:
                        MOCK_SETTINGS[k] = v
                self.send_json({"success": True, "settings": MOCK_SETTINGS})
            except Exception as e:
                self.send_json({"error": str(e)}, status=400)
            return

        # Handler: /api/v1/devices/<mac>/block or unblock
        if len(path_parts) == 5 and path_parts[0] == "api" and path_parts[1] == "v1" and path_parts[2] == "devices":
            mac = urllib.parse.unquote(path_parts[3])
            action = path_parts[4]

            device = next((d for d in MOCK_DEVICES if d["mac"].upper() == mac.upper()), None)
            if not device:
                self.send_json({"error": "Device not found"}, status=404)
                return

            if action == "block":
                device["status"] = "BLOCKED"
                self.send_json({
                    "success": True,
                    "mac": mac,
                    "status": "BLOCKED",
                    "message": f"Đã gửi lệnh chặn MAC {mac} tới Router và Tường lửa Windows."
                })
                return
            elif action == "unblock":
                device["status"] = "ONLINE"
                self.send_json({
                    "success": True,
                    "mac": mac,
                    "status": "ONLINE",
                    "message": f"Đã gỡ bỏ lệnh chặn MAC {mac} khỏi Router và Tường lửa Windows."
                })
                return

        self.send_json({"error": "Endpoint not found"}, status=404)

def run_server(port: int = PORT):
    print(f"==================================================")
    print(f"  NETWORK MANAGER - BACKEND API & WEB SERVER")
    print(f"==================================================")
    print(f"[*] Serving files from: {BASE_DIR}")
    print(f"[*] API Server running at: http://localhost:{port}")
    print(f"[*] REST Endpoints available at: http://localhost:{port}/api/v1/")
    print(f"[*] Press Ctrl+C to terminate.")

    with socketserver.TCPServer(("", port), NetworkManagerHTTPHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[!] Shutting down server gracefully...")

if __name__ == "__main__":
    port = PORT
    if len(sys.argv) > 1:
        for i, arg in enumerate(sys.argv[1:], 1):
            if arg in ("--port", "-p") and i < len(sys.argv) - 1:
                try:
                    port = int(sys.argv[i + 1])
                except ValueError:
                    pass
            elif arg.isdigit():
                port = int(arg)
    run_server(port)

"""
Network Manager - Multi-Layer Secure Web & REST API Server
Kiến trúc phòng thủ đa lớp (Defense-in-Depth):
- Lớp 1: HTTPS/TLS & Security Headers (CSP, HSTS, X-Content-Type-Options, X-Frame-Options)
- Lớp 2: Web Application Firewall (WAF) & Rate Limiting (Chống SQLi, XSS, Path Traversal, Brute-Force)
- Lớp 3 & 4: Authentication & RBAC (PBKDF2-HMAC-SHA256, Session Token, Admin/Operator/User)
- Lớp 5 & 6: Input Validation, Database Protection, Che giấu thông tin nhạy cảm
- Lớp 7: Secure Download Service (SHA-256 integrity, chống upload độc hại)
- Lớp 8, 9 & 10: Security Headers, Structured Audit Logging, Tự động sao lưu Database
"""

import http.server
import socketserver
import json
import os
import sys

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import urllib.parse
from pathlib import Path
from typing import Dict, Any, Optional

# Thêm đường dẫn để import các module nội bộ
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, WEB_DIR)

from backend.middleware.security_headers import apply_security_headers
from backend.middleware.waf import inspect_request
from backend.middleware.rate_limit import rate_limiter
from backend.auth.session import session_manager, UserRole
from backend.services.audit_service import audit_logger
from backend.services.download_service import download_service
from backend.services.backup_service import backup_service
from backend.api.routes import APIRouter

PORT = int(os.environ.get("PORT", 8080))
BASE_DIR = WEB_DIR

# Dữ liệu mẫu khởi tạo cho thiết bị và cảnh báo
INIT_DEVICES = [
    {
        "id": 1,
        "ip": "192.168.1.102",
        "mac": "38:B1:DB:54:A8:12",
        "hostname": "DESKTOP-DELL-XPS",
        "alias": "Dell XPS 15 (Workstation)",
        "vendor": "Dell Inc.",
        "device_type": "PC / Laptop",
        "first_seen": "2026-09-18 08:30:12",
        "last_seen": "Vừa xong",
        "status": "ONLINE",
        "blocked": False,
        "connection_medium": "📶 Wi-Fi 6 (5GHz)",
        "network_zone": "Wi-Fi Tổng (192.168.1.0/24)",
        "ping_ms": 1.5,
        "open_ports": [22, 443, 3389],
        "hop_path": ["192.168.1.102", "192.168.1.1", "203.113.131.1", "8.8.8.8"]
    },
    {
        "id": 2,
        "ip": "192.168.1.189",
        "mac": "3C:06:30:19:67:BC",
        "hostname": "MacBook-Pro-Nam",
        "alias": "MacBook Pro M2 (Nam)",
        "vendor": "Apple, Inc.",
        "device_type": "PC / Laptop",
        "first_seen": "2026-09-18 09:12:00",
        "last_seen": "Vừa xong",
        "status": "ONLINE",
        "blocked": False,
        "connection_medium": "📶 Wi-Fi 6 (5GHz)",
        "network_zone": "Wi-Fi Tổng (192.168.1.0/24)",
        "ping_ms": 2.1,
        "open_ports": [443, 5000],
        "hop_path": ["192.168.1.189", "192.168.1.1", "203.113.131.1", "8.8.8.8"]
    },
    {
        "id": 3,
        "ip": "192.168.1.115",
        "mac": "BC:D1:D3:45:90:E2",
        "hostname": "iPhone-15-Pro",
        "alias": "iPhone 15 Pro Max",
        "vendor": "Apple, Inc.",
        "device_type": "Smartphone",
        "first_seen": "2026-09-18 10:05:44",
        "last_seen": "Vừa xong",
        "status": "ONLINE",
        "blocked": False,
        "connection_medium": "📶 Wi-Fi 5GHz",
        "network_zone": "Wi-Fi Tổng (192.168.1.0/24)",
        "ping_ms": 4.8,
        "open_ports": [],
        "hop_path": ["192.168.1.115", "192.168.1.1", "203.113.131.1", "8.8.8.8"]
    },
    {
        "id": 4,
        "ip": "192.168.110.15",
        "mac": "50:C7:BF:88:21:44",
        "hostname": "Samsung-SmartTV-QLED",
        "alias": "Samsung Smart 4K TV",
        "vendor": "Samsung Electronics",
        "device_type": "Smart TV",
        "first_seen": "2026-09-17 18:22:10",
        "last_seen": "Vừa xong",
        "status": "ONLINE",
        "blocked": False,
        "connection_medium": "🔌 Dây LAN 1Gbps",
        "network_zone": "Router Phụ (192.168.110.0/24)",
        "ping_ms": 3.2,
        "open_ports": [8080, 8001],
        "hop_path": ["192.168.110.15", "192.168.110.1", "192.168.1.1", "8.8.8.8"]
    },
    {
        "id": 5,
        "ip": "192.168.110.45",
        "mac": "68:C6:3A:99:14:02",
        "hostname": "Ezviz-Cam-Gate",
        "alias": "Camera Cổng Ngoài (Ezviz)",
        "vendor": "Hangzhou Hikvision",
        "device_type": "Camera IP",
        "first_seen": "2026-09-16 12:00:00",
        "last_seen": "Vừa xong",
        "status": "ONLINE",
        "blocked": False,
        "connection_medium": "📶 Wi-Fi 2.4GHz",
        "network_zone": "Router Phụ (192.168.110.0/24)",
        "ping_ms": 8.5,
        "open_ports": [554, 8000],
        "hop_path": ["192.168.110.45", "192.168.110.1", "192.168.1.1", "8.8.8.8"]
    },
    {
        "id": 6,
        "ip": "192.168.110.88",
        "mac": "24:6F:28:FE:19:AA",
        "hostname": "ESP32-Relay-LivingRoom",
        "alias": "Công Tắc Thông Minh Phòng Khách",
        "vendor": "Espressif Inc.",
        "device_type": "IoT Smart Device",
        "first_seen": "2026-09-15 08:00:00",
        "last_seen": "Vừa xong",
        "status": "ONLINE",
        "blocked": False,
        "connection_medium": "📶 Wi-Fi 2.4GHz",
        "network_zone": "Router Phụ (192.168.110.0/24)",
        "ping_ms": 12.0,
        "open_ports": [1883],
        "hop_path": ["192.168.110.88", "192.168.110.1", "192.168.1.1", "8.8.8.8"]
    },
    {
        "id": 7,
        "ip": "192.168.1.205",
        "mac": "88:66:5A:11:33:99",
        "hostname": "Printer-HP-LaserJet",
        "alias": "Máy In HP LaserJet Pro",
        "vendor": "HP Inc.",
        "device_type": "Printer",
        "first_seen": "2026-09-17 14:10:00",
        "last_seen": "3 giờ trước",
        "status": "OFFLINE",
        "blocked": False,
        "connection_medium": "🔌 Dây LAN 100Mbps",
        "network_zone": "Wi-Fi Tổng (192.168.1.0/24)",
        "ping_ms": 0.0,
        "open_ports": [9100, 631],
        "hop_path": ["192.168.1.205", "192.168.1.1", "8.8.8.8"]
    }
]

INIT_SETTINGS = {
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

INIT_LOGS = [
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
    }
]

INIT_ALERTS = [
    {
        "id": 1,
        "severity": "CRITICAL",
        "title": "Phát hiện ARP Spoofing từ IP lạ",
        "device": "192.168.1.250",
        "mac": "00:11:22:33:44:55",
        "description": "Phát hiện gói tin ARP giả mạo Gateway 192.168.1.1. Có nguy cơ tấn công Man-in-the-Middle.",
        "time": "10 phút trước",
        "action_required": "Chặn thiết bị ngay lập tức"
    },
    {
        "id": 2,
        "severity": "WARNING",
        "title": "Băng thông tải xuống vượt ngưỡng 90%",
        "device": "192.168.110.15 (Samsung Smart TV)",
        "mac": "50:C7:BF:88:21:44",
        "description": "Lưu lượng phát trực tuyến 4K đạt 65.2 MB/s liên tục trong 15 phút.",
        "time": "25 phút trước",
        "action_required": "Giới hạn QoS dải 110.0/24"
    }
]

# Khởi tạo API Router tập trung
api_router = APIRouter(INIT_DEVICES, INIT_SETTINGS, INIT_LOGS, INIT_ALERTS)

class MultiLayerSecureHandler(http.server.SimpleHTTPRequestHandler):
    """
    Handler HTTP phục vụ cả Static File và REST API với đầy đủ các tầng bảo mật:
    - WAF (OWASP Top 10)
    - Rate Limiting (Sliding window)
    - Security Headers (CSP, HSTS, X-Content-Type-Options)
    - RBAC Authorization
    """

    def end_headers(self):
        """Gắn tự động toàn bộ Security Headers trước khi gửi response."""
        apply_security_headers(self)
        super().end_headers()

    def get_client_ip(self) -> str:
        """Trích xuất địa chỉ IP thực của Client (hỗ trợ Nginx Reverse Proxy)."""
        forwarded = self.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        real_ip = self.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        return self.client_address[0]

    def send_json(self, data: Any, status: int = 200, extra_headers: Optional[Dict[str, str]] = None):
        """Trả về phản hồi JSON an toàn kèm header tiêu chuẩn."""
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        if extra_headers:
            for k, v in extra_headers.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(payload)

    def _enforce_waf_and_rate_limit(self, body_text: str = "") -> bool:
        """
        Kiểm tra WAF và Rate Limit trước khi cho phép xử lý request.
        Trả về True nếu được phép tiếp tục, False nếu bị chặn.
        """
        client_ip = self.get_client_ip()
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = parsed.query

        # 1. Kiểm tra WAF (SQLi, XSS, Path Traversal, Command Injection)
        waf_res = inspect_request(path, query, body_text)
        if waf_res:
            audit_logger.log_event(
                "WAF_BLOCKED",
                actor="unknown",
                ip=client_ip,
                status="BLOCKED",
                details={
                    "path": path,
                    "attack_type": waf_res.attack_type,
                    "pattern": waf_res.matched_pattern
                }
            )
            self.send_json(
                {
                    "error": "Yêu cầu bị từ chối bởi hệ thống WAF bảo mật (403 Forbidden).",
                    "reason": f"Phát hiện dấu hiệu tấn công: {waf_res.attack_type}",
                    "client_ip": client_ip
                },
                status=403
            )
            return False

        # 2. Kiểm tra Rate Limiting
        zone = "api"
        max_req = 100
        if path == "/api/v1/auth/login":
            zone = "login"
            max_req = 5
        elif path.startswith("/downloads/"):
            zone = "downloads"
            max_req = 10

        is_limited, retry_after = rate_limiter.is_rate_limited(client_ip, zone=zone, max_requests=max_req)
        if is_limited:
            audit_logger.log_event(
                "RATE_LIMIT_HIT",
                actor="unknown",
                ip=client_ip,
                status="BLOCKED",
                details={"zone": zone, "retry_after": retry_after}
            )
            self.send_json(
                {
                    "error": "Quá nhiều yêu cầu trong thời gian ngắn (429 Too Many Requests).",
                    "retry_after_seconds": retry_after,
                    "client_ip": client_ip
                },
                status=429,
                extra_headers={"Retry-After": str(retry_after)}
            )
            return False

        return True

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        client_ip = self.get_client_ip()
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # 1. Kiểm tra WAF & Rate Limit
        if not self._enforce_waf_and_rate_limit():
            return

        auth_header = self.headers.get("Authorization")

        # 2. Xử lý các yêu cầu REST API
        if path.startswith("/api/"):
            data, status = api_router.handle_get(path, query, auth_header, client_ip)
            self.send_json(data, status=status)
            return

        # 3. Xử lý tải xuống tệp tin an toàn (/downloads/...)
        if path.startswith("/downloads/"):
            is_safe, abs_path, err = download_service.resolve_safe_download(path, client_ip)
            if not is_safe:
                self.send_json({"error": err}, status=403 if "từ chối" in err else 404)
                return

            # Gửi tệp tin đính kèm an toàn
            try:
                with open(abs_path, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Content-Disposition", f'attachment; filename="{os.path.basename(abs_path)}"')
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            except Exception as e:
                self.send_json({"error": f"Lỗi đọc file: {e}"}, status=500)
            return

        # 4. Chặn truy cập thư mục nội bộ nhạy cảm
        forbidden_folders = ["/config", "/logs", "/backups", "/backend", "/.git"]
        if any(path.startswith(fb) for fb in forbidden_folders):
            audit_logger.log_event("FORBIDDEN_DIR_ACCESS", ip=client_ip, status="BLOCKED", details={"path": path})
            self.send_json({"error": "Truy cập bị từ chối (403 Forbidden)."}, status=403)
            return

        # 5. Phục vụ Frontend Tĩnh từ web/html/, css, js, images
        rel_path = path.lstrip("/")
        if not rel_path or rel_path == "index.html":
            file_path = os.path.join(BASE_DIR, "html", "index.html")
        elif rel_path in ("privacy-policy.html", "thank-you.html", "404.html"):
            file_path = os.path.join(BASE_DIR, "html", rel_path)
        else:
            file_path = os.path.join(BASE_DIR, rel_path)

        canonical_path = os.path.abspath(file_path)
        canonical_base = os.path.abspath(BASE_DIR)

        if not canonical_path.startswith(canonical_base) or not os.path.exists(canonical_path):
            # Trả về 404 tùy chỉnh
            f404 = os.path.join(BASE_DIR, "html", "404.html")
            if os.path.exists(f404):
                with open(f404, "rb") as f:
                    body_404 = f.read()
                self.send_response(404)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body_404)))
                self.end_headers()
                self.wfile.write(body_404)
            else:
                self.send_error(404, "File not found")
            return

        # Định dạng MIME type
        mime_types = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".ico": "image/x-icon",
            ".svg": "image/svg+xml",
            ".json": "application/json; charset=utf-8",
            ".xml": "application/xml; charset=utf-8",
            ".txt": "text/plain; charset=utf-8"
        }
        ext = os.path.splitext(canonical_path)[1].lower()
        content_type = mime_types.get(ext, "application/octet-stream")

        try:
            with open(canonical_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Error reading file: {e}")

    def do_POST(self):
        client_ip = self.get_client_ip()
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # Đọc body của request
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 5 * 1024 * 1024:  # Giới hạn 5MB
            self.send_json({"error": "Dung lượng payload vượt quá 5MB."}, status=413)
            return

        body_bytes = self.rfile.read(content_length) if content_length > 0 else b"{}"
        try:
            body_text = body_bytes.decode("utf-8")
            body_json = json.loads(body_text) if body_text.strip() else {}
        except Exception:
            body_text = ""
            body_json = {}

        # 1. Kiểm tra WAF & Rate Limit
        if not self._enforce_waf_and_rate_limit(body_text=body_text):
            return

        auth_header = self.headers.get("Authorization")

        # 2. Xử lý qua API Router
        if path.startswith("/api/"):
            data, status = api_router.handle_post(path, body_json, auth_header, client_ip)
            self.send_json(data, status=status)
            return

        self.send_json({"error": "Endpoint không hỗ trợ POST"}, status=405)


class ThreadedHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


def run_server(port: int = PORT):
    print("=" * 65)
    print("    NETWORK MANAGER - MÁY CHỦ BẢO MẬT ĐA LỚP (MULTI-LAYER SECURITY)")
    print("=" * 65)
    print(f"[*] Cổng lắng nghe: {port}")
    print(f"[*] Thư mục gốc Web: {BASE_DIR}")
    print(f"[*] Địa chỉ truy cập: http://localhost:{port}")
    print(f"[*] Hệ thống WAF: KÍCH HOẠT (Chặn SQLi, XSS, Path Traversal, Cmd Inj)")
    print(f"[*] Hệ thống Rate Limiting: KÍCH HOẠT (Sliding-Window IP Guard)")
    print(f"[*] Hệ thống Xác thực RBAC: KÍCH HOẠT (Admin, Operator, User)")
    print(f"[*] Hệ thống Audit Log: KÍCH HOẠT (web/logs/audit/audit.log)")
    print("-" * 65)

    with ThreadedHTTPServer(("", port), MultiLayerSecureHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[*] Đang dừng máy chủ an toàn...")
            httpd.shutdown()


if __name__ == "__main__":
    p = PORT
    if len(sys.argv) > 1:
        try:
            p = int(sys.argv[1])
        except ValueError:
            pass
    run_server(p)

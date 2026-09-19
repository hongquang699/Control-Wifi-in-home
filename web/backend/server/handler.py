"""
HTTP Handler đa lớp bảo mật (WAF, Rate Limiting, RBAC, Security Headers).
"""

import http.server
import socketserver
import json
import os
import urllib.parse
from typing import Dict, Any, Optional

try:
    from web.security import (
        waf_engine, rate_limiter as web_rate_limiter,
        apply_security_headers as apply_web_security_headers,
        csrf_protector, audit_logger as sec_audit_logger,
        cors_manager, vpn_guard,
        request_guard, mask_sensitive_data
    )
except ImportError:
    from security import (
        waf_engine, rate_limiter as web_rate_limiter,
        apply_security_headers as apply_web_security_headers,
        csrf_protector, audit_logger as sec_audit_logger,
        cors_manager, vpn_guard,
        request_guard, mask_sensitive_data
    )

from backend.middleware.security_headers import apply_security_headers
from backend.middleware.waf import inspect_request
from backend.middleware.rate_limit import rate_limiter
from backend.services.audit_service import audit_logger
from backend.services.download_service import download_service
from backend.api.routes import APIRouter
from backend.server.mock_data import INIT_DEVICES, INIT_SETTINGS, INIT_LOGS, INIT_ALERTS
from backend.server.static_files import serve_static_resource

# Khởi tạo API Router tập trung
api_router = APIRouter(INIT_DEVICES, INIT_SETTINGS, INIT_LOGS, INIT_ALERTS)

class MultiLayerSecureHandler(http.server.SimpleHTTPRequestHandler):
    """
    Handler HTTP phục vụ cả Static File và REST API với đầy đủ các tầng bảo mật:
    - WAF (OWASP Top 10)
    - Rate Limiting (Sliding window)
    - Security Headers (CSP, HSTS, X-Content-Type-Options)
    - RBAC Authorization
    - CORS Policy & Preflight Handlers
    - VPN & Private Network Guard
    """

    def do_OPTIONS(self):
        """Xử lý yêu cầu CORS Preflight chuẩn RFC 6454."""
        origin = self.headers.get("Origin")
        cors_manager.handle_preflight(self, origin)

    def end_headers(self):
        """Gắn tự động toàn bộ Security Headers và CORS trước khi gửi response."""
        origin = self.headers.get("Origin")
        cors_manager.apply_cors_headers(self, origin)
        apply_web_security_headers(self, is_api_response=self.path.startswith("/api/"))
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
        """Trả về phản hồi JSON an toàn kèm header tiêu chuẩn và khử dữ liệu nhạy cảm."""
        masked_data = mask_sensitive_data(data)
        payload = json.dumps(masked_data, ensure_ascii=False).encode("utf-8")
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
        Kiểm tra Request Guard, WAF và Rate Limit trước khi cho phép xử lý request.
        Trả về True nếu được phép tiếp tục, False nếu bị chặn.
        """
        client_ip = self.get_client_ip()
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = parsed.query

        # 0. Kiểm tra kích thước và MIME type của Request (web.security.request_guard)
        is_req_valid, req_err_code, req_err_msg = request_guard.validate_request(
            method=self.command,
            path=path,
            headers=dict(self.headers)
        )
        if not is_req_valid:
            self.send_json(
                {
                    "error": req_err_msg or "Yêu cầu HTTP bị từ chối bởi Request Guard.",
                    "status": req_err_code,
                    "client_ip": client_ip
                },
                status=req_err_code
            )
            return False

        # 1. Kiểm tra WAF Chuyên Biệt (web.security.waf_engine)
        is_safe, rule_name, reason = waf_engine.inspect_request(
            path=self.path,
            headers=dict(self.headers),
            body=body_text,
            method=self.command
        )
        if not is_safe:
            web_rate_limiter.record_security_violation(client_ip, weight=3)
            sec_audit_logger.log_security_event(
                event_type="WAF_ATTACK_BLOCKED",
                actor="anonymous",
                ip_address=client_ip,
                details=f"Rule: {rule_name} | {reason}",
                severity="HIGH"
            )
            self.send_json(
                {
                    "error": "Yêu cầu bị từ chối bởi hệ thống WAF bảo mật (403 Forbidden).",
                    "reason": reason,
                    "rule": rule_name,
                    "client_ip": client_ip
                },
                status=403
            )
            return False

        # 2. Kiểm tra Rate Limiting & Auto-Jail (web.security.rate_limiter)
        allowed, retry_after, jail_reason = web_rate_limiter.is_allowed(client_ip, endpoint=path)
        if not allowed:
            sec_audit_logger.log_security_event(
                event_type="RATE_LIMIT_HIT",
                actor="anonymous",
                ip_address=client_ip,
                details=jail_reason or f"Rate limit exceeded on {path}",
                severity="WARNING"
            )
            self.send_json(
                {
                    "error": "Quá nhiều yêu cầu trong thời gian ngắn (429 Too Many Requests).",
                    "reason": jail_reason,
                    "retry_after_seconds": retry_after,
                    "client_ip": client_ip
                },
                status=429,
                extra_headers={"Retry-After": str(retry_after)}
            )
            return False

        # 3. Kiểm tra VPN & Mạng Riêng Tư (web.security.vpn_guard)
        is_vpn_allowed, vpn_err = vpn_guard.validate_route_access(client_ip, path)
        if not is_vpn_allowed:
            sec_audit_logger.log_security_event(
                event_type="PUBLIC_ACCESS_BLOCKED_VPN_REQUIRED",
                actor="anonymous",
                ip_address=client_ip,
                details=vpn_err or f"Admin route {path} requires VPN/LAN connection",
                severity="HIGH"
            )
            self.send_json(
                {
                    "error": "Truy cập bị từ chối bởi chính sách bảo mật mạng (403 Forbidden).",
                    "reason": vpn_err,
                    "client_ip": client_ip,
                    "requirement": "Yêu cầu kết nối qua kênh VPN an toàn hoặc mạng nội bộ được ủy quyền"
                },
                status=403
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

        # 2. Xử lý REST API
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

            try:
                file_size = os.path.getsize(abs_path)
                self.send_response(200)
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Content-Disposition", f'attachment; filename="{os.path.basename(abs_path)}"')
                self.send_header("Content-Length", str(file_size))
                self.send_header("Accept-Ranges", "bytes")
                self.send_header("Cache-Control", "public, max-age=3600")
                self.end_headers()

                # Stream file theo từng block 64KB để không tốn RAM và tải mượt mà
                with open(abs_path, "rb") as f:
                    while chunk := f.read(65536):
                        self.wfile.write(chunk)
            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
                # Client hủy tải file hoặc đóng kết nối trình duyệt
                pass
            except Exception as e:
                try:
                    self.send_json({"error": f"Lỗi đọc file: {e}"}, status=500)
                except Exception:
                    pass
            return

        # 4. Chặn truy cập thư mục nội bộ nhạy cảm
        forbidden_folders = ["/config", "/logs", "/backups", "/backend", "/.git"]
        if any(path.startswith(fb) for fb in forbidden_folders):
            audit_logger.log_event("FORBIDDEN_DIR_ACCESS", ip=client_ip, status="BLOCKED", details={"path": path})
            self.send_json({"error": "Truy cập bị từ chối (403 Forbidden)."}, status=403)
            return

        # 5. Phục vụ Frontend Tĩnh
        base_dir = getattr(self.server, "base_dir", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        serve_static_resource(self, base_dir, path)

    def do_POST(self):
        client_ip = self.get_client_ip()
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 5 * 1024 * 1024:  # Giới hạn 5MB
            self.send_json({"error": "Dung lượng payload vượt quá 5MB."}, status=413)
            return

        body_bytes = self.rfile.read(content_length) if content_length > 0 else b"{}"
        try:
            body_text = body_bytes.decode("utf-8", errors="ignore")
        except Exception:
            body_text = ""
        try:
            body_json = json.loads(body_text) if body_text.strip() else {}
        except Exception:
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

    def __init__(self, server_address, RequestHandlerClass, base_dir=None):
        self.base_dir = base_dir
        super().__init__(server_address, RequestHandlerClass)

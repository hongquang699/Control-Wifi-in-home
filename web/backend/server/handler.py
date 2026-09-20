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
        request_guard, mask_sensitive_data,
        dos_manager, ip_ban_bot
    )
except ImportError:
    from security import (
        waf_engine, rate_limiter as web_rate_limiter,
        apply_security_headers as apply_web_security_headers,
        csrf_protector, audit_logger as sec_audit_logger,
        cors_manager, vpn_guard,
        request_guard, mask_sensitive_data,
        dos_manager, ip_ban_bot
    )

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
        self.send_header("Connection", "close")
        self.close_connection = True
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

    def is_html_client(self) -> bool:
        """Xác định client đang duyệt trang bằng trình duyệt Web hay gọi REST API thuần."""
        if self.path.startswith("/api/"):
            return False
        accept = self.headers.get("Accept", "")
        return "text/html" in accept or accept == "*/*" or not accept

    def send_html_response(self, html_content: str, status: int = 200, extra_headers: Optional[Dict[str, str]] = None):
        """Gửi phản hồi HTML an toàn với đầy đủ Security Headers."""
        payload = html_content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        if extra_headers:
            for k, v in extra_headers.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(payload)

    def _render_429_page(self, client_ip: str, retry_after: int) -> str:
        """Đọc và điền tham số vào trang 429 Bạn bấm quá nhanh vui lòng thử lại."""
        file_path = os.path.join(self.server.base_dir, "html", "429.html")
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    content = content.replace('let secondsLeft = parseInt(urlParams.get(\'retry\')) || 60;', f'let secondsLeft = {retry_after};')
                    content = content.replace('<span id="countdown">60</span>', f'<span id="countdown">{retry_after}</span>')
                    content = content.replace('<strong class="text-slate-200" id="clientIp">Đang xác định...</strong>', f'<strong class="text-slate-200" id="clientIp">{client_ip}</strong>')
                    return content
            except Exception:
                pass
        # Fallback inline nếu file không đọc được
        return f"""<!DOCTYPE html><html lang="vi"><head><meta charset="UTF-8"><title>429 - Bạn Bấm Quá Nhanh</title><style>body{{background:#0b0f19;color:#fff;font-family:sans-serif;text-align:center;padding:10vh 20px;}}h1{{color:#f59e0b;font-size:2rem;}}p{{color:#94a3b8;}}</style></head><body><h1>Bạn Bấm Quá Nhanh, Vui Lòng Thử Lại!</h1><p>IP {client_ip} đã gửi hơn 100 requests/lần. Vui lòng thử lại sau {retry_after} giây.</p><p><a href="/" style="color:#38bdf8;">Quay về Trang chủ</a></p></body></html>"""

    def _render_banned_page(self, client_ip: str, incident_id: str = "BOT-BAN-1000", reason: str = "Vượt quá 1000 requests") -> str:
        """Đọc và điền tham số vào trang 403 Banned do Bot Ban IP."""
        file_path = os.path.join(self.server.base_dir, "html", "banned.html")
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    content = content.replace('<span class="text-white font-bold" id="bannedIp">Đang xác định...</span>', f'<span class="text-white font-bold" id="bannedIp">{client_ip}</span>')
                    content = content.replace('<span class="text-red-400 font-bold" id="incidentId">BOT-BAN-AUTO-998</span>', f'<span class="text-red-400 font-bold" id="incidentId">{incident_id}</span>')
                    return content
            except Exception:
                pass
        # Fallback inline nếu file không đọc được
        return f"""<!DOCTYPE html><html lang="vi"><head><meta charset="UTF-8"><title>403 - IP Đã Bị Cấm Bởi Bot An Ninh</title><style>body{{background:#090b12;color:#fff;font-family:sans-serif;text-align:center;padding:10vh 20px;}}h1{{color:#ef4444;font-size:2rem;}}p{{color:#94a3b8;}}</style></head><body><h1>Truy Cập Bị Cấm - IP Đã Bị Khóa Bởi Bot An Ninh</h1><p>Địa chỉ IP {client_ip} đã gửi hơn 1,000 requests và bị Bot Ban IP cấm.</p><p>Mã sự cố: {incident_id}</p></body></html>"""

    def _enforce_waf_and_rate_limit(self, body_text: str = "") -> bool:
        """
        Kiểm tra Request Guard, WAF và Rate Limit trước khi cho phép xử lý request.
        Trả về True nếu được phép tiếp tục, False nếu bị chặn.
        """
        client_ip = self.get_client_ip()
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = parsed.query

        # -2. Kiểm tra xem IP có đang bị Bot Ban (ngưỡng 1000 requests) hay không
        if ip_ban_bot:
            is_banned, ban_meta = ip_ban_bot.is_banned(client_ip)
            if is_banned:
                incident = ban_meta.get("incident_id", "BOT-BAN-1000") if ban_meta else "BOT-BAN-1000"
                reason = ban_meta.get("reason", "Vượt quá 1000 requests - Bị Bot cấm") if ban_meta else "Bị Bot cấm"
                sec_audit_logger.log_security_event(
                    event_type="BOT_BANNED_REQUEST_DROPPED",
                    actor="anonymous",
                    ip_address=client_ip,
                    details=f"Yêu cầu từ IP bị cấm {client_ip} đến {path} bị từ chối",
                    severity="HIGH"
                )
                if self.is_html_client():
                    banned_html = self._render_banned_page(client_ip, incident, reason)
                    self.send_html_response(banned_html, status=403)
                else:
                    self.send_json({
                        "error": "Truy cập bị từ chối: IP của bạn đã bị Bot an ninh cấm (Vượt quá 1000 requests).",
                        "status": 403,
                        "incident_id": incident,
                        "client_ip": client_ip,
                        "reason": reason
                    }, status=403)
                return False

        # -1. Kiểm tra Anti-DoS: Micro-burst và Trạng thái Under Attack (web.security.dos_guard)
        is_burst_ok, burst_code, burst_err = dos_manager.check_request(client_ip, endpoint=path)
        if not is_burst_ok:
            sec_audit_logger.log_security_event(
                event_type="DOS_BURST_ATTACK_BLOCKED",
                actor="anonymous",
                ip_address=client_ip,
                details=burst_err or f"Micro-burst DoS blocked on {path}",
                severity="CRITICAL"
            )
            if self.is_html_client():
                cooldown_html = self._render_429_page(client_ip, 60)
                self.send_html_response(cooldown_html, status=burst_code, extra_headers={"Retry-After": "60"})
            else:
                self.send_json(
                    {
                        "error": burst_err or "Yêu cầu bị từ chối bởi hệ thống phòng thủ Anti-DoS.",
                        "status": burst_code,
                        "client_ip": client_ip
                    },
                    status=burst_code,
                    extra_headers={"Retry-After": "60"}
                )
            return False

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

        # 2. Kiểm tra Rate Limiting (100 req) & Bot Ban (1000 req) (web.security.rate_limiter)
        allowed, retry_after, jail_reason = web_rate_limiter.is_allowed(client_ip, endpoint=path)
        if not allowed:
            # Nếu lý do là do Bot Ban (vừa chạm mốc 1000 requests)
            if jail_reason and "BOT_BANNED" in jail_reason:
                if self.is_html_client():
                    banned_html = self._render_banned_page(client_ip, "BOT-BAN-1000", jail_reason)
                    self.send_html_response(banned_html, status=403)
                else:
                    self.send_json({
                        "error": "Địa chỉ IP đã gửi hơn 1000 requests và bị Bot Ban IP cấm.",
                        "status": 403,
                        "client_ip": client_ip,
                        "reason": jail_reason
                    }, status=403)
                return False

            # Vượt quá 100 requests: Hiện trang "bạn bấm quá nhanh vui lòng thử lại"
            sec_audit_logger.log_security_event(
                event_type="RATE_LIMIT_HIT",
                actor="anonymous",
                ip_address=client_ip,
                details=jail_reason or f"Rate limit 100 req exceeded on {path}",
                severity="WARNING"
            )
            if self.is_html_client():
                cooldown_html = self._render_429_page(client_ip, retry_after)
                self.send_html_response(cooldown_html, status=429, extra_headers={"Retry-After": str(retry_after)})
            else:
                self.send_json(
                    {
                        "error": "Bạn bấm quá nhanh, vui lòng thử lại sau.",
                        "reason": jail_reason,
                        "retry_after_seconds": retry_after,
                        "client_ip": client_ip,
                        "limit": 100
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
    """
    Máy chủ HTTP đa luồng tích hợp khiên chắn Anti-DoS & Anti-Slowloris:
    - Kiểm soát số lượng kết nối đồng thời theo IP (L4/L7 Concurrency Shield)
    - Giới hạn tải toàn hệ thống tránh cạn kiệt luồng và bộ nhớ RAM
    - Strict Socket Timeout (5.0s) triệt tiêu tấn công Slowloris và Slow POST
    """
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, server_address, RequestHandlerClass, base_dir=None):
        self.base_dir = base_dir
        super().__init__(server_address, RequestHandlerClass)

    def verify_request(self, request, client_address):
        """
        Tầng L4/L7 Connection Shield: Kiểm tra giới hạn kết nối đồng thời trước khi sinh luồng (Thread).
        Từ chối và đóng socket ngay lập tức nếu IP hoặc server chạm ngưỡng giới hạn.
        """
        client_ip = client_address[0]
        try:
            # Thiết lập strict socket timeout chống Slowloris / Slow POST
            request.settimeout(dos_manager.socket_timeout)
        except Exception:
            pass

        allowed, reason = dos_manager.register_connection(client_ip)
        if not allowed:
            try:
                # Gửi nhanh phản hồi HTTP 503 trước khi ngắt kết nối
                resp = (
                    b"HTTP/1.1 503 Service Unavailable\r\n"
                    b"Content-Type: application/json; charset=utf-8\r\n"
                    b"Connection: close\r\n"
                    b"Retry-After: 5\r\n\r\n"
                    b'{"error":"Server overloaded or connection limit reached (Anti-DoS Protection).","status":503}\r\n'
                )
                request.sendall(resp)
            except Exception:
                pass
            return False

        return True

    def process_request_thread(self, request, client_address):
        """Xử lý yêu cầu trong luồng riêng biệt và giải phóng kết nối trong khối finally."""
        try:
            self.finish_request(request, client_address)
        except Exception:
            self.handle_error(request, client_address)
        finally:
            self.shutdown_request(request)
            dos_manager.release_connection(client_address[0])

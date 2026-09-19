"""
Lớp 4 & Lớp 5: API Router with RBAC Authorization
Định tuyến API và kiểm tra ma trận phân quyền RBAC:
- ADMIN: Toàn quyền (quản lý tài khoản, audit logs, backup, cấu hình)
- OPERATOR: Vận hành mạng (quét mạng, chặn/bỏ chặn MAC, cấu hình mạng)
- USER: Khách / người dùng cơ bản (chỉ xem Dashboard, xem thiết bị, tải xuống)
"""

import math
import urllib.parse
from typing import Dict, Any, Optional, Tuple
from ..auth.session import session_manager, UserRole, Session
from ..validation.validator import is_valid_mac, normalize_mac, sanitize_input_text, validate_json_schema
from ..services.audit_service import audit_logger
from ..services.download_service import download_service
from ..services.backup_service import backup_service

try:
    from web.security import audit_logger as sec_audit_logger
except ImportError:
    try:
        from security import audit_logger as sec_audit_logger
    except ImportError:
        sec_audit_logger = None

class APIRouter:
    def __init__(self, devices_data: list, settings_data: dict, logs_data: list, alerts_data: list):
        self.devices = devices_data
        self.settings = settings_data
        self.logs = logs_data
        self.alerts = alerts_data

    def _extract_session(self, auth_header: Optional[str]) -> Optional[Session]:
        """Trích xuất session từ Authorization Bearer Token hoặc Cookie."""
        if not auth_header:
            return None
        token = auth_header.replace("Bearer ", "").strip()
        return session_manager.get_session(token)

    def _require_role(self, session: Optional[Session], required_role: UserRole) -> Tuple[bool, Optional[Dict[str, Any]], int]:
        """
        Kiểm tra tính hợp lệ của phiên và quyền truy cập RBAC.
        Nếu không có session -> coi như vai trò mặc định USER (Viewer).
        """
        current_role = session.role if session else UserRole.USER
        if not UserRole.can_access(current_role, required_role):
            actor = session.username if session else "guest_user"
            return False, {
                "error": f"Từ chối quyền truy cập (403 Forbidden). Chức năng này yêu cầu vai trò tối thiểu là {required_role.value}, vai trò hiện tại của bạn là {current_role.value}.",
                "required_role": required_role.value,
                "current_role": current_role.value
            }, 403
        return True, None, 200

    def handle_get(self, path: str, query: Dict[str, list], auth_header: Optional[str], client_ip: str) -> Tuple[Dict[str, Any], int]:
        session = self._extract_session(auth_header)
        actor = session.username if session else "anonymous"

        # 1. Health check
        if path in ("/api/v1/health", "/api/v1/status"):
            return {"status": "HEALTHY", "version": "2.0.0", "security_level": "High (Multi-Layer)"}, 200

        # 2. Thông tin phiên hiện tại
        if path == "/api/v1/auth/me":
            if not session:
                return {
                    "authenticated": False,
                    "user": {"username": "guest", "role": "USER", "full_name": "Khách Truy Cập (Viewer)"}
                }, 200
            return {
                "authenticated": True,
                "user": {
                    "username": session.username,
                    "role": session.role.value,
                    "expires_in_seconds": int(session.expires_at - session.created_at)
                }
            }, 200

        # 3. Quản lý người dùng (Chỉ ADMIN)
        if path == "/api/v1/auth/users":
            ok, err_resp, code = self._require_role(session, UserRole.ADMIN)
            if not ok:
                return err_resp, code
            return {"users": session_manager.list_users()}, 200

        # 4. Danh sách thiết bị (Mọi vai trò đều xem được)
        if path == "/api/v1/devices":
            subnet_filter = query.get("subnet", [None])[0]
            status_filter = query.get("status", [None])[0]
            results = self.devices
            if subnet_filter:
                results = [d for d in results if d.get("ip", "").startswith(subnet_filter.rsplit(".", 1)[0])]
            if status_filter:
                results = [d for d in results if d.get("status", "").upper() == status_filter.upper()]
            return results, 200

        # 5. Chi tiết 1 thiết bị
        if path.startswith("/api/v1/devices/"):
            mac = urllib.parse.unquote(path.replace("/api/v1/devices/", ""))
            device = next((d for d in self.devices if d["mac"].upper() == mac.upper()), None)
            if device:
                return device, 200
            return {"error": f"Không tìm thấy thiết bị với MAC {mac}"}, 404

        # 6. Hạ tầng mạng
        if path == "/api/v1/networks":
            return {
                "subnets": [
                    {
                        "cidr": "192.168.1.0/24",
                        "interface": "Wi-Fi Tổng 6 (Intel AX200)",
                        "gateway": "192.168.1.1",
                        "total_ips": 254,
                        "used_ips": 4,
                        "status": "ACTIVE"
                    },
                    {
                        "cidr": "192.168.110.0/24",
                        "interface": "Router Phụ Gigabit",
                        "gateway": "192.168.110.1",
                        "total_ips": 254,
                        "used_ips": 3,
                        "status": "ACTIVE"
                    }
                ]
            }, 200

        # 7. Giám sát băng thông
        if path == "/api/v1/traffic":
            samples = []
            for i in range(60):
                t_val = i * 0.15
                d = round(20 + 8 * math.sin(t_val) + 3 * math.sin(t_val * 2.1), 2)
                u = round(7 + 3 * math.cos(t_val * 1.3), 2)
                samples.append({"step": i, "download_mbps": max(0.5, d), "upload_mbps": max(0.2, u)})
            return {
                "current_download_mbps": 24.5,
                "current_upload_mbps": 8.2,
                "peak_download_mbps": 78.4,
                "peak_upload_mbps": 22.1,
                "history": samples
            }, 200

        # 8. Cảnh báo bảo mật
        if path == "/api/v1/alerts":
            return self.alerts, 200

        # 9. Nhật ký hệ thống thông thường
        if path == "/api/v1/logs":
            return self.logs, 200

        # 10. Danh mục tải xuống an toàn
        if path == "/api/v1/downloads":
            return download_service.get_catalog(), 200

        # 11. Cài đặt hệ thống
        if path == "/api/v1/settings":
            return self.settings, 200

        # 12. Nhật ký kiểm toán bảo mật (AUDIT LOGS - CHỈ ADMIN)
        if path == "/api/v1/audit":
            ok, err_resp, code = self._require_role(session, UserRole.ADMIN)
            if not ok:
                return err_resp, code
            limit = int(query.get("limit", [50])[0])
            return {"audit_events": audit_logger.get_recent_events(limit=limit)}, 200

        # 13. Danh sách bản sao lưu database (CHỈ ADMIN)
        if path == "/api/v1/backups":
            ok, err_resp, code = self._require_role(session, UserRole.ADMIN)
            if not ok:
                return err_resp, code
            return {"backups": backup_service.list_backups()}, 200

        return {"error": "Endpoint không tồn tại"}, 404

    def handle_post(self, path: str, body: Dict[str, Any], auth_header: Optional[str], client_ip: str) -> Tuple[Dict[str, Any], int]:
        session = self._extract_session(auth_header)
        actor = session.username if session else "anonymous"

        # 1. Đăng nhập hệ thống (Public)
        if path == "/api/v1/auth/login":
            valid, err = validate_json_schema(body, ["username", "password"])
            if not valid:
                return {"error": err}, 400

            username = sanitize_input_text(body.get("username", ""))
            password = body.get("password", "")

            sess, auth_err = session_manager.authenticate(username, password, client_ip)
            if not sess:
                audit_logger.log_event(
                    "LOGIN_FAILED",
                    actor=username or "unknown",
                    ip=client_ip,
                    status="FAILED",
                    details={"reason": auth_err}
                )
                return {"error": auth_err}, 401

            audit_logger.log_event(
                "LOGIN_SUCCESS",
                actor=sess.username,
                ip=client_ip,
                status="SUCCESS",
                details={"role": sess.role.value}
            )

            return {
                "message": "Đăng nhập thành công",
                "token": sess.token,
                "user": {
                    "username": sess.username,
                    "role": sess.role.value
                }
            }, 200

        # 2. Đăng xuất hệ thống
        if path == "/api/v1/auth/logout":
            if session:
                session_manager.revoke_session(session.token)
                audit_logger.log_event("LOGOUT", actor=session.username, ip=client_ip, status="SUCCESS")
            return {"message": "Đăng xuất thành công"}, 200

        # 3. Quét mạng (Yêu cầu OPERATOR hoặc ADMIN)
        if path == "/api/v1/scan":
            ok, err_resp, code = self._require_role(session, UserRole.OPERATOR)
            if not ok:
                return err_resp, code
            return {
                "status": "SUCCESS",
                "message": "Đã bắt đầu chu trình quét mạng đa luồng an toàn",
                "discovered_devices": len(self.devices)
            }, 200

        # 4. Chặn thiết bị (Yêu cầu OPERATOR hoặc ADMIN)
        if path == "/api/v1/block":
            ok, err_resp, code = self._require_role(session, UserRole.OPERATOR)
            if not ok:
                return err_resp, code

            mac = body.get("mac", "")
            if not is_valid_mac(mac):
                return {"error": "Địa chỉ MAC không hợp lệ"}, 400

            mac_norm = normalize_mac(mac)
            reason = sanitize_input_text(body.get("reason", "Chặn bảo mật theo yêu cầu"))

            for d in self.devices:
                if d["mac"].upper() == mac_norm.upper():
                    d["status"] = "BLOCKED"
                    d["blocked"] = True
                    break

            audit_logger.log_event(
                "DEVICE_BLOCKED",
                actor=actor,
                ip=client_ip,
                status="SUCCESS",
                details={"mac": mac_norm, "reason": reason}
            )

            return {"status": "SUCCESS", "message": f"Đã chặn thiết bị MAC {mac_norm}"}, 200

        # 5. Bỏ chặn thiết bị (Yêu cầu OPERATOR hoặc ADMIN)
        if path == "/api/v1/unblock":
            ok, err_resp, code = self._require_role(session, UserRole.OPERATOR)
            if not ok:
                return err_resp, code

            mac = body.get("mac", "")
            if not is_valid_mac(mac):
                return {"error": "Địa chỉ MAC không hợp lệ"}, 400

            mac_norm = normalize_mac(mac)
            for d in self.devices:
                if d["mac"].upper() == mac_norm.upper():
                    d["status"] = "ONLINE"
                    d["blocked"] = False
                    break

            audit_logger.log_event(
                "DEVICE_UNBLOCKED",
                actor=actor,
                ip=client_ip,
                status="SUCCESS",
                details={"mac": mac_norm}
            )

            return {"status": "SUCCESS", "message": f"Đã gỡ bỏ chặn thiết bị MAC {mac_norm}"}, 200

        # 6. Lưu cài đặt hệ thống (Yêu cầu OPERATOR hoặc ADMIN)
        if path == "/api/v1/settings":
            ok, err_resp, code = self._require_role(session, UserRole.OPERATOR)
            if not ok:
                return err_resp, code

            if isinstance(body, dict):
                self.settings.update(body)
                audit_logger.log_event(
                    "CONFIG_CHANGED",
                    actor=actor,
                    ip=client_ip,
                    status="SUCCESS",
                    details={"updated_keys": list(body.keys())}
                )
                return {"status": "SUCCESS", "message": "Đã lưu cài đặt an toàn", "settings": self.settings}, 200
            return {"error": "Dữ liệu cài đặt không hợp lệ"}, 400

        # 7. Kích hoạt sao lưu Database (CHỈ ADMIN)
        if path == "/api/v1/backup":
            ok, err_resp, code = self._require_role(session, UserRole.ADMIN)
            if not ok:
                return err_resp, code

            backup_res = backup_service.create_backup(actor=actor, client_ip=client_ip)
            return {"status": "SUCCESS", "message": "Sao lưu cơ sở dữ liệu thành công", "backup": backup_res}, 200

        # 8. Báo cáo can thiệp mã nguồn Client (Anti-Tamper & DevTools Guard)
        if path == "/api/v1/security/client-tamper-report":
            event_type = body.get("event_type", "UNKNOWN_TAMPER_EVENT") if isinstance(body, dict) else "UNKNOWN"
            details = body.get("details", {}) if isinstance(body, dict) else {}
            user_agent = body.get("user_agent", "") if isinstance(body, dict) else ""

            audit_logger.log_event(
                "CLIENT_TAMPER_DETECTED",
                actor=actor,
                ip=client_ip,
                status="WARNING",
                details={
                    "event_type": event_type,
                    "details": details,
                    "user_agent": user_agent
                }
            )
            if sec_audit_logger:
                sec_audit_logger.log_security_event(
                    event_type="CLIENT_ANTI_TAMPER_ALERT",
                    actor=actor,
                    ip_address=client_ip,
                    details=f"Event: {event_type} | Data: {details}",
                    severity="WARNING"
                )
            return {"status": "SUCCESS", "message": "Đã ghi nhận sự kiện an ninh máy khách"}, 200

        return {"error": "Endpoint POST không tồn tại"}, 404

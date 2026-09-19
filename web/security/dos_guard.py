"""
Hệ Thống Phòng Chống Tấn Công Từ Chối Dịch Vụ Đa Tầng (Anti-DoS & Anti-DDoS Guard)
web/security/dos_guard.py

Triển khai 4 lớp phòng thủ chuyên sâu:
1. L4/L7 Connection Shield: Giới hạn số lượng socket đồng thời theo IP và toàn hệ thống.
2. Slowloris Mitigation: Strict socket timeout và giám sát tốc độ truyền dữ liệu.
3. Micro-burst Throttler: Ngăn chặn dồn dập gói tin trong khung thời gian 1-3 giây.
4. Adaptive Under-Attack Mode & Cryptographic Proof-of-Work (PoW) Shield:
   Tự động phát hiện botnet phân tán khi RPS toàn hệ thống vượt ngưỡng và yêu cầu giải thử thách băm SHA-256.
"""

import time
import hashlib
import hmac
import secrets
import threading
from typing import Dict, List, Tuple, Optional, Any

class DoSProtectionManager:
    """Quản lý và điều phối các tầng phòng thủ chống tấn công từ chối dịch vụ (DoS/DDoS)."""

    def __init__(
        self,
        max_conns_per_ip: int = 15,
        max_global_conns: int = 128,
        socket_timeout: float = 5.0,
        microburst_window_seconds: float = 2.0,
        microburst_limit: int = 25,
        under_attack_threshold_rps: float = 60.0,
        under_attack_cooldown_seconds: float = 30.0,
        pow_difficulty: int = 4
    ):
        self.max_conns_per_ip = max_conns_per_ip
        self.max_global_conns = max_global_conns
        self.socket_timeout = socket_timeout
        self.microburst_window = microburst_window_seconds
        self.microburst_limit = microburst_limit
        self.under_attack_threshold_rps = under_attack_threshold_rps
        self.under_attack_cooldown = under_attack_cooldown_seconds
        self.pow_difficulty = pow_difficulty

        self._lock = threading.Lock()
        self._secret_key = secrets.token_bytes(32)

        # IP -> Số lượng kết nối socket TCP đang mở
        self._active_connections_by_ip: Dict[str, int] = {}
        self._total_active_connections: int = 0

        # IP -> List[timestamps] cho Micro-burst
        self._burst_logs: Dict[str, List[float]] = {}

        # Global Request Timestamps để đo RPS toàn hệ thống
        self._global_request_timestamps: List[float] = []
        self._under_attack_until: float = 0.0

        # Danh sách IP bị Blackhole khẩn cấp do DoS
        self._blackholed_ips: Dict[str, float] = {}

    # -------------------------------------------------------------------------
    # 1. Tầng Quản Lý Kết Nối L4/L7 (Connection & Slowloris Guard)
    # -------------------------------------------------------------------------
    def register_connection(self, client_ip: str) -> Tuple[bool, str]:
        """
        Ghi nhận một kết nối TCP mới.
        Từ chối ngay lập tức nếu IP hoặc toàn hệ thống chạm ngưỡng giới hạn socket.
        """
        now = time.time()
        with self._lock:
            # Kiểm tra xem IP có đang bị Blackhole hay không
            if client_ip in self._blackholed_ips:
                exp = self._blackholed_ips[client_ip]
                if now < exp:
                    return False, f"IP bị khóa Blackhole chống DoS ({int(exp - now)}s còn lại)"
                else:
                    del self._blackholed_ips[client_ip]

            # Bỏ qua giới hạn socket cho Loopback nội bộ
            if client_ip in ("127.0.0.1", "::1", "localhost"):
                self._total_active_connections += 1
                return True, "OK"

            # 1. Giới hạn tổng kết nối toàn server
            if self._total_active_connections >= self.max_global_conns:
                return False, "GLOBAL_CONCURRENCY_EXHAUSTED"

            # 2. Giới hạn kết nối đồng thời trên mỗi IP
            current_ip_conns = self._active_connections_by_ip.get(client_ip, 0)
            if current_ip_conns >= self.max_conns_per_ip:
                return False, "IP_CONCURRENCY_LIMIT_EXCEEDED"

            self._active_connections_by_ip[client_ip] = current_ip_conns + 1
            self._total_active_connections += 1
            return True, "OK"

    def release_connection(self, client_ip: str):
        """Giải phóng kết nối khi socket đóng hoặc yêu cầu hoàn thành."""
        with self._lock:
            if client_ip in ("127.0.0.1", "::1", "localhost"):
                self._total_active_connections = max(0, self._total_active_connections - 1)
                return

            if client_ip in self._active_connections_by_ip:
                conns = self._active_connections_by_ip[client_ip] - 1
                if conns <= 0:
                    del self._active_connections_by_ip[client_ip]
                else:
                    self._active_connections_by_ip[client_ip] = conns

            self._total_active_connections = max(0, self._total_active_connections - 1)

    # -------------------------------------------------------------------------
    # 2. Tầng Phòng Thủ Micro-burst & Đo Lường Lưu Lượng Toàn Hệ Thống
    # -------------------------------------------------------------------------
    def check_request(self, client_ip: str, endpoint: str = "") -> Tuple[bool, int, Optional[str]]:
        """
        Kiểm tra yêu cầu trước khi xử lý:
        - Đo lường RPS toàn cục và kích hoạt Under-Attack Mode nếu cần
        - Kiểm tra Micro-burst theo IP
        Trả về: (is_allowed, status_code, error_message)
        """
        now = time.time()

        with self._lock:
            # 1. Cập nhật cửa sổ đo RPS toàn cục (1 giây qua)
            self._global_request_timestamps = [t for t in self._global_request_timestamps if now - t <= 1.0]
            self._global_request_timestamps.append(now)
            current_rps = len(self._global_request_timestamps)

            # Tự động kích hoạt chế độ "Under Attack Mode" nếu RPS vượt ngưỡng
            if current_rps >= self.under_attack_threshold_rps:
                self._under_attack_until = max(self._under_attack_until, now + self.under_attack_cooldown)

            # 2. Kiểm tra Micro-burst theo IP (ví dụ > 25 req trong 2 giây)
            window_start = now - self.microburst_window
            ip_logs = [t for t in self._burst_logs.get(client_ip, []) if t > window_start]

            # Xác định hạn mức: nếu đang trong trạng thái Under Attack -> siết chặt hạn mức
            effective_limit = self.microburst_limit
            if self._under_attack_until > now and client_ip not in ("127.0.0.1", "::1", "localhost"):
                effective_limit = max(5, self.microburst_limit // 3)

            if len(ip_logs) >= effective_limit and client_ip not in ("127.0.0.1", "::1", "localhost"):
                # Ghi nhận vi phạm burst -> đưa vào Blackhole tạm thời 60 giây
                self._blackholed_ips[client_ip] = now + 60.0
                return False, 429, f"Phát hiện tấn công Micro-burst DoS ({len(ip_logs)} req/{self.microburst_window}s). IP bị tạm ngắt."

            ip_logs.append(now)
            self._burst_logs[client_ip] = ip_logs

            return True, 200, None

    # -------------------------------------------------------------------------
    # 3. Tầng Under-Attack Mode & Cryptographic Proof-of-Work (PoW) Shield
    # -------------------------------------------------------------------------
    def is_under_attack_mode(self) -> bool:
        """Kiểm tra xem hệ thống có đang ở trạng thái Under Attack hay không."""
        with self._lock:
            return time.time() < self._under_attack_until

    def trigger_under_attack_mode(self, duration_seconds: float = 30.0):
        """Kích hoạt thủ công hoặc khẩn cấp chế độ Under Attack."""
        with self._lock:
            self._under_attack_until = time.time() + duration_seconds

    def generate_pow_challenge(self, client_ip: str) -> Dict[str, Any]:
        """
        Sinh thử thách Proof-of-Work (PoW) yêu cầu máy trạm tính toán hàm băm SHA-256.
        Dùng để chặn botnet phân tán tiêu thụ CPU máy chủ.
        """
        timestamp = int(time.time())
        nonce = secrets.token_hex(8)
        raw_signature = f"{client_ip}:{timestamp}:{nonce}".encode("utf-8")
        token = hmac.new(self._secret_key, raw_signature, hashlib.sha256).hexdigest()

        return {
            "algorithm": "SHA-256",
            "difficulty": self.pow_difficulty,
            "prefix": "0" * self.pow_difficulty,
            "challenge": f"{nonce}:{timestamp}",
            "token": token,
            "client_ip": client_ip,
            "instructions": f"Find proof string S such that sha256('{nonce}:{timestamp}:' + S) starts with {'0' * self.pow_difficulty}"
        }

    def verify_pow_solution(self, client_ip: str, challenge: str, token: str, proof: str) -> bool:
        """Xác thực lời giải bài toán Proof-of-Work từ client."""
        try:
            parts = challenge.split(":")
            if len(parts) != 2:
                return False
            nonce, ts_str = parts
            timestamp = int(ts_str)

            # Thử thách chỉ hợp lệ trong vòng 90 giây
            if abs(time.time() - timestamp) > 90.0:
                return False

            # Kiểm tra chữ ký HMAC tính toàn vẹn của thử thách
            expected_raw = f"{client_ip}:{timestamp}:{nonce}".encode("utf-8")
            expected_token = hmac.new(self._secret_key, expected_raw, hashlib.sha256).hexdigest()
            if not hmac.compare_digest(token, expected_token):
                return False

            # Kiểm tra kết quả băm
            candidate = f"{challenge}:{proof}".encode("utf-8")
            h = hashlib.sha256(candidate).hexdigest()
            required_prefix = "0" * self.pow_difficulty
            return h.startswith(required_prefix)
        except Exception:
            return False

    # -------------------------------------------------------------------------
    # 4. Quản Lý & Chẩn Đoán Trạng Thái
    # -------------------------------------------------------------------------
    def blackhole_ip(self, client_ip: str, duration_seconds: float = 300.0):
        """Đưa trực tiếp một IP vào danh sách cô lập hoàn toàn (Blackhole)."""
        if client_ip in ("127.0.0.1", "::1", "localhost"):
            return
        with self._lock:
            self._blackholed_ips[client_ip] = time.time() + duration_seconds

    def unblackhole_ip(self, client_ip: str):
        """Gỡ bỏ IP khỏi danh sách Blackhole."""
        with self._lock:
            self._blackholed_ips.pop(client_ip, None)

    def reset(self):
        """Khởi tạo lại toàn bộ bộ nhớ giám sát DoS."""
        with self._lock:
            self._active_connections_by_ip.clear()
            self._total_active_connections = 0
            self._burst_logs.clear()
            self._global_request_timestamps.clear()
            self._under_attack_until = 0.0
            self._blackholed_ips.clear()

    def get_metrics(self) -> Dict[str, Any]:
        """Lấy các chỉ số giám sát DoS thời gian thực."""
        now = time.time()
        with self._lock:
            recent_rps = len([t for t in self._global_request_timestamps if now - t <= 1.0])
            active_blackholes = {ip: max(0, int(t - now)) for ip, t in self._blackholed_ips.items() if t > now}
            return {
                "total_active_connections": self._total_active_connections,
                "current_rps": recent_rps,
                "under_attack_mode": now < self._under_attack_until,
                "under_attack_remaining_seconds": max(0, int(self._under_attack_until - now)),
                "blackholed_ips_count": len(active_blackholes),
                "blackholed_ips": active_blackholes,
                "active_ips_count": len(self._active_connections_by_ip)
            }

# Khởi tạo singleton DoS Protection Manager
dos_manager = DoSProtectionManager()

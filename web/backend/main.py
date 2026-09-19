"""
Network Manager - Multi-Layer Secure Web & REST API Server Launcher.
Điểm khởi chạy tinh gọn của máy chủ bảo mật đa lớp.
"""

import os
import sys

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.dirname(CURRENT_DIR)
if WEB_DIR not in sys.path:
    sys.path.insert(0, WEB_DIR)

from backend.server import MultiLayerSecureHandler, ThreadedHTTPServer

PORT = int(os.environ.get("PORT", 8080))
BASE_DIR = WEB_DIR

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

    with ThreadedHTTPServer(("", port), MultiLayerSecureHandler, base_dir=BASE_DIR) as httpd:
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

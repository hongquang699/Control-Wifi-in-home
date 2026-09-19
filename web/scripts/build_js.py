"""
Trình ghép nối JavaScript tự động (JS Module Bundler).
Tập hợp các module độc lập từ web/js/modules/ thành web/js/app.js hoàn chỉnh.
"""

import os
import sys

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS_DIR = os.path.join(BASE_DIR, "js")
MODULES_DIR = os.path.join(JS_DIR, "modules")
OUTPUT_FILE = os.path.join(JS_DIR, "app.js")

MODULE_ORDER = [
    "anti_tamper.js",
    "i18n.js",
    "router.js",
    "demo_dashboard.js",
    "demo_devices.js",
    "demo_networks.js",
    "demo_alerts.js",
    "demo_logs.js",
    "demo_settings.js",
    "demo_live.js",
    "demo_traffic.js",
    "pages_extra.js",
    "toast.js",
    "auth.js"
]

def build_app_js():
    print("[*] Đang ghép nối các module JavaScript...")
    chunks = []
    
    for mod_name in MODULE_ORDER:
        mod_path = os.path.join(MODULES_DIR, mod_name)
        if os.path.exists(mod_path):
            with open(mod_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            chunks.append(f"// ===== MODULE: {mod_name} =====\n{content}")
        else:
            print(f"[!] Cảnh báo: Không tìm thấy module {mod_name}")

    header = "/**\n * Network Manager - Web Application Client Bundle\n * Tự động tạo từ các module độc lập trong web/js/modules/\n */\n\n"
    bundle_code = header + "\n\n".join(chunks) + "\n"

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(bundle_code)

    print(f"[✓] Ghép nối JS thành công! Tệp đích: {OUTPUT_FILE} ({len(bundle_code)} bytes)")

if __name__ == "__main__":
    build_app_js()

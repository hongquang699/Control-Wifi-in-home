"""
Trình ghép nối HTML tự động (SPA Shell Builder).
Tạo web/html/index.html tinh gọn và đảm bảo các component độc lập trong web/html/components/ sẵn sàng.
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
HTML_DIR = os.path.join(BASE_DIR, "html")
COMPONENTS_DIR = os.path.join(HTML_DIR, "components")
DEMO_DIR = os.path.join(COMPONENTS_DIR, "demo")
OUTPUT_FILE = os.path.join(HTML_DIR, "index.html")

def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

def build_index_html():
    print("[*] Đang xây dựng SPA index.html tinh gọn từ các component...")
    
    # 1. Đảm bảo dashboard.html có đầy đủ 8 tab demo
    dashboard_path = os.path.join(COMPONENTS_DIR, "dashboard.html")
    if os.path.exists(dashboard_path):
        dashboard_content = read_file(dashboard_path)
        demo_tabs = [
            ("<!-- include: demo/tab_overview.html -->", os.path.join(DEMO_DIR, "tab_overview.html")),
            ("<!-- include: demo/tab_devices.html -->", os.path.join(DEMO_DIR, "tab_devices.html")),
            ("<!-- include: demo/tab_networks.html -->", os.path.join(DEMO_DIR, "tab_networks.html")),
            ("<!-- include: demo/tab_traffic.html -->", os.path.join(DEMO_DIR, "tab_traffic.html")),
            ("<!-- include: demo/tab_alerts.html -->", os.path.join(DEMO_DIR, "tab_alerts.html")),
            ("<!-- include: demo/tab_logs.html -->", os.path.join(DEMO_DIR, "tab_logs.html")),
            ("<!-- include: demo/tab_settings.html -->", os.path.join(DEMO_DIR, "tab_settings.html")),
            ("<!-- include: demo/tab_audit.html -->", os.path.join(DEMO_DIR, "tab_audit.html")),
        ]
        has_changes = False
        for placeholder, tab_path in demo_tabs:
            if placeholder in dashboard_content and os.path.exists(tab_path):
                tab_code = read_file(tab_path)
                dashboard_content = dashboard_content.replace(placeholder, tab_code)
                has_changes = True
        if has_changes:
            with open(dashboard_path, "w", encoding="utf-8") as f:
                f.write(dashboard_content)
            print(f"[✓] Đã đồng bộ các tab demo vào {dashboard_path}")

    # 2. Đọc các khung thành phần chính của SPA
    head_part = read_file(os.path.join(COMPONENTS_DIR, "head.html"))
    navbar_part = read_file(os.path.join(COMPONENTS_DIR, "navbar.html"))
    modals_part = read_file(os.path.join(COMPONENTS_DIR, "modals.html"))
    footer_part = read_file(os.path.join(COMPONENTS_DIR, "footer.html"))

    # 3. Ghép nối SPA container tinh gọn
    spa_html = f"""{head_part}
<body class="bg-[#0b0f19] text-slate-100 font-sans flex flex-col min-h-screen relative overflow-x-hidden selection:bg-sky-500 selection:text-white pb-16 xl:pb-0">

  <!-- Ambient Light Glows -->
  <div class="ambient-glow-1"></div>
  <div class="ambient-glow-2"></div>

  <!-- STICKY HEADER & NAVBAR -->
  {navbar_part}

  <!-- MAIN SPA CONTENT CONTAINER (Nạp động trang theo Hash Router) -->
  <main class="flex-1 relative">
    <!-- Page Loading Spinner -->
    <div id="pageLoader" class="hidden py-32 flex flex-col items-center justify-center">
      <div class="w-10 h-10 border-4 border-sky-400/30 border-t-sky-400 rounded-full animate-spin"></div>
      <p class="mt-4 text-xs font-mono text-slate-400 tracking-wider uppercase">Đang tải trang...</p>
    </div>

    <!-- Active Component Views Injected Dynamically -->
    <div id="pageContainer"></div>
  </main>

  <!-- STICKY MOBILE CTA ACTION BAR -->
  <aside aria-label="Mobile Action Bar" class="fixed bottom-0 inset-x-0 z-40 xl:hidden bg-[#0d1322]/95 backdrop-blur-xl border-t border-white/10 p-3 flex items-center justify-between gap-3 shadow-2xl">
    <a href="#/download" class="flex-1 py-2.5 rounded-xl bg-sky-500 text-white text-xs font-bold text-center shadow-lg shadow-sky-500/25 flex items-center justify-center gap-1.5">
      <i class="fi fi-rr-download"></i> Tải xuống v2.0
    </a>
    <a href="#/dashboard" class="flex-1 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-slate-200 text-xs font-semibold text-center flex items-center justify-center gap-1.5">
      <i class="fi fi-rr-play-alt"></i> Thử Demo Live
    </a>
  </aside>

  <!-- GLOBAL MODALS -->
  {modals_part}

  <!-- FOOTER -->
  {footer_part}

  <!-- Toast Notification Container -->
  <div id="toastContainer" class="fixed bottom-6 right-6 z-50 flex flex-col gap-2 pointer-events-none"></div>

  <!-- Scripts -->
  <script src="/js/app.js"></script>
</body>
</html>
"""

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(spa_html)

    lines_count = len(spa_html.splitlines())
    print(f"[✓] Tạo index.html tinh gọn thành công! Tệp đích: {OUTPUT_FILE} ({lines_count} dòng, {len(spa_html)} bytes)")

if __name__ == "__main__":
    build_index_html()

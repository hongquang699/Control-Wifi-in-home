"""
Trình ghép nối HTML tự động (Component Assembler).
Ghép các component nhỏ độc lập trong web/html/components/ thành web/html/index.html hoàn chỉnh.
"""

import os
import re
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
    print("[*] Đang ghép nối các thành phần HTML...")
    
    # 1. Header & Head
    head_part = read_file(os.path.join(COMPONENTS_DIR, "head.html"))
    navbar_part = read_file(os.path.join(COMPONENTS_DIR, "navbar.html"))

    # 2. Main Pages
    home_part = read_file(os.path.join(COMPONENTS_DIR, "home.html"))
    about_part = read_file(os.path.join(COMPONENTS_DIR, "about.html"))
    features_part = read_file(os.path.join(COMPONENTS_DIR, "features.html"))

    # 3. Dashboard Demo and Tabs
    dashboard_shell = read_file(os.path.join(COMPONENTS_DIR, "dashboard.html"))
    
    # Substitute or insert demo tabs into dashboard
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
    
    dashboard_full = dashboard_shell
    for placeholder, tab_path in demo_tabs:
        if os.path.exists(tab_path):
            tab_content = read_file(tab_path)
            dashboard_full = dashboard_full.replace(placeholder, tab_content)

    # 4. Remaining Pages & Modals & Footer
    modals_part = read_file(os.path.join(COMPONENTS_DIR, "modals.html"))
    download_part = read_file(os.path.join(COMPONENTS_DIR, "download.html"))
    docs_part = read_file(os.path.join(COMPONENTS_DIR, "docs.html"))
    news_part = read_file(os.path.join(COMPONENTS_DIR, "news.html"))
    contact_part = read_file(os.path.join(COMPONENTS_DIR, "contact.html"))
    footer_part = read_file(os.path.join(COMPONENTS_DIR, "footer.html"))

    # Assemble everything
    full_html = f"""{head_part}
<body class="bg-[#0b0f19] text-slate-100 font-sans flex flex-col min-h-screen relative overflow-x-hidden selection:bg-sky-500 selection:text-white pb-16 xl:pb-0">

  <!-- Ambient Light Glows -->
  <div class="ambient-glow-1"></div>
  <div class="ambient-glow-2"></div>

  <!-- STICKY HEADER & NAVBAR -->
  {navbar_part}

  <!-- MAIN CONTENT PAGES -->
  <main class="flex-1">
    <!-- PAGE 1: HOME -->
    {home_part}

    <!-- PAGE 2: ABOUT -->
    {about_part}

    <!-- PAGE 3: FEATURES -->
    {features_part}

    <!-- PAGE 4: DASHBOARD DEMO -->
    {dashboard_full}

    <!-- MODALS -->
    {modals_part}

    <!-- PAGE 5: DOWNLOAD -->
    {download_part}

    <!-- PAGE 6: DOCS -->
    {docs_part}

    <!-- PAGE 7: NEWS -->
    {news_part}

    <!-- PAGE 8: CONTACT -->
    {contact_part}
  </main>

  <!-- FOOTER -->
  {footer_part}

  <!-- Toast Notification Container -->
  <div id="toastContainer" class="fixed bottom-6 right-6 z-50 flex flex-col gap-2 pointer-events-none"></div>

  <!-- Scripts -->
  <script src="../js/app.js"></script>
</body>
</html>
"""

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(full_html)

    print(f"[✓] Ghép nối thành công! Tệp đích: {OUTPUT_FILE} ({len(full_html)} bytes)")

if __name__ == "__main__":
    build_index_html()

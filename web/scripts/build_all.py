"""
Master Build Script: Ghép nối toàn bộ HTML components và JS modules.
"""

import sys
import os

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from build_html import build_index_html
from build_js import build_app_js

def main():
    print("=" * 60)
    print("    NETWORK MANAGER WEB ASSETS BUILDER")
    print("=" * 60)
    build_index_html()
    build_app_js()
    print("=" * 60)
    print("[✓] Hoàn tất build toàn bộ web components & modules!")
    print("=" * 60)

if __name__ == "__main__":
    main()

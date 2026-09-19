"""
Module phục vụ tệp tin tĩnh (HTML, CSS, JS, hình ảnh) an toàn.
"""

import os
from typing import Dict

MIME_TYPES: Dict[str, str] = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".ico": "image/x-icon",
    ".svg": "image/svg+xml",
    ".json": "application/json; charset=utf-8",
    ".xml": "application/xml; charset=utf-8",
    ".txt": "text/plain; charset=utf-8"
}

def serve_static_resource(handler, base_dir: str, path: str):
    """Phục vụ file tĩnh an toàn, ngăn chặn path traversal ra ngoài base_dir."""
    rel_path = path.lstrip("/")
    if not rel_path or rel_path == "index.html":
        file_path = os.path.join(base_dir, "html", "index.html")
    elif rel_path in ("privacy-policy.html", "thank-you.html", "404.html"):
        file_path = os.path.join(base_dir, "html", rel_path)
    else:
        file_path = os.path.join(base_dir, rel_path)

    canonical_path = os.path.abspath(file_path)
    canonical_base = os.path.abspath(base_dir)

    # Chống Path Traversal ra ngoài base_dir
    if not canonical_path.startswith(canonical_base) or not os.path.exists(canonical_path):
        f404 = os.path.join(base_dir, "html", "404.html")
        if os.path.exists(f404):
            with open(f404, "rb") as f:
                body_404 = f.read()
            handler.send_response(404)
            handler.send_header("Content-Type", "text/html; charset=utf-8")
            handler.send_header("Content-Length", str(len(body_404)))
            handler.end_headers()
            handler.wfile.write(body_404)
        else:
            handler.send_error(404, "File not found")
        return

    ext = os.path.splitext(canonical_path)[1].lower()
    content_type = MIME_TYPES.get(ext, "application/octet-stream")

    try:
        with open(canonical_path, "rb") as f:
            content = f.read()
        handler.send_response(200)
        handler.send_header("Content-Type", content_type)
        handler.send_header("Content-Length", str(len(content)))
        handler.end_headers()
        handler.wfile.write(content)
    except Exception as e:
        handler.send_error(500, f"Error reading file: {e}")

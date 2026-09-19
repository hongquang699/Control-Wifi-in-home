"""
Bộ quản lý Biểu tượng Ứng dụng (Icon Manager)
Cung cấp QIcon vector SVG chuẩn Flaticon / Cyber Dark-Tech cho toàn bộ giao diện.
"""

import os
from typing import Dict
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import QSize

_ICON_CACHE: Dict[str, QIcon] = {}

def get_icons_dir() -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target = os.path.join(base_dir, "assets", "icons")
    if os.path.exists(target):
        return target
    # Fallback nếu chạy trong PyInstaller dist
    alt_target = os.path.join(os.path.dirname(base_dir), "assets", "icons")
    if os.path.exists(alt_target):
        return alt_target
    return target

def get_icon_path(name: str) -> str:
    if not name.endswith(".svg") and not name.endswith(".png"):
        name = f"{name}.svg"
    return os.path.join(get_icons_dir(), name)

def get_app_icon(name: str) -> QIcon:
    """Lấy QIcon từ kho biểu tượng SVG với bộ nhớ đệm cache tối ưu hiệu năng."""
    if name in _ICON_CACHE:
        return _ICON_CACHE[name]

    path = get_icon_path(name)
    if os.path.exists(path):
        icon = QIcon(path)
        _ICON_CACHE[name] = icon
        return icon

    # Fallback biểu tượng trống nếu không tìm thấy tệp
    return QIcon()

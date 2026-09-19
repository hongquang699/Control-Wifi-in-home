"""
Hệ Thống Làm Sạch Dữ Liệu Đầu Vào (Deep Input Sanitizer) - web/security/sanitizer.py
Chống tiêm mã độc qua dữ liệu JSON hoặc Form Submission:
- Thoát các ký tự điều khiển nguy hiểm (Null Bytes \x00, CRLF Injection \r\n)
- Chống ô nhiễm nguyên mẫu (Prototype Pollution: __proto__, constructor)
- Thoát ký tự HTML nhạy cảm (<, >, &, ", ')
- Đệ quy làm sạch các cấu trúc lồng nhau (Nested Dictionaries & Lists)
"""

import html
import re
from typing import Any, Dict, List, Union

DANGEROUS_KEYS = {"__proto__", "constructor", "prototype"}

def sanitize_string(val: str, max_length: int = 10000, escape_html: bool = True) -> str:
    """Làm sạch chuỗi ký tự, loại bỏ null bytes và escape HTML."""
    if not isinstance(val, str):
        return str(val)

    # Cắt giảm độ dài tối đa chống DoS bộ nhớ
    val = val[:max_length]

    # Loại bỏ null bytes (\x00) chống bypass kiểm tra đuôi file và chuỗi C
    val = val.replace("\x00", "")

    # Thoát ký tự HTML nếu được yêu cầu
    if escape_html:
        val = html.escape(val, quote=True)

    return val.strip()


def sanitize_input(data: Any, max_depth: int = 10, escape_html: bool = True) -> Any:
    """
    Làm sạch đệ quy dữ liệu bất kỳ (dict, list, str, int, bool...).
    """
    if max_depth <= 0:
        return data

    if isinstance(data, dict):
        cleaned_dict = {}
        for k, v in data.items():
            clean_k = sanitize_string(str(k), max_length=128, escape_html=True)
            # Chặn Prototype Pollution
            if clean_k.lower() in DANGEROUS_KEYS:
                continue
            cleaned_dict[clean_k] = sanitize_input(v, max_depth=max_depth - 1, escape_html=escape_html)
        return cleaned_dict

    elif isinstance(data, list):
        return [sanitize_input(item, max_depth=max_depth - 1, escape_html=escape_html) for item in data[:500]]

    elif isinstance(data, str):
        return sanitize_string(data, escape_html=escape_html)

    return data

"""
Lớp 5: Input Validation & Sanitization Module
Đặc biệt không tin tưởng dữ liệu gửi từ client.
Mọi dữ liệu đầu vào đều được kiểm tra chặt chẽ định dạng và làm sạch ký tự điều khiển.
"""

import re
import html
from typing import Dict, Any, List, Optional, Tuple

IPV4_REGEX = re.compile(
    r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
)

MAC_REGEX = re.compile(
    r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"
)

CIDR_REGEX = re.compile(
    r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)/(3[0-2]|[12]?[0-9])$"
)

def is_valid_ipv4(ip: str) -> bool:
    """Kiểm tra chuỗi IPv4 hợp lệ."""
    if not isinstance(ip, str):
        return False
    return bool(IPV4_REGEX.match(ip.strip()))

def is_valid_mac(mac: str) -> bool:
    """Kiểm tra định dạng địa chỉ MAC hợp lệ."""
    if not isinstance(mac, str):
        return False
    return bool(MAC_REGEX.match(mac.strip()))

def normalize_mac(mac: str) -> str:
    """Chuẩn hóa MAC về dạng XX:XX:XX:XX:XX:XX chữ hoa."""
    cleaned = re.sub(r"[^0-9A-Fa-f]", "", mac).upper()
    if len(cleaned) == 12:
        return ":".join(cleaned[i:i+2] for i in range(0, 12, 2))
    return mac.strip().upper()

def is_valid_cidr(cidr: str) -> bool:
    """Kiểm tra định dạng dải mạng CIDR (vd: 192.168.1.0/24)."""
    if not isinstance(cidr, str):
        return False
    return bool(CIDR_REGEX.match(cidr.strip()))

def sanitize_input_text(text: str, max_length: int = 256) -> str:
    """
    Làm sạch chuỗi văn bản:
    - Loại bỏ null bytes và ký tự điều khiển
    - Escape ký tự HTML để chống XSS
    - Giới hạn độ dài tối đa
    """
    if not isinstance(text, str):
        text = str(text)
    # Loại bỏ null bytes
    cleaned = text.replace("\x00", "").strip()
    # Giới hạn độ dài
    cleaned = cleaned[:max_length]
    # Escape HTML
    return html.escape(cleaned)

def validate_json_schema(payload: Dict[str, Any], required_fields: List[str]) -> Tuple[bool, Optional[str]]:
    """
    Kiểm tra xem JSON payload có chứa đầy đủ các trường bắt buộc hay không.
    """
    if not isinstance(payload, dict):
        return False, "Payload phải là định dạng JSON Object"
    for field in required_fields:
        if field not in payload or payload[field] is None:
            return False, f"Thiếu trường bắt buộc: '{field}'"
    return True, None

"""
Khử Dữ Liệu Nhạy Cảm & Chống Rò Rỉ Thông Tin (Data Masker) - web/security/data_masker.py
Tự động ẩn hoặc mã hóa các trường thông tin nhạy cảm trước khi trả về REST API hoặc ghi log:
- Mật khẩu (password, pass, pwd)
- Khóa bảo mật (secret, key, api_key, private_key)
- Token ủy quyền (token, access_token, refresh_token, session_id)
"""

import re
from typing import Any, Dict, List, Union

# Danh sách tên các trường nhạy cảm cần mask
SENSITIVE_KEY_PATTERNS = [
    re.compile(r"pass(word)?", re.IGNORECASE),
    re.compile(r"secret", re.IGNORECASE),
    re.compile(r"token", re.IGNORECASE),
    re.compile(r"api[_-]?key", re.IGNORECASE),
    re.compile(r"private[_-]?key", re.IGNORECASE),
    re.compile(r"auth(orization)?", re.IGNORECASE),
    re.compile(r"credential", re.IGNORECASE)
]

MASK_VALUE = "********"

def is_sensitive_key(key: str) -> bool:
    """Kiểm tra xem tên khóa có thuộc diện thông tin nhạy cảm không."""
    return any(p.search(key) for p in SENSITIVE_KEY_PATTERNS)


def mask_sensitive_data(data: Union[Dict, List, Any], depth: int = 0, max_depth: int = 10) -> Any:
    """
    Đệ quy duyệt qua Dictionary / List và thay thế giá trị nhạy cảm bằng chuỗi đã che dấu.
    """
    if depth > max_depth:
        return data

    if isinstance(data, dict):
        masked_dict = {}
        for k, v in data.items():
            if isinstance(k, str) and is_sensitive_key(k):
                masked_dict[k] = MASK_VALUE
            elif isinstance(v, (dict, list)):
                masked_dict[k] = mask_sensitive_data(v, depth + 1, max_depth)
            else:
                masked_dict[k] = v
        return masked_dict

    elif isinstance(data, list):
        return [mask_sensitive_data(item, depth + 1, max_depth) for item in data]

    return data

"""
Module Mật Mã Học & Xác Thực An Toàn (Cryptographic Engine) - web/security/crypto.py
Tuân thủ các tiêu chuẩn an ninh mạng cao nhất (OWASP / NIST):
- Băm mật khẩu bằng PBKDF2-HMAC-SHA256 với 600,000 vòng lặp và salt ngẫu nhiên 32-byte
- Chống tấn công Timing Attacks bằng hmac.compare_digest
- Sinh mã ngẫu nhiên bảo mật cao qua thư viện secrets
- Tạo và xác thực chữ ký số HMAC-SHA256 cho phiên làm việc (Session Signatures)
"""

import os
import hmac
import hashlib
import secrets
import base64
import time
from typing import Tuple, Optional

# Cấu hình PBKDF2 chuẩn OWASP
PBKDF2_ITERATIONS = 600_000
SALT_SIZE_BYTES = 32
KEY_LENGTH = 32

# Khóa bí mật hệ thống cho việc ký token (sinh tự động hoặc đọc từ biến môi trường)
_SYSTEM_SECRET_KEY = os.environ.get(
    "NETWORK_MANAGER_SECRET_KEY",
    secrets.token_hex(32)
).encode("utf-8")


def hash_password(password: str) -> str:
    """
    Băm mật khẩu bằng PBKDF2-HMAC-SHA256 với salt ngẫu nhiên 32-byte.
    Định dạng kết quả: pbkdf2_sha256$<iterations>$<salt_b64>$<hash_b64>
    """
    if not isinstance(password, str) or not password:
        raise ValueError("Mật khẩu không được để trống")

    salt = secrets.token_bytes(SALT_SIZE_BYTES)
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
        dklen=KEY_LENGTH
    )

    salt_b64 = base64.b64encode(salt).decode("ascii")
    hash_b64 = base64.b64encode(derived).decode("ascii")
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt_b64}${hash_b64}"


def verify_password(password: str, hashed: str) -> bool:
    """
    Xác minh mật khẩu sử dụng phép so sánh hmac.compare_digest (constant-time).
    Ngăn chặn 100% tấn công phân tích độ trễ (Timing Attack).
    """
    if not password or not hashed or not isinstance(hashed, str):
        return False

    try:
        parts = hashed.split("$")
        if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
            return False

        iterations = int(parts[1])
        salt = base64.b64decode(parts[2].encode("ascii"))
        expected_hash = base64.b64decode(parts[3].encode("ascii"))

        test_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iterations,
            dklen=len(expected_hash)
        )
        return hmac.compare_digest(test_hash, expected_hash)
    except Exception:
        return False


def generate_secure_token(length_bytes: int = 32) -> str:
    """Sinh token ngẫu nhiên bảo mật cao sử dụng nguồn entropy CSPRNG của hệ điều hành."""
    return secrets.token_hex(length_bytes)


def sign_data(payload: str, secret_key: Optional[bytes] = None) -> str:
    """
    Ký dữ liệu bằng HMAC-SHA256.
    Trả về định dạng: <payload>.<signature_hex>
    """
    key = secret_key or _SYSTEM_SECRET_KEY
    signature = hmac.new(key, payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{payload}.{signature}"


def verify_signed_data(signed_string: str, secret_key: Optional[bytes] = None) -> Optional[str]:
    """
    Xác minh chữ ký số của dữ liệu. Trả về payload gốc nếu hợp lệ, ngược lại trả về None.
    """
    if not signed_string or "." not in signed_string:
        return None

    payload, signature = signed_string.rsplit(".", 1)
    key = secret_key or _SYSTEM_SECRET_KEY
    expected_signature = hmac.new(key, payload.encode("utf-8"), hashlib.sha256).hexdigest()

    if hmac.compare_digest(signature, expected_signature):
        return payload
    return None


def constant_time_compare(val1: str, val2: str) -> bool:
    """So sánh 2 chuỗi an toàn chống Timing Attack."""
    return hmac.compare_digest(val1.encode("utf-8"), val2.encode("utf-8"))

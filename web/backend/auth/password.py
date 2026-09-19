"""
Lớp 3: Password Hashing Module (Không lưu mật khẩu dạng plaintext)
Sử dụng chuẩn bảo mật NIST: PBKDF2-HMAC-SHA256 với Salt 16-byte ngẫu nhiên và 200,000 vòng lặp.
So sánh hash bằng secrets.compare_digest chống Timing Attack.
"""

import hashlib
import secrets
from typing import Tuple

ITERATIONS = 200_000
ALGORITHM = "sha256"

def hash_password(password: str) -> str:
    """
    Băm mật khẩu người dùng với salt ngẫu nhiên và 200.000 vòng lặp PBKDF2.
    Định dạng đầu ra: pbkdf2:sha256:200000$<salt_hex>$<hash_hex>
    """
    if not isinstance(password, str):
        password = str(password)
        
    salt = secrets.token_bytes(16)
    key = hashlib.pbkdf2_hmac(
        ALGORITHM,
        password.encode("utf-8"),
        salt,
        ITERATIONS
    )
    return f"pbkdf2:{ALGORITHM}:{ITERATIONS}${salt.hex()}${key.hex()}"

def verify_password(password: str, stored_hash: str) -> bool:
    """
    Xác thực mật khẩu ứng viên với hash đã lưu trữ bằng so sánh thời gian cố định.
    """
    if not password or not stored_hash:
        return False
        
    try:
        parts = stored_hash.split("$")
        if len(parts) != 3:
            return False
            
        header, salt_hex, key_hex = parts
        _, algo, iters_str = header.split(":")
        iterations = int(iters_str)
        salt = bytes.fromhex(salt_hex)
        expected_key = bytes.fromhex(key_hex)
        
        computed_key = hashlib.pbkdf2_hmac(
            algo,
            password.encode("utf-8"),
            salt,
            iterations
        )
        # So sánh an toàn chống timing attack
        return secrets.compare_digest(computed_key, expected_key)
    except Exception:
        return False

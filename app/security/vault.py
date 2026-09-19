"""
Két Sắt Lưu Trữ Mật Khẩu Mã Hóa Cục Bộ (Hardware-Bound Credentials Vault) - app/security/vault.py
Bảo vệ mật khẩu quản trị Router và Token nhạy cảm trên máy tính cục bộ:
- Phái sinh khóa mã hóa từ phần cứng máy tính (MachineGUID + Hardware Entropy)
- Không bao giờ lưu trữ mật khẩu Router dưới dạng văn bản thô (Plaintext) trên đĩa
- Thuật toán xác thực mã hóa Encrypt-then-MAC (HMAC-SHA256 + Keystream CTR)
"""

import os
import sys
import hmac
import hashlib
import secrets
import base64
import platform
from typing import Optional

VAULT_HEADER = "vault_v1"
PBKDF2_ROUNDS = 200_000

def _get_hardware_entropy() -> bytes:
    """Thu thập thông tin phần cứng duy nhất của máy trạm để làm khóa gốc."""
    entropy_parts = [
        platform.node(),
        platform.machine(),
        platform.processor(),
        os.environ.get("COMPUTERNAME", "UNKNOWN_PC"),
        os.environ.get("USERNAME", "DEFAULT_USER")
    ]

    # Cố gắng đọc Windows MachineGUID từ Registry
    if sys.platform == "win32":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography") as key:
                guid, _ = winreg.QueryValueEx(key, "MachineGuid")
                entropy_parts.append(str(guid))
        except Exception:
            pass

    combined = "##".join(entropy_parts).encode("utf-8")
    return hashlib.sha256(combined).digest()


def _derive_encryption_key(salt: bytes) -> bytes:
    """Phái sinh khóa 256-bit từ hardware entropy qua PBKDF2."""
    master_entropy = _get_hardware_entropy()
    return hashlib.pbkdf2_hmac("sha256", master_entropy, salt, PBKDF2_ROUNDS, dklen=32)


def encrypt_secret(plaintext: str) -> str:
    """
    Mã hóa bí mật (mật khẩu/token). Trả về chuỗi bundle an toàn.
    Định dạng: vault_v1$<salt_b64>$<iv_b64>$<ciphertext_b64>$<mac_b64>
    """
    if not plaintext:
        return ""

    salt = secrets.token_bytes(16)
    iv = secrets.token_bytes(16)
    derived_key = _derive_encryption_key(salt)

    # Sinh Keystream CTR từ derived_key + IV
    data_bytes = plaintext.encode("utf-8")
    blocks_needed = (len(data_bytes) + 31) // 32
    keystream = bytearray()
    for counter in range(blocks_needed):
        counter_block = iv + counter.to_bytes(4, byteorder="big")
        keystream.extend(hmac.new(derived_key, counter_block, hashlib.sha256).digest())

    ciphertext = bytes(a ^ b for a, b in zip(data_bytes, keystream[:len(data_bytes)]))

    # Tính toán MAC xác thực tính toàn vẹn (Encrypt-then-MAC)
    mac = hmac.new(derived_key, iv + ciphertext, hashlib.sha256).digest()

    salt_b64 = base64.b64encode(salt).decode("ascii")
    iv_b64 = base64.b64encode(iv).decode("ascii")
    cipher_b64 = base64.b64encode(ciphertext).decode("ascii")
    mac_b64 = base64.b64encode(mac).decode("ascii")

    return f"{VAULT_HEADER}${salt_b64}${iv_b64}${cipher_b64}${mac_b64}"


def decrypt_secret(encrypted_bundle: str) -> str:
    """
    Giải mã bí mật từ chuỗi bundle an toàn.
    Nếu mật khẩu chưa được mã hóa (legacy plain text), trả về trực tiếp.
    """
    if not encrypted_bundle:
        return ""

    # Nếu không phải định dạng mã hóa của vault -> tương thích ngược
    if not encrypted_bundle.startswith(f"{VAULT_HEADER}$"):
        return encrypted_bundle

    try:
        parts = encrypted_bundle.split("$")
        if len(parts) != 5:
            return encrypted_bundle

        salt = base64.b64decode(parts[1].encode("ascii"))
        iv = base64.b64decode(parts[2].encode("ascii"))
        ciphertext = base64.b64decode(parts[3].encode("ascii"))
        expected_mac = base64.b64decode(parts[4].encode("ascii"))

        derived_key = _derive_encryption_key(salt)

        # Kiểm tra MAC trước khi giải mã
        computed_mac = hmac.new(derived_key, iv + ciphertext, hashlib.sha256).digest()
        if not hmac.compare_digest(computed_mac, expected_mac):
            raise ValueError("Chữ ký MAC không khớp! Dữ liệu đã bị can thiệp hoặc chuyển sang máy khác.")

        blocks_needed = (len(ciphertext) + 31) // 32
        keystream = bytearray()
        for counter in range(blocks_needed):
            counter_block = iv + counter.to_bytes(4, byteorder="big")
            keystream.extend(hmac.new(derived_key, counter_block, hashlib.sha256).digest())

        plaintext_bytes = bytes(a ^ b for a, b in zip(ciphertext, keystream[:len(ciphertext)]))
        return plaintext_bytes.decode("utf-8")
    except Exception:
        # Nếu giải mã thất bại (do đổi máy hoặc file lỗi), fallback an toàn
        return encrypted_bundle


def decrypt_secret_secure(encrypted_bundle: str):
    """
    Giải mã bí mật và đóng gói trong đối tượng SecureBuffer.
    Cho phép sử dụng trong context manager và tự động zeroize bộ nhớ sau khi dùng:
    with decrypt_secret_secure(bundle) as sec:
        use(sec.get_string())
    """
    from security.zeroize import SecureBuffer
    decrypted_str = decrypt_secret(encrypted_bundle)
    return SecureBuffer(decrypted_str)


"""
Hệ Thống Kiểm Tra Tính Toàn Vẹn Tệp & Cơ Sở Dữ Liệu (File & Database Integrity Guard) - app/security/integrity.py
Phát hiện các hành vi can thiệp trái phép, mã độc sửa đổi cơ sở dữ liệu SQLite hoặc tệp cấu hình:
- Sử dụng HMAC-SHA256 kết hợp khóa bí mật phái sinh từ phần cứng máy
- Giám sát các tệp cốt lõi: data/network.db, config/config.json, config/routers.json
- Lưu giữ chữ ký tại data/.integrity.sig
"""

import os
import json
import hmac
import hashlib
from typing import Dict, Tuple
from security.vault import _get_hardware_entropy
from core.logger import logger

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTEGRITY_SIG_FILE = os.path.join(APP_DIR, "data", ".integrity.sig")

def _get_integrity_key() -> bytes:
    master = _get_hardware_entropy()
    return hashlib.sha256(master + b"::NETWORK_MANAGER_INTEGRITY::").digest()


def calculate_file_hmac(file_path: str) -> str:
    """Tính toán chữ ký HMAC-SHA256 của tệp tin."""
    if not os.path.exists(file_path):
        return ""
    key = _get_integrity_key()
    h = hmac.new(key, digestmod=hashlib.sha256)
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        logger.error(f"[Integrity] Lỗi đọc tệp {file_path}: {e}")
        return ""


def save_baseline_signatures(files_to_track: list = None):
    """Ghi nhận lại chữ ký mẫu (baseline) cho các tệp hệ thống."""
    if files_to_track is None:
        files_to_track = [
            os.path.join(APP_DIR, "config", "config.json"),
            os.path.join(APP_DIR, "config", "routers.json"),
            os.path.join(APP_DIR, "data", "network.db")
        ]

    manifest = {}
    for fpath in files_to_track:
        if os.path.exists(fpath):
            manifest[fpath] = calculate_file_hmac(fpath)

    os.makedirs(os.path.dirname(INTEGRITY_SIG_FILE), exist_ok=True)
    with open(INTEGRITY_SIG_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    logger.info(f"[Integrity] Đã cập nhật chữ ký baseline cho {len(manifest)} tệp tin.")


def verify_file_integrity(file_path: str) -> Tuple[bool, str]:
    """Kiểm tra tệp tin có bị thay đổi trái phép so với baseline hay không."""
    if not os.path.exists(file_path):
        return False, f"Tệp tin không tồn tại: {file_path}"

    if not os.path.exists(INTEGRITY_SIG_FILE):
        # Nếu chưa có baseline, tự động khởi tạo lần đầu
        save_baseline_signatures([file_path])
        return True, "Khởi tạo baseline tính toàn vẹn lần đầu."

    try:
        with open(INTEGRITY_SIG_FILE, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        expected_sig = manifest.get(file_path)
        if not expected_sig:
            # Tệp mới chưa nằm trong baseline
            manifest[file_path] = calculate_file_hmac(file_path)
            with open(INTEGRITY_SIG_FILE, "w", encoding="utf-8") as f_out:
                json.dump(manifest, f_out, indent=2)
            return True, "Đã thêm tệp vào danh mục theo dõi toàn vẹn."

        current_sig = calculate_file_hmac(file_path)
        if hmac.compare_digest(current_sig, expected_sig):
            return True, "Tệp tin nguyên vẹn 100%, không bị can thiệp."
        else:
            return False, f"CẢNH BÁO: Tệp '{file_path}' đã bị chỉnh sửa từ bên ngoài!"
    except Exception as e:
        return False, f"Lỗi xác minh: {e}"


def verify_all_system_files() -> Dict[str, Tuple[bool, str]]:
    """Kiểm tra toàn bộ hệ thống tệp quan trọng."""
    targets = [
        os.path.join(APP_DIR, "config", "config.json"),
        os.path.join(APP_DIR, "config", "routers.json"),
        os.path.join(APP_DIR, "data", "network.db")
    ]
    results = {}
    for tgt in targets:
        if os.path.exists(tgt):
            results[tgt] = verify_file_integrity(tgt)
    return results

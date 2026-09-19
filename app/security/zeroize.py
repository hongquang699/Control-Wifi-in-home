"""
Cơ Chế Xóa Sạch Bộ Nhớ & Bảo Vệ Bí Mật Nhạy Cảm (Memory Zeroization) - app/security/zeroize.py
Ngăn chặn trích xuất mật khẩu router và token từ RAM (Memory Scraper / Process Dump):
- Cung cấp hàm ghi đè mảng byte bộ nhớ bằng null bytes (0x00)
- Context manager `SecureBuffer` tự động giải phóng và làm sạch bộ nhớ khi thoát scope
"""

import ctypes
from typing import Optional, Union

def zeroize_memory(target: Union[bytearray, memoryview, ctypes.Array]) -> None:
    """
    Ghi đè trực tiếp lên vùng nhớ vật lý của buffer bằng các byte 0x00.
    """
    if isinstance(target, bytearray):
        length = len(target)
        if length > 0:
            # Ghi đè 2 lần: lần 1 bằng 0xFF, lần 2 bằng 0x00 để xóa triệt để
            for i in range(length):
                target[i] = 0xFF
            for i in range(length):
                target[i] = 0x00
    elif isinstance(target, memoryview):
        length = target.nbytes
        if length > 0:
            target[:length] = b"\x00" * length
    elif hasattr(target, "_type_") and hasattr(target, "_length_"):
        ctypes.memset(ctypes.addressof(target), 0, ctypes.sizeof(target))


class SecureBuffer:
    """
    Buffer lưu trữ dữ liệu nhạy cảm dạng bytearray.
    Tự động zeroize khi hoàn thành hoặc khi garbage collector thu gom.
    """
    def __init__(self, data: Union[str, bytes, bytearray]):
        if isinstance(data, str):
            self._buffer = bytearray(data.encode("utf-8"))
        elif isinstance(data, bytes):
            self._buffer = bytearray(data)
        elif isinstance(data, bytearray):
            self._buffer = bytearray(data)
        else:
            raise TypeError("Dữ liệu phải là str, bytes hoặc bytearray")

        self._cleared = False

    def get_bytes(self) -> bytes:
        """Đọc bản sao dạng bytes (chỉ dùng khi cần gửi qua socket/subprocess)."""
        if self._cleared:
            raise ValueError("Buffer đã bị xóa sạch (Zeroized)!")
        return bytes(self._buffer)

    def get_string(self) -> str:
        """Giải mã thành chuỗi tạm thời."""
        if self._cleared:
            raise ValueError("Buffer đã bị xóa sạch (Zeroized)!")
        return self._buffer.decode("utf-8", errors="replace")

    def wipe(self) -> None:
        """Xóa sạch vùng nhớ ngay lập tức."""
        if not self._cleared and hasattr(self, "_buffer"):
            zeroize_memory(self._buffer)
            self._cleared = True

    @property
    def is_wiped(self) -> bool:
        return self._cleared

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.wipe()

    def __del__(self):
        self.wipe()

    def __repr__(self) -> str:
        return "<SecureBuffer: [PROTECTED/HIDDEN]>"

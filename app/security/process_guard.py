"""
Giám Sát Toàn Vẹn Tiến Trình & Chống Can Thiệp Mã (Process Integrity & Anti-Hook Guard) - app/security/process_guard.py
Bảo vệ ứng dụng Desktop trước các công cụ can thiệp bộ nhớ, Debugger, và DLL Hooking:
- Phát hiện Debugger gắn vào tiến trình (IsDebuggerPresent / CheckRemoteDebuggerPresent)
- Quét danh sách Dynamic Link Libraries (DLLs) / Shared Libraries phát hiện DLL Injection
- Phát hiện công cụ can thiệp thông dụng: Frida, Detours, Cheat Engine, ScyllaHide
"""

import os
import sys
import ctypes
from typing import List, Dict, Any

# Danh sách tên các thư viện hook/can thiệp thường gặp
SUSPICIOUS_MODULE_SIGNATURES = [
    "frida",
    "detours",
    "cheatengine",
    "speedhack",
    "scyllahide",
    "x64dbg",
    "x32dbg",
    "windbg",
    "minhook",
    "apimonitor"
]


def is_debugger_present() -> bool:
    """
    Kiểm tra xem có Debugger nào đang gắn bẫy gỡ lỗi vào tiến trình không.
    Hỗ trợ Windows API IsDebuggerPresent và CheckRemoteDebuggerPresent.
    """
    if sys.platform != "win32":
        # Fallback cho Linux: kiểm tra TracerPid trong /proc/self/status
        try:
            with open("/proc/self/status", "r") as f:
                for line in f:
                    if line.startswith("TracerPid:"):
                        tracer = int(line.split(":")[1].strip())
                        return tracer > 0
        except Exception:
            return False
        return False

    try:
        kernel32 = ctypes.windll.kernel32
        # 1. Kiểm tra cờ PEB BeingDebugged
        if kernel32.IsDebuggerPresent():
            return True

        # 2. Kiểm tra Remote Debugger Port
        is_remote = ctypes.c_bool(False)
        current_process = kernel32.GetCurrentProcess()
        if hasattr(kernel32, "CheckRemoteDebuggerPresent"):
            kernel32.CheckRemoteDebuggerPresent(current_process, ctypes.byref(is_remote))
            if is_remote.value:
                return True
    except Exception:
        pass

    return False


def get_loaded_modules() -> List[str]:
    """
    Lấy danh sách các module / DLL đang nạp vào tiến trình hiện tại trên Windows.
    """
    modules: List[str] = []
    if sys.platform != "win32":
        return modules

    try:
        psapi = ctypes.windll.psapi
        kernel32 = ctypes.windll.kernel32
        h_process = kernel32.GetCurrentProcess()

        cb_needed = ctypes.c_ulong()
        # Cấp phát mảng con trỏ HMODULE
        h_mods = (ctypes.c_void_p * 1024)()
        if psapi.EnumProcessModules(h_process, ctypes.byref(h_mods), ctypes.sizeof(h_mods), ctypes.byref(cb_needed)):
            mod_count = int(cb_needed.value / ctypes.sizeof(ctypes.c_void_p))
            name_buf = ctypes.create_unicode_buffer(512)
            for i in range(min(mod_count, 1024)):
                if h_mods[i]:
                    if psapi.GetModuleBaseNameW(h_process, h_mods[i], name_buf, 512):
                        modules.append(name_buf.value)
    except Exception:
        pass

    return modules


def detect_suspicious_modules() -> List[str]:
    """
    Kiểm tra danh sách module để phát hiện các DLL hook can thiệp trái phép.
    """
    loaded = get_loaded_modules()
    suspicious = []
    for mod in loaded:
        mod_lower = mod.lower()
        for sig in SUSPICIOUS_MODULE_SIGNATURES:
            if sig in mod_lower:
                suspicious.append(mod)
                break
    return suspicious


def verify_process_security() -> Dict[str, Any]:
    """
    Thực hiện kiểm tra an ninh tiến trình toàn diện.
    Trả về báo cáo tình trạng toàn vẹn tiến trình.
    """
    dbg = is_debugger_present()
    suspicious_mods = detect_suspicious_modules()
    is_secure = (not dbg) and (len(suspicious_mods) == 0)

    return {
        "secure": is_secure,
        "debugger_detected": dbg,
        "suspicious_modules": suspicious_mods,
        "total_modules_loaded": len(get_loaded_modules()) if sys.platform == "win32" else 0
    }

"""
Tiện ích thực thi an toàn các lệnh hệ thống (Subprocess).
"""

import subprocess
import os
import sys
from typing import Tuple, List, Optional
from core.logger import logger

def run_cmd(
    cmd: List[str] | str,
    timeout: int = 30,
    shell: bool = False,
    cwd: Optional[str] = None
) -> Tuple[int, str, str]:
    """
    Thực thi lệnh an toàn, bắt timeout và decode đúng tiếng Việt/Unicode trên Windows.
    Trả về: (returncode, stdout, stderr)
    """
    cmd_str = cmd if isinstance(cmd, str) else " ".join(cmd)
    try:
        startupinfo = None
        if os.name == 'nt':
            # Ẩn cửa sổ command prompt trên Windows
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            shell=shell,
            cwd=cwd,
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        stdout_bytes, stderr_bytes = process.communicate(timeout=timeout)
        
        # Thử decode utf-8 trước, fallback sang cp437 hoặc utf-8 replace
        def decode_bytes(b: bytes) -> str:
            for enc in ('utf-8', 'cp1258', 'cp437', 'latin-1'):
                try:
                    return b.decode(enc)
                except UnicodeDecodeError:
                    continue
            return b.decode('utf-8', errors='replace')
            
        return (
            process.returncode,
            decode_bytes(stdout_bytes),
            decode_bytes(stderr_bytes)
        )
    except subprocess.TimeoutExpired:
        logger.warning(f"Lệnh bị quá thời gian ({timeout}s): {cmd_str}")
        try:
            process.kill()
        except Exception:
            pass
        return (-1, "", f"Timeout after {timeout} seconds")
    except Exception as e:
        logger.error(f"Lỗi khi thực thi lệnh [{cmd_str}]: {e}")
        return (-2, "", str(e))

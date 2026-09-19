"""
Lớp 2: Web Application Firewall (WAF) Middleware
Phát hiện và ngăn chặn các mẫu tấn công phổ biến theo tiêu chuẩn OWASP Top 10:
- SQL Injection (SQLi)
- Cross-Site Scripting (XSS)
- Path Traversal / Local File Inclusion
- Command Injection
- Null-byte Injection & Dangerous HTTP methods
"""

import re
import urllib.parse
from typing import Tuple, Optional

# Các biểu thức chính quy nhận diện mẫu tấn công
SQLI_PATTERNS = [
    re.compile(r"(\b(UNION(\s+ALL)?|SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE)\b.*\b(FROM|INTO|TABLE|DATABASE)\b)", re.IGNORECASE),
    re.compile(r"('|\")?\s*\b(OR|AND)\b\s*('|\")?.*(=|<|>|LIKE).*('|\")?", re.IGNORECASE),
    re.compile(r"(--|#|/\*).*$", re.MULTILINE),
    re.compile(r"\bWAITFOR\s+DELAY\b|\bSLEEP\s*\(|\bBENCHMARK\s*\(", re.IGNORECASE),
]

XSS_PATTERNS = [
    re.compile(r"<\s*script[^>]*>.*?", re.IGNORECASE),
    re.compile(r"javascript\s*:\s*.*?", re.IGNORECASE),
    re.compile(r"on(load|error|click|mouseover|submit|focus|blur)\s*=\s*.*?", re.IGNORECASE),
    re.compile(r"<\s*(iframe|object|embed|applet|svg|meta|link)[^>]*>", re.IGNORECASE),
    re.compile(r"document\.(cookie|location|write)", re.IGNORECASE),
]

PATH_TRAVERSAL_PATTERNS = [
    re.compile(r"\.\.[\\/]", re.IGNORECASE),
    re.compile(r"(%2e|%252e){2}(%2f|%5c|%252f|%255c)", re.IGNORECASE),
    re.compile(r"\0|%00", re.IGNORECASE),  # Null byte injection
    re.compile(r"(/|\\)(etc|proc|var|windows|winnt|system32)(/|\\)", re.IGNORECASE),
]

CMD_INJECTION_PATTERNS = [
    re.compile(r"(\||;|&&|\$\(|\`)\s*(cat|ls|dir|rm|del|powershell|cmd|sh|bash|wget|curl|nc|netcat|whoami)\b", re.IGNORECASE),
]

class WAFInspectionResult:
    def __init__(self, is_blocked: bool, attack_type: Optional[str] = None, matched_pattern: Optional[str] = None):
        self.is_blocked = is_blocked
        self.attack_type = attack_type
        self.matched_pattern = matched_pattern

    def __bool__(self):
        return self.is_blocked

def _inspect_string(text: str) -> Optional[Tuple[str, str]]:
    """Kiểm tra một chuỗi văn bản xem có khớp với các rule WAF hay không."""
    if not text:
        return None

    # Giải mã URL nếu có encoding
    try:
        decoded_text = urllib.parse.unquote_plus(text)
    except Exception:
        decoded_text = text

    # 1. Path Traversal
    for pat in PATH_TRAVERSAL_PATTERNS:
        if pat.search(text) or pat.search(decoded_text):
            return "PATH_TRAVERSAL", pat.pattern

    # 2. SQL Injection
    for pat in SQLI_PATTERNS:
        if pat.search(decoded_text):
            return "SQL_INJECTION", pat.pattern

    # 3. Cross-Site Scripting (XSS)
    for pat in XSS_PATTERNS:
        if pat.search(decoded_text):
            return "XSS", pat.pattern

    # 4. Command Injection
    for pat in CMD_INJECTION_PATTERNS:
        if pat.search(decoded_text):
            return "COMMAND_INJECTION", pat.pattern

    return None

def inspect_request(path: str, query_string: str = "", body: str = "") -> WAFInspectionResult:
    """
    Kiểm tra tổng thể một HTTP Request (URL Path, Query Parameters, và Body).
    """
    # 1. Kiểm tra Path
    match = _inspect_string(path)
    if match:
        return WAFInspectionResult(True, match[0], match[1])

    # 2. Kiểm tra Query String
    if query_string:
        match = _inspect_string(query_string)
        if match:
            return WAFInspectionResult(True, match[0], match[1])

    # 3. Kiểm tra Body (chỉ kiểm tra nếu body tồn tại và dưới 1MB)
    if body and len(body) < 1_000_000:
        match = _inspect_string(body)
        if match:
            return WAFInspectionResult(True, match[0], match[1])

    return WAFInspectionResult(False)

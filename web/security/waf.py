"""
Hệ Thống Tường Lửa Ứng Dụng Web (Web Application Firewall - WAF) - web/security/waf.py
Bảo vệ tầng ứng dụng HTTP trước các cuộc tấn công phổ biến nhất theo chuẩn OWASP Top 10:
- SQL Injection (SQLi)
- Cross-Site Scripting (XSS)
- Path Traversal & LFI / RFI
- Remote Command Execution (RCE) & Command Injection
- Malicious Scanners & Botnet User-Agents
"""

import re
import urllib.parse
from typing import Tuple, Dict, Any, List, Optional

class WAFSecurityException(Exception):
    """Ngoại lệ khi WAF phát hiện hành vi xâm nhập độc hại."""
    def __init__(self, rule_name: str, pattern: str, detected_in: str):
        self.rule_name = rule_name
        self.pattern = pattern
        self.detected_in = detected_in
        super().__init__(f"[WAF Block] Quy tắc: {rule_name} | Vị trí: {detected_in}")


class WAFEngine:
    """Động cơ phân tích và lọc gói tin Web Application Firewall."""

    def __init__(self):
        # 1. Các mẫu SQL Injection nguy hiểm
        self.sqli_patterns = [
            re.compile(r"(\b(UNION(\s+ALL)?|SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE)\b\s+.*\b(FROM|INTO|TABLE|DATABASE)\b)", re.IGNORECASE),
            re.compile(r"('\s*OR\s*['\"0-9\w\s]*\s*=\s*['\"0-9\w\s]*)", re.IGNORECASE),
            re.compile(r"((\bOR\b|\bAND\b)\s+[0-9]+\s*=\s*[0-9]+)", re.IGNORECASE),
            re.compile(r"(;\s*DROP\s+TABLE)", re.IGNORECASE),
            re.compile(r"(\bWAITFOR\s+DELAY\b|\bSLEEP\([0-9]+\)|\bBENCHMARK\()", re.IGNORECASE),
            re.compile(r"(\bINFORMATION_SCHEMA\b|\bSYS\.TABLES\b|\bPG_SLEEP\b)", re.IGNORECASE),
            re.compile(r"(--\s*$|/\*.*\*/)", re.IGNORECASE),
        ]

        # 2. Các mẫu Cross-Site Scripting (XSS)
        self.xss_patterns = [
            re.compile(r"(<script\b[^>]*>.*?</script>)", re.IGNORECASE | re.DOTALL),
            re.compile(r"(javascript\s*:\s*[^\s]+)", re.IGNORECASE),
            re.compile(r"(<iframe\b[^>]*>|<embed\b[^>]*>|<object\b[^>]*>)", re.IGNORECASE),
            re.compile(r"(\bon(error|load|click|mouse|hover|focus|blur|submit)\s*=\s*['\"][^'\"]*['\"])", re.IGNORECASE),
            re.compile(r"(alert\s*\(|prompt\s*\(|confirm\s*\(|document\.cookie|window\.location)", re.IGNORECASE),
            re.compile(r"(<svg\b[^>]*\bonload\s*=)", re.IGNORECASE),
            re.compile(r"(<img\b[^>]*\bonerror\s*=)", re.IGNORECASE),
        ]

        # 3. Các mẫu Path Traversal & Local File Inclusion (LFI)
        self.traversal_patterns = [
            re.compile(r"(\.\./|\.\.\\|%2e%2e%2f|%2e%2e/|\.\.%2f)", re.IGNORECASE),
            re.compile(r"(/etc/(passwd|shadow|hosts|group))", re.IGNORECASE),
            re.compile(r"(c:\\windows\\system32|win\.ini|boot\.ini)", re.IGNORECASE),
            re.compile(r"(/proc/self/|/sys/kernel/)", re.IGNORECASE),
        ]

        # 4. Các mẫu Command Injection / Remote Code Execution (RCE)
        self.rce_patterns = [
            re.compile(r"([;&|`]\s*(cat|ls|dir|whoami|netstat|powershell|cmd\.exe|bash|sh|wget|curl|nc)\b)", re.IGNORECASE),
            re.compile(r"(\b(eval|system|exec|passthru|shell_exec)\s*\()", re.IGNORECASE),
            re.compile(r"(\$\{.*?\})", re.IGNORECASE),
        ]

        # 5. Các mẫu NoSQL Injection (MongoDB, Document Stores)
        self.nosql_patterns = [
            re.compile(r"(['\"]?\$where['\"]?\s*:\s*)", re.IGNORECASE),
            re.compile(r"(['\"]?\$(gt|gte|lt|lte|ne|nin|in|or|and|not|nor|exists|type|mod|regex|text|expr|jsonSchema)['\"]?\s*:\s*)", re.IGNORECASE),
            re.compile(r"(\{\s*['\"]\$ne['\"]\s*:\s*(null|['\"]))", re.IGNORECASE),
            re.compile(r"(\{\s*['\"]\$gt['\"]\s*:\s*['\"])", re.IGNORECASE),
            re.compile(r"(tojson\s*\(|db\.[a-zA-Z0-9_]+\.(find|insert|update|remove|drop)\()", re.IGNORECASE),
        ]

        # 6. Các User-Agent độc hại và công cụ rà quét lỗ hổng tự động
        self.bad_user_agents = [
            "sqlmap", "nikto", "masscan", "nmap", "dirbuster",
            "havij", "acunetix", "w3af", "nessus", "openvas",
            "metasploit", "zgrab", "gobuster"
        ]

    def inspect_request(
        self,
        path: str,
        headers: Dict[str, str],
        body: Optional[str] = None,
        method: str = "GET"
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Kiểm định tính an toàn của request HTTP.
        Trả về: (is_safe: bool, rule_name: Optional[str], reason: Optional[str])
        """
        # 1. Kiểm tra User-Agent độc hại
        user_agent = headers.get("User-Agent", "").lower()
        for bad_ua in self.bad_user_agents:
            if bad_ua in user_agent:
                return False, "MALICIOUS_USER_AGENT", f"Phát hiện công cụ quét tự động: '{bad_ua}'"

        # 2. Giải mã URL và kiểm tra URL Path & Query String
        decoded_path = urllib.parse.unquote(urllib.parse.unquote(path))
        is_safe, rule, reason = self._scan_text(decoded_path, "URL Path/Query")
        if not is_safe:
            return False, rule, reason

        # 3. Kiểm tra Request Body nếu có
        if body:
            decoded_body = urllib.parse.unquote(body)
            is_safe, rule, reason = self._scan_text(decoded_body, "Request Body")
            if not is_safe:
                return False, rule, reason

        return True, None, None

    def _scan_text(self, text: str, location: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Quét chuỗi văn bản qua toàn bộ cơ sở dữ liệu mẫu tấn công."""
        # Kiểm tra Path Traversal
        for pat in self.traversal_patterns:
            if pat.search(text):
                return False, "PATH_TRAVERSAL", f"Phát hiện mẫu duyệt thư mục trái phép tại {location}"

        # Kiểm tra SQL Injection
        for pat in self.sqli_patterns:
            if pat.search(text):
                return False, "SQL_INJECTION", f"Phát hiện mẫu SQL Injection độc hại tại {location}"

        # Kiểm tra XSS
        for pat in self.xss_patterns:
            if pat.search(text):
                return False, "XSS_ATTACK", f"Phát hiện mã Cross-Site Scripting (XSS) tại {location}"

        # Kiểm tra RCE / Command Injection
        for pat in self.rce_patterns:
            if pat.search(text):
                return False, "COMMAND_INJECTION", f"Phát hiện mẫu thực thi lệnh hệ điều hành tại {location}"

        # Kiểm tra NoSQL Injection
        for pat in self.nosql_patterns:
            if pat.search(text):
                return False, "NOSQL_INJECTION", f"Phát hiện mẫu NoSQL Injection độc hại tại {location}"

        return True, None, None

# Khởi tạo singleton WAF Engine
waf_engine = WAFEngine()

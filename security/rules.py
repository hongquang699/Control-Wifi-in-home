"""
Định nghĩa các quy tắc chặn (Block Rules).
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class BlockRule:
    mac: str
    ip: Optional[str] = None
    reason: str = "Chặn bởi người quản trị mạng"
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    active: bool = True
    apply_to_router: bool = True
    apply_to_firewall: bool = True

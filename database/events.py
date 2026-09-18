"""
DAO ghi và truy vấn lịch sử sự kiện mạng (bảng events).
"""

from datetime import datetime
from typing import List, Dict, Optional
from database.database import Database
from utils.validators import normalize_mac
from core.logger import logger

class EventDAO:
    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database.get_instance()

    def log_event(
        self,
        event_type: str,
        mac: str = "",
        description: str = "",
        device_id: Optional[int] = None
    ) -> int:
        """Ghi sự kiện mới vào lịch sử."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        mac_norm = normalize_mac(mac) if mac else ""
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            # Nếu chưa có device_id nhưng có MAC, thử tìm id
            if not device_id and mac_norm:
                cursor.execute("SELECT id FROM devices WHERE mac = ?", (mac_norm,))
                row = cursor.fetchone()
                if row:
                    device_id = row[0]

            cursor.execute("""
                INSERT INTO events (timestamp, device_id, mac, event_type, description)
                VALUES (?, ?, ?, ?, ?)
            """, (timestamp, device_id, mac_norm, event_type, description))
            conn.commit()
            return cursor.lastrowid

    def get_recent_events(self, limit: int = 50) -> List[Dict]:
        """Lấy danh sách các sự kiện gần đây kèm thông tin thiết bị."""
        query = """
            SELECT e.id, e.timestamp, e.mac, e.event_type, e.description,
                   d.ip, d.hostname, d.custom_name, d.vendor
            FROM events e
            LEFT JOIN devices d ON e.mac = d.mac
            ORDER BY e.id DESC
            LIMIT ?
        """
        results = []
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (limit,))
            for r in cursor.fetchall():
                results.append({
                    "id": r[0],
                    "timestamp": r[1],
                    "mac": r[2],
                    "event_type": r[3],
                    "description": r[4],
                    "ip": r[5] or "",
                    "hostname": r[6] or "",
                    "custom_name": r[7] or "",
                    "vendor": r[8] or ""
                })
        return results

    def get_events_for_mac(self, mac: str, limit: int = 30) -> List[Dict]:
        """Lấy lịch sử sự kiện của riêng một thiết bị."""
        mac_norm = normalize_mac(mac)
        query = """
            SELECT id, timestamp, mac, event_type, description
            FROM events
            WHERE mac = ?
            ORDER BY id DESC
            LIMIT ?
        """
        results = []
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (mac_norm, limit))
            for r in cursor.fetchall():
                results.append({
                    "id": r[0],
                    "timestamp": r[1],
                    "mac": r[2],
                    "event_type": r[3],
                    "description": r[4]
                })
        return results

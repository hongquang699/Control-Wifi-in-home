"""
DAO thao tác với bảng devices trong SQLite.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Dict
from core.device import Device
from database.database import Database
from core.logger import logger
from utils.validators import normalize_mac

class DeviceDAO:
    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database.get_instance()

    def upsert_device(self, device: Device) -> Tuple[Device, bool, bool]:
        """
        Cập nhật hoặc thêm mới thiết bị.
        Trả về: (Device sau cập nhật, is_new, ip_changed)
        """
        mac = normalize_mac(device.mac)
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        is_new = False
        ip_changed = False

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, ip, hostname, vendor, device_type, custom_name, blocked, block_reason, status, connection_type, network_name FROM devices WHERE mac = ?", (mac,))
            row = cursor.fetchone()

            if row:
                dev_id, old_ip, old_host, old_vendor, old_type, custom_name, blocked, reason, old_status, old_conn, old_net = row
                device.id = dev_id
                device.blocked = bool(blocked)
                device.block_reason = reason or ""
                device.custom_name = custom_name or ""
                
                if old_ip != device.ip:
                    ip_changed = True

                # Giữ hostname/vendor cũ nếu kết quả quét mới trả về rỗng/Unknown
                new_host = device.hostname if device.hostname else (old_host or "")
                new_vendor = device.vendor if (device.vendor and device.vendor != "Unknown") else (old_vendor or "Unknown")
                new_type = device.device_type if (device.device_type and device.device_type != "Unknown") else (old_type or "Unknown")
                new_conn = device.connection_type if (device.connection_type and device.connection_type != "Wi-Fi") else (old_conn or device.connection_type or "Wi-Fi")
                new_net = device.network_name if device.network_name else (old_net or "")

                cursor.execute("""
                    UPDATE devices
                    SET ip = ?, hostname = ?, vendor = ?, device_type = ?, last_seen = ?, status = 'ONLINE', connection_type = ?, network_name = ?
                    WHERE id = ?
                """, (device.ip, new_host, new_vendor, new_type, now_str, new_conn, new_net, dev_id))
                
                device.hostname = new_host
                device.vendor = new_vendor
                device.device_type = new_type
                device.connection_type = new_conn
                device.network_name = new_net
                device.last_seen = now_str
                device.status = "ONLINE"
            else:
                is_new = True
                conn_type = device.connection_type or "Wi-Fi"
                net_name = device.network_name or ""
                cursor.execute("""
                    INSERT INTO devices (ip, mac, hostname, vendor, device_type, custom_name, first_seen, last_seen, status, blocked, block_reason, connection_type, network_name)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'ONLINE', 0, '', ?, ?)
                """, (
                    device.ip,
                    mac,
                    device.hostname or "",
                    device.vendor or "Unknown",
                    device.device_type or "Unknown",
                    device.custom_name or "",
                    now_str,
                    now_str,
                    conn_type,
                    net_name
                ))
                device.id = cursor.lastrowid
                device.mac = mac
                device.first_seen = now_str
                device.last_seen = now_str
                device.status = "ONLINE"
                device.connection_type = conn_type
                device.network_name = net_name

            conn.commit()

        return device, is_new, ip_changed

    def get_all_devices(
        self,
        status_filter: Optional[str] = None,
        blocked_filter: Optional[bool] = None,
        search_keyword: Optional[str] = None
    ) -> List[Device]:
        """Truy vấn danh sách thiết bị có hỗ trợ lọc và tìm kiếm."""
        query = "SELECT id, ip, mac, hostname, vendor, device_type, custom_name, first_seen, last_seen, status, blocked, block_reason, connection_type, network_name FROM devices WHERE 1=1"
        params = []

        if status_filter and status_filter.upper() != "ALL":
            query += " AND status = ?"
            params.append(status_filter.upper())

        if blocked_filter is not None:
            query += " AND blocked = ?"
            params.append(1 if blocked_filter else 0)

        if search_keyword:
            kw = f"%{search_keyword.strip()}%"
            query += " AND (ip LIKE ? OR mac LIKE ? OR hostname LIKE ? OR vendor LIKE ? OR custom_name LIKE ? OR connection_type LIKE ? OR network_name LIKE ?)"
            params.extend([kw, kw, kw, kw, kw, kw, kw])

        query += " ORDER BY status DESC, last_seen DESC"

        devices = []
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            for row in cursor.fetchall():
                devices.append(Device.from_row(row))
        return devices

    def get_device_by_mac(self, mac: str) -> Optional[Device]:
        mac_norm = normalize_mac(mac)
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, ip, mac, hostname, vendor, device_type, custom_name, first_seen, last_seen, status, blocked, block_reason, connection_type, network_name FROM devices WHERE mac = ?",
                (mac_norm,)
            )
            row = cursor.fetchone()
            if row:
                return Device.from_row(row)
        return None

    def get_device_by_id(self, dev_id: int) -> Optional[Device]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, ip, mac, hostname, vendor, device_type, custom_name, first_seen, last_seen, status, blocked, block_reason, connection_type, network_name FROM devices WHERE id = ?",
                (dev_id,)
            )
            row = cursor.fetchone()
            if row:
                return Device.from_row(row)
        return None

    def set_blocked(self, mac: str, blocked: bool, reason: str = "") -> bool:
        mac_norm = normalize_mac(mac)
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE devices SET blocked = ?, block_reason = ? WHERE mac = ?",
                (1 if blocked else 0, reason, mac_norm)
            )
            conn.commit()
            return cursor.rowcount > 0

    def update_custom_name(self, mac: str, custom_name: str, device_type: Optional[str] = None) -> bool:
        mac_norm = normalize_mac(mac)
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            if device_type:
                cursor.execute(
                    "UPDATE devices SET custom_name = ?, device_type = ? WHERE mac = ?",
                    (custom_name, device_type, mac_norm)
                )
            else:
                cursor.execute(
                    "UPDATE devices SET custom_name = ? WHERE mac = ?",
                    (custom_name, mac_norm)
                )
            conn.commit()
            return cursor.rowcount > 0

    def update_connection_info(self, mac: str, connection_type: str, network_name: Optional[str] = None) -> bool:
        """Cập nhật phương thức kết nối (Wi-Fi/Ethernet) và tên mạng."""
        mac_norm = normalize_mac(mac)
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            if network_name is not None:
                cursor.execute(
                    "UPDATE devices SET connection_type = ?, network_name = ? WHERE mac = ?",
                    (connection_type, network_name, mac_norm)
                )
            else:
                cursor.execute(
                    "UPDATE devices SET connection_type = ? WHERE mac = ?",
                    (connection_type, mac_norm)
                )
            conn.commit()
            return cursor.rowcount > 0

    def mark_offline_older_than(self, threshold_seconds: int = 300) -> List[Device]:
        """Đánh dấu OFFLINE các thiết bị không phản hồi trong ngưỡng thời gian."""
        threshold_dt = datetime.now() - timedelta(seconds=threshold_seconds)
        threshold_str = threshold_dt.strftime("%Y-%m-%d %H:%M:%S")
        
        changed_devices = []
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, ip, mac, hostname, vendor, device_type, custom_name, first_seen, last_seen, status, blocked, block_reason, connection_type, network_name
                FROM devices
                WHERE status = 'ONLINE' AND last_seen < ?
            """, (threshold_str,))
            rows = cursor.fetchall()
            for r in rows:
                dev = Device.from_row(r)
                dev.status = "OFFLINE"
                changed_devices.append(dev)

            cursor.execute("""
                UPDATE devices
                SET status = 'OFFLINE'
                WHERE status = 'ONLINE' AND last_seen < ?
            """, (threshold_str,))
            conn.commit()

        return changed_devices

    def get_device_counts(self) -> Dict[str, int]:
        """Lấy số lượng tổng quan cho Dashboard."""
        counts = {"total": 0, "online": 0, "offline": 0, "blocked": 0}
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM devices")
            counts["total"] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM devices WHERE status = 'ONLINE'")
            counts["online"] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM devices WHERE status = 'OFFLINE'")
            counts["offline"] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM devices WHERE blocked = 1")
            counts["blocked"] = cursor.fetchone()[0]
        return counts

    def get_network_distribution(self) -> Dict[str, int]:
        """Thống kê số lượng thiết bị theo mạng và phương thức kết nối."""
        dist = {
            "wifi": 0,
            "ethernet": 0,
            "wan": 0,
            "primary_net": 0,
            "secondary_net": 0,
            "other_net": 0
        }
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ip, connection_type FROM devices WHERE status = 'ONLINE'")
            for ip, ctype in cursor.fetchall():
                c = (ctype or "Wi-Fi").lower()
                if "ethernet" in c or "lan" in c:
                    dist["ethernet"] += 1
                elif "wan" in c:
                    dist["wan"] += 1
                else:
                    dist["wifi"] += 1

                if ip.startswith("192.168.1.") or ip.startswith("192.168.0."):
                    dist["primary_net"] += 1
                elif ip.startswith("192.168.110."):
                    dist["secondary_net"] += 1
                else:
                    dist["other_net"] += 1
        return dist

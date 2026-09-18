"""
Khởi tạo và quản lý cơ sở dữ liệu SQLite cho Network Manager.
"""

import sqlite3
import os
from typing import Optional
from core.logger import logger

class Database:
    _instance: Optional["Database"] = None

    def __init__(self, db_path: str = "data/network.db"):
        self.db_path = db_path
        self._ensure_dir()
        self.init_db()

    @classmethod
    def get_instance(cls, db_path: str = "data/network.db") -> "Database":
        if cls._instance is None:
            cls._instance = cls(db_path)
        return cls._instance

    def _ensure_dir(self):
        directory = os.path.dirname(self.db_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        """Tạo kết nối mới với timeout và row_factory linh hoạt."""
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        return conn

    def init_db(self):
        """Khởi tạo bảng devices và events theo thiết kế kiến trúc."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Bảng devices
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS devices (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ip TEXT NOT NULL,
                        mac TEXT NOT NULL UNIQUE,
                        hostname TEXT DEFAULT '',
                        vendor TEXT DEFAULT 'Unknown',
                        device_type TEXT DEFAULT 'Unknown',
                        custom_name TEXT DEFAULT '',
                        first_seen TEXT NOT NULL,
                        last_seen TEXT NOT NULL,
                        status TEXT DEFAULT 'ONLINE',
                        blocked INTEGER DEFAULT 0,
                        block_reason TEXT DEFAULT '',
                        connection_type TEXT DEFAULT 'Wi-Fi',
                        network_name TEXT DEFAULT ''
                    )
                """)

                # Tự động migration bổ sung cột cho database hiện hữu
                cursor.execute("PRAGMA table_info(devices)")
                cols = [r[1] for r in cursor.fetchall()]
                if "connection_type" not in cols:
                    cursor.execute("ALTER TABLE devices ADD COLUMN connection_type TEXT DEFAULT 'Wi-Fi'")
                if "network_name" not in cols:
                    cursor.execute("ALTER TABLE devices ADD COLUMN network_name TEXT DEFAULT ''")

                # Bảng events (lịch sử sự kiện)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        device_id INTEGER,
                        mac TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        description TEXT,
                        FOREIGN KEY (device_id) REFERENCES devices (id) ON DELETE SET NULL
                    )
                """)

                # Tạo index cho truy vấn nhanh
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_devices_mac ON devices(mac)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_devices_ip ON devices(ip)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_devices_status ON devices(status)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_mac ON events(mac)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)")

                conn.commit()
                logger.info(f"Khởi tạo cơ sở dữ liệu thành công tại {self.db_path}")
        except Exception as e:
            logger.error(f"Lỗi khởi tạo database: {e}")
            raise

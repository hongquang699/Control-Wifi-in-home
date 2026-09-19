"""
Dữ liệu mẫu khởi tạo cho thiết bị mạng, cấu hình, nhật ký và cảnh báo.
"""

INIT_DEVICES = [
    {
        "id": 1,
        "ip": "192.168.1.102",
        "mac": "38:B1:DB:54:A8:12",
        "hostname": "DESKTOP-DELL-XPS",
        "alias": "Dell XPS 15 (Workstation)",
        "vendor": "Dell Inc.",
        "device_type": "PC / Laptop",
        "first_seen": "2026-09-18 08:30:12",
        "last_seen": "Vừa xong",
        "status": "ONLINE",
        "blocked": False,
        "connection_medium": "📶 Wi-Fi 6 (5GHz)",
        "network_zone": "Wi-Fi Tổng (192.168.1.0/24)",
        "ping_ms": 1.5,
        "open_ports": [22, 443, 3389],
        "hop_path": ["192.168.1.102", "192.168.1.1", "203.113.131.1", "8.8.8.8"]
    },
    {
        "id": 2,
        "ip": "192.168.1.189",
        "mac": "3C:06:30:19:67:BC",
        "hostname": "MacBook-Pro-Nam",
        "alias": "MacBook Pro M2 (Nam)",
        "vendor": "Apple, Inc.",
        "device_type": "PC / Laptop",
        "first_seen": "2026-09-18 09:12:00",
        "last_seen": "Vừa xong",
        "status": "ONLINE",
        "blocked": False,
        "connection_medium": "📶 Wi-Fi 6 (5GHz)",
        "network_zone": "Wi-Fi Tổng (192.168.1.0/24)",
        "ping_ms": 2.1,
        "open_ports": [443, 5000],
        "hop_path": ["192.168.1.189", "192.168.1.1", "203.113.131.1", "8.8.8.8"]
    },
    {
        "id": 3,
        "ip": "192.168.1.115",
        "mac": "BC:D1:D3:45:90:E2",
        "hostname": "iPhone-15-Pro",
        "alias": "iPhone 15 Pro Max",
        "vendor": "Apple, Inc.",
        "device_type": "Smartphone",
        "first_seen": "2026-09-18 10:05:44",
        "last_seen": "Vừa xong",
        "status": "ONLINE",
        "blocked": False,
        "connection_medium": "📶 Wi-Fi 5GHz",
        "network_zone": "Wi-Fi Tổng (192.168.1.0/24)",
        "ping_ms": 4.8,
        "open_ports": [],
        "hop_path": ["192.168.1.115", "192.168.1.1", "203.113.131.1", "8.8.8.8"]
    },
    {
        "id": 4,
        "ip": "192.168.110.15",
        "mac": "50:C7:BF:88:21:44",
        "hostname": "Samsung-SmartTV-4K",
        "alias": "Samsung Smart 4K TV",
        "vendor": "Samsung Electronics",
        "device_type": "Smart TV",
        "first_seen": "2026-09-18 11:20:10",
        "last_seen": "Vừa xong",
        "status": "ONLINE",
        "blocked": False,
        "connection_medium": "🔌 Dây LAN 1Gbps",
        "network_zone": "Router Phụ (192.168.110.0/24)",
        "ping_ms": 1.2,
        "open_ports": [8080, 8001],
        "hop_path": ["192.168.110.15", "192.168.110.1", "192.168.1.1", "203.113.131.1", "8.8.8.8"]
    },
    {
        "id": 5,
        "ip": "192.168.110.45",
        "mac": "1C:3B:F3:11:AA:56",
        "hostname": "Ezviz-Cam-LivingRoom",
        "alias": "Ezviz Security Cam",
        "vendor": "Hangzhou Ezviz Software",
        "device_type": "Camera IP",
        "first_seen": "2026-09-18 07:15:00",
        "last_seen": "Vừa xong",
        "status": "ONLINE",
        "blocked": False,
        "connection_medium": "📶 Wi-Fi 2.4GHz",
        "network_zone": "Router Phụ (192.168.110.0/24)",
        "ping_ms": 5.4,
        "open_ports": [554, 8000],
        "hop_path": ["192.168.110.45", "192.168.110.1", "192.168.1.1", "203.113.131.1", "8.8.8.8"]
    },
    {
        "id": 6,
        "ip": "192.168.110.99",
        "mac": "DC:4F:22:90:34:11",
        "hostname": "Sonoff-SmartRelay-01",
        "alias": "Sonoff Smart Switch",
        "vendor": "Sonoff Technology",
        "device_type": "IoT Relay",
        "first_seen": "2026-09-18 08:00:00",
        "last_seen": "Vừa xong",
        "status": "ONLINE",
        "blocked": False,
        "connection_medium": "📶 Wi-Fi 2.4GHz",
        "network_zone": "Router Phụ (192.168.110.0/24)",
        "ping_ms": 6.8,
        "open_ports": [1883],
        "hop_path": ["192.168.110.99", "192.168.110.1", "192.168.1.1", "203.113.131.1", "8.8.8.8"]
    },
    {
        "id": 7,
        "ip": "192.168.1.205",
        "mac": "AA:BB:CC:11:22:33",
        "hostname": "Unknown-Device",
        "alias": "Thiết bị khả nghi",
        "vendor": "Unknown",
        "device_type": "Chưa rõ",
        "first_seen": "2026-09-18 12:40:00",
        "last_seen": "1 giờ trước",
        "status": "OFFLINE",
        "blocked": False,
        "connection_medium": "📶 Wi-Fi",
        "network_zone": "Wi-Fi Tổng (192.168.1.0/24)",
        "ping_ms": 0,
        "open_ports": [],
        "hop_path": ["192.168.1.205", "192.168.1.1", "203.113.131.1", "8.8.8.8"]
    }
]

INIT_SETTINGS = {
    "scan_interval": 60,
    "timeout_ms": 1500,
    "primary_subnet": "192.168.1.0/24",
    "secondary_subnet": "192.168.110.0/24",
    "router_ip": "192.168.1.1",
    "router_model": "tplink",
    "router_username": "admin",
    "auto_scan": True,
    "sync_defender": True,
    "confirm_block": True,
    "active_language": "vi"
}

INIT_LOGS = [
    {
        "id": 1,
        "time": "2026-09-19 10:15:20",
        "type": "JOIN",
        "ip": "192.168.1.189",
        "mac": "3C:06:30:19:67:BC",
        "details": "MacBook Pro M2 (Nam) kết nối vào mạng Wi-Fi Tổng (5GHz)"
    },
    {
        "id": 2,
        "time": "2026-09-19 10:10:05",
        "type": "SCAN",
        "ip": "192.168.1.0/24",
        "mac": "---",
        "details": "Hoàn tất chu kỳ quét mạng tự động. Phát hiện 6 thiết bị trực tuyến."
    },
    {
        "id": 3,
        "time": "2026-09-19 09:45:12",
        "type": "JOIN",
        "ip": "192.168.110.15",
        "mac": "50:C7:BF:88:21:44",
        "details": "Samsung Smart 4K TV kết nối dây LAN Gigabit qua Router Phụ"
    },
    {
        "id": 4,
        "time": "2026-09-19 08:30:00",
        "type": "LEFT",
        "ip": "192.168.1.205",
        "mac": "AA:BB:CC:11:22:33",
        "details": "Thiết bị khả nghi ngắt kết nối khỏi mạng (Offline)"
    }
]

INIT_ALERTS = [
    {
        "id": 1,
        "severity": "CRITICAL",
        "title": "Phát hiện ARP Spoofing từ IP lạ",
        "device": "192.168.1.250",
        "mac": "00:11:22:33:44:55",
        "description": "Phát hiện gói tin ARP giả mạo Gateway 192.168.1.1. Có nguy cơ tấn công Man-in-the-Middle.",
        "time": "10 phút trước",
        "action_required": "Chặn thiết bị ngay lập tức"
    },
    {
        "id": 2,
        "severity": "WARNING",
        "title": "Băng thông tải xuống vượt ngưỡng 90%",
        "device": "192.168.110.15 (Samsung Smart TV)",
        "mac": "50:C7:BF:88:21:44",
        "description": "Lưu lượng phát trực tuyến 4K đạt 65.2 MB/s liên tục trong 15 phút.",
        "time": "25 phút trước",
        "action_required": "Giới hạn QoS dải 110.0/24"
    }
]

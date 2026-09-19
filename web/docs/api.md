# Đặc Tả Network Manager REST API (API Specification)

Network Manager cung cấp hệ thống REST API chuẩn để truy xuất số liệu giám sát, điều khiển danh sách thiết bị và kiểm tra trạng thái mạng.

- **Base URL**: `http://localhost:8000/api/v1`
- **Content-Type**: `application/json`
- **Mã phản hồi chuẩn**: `200 OK`, `400 Bad Request`, `404 Not Found`, `500 Server Error`.

---

## 1. Hệ Thống & Kiểm Tra Trạng Thái

### GET `/health`
Kiểm tra tình trạng hoạt động của API Server.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-09-19T09:00:00Z"
}
```

---

### GET `/stats`
Lấy các chỉ số tổng quan mạng theo thời gian thực (Metrics).

**Response:**
```json
{
  "total_devices": 21,
  "online_devices": 18,
  "offline_devices": 3,
  "blocked_devices": 1,
  "traffic": {
    "download_speed_mbps": 24.5,
    "upload_speed_mbps": 8.2
  },
  "system": {
    "cpu_percent": 14.2,
    "ram_percent": 32.5,
    "uptime_seconds": 1231200,
    "uptime_display": "14d 6h 0m"
  }
}
```

---

## 2. Quản Lý Thiết Bị Mạng (Devices)

### GET `/devices`
Lấy danh sách tất cả các thiết bị đã phát hiện trong mạng nội bộ.

**Query Parameters:**
- `status`: Lọc theo `ONLINE`, `OFFLINE`, `BLOCKED` (tùy chọn).
- `subnet`: Lọc theo `primary` (192.168.1.x) hoặc `secondary` (192.168.110.x).
- `search`: Từ khóa tìm kiếm theo IP, MAC, Tên, Vendor.

**Response:**
```json
[
  {
    "id": 1,
    "ip": "192.168.1.102",
    "mac": "38:B1:DB:54:A8:12",
    "hostname": "DESKTOP-DELL-XPS",
    "alias": "Dell XPS 15 (Workstation)",
    "vendor": "Dell Inc.",
    "device_type": "PC / Laptop",
    "network_zone": "Wi-Fi Tổng (192.168.1.x)",
    "medium": "Wi-Fi",
    "latency_ms": 2,
    "status": "ONLINE",
    "first_seen": "2026-09-01T08:00:00Z",
    "last_seen": "2026-09-19T09:00:00Z"
  }
]
```

---

### POST `/devices/{mac}/block`
Gửi lệnh chặn phần cứng tới Router và thiết lập tường lửa cho địa chỉ MAC chỉ định.

**Request Body:**
```json
{
  "reason": "Vi phạm chính sách bảo mật mạng"
}
```

**Response:**
```json
{
  "success": true,
  "mac": "38:B1:DB:54:A8:12",
  "status": "BLOCKED",
  "message": "Đã chặn thiết bị thành công qua Router & Firewall."
}
```

---

### POST `/devices/{mac}/unblock`
Gỡ bỏ lệnh chặn thiết bị, khôi phục quyền truy cập mạng.

**Response:**
```json
{
  "success": true,
  "mac": "38:B1:DB:54:A8:12",
  "status": "ONLINE",
  "message": "Đã gỡ bỏ lệnh chặn thành công."
}
```

---

## 3. Cảnh Báo An Ninh & Sự Kiện (Alerts & Logs)

### GET `/alerts`
Lấy luồng cảnh báo an ninh mạng gần đây.

**Response:**
```json
[
  {
    "id": "alt-101",
    "level": "WARNING",
    "title": "Phát hiện thiết bị mới kết nối",
    "description": "Thiết bị mới IP: 192.168.1.134, MAC: 7C:49:EB:11:8A:92 (Xiaomi Communications) vừa tham gia mạng.",
    "timestamp": "2026-09-19T08:45:12Z"
  }
]
```

---

## 4. Danh Sách Gói Tải Xuống (Downloads)

### GET `/downloads`
Lấy danh sách các bản phân phối chính thức kèm dung lượng và mã băm SHA-256.

**Response:**
```json
[
  {
    "platform": "windows",
    "name": "Windows x64",
    "filename": "NetworkManager-v1.0.0-windows-x64.zip",
    "size_display": "45.2 MB",
    "release_date": "19/09/2026",
    "version": "1.0.0",
    "sha256": "8c5c757467ddd568debc7a2b3536fbfdf87604c603f917b546f002d240cace19",
    "url": "/downloads/windows/NetworkManager-v1.0.0-windows-x64.zip"
  }
]
```

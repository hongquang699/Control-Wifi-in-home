# Network Manager REST API Specification

Network Manager provides a standardized RESTful API to query network telemetry, manage device inventories, trigger hardware-level blocking, and monitor security events.

- **Base URL**: `http://localhost:8080/api/v1`
- **Content-Type**: `application/json`
- **Standard HTTP Codes**: `200 OK`, `400 Bad Request`, `403 Forbidden`, `404 Not Found`, `429 Too Many Requests`, `500 Server Error`.

---

## 1. System Health & Real-Time Metrics

### GET `/health`
Verifies the operational status and uptime of the API server.

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
Retrieves aggregated network statistics, active client counts, throughput, and host resource utilization.

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

## 2. Device Management & Access Control

### GET `/devices`
Returns the full inventory of detected devices across all local network subnets.

**Query Parameters:**
- `status`: Filter by state (`ONLINE`, `OFFLINE`, `BLOCKED`) (optional).
- `subnet`: Filter by network zone (`primary` for 192.168.1.x, `secondary` for 192.168.110.x).
- `search`: Case-insensitive text filter matching IP, MAC, hostname, or vendor.

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
    "network_zone": "Primary Wi-Fi (192.168.1.x)",
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
Enforces hardware MAC filtering on the router adapter and configures host firewall isolation rules for the specified MAC address.

**Request Headers:**
- `X-CSRF-Token`: `<valid_csrf_token>`

**Request Body:**
```json
{
  "reason": "Security policy violation"
}
```

**Response:**
```json
{
  "success": true,
  "mac": "38:B1:DB:54:A8:12",
  "status": "BLOCKED",
  "message": "Device successfully blocked via Router ACL and Host Firewall."
}
```

---

### POST `/devices/{mac}/unblock`
Removes isolation rules from the router and host firewall, restoring network access.

**Request Headers:**
- `X-CSRF-Token`: `<valid_csrf_token>`

**Response:**
```json
{
  "success": true,
  "mac": "38:B1:DB:54:A8:12",
  "status": "ONLINE",
  "message": "Device successfully unblocked."
}
```

---

## 3. Security Alerts & Audit Logging

### GET `/alerts`
Retrieves recent network security alerts, rogue device notifications, and ARP anomaly reports.

**Response:**
```json
[
  {
    "id": "alt-101",
    "level": "WARNING",
    "title": "New unclassified device detected",
    "description": "Device IP: 192.168.1.134, MAC: 7C:49:EB:11:8A:92 (Xiaomi Communications) joined the network.",
    "timestamp": "2026-09-19T08:45:12Z"
  }
]
```

---

## 4. Software Distribution Packages

### GET `/downloads`
Lists official release packages, architectures, download URLs, and verified SHA-256 integrity checksums.

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

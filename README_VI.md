# NETWORK MANAGER — Hệ Thống Quản Lý & Giám Sát Mạng Nội Bộ Chuyên Nghiệp

<div align="center">

[![Tiếng Việt](https://img.shields.io/badge/🇻🇳%20Đang%20xem-README%20Tiếng%20Việt-crimson?style=for-the-badge&logo=github)](README_VI.md)
[![English Documentation](https://img.shields.io/badge/🇬🇧%20Bấm%20để%20xem-English%20README-2563eb?style=for-the-badge&logo=github)](README.md)

### 📌 [👉 Click here to switch to English Documentation (README.md) 👈](README.md)

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/GUI-PySide6%20Qt6-brightgreen.svg)](https://pypi.org/project/PySide6/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Security](https://img.shields.io/badge/Security-Multi--Layer%20WAF%20%2B%20CSP-red.svg)](#7-k%E1%BB%B9-thu%E1%BA%ADt-b%E1%BA%A3o-m%E1%BA%ADt-api-7-core-api-security-techniques)
[![English](https://img.shields.io/badge/Language-English%20Version-blue.svg?logo=readme)](README.md)

</div>

> [!NOTE]
> 🇬🇧 **Looking for English documentation?** Please visit the main **[README.md (English Version)](README.md)**.

---

## 🌟 Tính Năng Nổi Bật (Key Features)

### 1. Phân Hệ Ứng Dụng Desktop (Desktop App)
- **Động cơ quét kép (Hybrid Scanner)**: Tự động nhận diện card mạng, Gateway và subnet (`/24`, `/16`). Quét siêu tốc qua Nmap ARP ping kết hợp cơ chế fallback Native ARP + ICMP Ping đa luồng khi không có Nmap hoặc chạy quyền người dùng thông thường.
- **Nhận diện thiết bị thông minh qua MAC OUI**: Tích hợp cơ sở dữ liệu OUI hàng chục nghìn nhà sản xuất (Apple, Samsung, Intel, Dell, TP-Link, Xiaomi, Espressif IoT, Hikvision, Realtek,...), phân loại tự động thành 6 nhóm thiết bị.
- **Phân tích Topo mạng & Internet Hop Path**: Tự động bóc tách dải Wi-Fi Tổng (192.168.1.x) và Router Phụ (192.168.110.x), xác định kết nối Wi-Fi 5GHz hay dây LAN, vẽ sơ đồ lộ trình hop từ thiết bị ra Internet.
- **Giám sát lưu lượng & Biểu đồ sóng động**: Đo tốc độ Download / Upload thời gian thực, hiển thị biểu đồ sóng canvas mượt mà.
- **Chặn thiết bị cấp phần cứng (Access Control)**:
  - **Router Adapters**: Đẩy quy tắc chặn MAC Filtering / ACL trực tiếp đến router phần cứng TP-Link, OpenWrt, MikroTik.
  - **Mock Mode**: Chế độ giả lập an toàn để thử nghiệm tính năng mà không cần can thiệp router thật.
  - **Tường lửa Windows 2 chiều**: Tự động tạo rule Inbound & Outbound trên máy quản trị.
- **Giao diện Modern Cyber Dark-Tech & Vector SVG Icons**: Thay thế 100% emoji văn bản bằng bộ hơn 37 biểu tượng vector SVG sắc nét (phong cách Flaticon / Cyber Minimalist), hỗ trợ co giãn High-DPI và bộ đệm Icon Cache tối ưu hiệu năng.
- **Cơ sở dữ liệu SQLite & Kiểm toán an ninh**: Lưu trữ lịch sử `first_seen`, `last_seen`, tự động ghi nhật ký audit log cho các sự kiện gia nhập, ngắt kết nối, đổi IP, chặn/bỏ chặn.

### 2. Phân Hệ Web Portal & REST API Server (Web Suite)
- **Kiến trúc SPA 8-trong-1 mô đun hóa**: 8 trang chức năng (*Trang chủ, Giới thiệu, Tính năng, Dashboard Demo Live, Tải xuống, Tài liệu, Tin tức, Liên hệ*) được tách thành các component HTML và module JS độc lập.
- **Bố cục hiển thị mở rộng (Full-Width Responsive)**: Sử dụng thiết kế `max-w-screen-2xl` thoáng đãng, tận dụng tối đa chiều rộng màn hình lớn, không bị bó hẹp dồn giữa.
- **Bộ icon vector Flaticon Uicons hiện đại**: Thay thế hoàn toàn raw emoji bằng các icon vector tinh tế, căn chỉnh chuẩn xác theo hệ màu Dark Tech.
- **Dashboard Demo tương tác trực tiếp**: Mô phỏng đầy đủ danh sách thiết bị, thao tác chặn/bỏ chặn trực tiếp, biểu đồ sóng thời gian thực, nhật ký sự kiện và cảnh báo an ninh.
- **Trung tâm phân phối cài đặt**: Cung cấp các gói phát hành cho Windows x64, Linux x64, macOS Apple Silicon kèm mã băm SHA-256 xác thực toàn vẹn.

---

## 🌐 Song Ngữ Toàn Diện (Bilingual Support)

Hệ thống hỗ trợ **100% song ngữ Tiếng Việt 🇻🇳 và English 🇬🇧** xuyên suốt cả ứng dụng Desktop lẫn trang Web:
- **Chuyển đổi tức thì**: Nhấp vào nút **Tiếng Việt / English** trên thanh điều hướng để đổi ngôn ngữ ngay lập tức mà không cần tải lại trang.
- **Lưu trữ tùy chọn**: Tự động lưu trạng thái vào `localStorage` (`nm_lang`), duy trì ngôn ngữ người dùng đã chọn qua các phiên làm việc.
- **Bao phủ toàn diện**: Chuyển đổi từ tiêu đề, nội dung thẻ tính năng, nghiên cứu điển hình (Case Studies), bảng thông số, hướng dẫn cài đặt, cho đến biểu mẫu và thông báo hệ thống.

---

## 🛡️ 7 Kỹ Thuật Bảo Mật API (7 Core API Security Techniques)

Hệ thống đáp ứng trọn vẹn và chuyên sâu **7 kỹ thuật bảo mật API tiêu chuẩn doanh nghiệp**:

```text
               MA TRẬN 7 KỸ THUẬT BẢO MẬT API (ENTERPRISE API DEFENSE)

 ┌───┬──────────────────────────────────┬─────────────────────────────────────────────────────────────┐
 │ # │ KỸ THUẬT BẢO MẬT                │ CƠ CHẾ TRIỂN KHAI TRONG DỰ ÁN                               │
 ├───┼──────────────────────────────────┼─────────────────────────────────────────────────────────────┤
 │ 1 │ Rate Limiting                    │ Sliding-Window Log + Auto-Jail IP phạt theo cấp số nhân     │
 │ 2 │ CORS (Cross-Origin Sharing)      │ Whitelist Origin nghiêm ngặt + Xử lý Preflight OPTIONS RFC  │
 │ 3 │ SQL & NoSQL Injection            │ WAF Regex Filter + Parameterized Queries 100% SQLite DAO    │
 │ 4 │ Firewalls                        │ L7 Web Application Firewall (WAF) + L3/4 Host Firewall      │
 │ 5 │ VPNs (Virtual Private Network)   │ VPN Network Guard (WireGuard, OpenVPN, Tailscale CGNAT)     │
 │ 6 │ CSRF (Cross-Site Request Forgery)│ Cryptographic Double-Submit Token + Header X-CSRF-Token     │
 │ 7 │ XSS (Cross-Site Scripting)       │ Deep Recursive Sanitizer + Strict CSP + Anti-Tamper Guard   │
 └───┴──────────────────────────────────┴─────────────────────────────────────────────────────────────┘
```

1. **Rate Limiting (`web/security/rate_limiter.py`)**: Giới hạn tần suất request theo IP (100 req/min cho API, 5 req/min cho Login, 10 req/min cho Download). Tự động kích hoạt cơ chế **Auto-Jail** cách ly IP vi phạm với thời gian khóa tăng dần (60s -> 300s -> 1800s).
2. **CORS - Cross-Origin Resource Sharing (`web/security/cors.py`)**: Kiểm soát xuất xứ Origin qua danh sách whitelist được cấp phép; xử lý yêu cầu Preflight `OPTIONS` chuẩn RFC; cô lập Cookie/Token không bao giờ dùng Wildcard `*` khi bật `Access-Control-Allow-Credentials`.
3. **SQL & NoSQL Injection (`web/security/waf.py` & `app/database/`)**: Bộ quy tắc WAF chặn đứng các mẫu SQLi (`UNION SELECT`, stacked queries, `' OR 1=1`) và NoSQLi (`$where`, `$gt`, `$ne`, `$regex`, MongoDB operators); toàn bộ truy vấn cơ sở dữ liệu SQLite sử dụng 100% Parameterized Statements (`?` placeholder).
4. **Firewalls (`web/security/waf.py` & `app/security/firewall.py`)**: Phòng thủ 2 tầng: Tường lửa ứng dụng L7 WAF kiểm tra payload theo thời gian thực kết hợp Tường lửa máy trạm L3/4 (Windows Defender Firewall tự động tạo rule Inbound/Outbound qua `safe_run_command`).
5. **VPNs & Private Network Restriction (`web/security/vpn_guard.py`)**: Phân định chính xác các kênh kết nối từ VPN Tunnel (WireGuard `10.8.0.0/16`, Tailscale `100.64.0.0/10`) và mạng nội bộ riêng tư (RFC 1918). Tự động khóa các API quản trị nhạy cảm (`/api/v1/settings`, `/api/v1/backup`, `/api/v1/auth/users`) nếu truy cập từ Public Internet WAN mà không có kết nối VPN.
6. **CSRF - Cross-Site Request Forgery (`web/security/csrf.py`)**: Triển khai giải pháp Double-Submit Cookie kết hợp header `X-CSRF-Token`, token được sinh bằng `secrets.token_hex(32)`, ràng buộc thời gian sống (TTL) và xác thực bắt buộc trên toàn bộ phương thức POST, PUT, DELETE.
7. **XSS - Cross-Site Scripting (`web/security/sanitizer.py`, `headers.py`, `anti_tamper.js`)**: Làm sạch đệ quy JSON, mã hóa thực thể HTML (`&lt;`, `&gt;`), thiết lập Content-Security-Policy (CSP) loại bỏ `eval`, cùng động cơ DOM MutationObserver phát hiện và triệt tiêu thẻ script lạ chèn vào trang.

---

## 📂 Cấu Trúc Dự Án (Directory Structure)

```text
Control-wifi/
├── run_app.bat                     # 1-Click khởi chạy ứng dụng Desktop
├── run_admin.bat                   # 1-Click chạy Desktop với quyền Administrator
├── serve_website.bat               # 1-Click khởi chạy Web & REST API Server (port 8080)
├── README.md                       # Tài liệu hướng dẫn sử dụng tiếng Anh (Primary)
├── README_VI.md                    # Tài liệu hướng dẫn sử dụng tiếng Việt
├── NOTES.md                        # Ghi chú kỹ thuật & kiến trúc hệ thống
│
├── app/                            # PHÂN HỆ DESKTOP (PYTHON / PYSIDE6)
│   ├── main.py                     # Điểm khởi chạy chính ứng dụng (GUI / CLI)
│   ├── requirements.txt            # Thư viện phụ thuộc cho Desktop
│   ├── NetworkManager.spec         # File cấu hình đóng gói PyInstaller
│   ├── core/                       # Lõi quét mạng, phân tích topo, đo băng thông, i18n
│   ├── gui/                        # Giao diện người dùng PySide6 hiện đại
│   ├── router/                     # Bộ điều khiển Router (TP-Link, OpenWrt, MikroTik, Mock)
│   ├── security/                   # GÓI BẢO MẬT ĐỘC LẬP CHO DESKTOP
│   │   ├── __init__.py             # Export facade an toàn
│   │   ├── safe_exec.py            # Chống Command Injection, kiểm tra IP/MAC
│   │   ├── vault.py                # Két mã hóa mật khẩu theo phần cứng máy tính
│   │   ├── zeroize.py              # Xóa sạch bộ nhớ đệm RAM chứa mật khẩu sau khi dùng
│   │   ├── process_guard.py        # Giám sát toàn vẹn tiến trình, chống Debug & DLL Hook
│   │   ├── dns_guard.py            # Giám sát đầu độc DNS, phát hiện máy chủ DHCP DNS lạ
│   │   ├── rbac.py                 # Kiểm soát truy cập dựa trên vai trò (RBAC)
│   │   ├── integrity.py            # Kiểm tra toàn vẹn file cấu hình & DB (HMAC-SHA256)
│   │   ├── arp_guard.py            # Phát hiện ARP Poisoning / Spoofing
│   │   ├── firewall.py             # Tường lửa Windows 2 chiều & Cách ly khẩn cấp (Quarantine)
│   │   ├── blocker.py              # Bộ điều phối chặn đa tầng tích hợp RBAC
│   │   └── audit_logger.py         # Nhật ký kiểm toán pháp chứng
│   ├── services/                   # Dịch vụ định danh OUI, background scheduler
│   ├── database/                   # SQLite database & DAO
│   ├── config/                     # File cấu hình JSON
│   ├── assets/                     # Icon vector SVG, logo phần mềm
│   └── tests/                      # Bộ kiểm thử (test_all.py, test_app_security.py)
│
└── web/                            # PHÂN HỆ WEB & REST API SERVER
    ├── backend/                    # Máy chủ HTTP đa luồng bảo mật
    │   ├── main.py                 # Điểm khởi động web server
    │   ├── server/                 # Handler xử lý request & static file an toàn
    │   ├── api/                    # Router định tuyến REST API (/api/v1/...)
    │   ├── middleware/             # Middleware điều phối
    │   ├── services/               # Dịch vụ tải file an toàn & audit log
    │   └── tests/                  # Bộ kiểm thử (test_security.py, test_web_security.py)
    ├── security/                   # GÓI BẢO MẬT ĐỘC LẬP CHO WEB SERVER
    │   ├── __init__.py             # Export facade an toàn
    │   ├── crypto.py               # PBKDF2-HMAC-SHA256 (600,000 rounds) & constant-time
    │   ├── waf.py                  # WAF nâng cao (SQLi, NoSQLi, SSRF, SSTI, JNDI, RCE)
    │   ├── rate_limiter.py         # Sliding-Window Rate Limiter & Auto-Jail
    │   ├── account_lockout.py      # Khóa tài khoản chống brute-force phân tán botnet
    │   ├── headers.py              # Tiêu đề an ninh quân sự (CSP, HSTS, COOP, COEP, CORP)
    │   ├── request_guard.py        # Giới hạn kích thước payload (< 2MB) & MIME type
    │   ├── data_masker.py          # Che giấu dữ liệu nhạy cảm (passwords, tokens, secret keys)
    │   ├── csrf.py                 # Chống tấn công CSRF (Double-Submit Token)
    │   ├── cors.py                 # Quản lý CORS, whitelist origins & RFC preflight
    │   ├── vpn_guard.py            # Thẩm định VPN & bảo vệ route nhạy cảm
    │   ├── sanitizer.py            # Làm sạch dữ liệu JSON, ngăn Prototype Pollution
    │   └── audit.py                # Chained-Hash Audit Logger (Blockchain-style log)
    ├── html/                       # Giao diện Web SPA (8 trang component)
    ├── js/                         # Bộ mã JavaScript SPA mô đun hóa
    ├── css/                        # Stylesheet, Dark Tech theme & Glassmorphism
    ├── downloads/                  # Thư mục chứa file cài đặt phân phối
    └── scripts/                    # Scripts build tự động hóa
```

---

## 🚀 Hướng Dẫn Cài Đặt & Sử Dụng

### Yêu Cầu Hệ Thống
- Hệ điều hành: Windows 10 / 11, Linux (Ubuntu, Debian, Fedora), hoặc macOS.
- Python: Phiên bản 3.12 trở lên.
- Nmap *(khuyến nghị)*: Tải tại [nmap.org](https://nmap.org/download.html) để đạt tốc độ quét ARP cao nhất.

### 1. Khởi Chạy Ứng Dụng Desktop
```powershell
# Bước 1: Tạo và kích hoạt môi trường ảo
python -m venv venv
.\venv\Scripts\activate

# Bước 2: Cài đặt các thư viện cần thiết
pip install -r app/requirements.txt

# Bước 3: Khởi chạy giao diện Desktop
python app/main.py
```
*Hoặc nhấp đúp tệp **`run_app.bat`** (hoặc **`run_admin.bat`** để chạy với quyền quản trị viên).*

### 2. Khởi Chạy Trang Web & REST API Server
```powershell
# Khởi chạy server tại cổng 8080
python web/backend/main.py 8080
```
*Hoặc nhấp đúp tệp **`serve_website.bat`** trên Windows.*

Sau khi khởi chạy, truy cập trình duyệt tại: **`http://localhost:8080/`**

---

## 🛠️ Trình Biên Dịch Tự Động Hóa (Build System)

Dự án áp dụng mô hình phát triển phân tách mô-đun: bạn chỉ cần chỉnh sửa các file nhỏ trong `web/html/components/` và `web/js/modules/`. Khi muốn cập nhật trang web phát hành:

```powershell
python web/scripts/build_all.py
```
Script sẽ tự động:
1. Đọc và ghép nối các component HTML thành [`web/html/index.html`](web/html/index.html) tinh gọn.
2. Ghép nối toàn bộ module JS thành [`web/js/app.js`](web/js/app.js).
3. Đảm bảo cấu trúc chuẩn hóa, không có code thừa và đồng bộ song ngữ.

---

## 🧪 Kiểm Thử Hệ Thống (Automated Testing)

Dự án có đầy đủ unit test cho cả phân hệ Desktop và Web:

```powershell
# Kiểm thử toàn diện Desktop (Discovery, Database, Blocker, Topology, Security)
.\venv\Scripts\python.exe -m unittest discover -s app/tests -p "test_*.py"
# Kết quả: 16/16 PASS

# Kiểm thử bảo mật Web Backend (7 API Security Techniques, WAF, RateLimit, CORS, VPN, CSRF)
.\venv\Scripts\python.exe -m unittest discover -s web/backend/tests -p "test_*.py"
# Kết quả: 23/23 PASS
```

---

## ⚖️ Lưu Ý Pháp Lý & Trách Nhiệm Sử Dụng (Legal Notice)

> [!IMPORTANT]
> Phần mềm **Network Manager** được phát triển phục vụ công tác quản trị mạng được ủy quyền, giám sát an ninh hạ tầng và nghiên cứu học tập trên hệ thống mạng thuộc quyền sở hữu hợp pháp. Mọi hành vi quét mạng, can thiệp hoặc chặn truy cập trên hạ tầng không được phép đều bị nghiêm cấm theo quy định pháp luật.

---

**© 2026 Network Manager Engineering Team. Phát hành theo giấy phép MIT License.**

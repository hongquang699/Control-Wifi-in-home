# NETWORK MANAGER — Hệ Thống Quản Lý & Giám Sát Mạng Nội Bộ Chuyên Nghiệp

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/GUI-PySide6%20Qt6-brightgreen.svg)](https://pypi.org/project/PySide6/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Security](https://img.shields.io/badge/Security-Multi--Layer%20WAF%20%2B%20CSP-red.svg)](#h%E1%BB%87-th%E1%BB%91ng-b%E1%BA%A3o-m%E1%BA%ADt-%C4%91a-l%E1%BB%9Bp)
[![Bilingual](https://img.shields.io/badge/Bilingual-Ti%E1%BA%BFng%20Vi%E1%BB%87t%20%7C%20English-blueviolet.svg)](#song-ng%E1%BB%AF-to%C3%A0n-di%E1%BB%87n-bilingual-support)

Hệ thống quét mạng, phân tích topo đa tầng, theo dõi băng thông thời gian thực và quản lý kiểm soát truy cập cấp phần cứng Router dành cho quản trị viên mạng và gia đình. Phát triển bằng **Python 3.12**, **PySide6 (Qt6)**, **Nmap / Native ARP Ping**, **SQLite**, cùng hệ sinh thái **Web SPA 8-trang & REST API Server** bảo mật đa lớp.

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

## 🛡️ Hệ Thống Bảo Mật Độc Lập & Chuyên Sâu (Dedicated Security Architecture)

Hệ thống được trang bị 2 gói bảo mật chuyên biệt độc lập cho cả **Web Server (`web/security/`)** và **Desktop App (`app/security/`)**, đáp ứng các tiêu chuẩn phòng thủ chiều sâu (Defense-in-Depth) theo khuyến nghị của OWASP và CIS Benchmark:

```text
               KIẾN TRÚC PHÒNG THỦ ĐA TẦNG (DEFENSE-IN-DEPTH)

  ┌───────────────────────────────────────────────┐  ┌───────────────────────────────────────────────┐
  │         WEB SECURITY SUITE (web/security/)    │  │         APP SECURITY SUITE (app/security/)    │
  ├───────────────────────────────────────────────┤  ├───────────────────────────────────────────────┤
  │ 1. Enterprise Security Headers (CSP, HSTS...) │  │ 1. Safe Exec Engine (Zero Command Injection)  │
  │ 2. OWASP Top 10 WAF (SQLi, XSS, RCE, Bots)    │  │ 2. Hardware-Bound Vault (MachineGuid Encrypt) │
  │ 3. Sliding-Window Rate Limiter & Auto-Jail    │  │ 3. Granular RBAC (Admin, Operator, Viewer)    │
  │ 4. Anti-CSRF Token / Double-Submit Cookies    │  │ 4. File & DB HMAC-SHA256 Integrity Guard      │
  │ 5. Deep Recursive Input Sanitizer             │  │ 5. Anti-ARP Spoofing & Poisoning Monitor      │
  │ 6. PBKDF2-HMAC-SHA256 (600,000 rounds) Crypto │  │ 6. Bidirectional Windows Host Firewall        │
  │ 7. Chained-Hash Audit Logger (Tamper-evident) │  │ 7. Multi-Layer Blocker & Forensic Audit Logger│
  └───────────────────────────────────────────────┘  └───────────────────────────────────────────────┘
```

### 1. Web Security Suite (`web/security/`)
- **`waf.py` - OWASP Top 10 WAF Engine**: Phát hiện và chặn đứng tấn công SQL Injection, Cross-Site Scripting (XSS), Path Traversal (`../`, `..\\`), Remote Code Execution (RCE), và các công cụ quét tự động độc hại (sqlmap, nikto, wpscan,...).
- **`rate_limiter.py` - Sliding-Window Rate Limiter & Auto-Jail**: Giới hạn tần suất request theo IP (100 req/min cho API, 10 req/min cho download). Khi phát hiện dấu hiệu tấn công dồn dập hoặc vi phạm WAF liên tiếp, hệ thống tự động đưa IP vào danh sách **Auto-Jail** (cấm truy cập với thời gian phạt tăng theo cấp số nhân).
- **`headers.py` - Military-Grade Security Headers**: Thiết lập Content Security Policy (CSP) nghiêm ngặt (whitelist tài nguyên), HSTS (`includeSubDomains; preload`), X-Frame-Options (`DENY`), X-Content-Type-Options (`nosniff`), Referrer-Policy và Cache-Control chống rò rỉ dữ liệu.
- **`csrf.py` - Anti-CSRF Guard**: Xác thực token bảo mật ngẫu nhiên cao (Double-Submit Cookie & Header `X-CSRF-Token`) trên toàn bộ các endpoint thay đổi trạng thái (POST, PUT, DELETE).
- **`sanitizer.py` - Deep Recursive Sanitizer**: Làm sạch sâu dữ liệu đầu vào JSON và biểu mẫu, loại bỏ null bytes (`\x00`), chống Prototype Pollution (`__proto__`, `constructor`), và mã hóa HTML an toàn.
- **`crypto.py` - PBKDF2-HMAC-SHA256 & Constant-Time Crypto**: Băm mật khẩu với 600,000 vòng lặp kèm salt ngẫu nhiên 32-byte, sinh token bảo mật bằng `secrets`, ký và xác thực HMAC dữ liệu, so sánh thời gian bất biến `hmac.compare_digest` chống Timing Attacks.
- **`audit.py` - Chained-Hash Audit Logger**: Nhật ký kiểm toán bảo mật với cơ chế băm xâu chuỗi (tương tự Blockchain log), mỗi bản ghi liên kết mã băm của bản ghi trước đó, hỗ trợ hàm `verify_log_integrity()` phát hiện mọi hành vi sửa đổi hoặc xóa nhật ký.

### 2. App Security Suite (`app/security/`)
- **`safe_exec.py` - Safe Subprocess Execution**: Loại bỏ hoàn toàn lỗ hổng Command Injection bằng cách cấm tuyệt đối `shell=True`, sử dụng danh sách tham số dạng list, kiểm tra whitelist nhị phân (`netsh`, `route`, `arp`, `ping`, `nmap`), và xác thực chặt chẽ IP / MAC qua regex và thư viện chuẩn `ipaddress`.
- **`vault.py` - Hardware-Bound Credentials Vault**: Mã hóa mật khẩu đăng nhập router bằng khóa dẫn xuất từ thông tin định danh phần cứng máy tính (Windows `MachineGuid` kết hợp entropy hệ thống), ngăn chặn đánh cắp file cấu hình mang sang máy khác giải mã.
- **`rbac.py` - Role-Based Access Control (RBAC)**: Phân quyền chặt chẽ 3 cấp độ (*Admin, Operator, Viewer*). Cung cấp các decorator `@require_role` và `@require_permission` kiểm soát quyền chặn/bỏ chặn thiết bị, quét mạng và thay đổi cấu hình.
- **`integrity.py` - File & Database HMAC-SHA256 Guard**: Giám sát tính toàn vẹn của cơ sở dữ liệu `network.db`, cấu hình `config.json`, và danh sách router `routers.json`, tự động phát hiện nếu file bị can thiệp trái phép.
- **`arp_guard.py` - Anti-ARP Spoofing Monitor**: Giám sát bảng ARP của Windows theo thời gian thực, phát hiện hành vi đầu độc ARP (thay đổi MAC Gateway bất thường hoặc trùng lặp địa chỉ MAC trên mạng).
- **`firewall.py` - Bidirectional Host Firewall**: Điều khiển tường lửa Windows (Inbound & Outbound) thông qua động cơ thực thi an toàn `safe_run_command`.
- **`blocker.py` & `audit_logger.py` - Multi-Layer Access Control & Forensic Log**: Tích hợp kiểm tra quyền RBAC, giải mã an toàn từ Vault, thực thi chặn đa tầng (Router ACL + Host Firewall), và ghi log pháp chứng `data/audit_compliance.log`.

---

## 📂 Cấu Trúc Dự Án (Directory Structure)

```text
Control-wifi/
├── run_app.bat                     # 1-Click khởi chạy ứng dụng Desktop
├── run_admin.bat                   # 1-Click chạy Desktop với quyền Administrator
├── serve_website.bat               # 1-Click khởi chạy Web & REST API Server (port 8080)
├── README.md                       # Tài liệu hướng dẫn sử dụng
│
├── app/                            # PHÂN HỆ DESKTOP (PYTHON / PYSIDE6)
│   ├── main.py                     # Điểm khởi chạy chính ứng dụng (GUI / CLI)
│   ├── requirements.txt            # Thư viện phụ thuộc cho Desktop
│   ├── NetworkManager.spec        # File cấu hình đóng gói PyInstaller
│   ├── core/                       # Lõi quét mạng, phân tích topo, đo băng thông, i18n
│   ├── gui/                        # Giao diện người dùng PySide6 hiện đại
│   ├── router/                     # Bộ điều khiển Router (TP-Link, OpenWrt, MikroTik, Mock)
│   ├── security/                   # GÓI BẢO MẬT ĐỘC LẬP CHO DESKTOP
│   │   ├── __init__.py             # Export facade an toàn
│   │   ├── safe_exec.py            # Chống Command Injection, kiểm tra IP/MAC
│   │   ├── vault.py                # Két mã hóa mật khẩu theo phần cứng máy tính
│   │   ├── rbac.py                 # Kiểm soát truy cập dựa trên vai trò (RBAC)
│   │   ├── integrity.py            # Kiểm tra toàn vẹn file cấu hình & DB (HMAC-SHA256)
│   │   ├── arp_guard.py            # Phát hiện ARP Poisoning / Spoofing
│   │   ├── firewall.py             # Tường lửa Windows 2 chiều an toàn
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
    │   ├── waf.py                  # OWASP Top 10 WAF (SQLi, XSS, RCE, Bot Filter)
    │   ├── rate_limiter.py         # Sliding-Window Rate Limiter & Auto-Jail
    │   ├── headers.py              # Military-Grade Security Headers (CSP, HSTS)
    │   ├── csrf.py                 # Chống tấn công CSRF (Double-Submit Token)
    │   ├── sanitizer.py            # Làm sạch dữ liệu JSON, ngăn Prototype Pollution
    │   └── audit.py                # Chained-Hash Audit Logger (Blockchain-style log)
    ├── html/                       # Giao diện Web SPA (8 trang component)
    ├── js/                         # Bộ mã JavaScript SPA mô đun hóa
    ├── css/                        # Stylesheet, Dark Tech theme & Glassmorphism
    ├── downloads/                  # Thư mục chứa file cài đặt phân phối
    └── scripts/                    # Scripts build tự động hóa
```
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
# Kiểm thử toàn diện Desktop (Discovery, Database, Blocker, Topology)
.\venv\Scripts\python.exe -m unittest app/tests/test_all.py
# Kết quả: 9/9 PASS

# Kiểm thử bảo mật Web Backend (WAF, Rate Limiting, CSP, Path Traversal)
python -m unittest web/backend/tests/test_security.py
# Kết quả: 10/10 PASS
```

---

## ⚖️ Lưu Ý Pháp Lý & Trách Nhiệm Sử Dụng (Legal Notice)

> [!IMPORTANT]
> Phần mềm **Network Manager** được phát triển phục vụ công tác quản trị mạng được ủy quyền, giám sát an ninh hạ tầng và nghiên cứu học tập trên hệ thống mạng thuộc quyền sở hữu hợp pháp. Mọi hành vi quét mạng, can thiệp hoặc chặn truy cập trên hạ tầng không được phép đều bị nghiêm cấm theo quy định pháp luật.

---

**© 2026 Network Manager Engineering Team. Phát hành theo giấy phép MIT License.**

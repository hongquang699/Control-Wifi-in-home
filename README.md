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

## 🛡️ Hệ Thống Bảo Mật Đa Lớp (Multi-Layer Security)

Máy chủ Web & REST API tích hợp kiến trúc bảo mật nhiều tầng phòng thủ:

```text
INTERNET
   │
   ▼
┌───────────────────────────────────────────────┐
│ Lớp 1: HTTP Security Headers (CSP, HSTS, ...)  │
├───────────────────────────────────────────────┤
│ Lớp 2: WAF (Chống SQLi, XSS, Path Traversal)  │
├───────────────────────────────────────────────┤
│ Lớp 3: Rate Limiting (Sliding Window IP Guard)│
├───────────────────────────────────────────────┤
│ Lớp 4: REST API Router & Parameter Validator   │
├───────────────────────────────────────────────┤
│ Lớp 5: Secure Static File Server              │
├───────────────────────────────────────────────┤
│ Lớp 6: Audit Logging Engine (web/logs/audit/) │
└───────────────────────────────────────────────┘
```

1. **Content Security Policy (CSP)**: Whitelist an toàn cho tài nguyên nội bộ, Google Fonts, Tailwind CDN, Flaticon CDN. Ngăn chặn triệt để tấn công XSS và chèn script lạ.
2. **Web Application Firewall (WAF)**: Tự động kiểm tra payload và URL query, phát hiện và chặn đứng SQL Injection, XSS, Path Traversal (`../`), và Command Injection.
3. **Sliding-Window Rate Limiter**: Giới hạn tần suất request theo IP (API chung: 100 req/min, Tải file: 10 req/min).
4. **Audit Logging**: Ghi nhật ký đầy đủ sự kiện truy cập, chặn WAF, vượt ngưỡng rate limit vào file audit an toàn.

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
│   ├── security/                   # Module tích hợp Windows Host Firewall
│   ├── services/                   # Dịch vụ định danh OUI, background scheduler
│   ├── database/                   # SQLite database & DAO
│   ├── config/                     # File cấu hình JSON
│   ├── assets/                     # Icon, logo phần mềm
│   └── tests/                      # Bộ kiểm thử ứng dụng (test_all.py)
│
└── web/                            # PHÂN HỆ WEB & REST API SERVER
    ├── backend/                    # Máy chủ HTTP đa luồng bảo mật
    │   ├── main.py                 # Điểm khởi động web server
    │   ├── server/                 # Handler xử lý request & static file an toàn
    │   ├── api/                    # Router định tuyến REST API (/api/v1/...)
    │   ├── middleware/             # WAF, Rate Limiter, Security Headers CSP
    │   ├── services/               # Dịch vụ tải file an toàn & audit log
    │   └── tests/                  # Bộ kiểm thử bảo mật backend (test_security.py)
    ├── html/                       # Giao diện Web SPA
    │   ├── index.html              # Trang chủ SPA hoàn chỉnh (được biên dịch tự động)
    │   ├── 404.html                # Trang lỗi 404
    │   ├── thank-you.html          # Trang cảm ơn sau khi gửi biểu mẫu
    │   ├── privacy-policy.html     # Chính sách bảo mật
    │   └── components/             # Các khối component HTML độc lập
    │       ├── head.html           # Thẻ meta, CDN, font, CSP
    │       ├── navbar.html         # Thanh menu điều hướng & nút đổi ngôn ngữ
    │       ├── home.html           # Trang chủ (Hero, Metrics, Flow, Reviews)
    │       ├── about.html          # Trang giới thiệu (Case Studies, Core Team)
    │       ├── features.html       # 7 card mô tả tính năng chi tiết
    │       ├── dashboard.html      # Giao diện Dashboard demo trực quan
    │       ├── download.html       # Khu vực tải phần mềm & SHA-256
    │       ├── docs.html           # Tài liệu kỹ thuật, API spec, 5 FAQs
    │       ├── news.html           # Tin tức phiên bản & lộ trình phát triển
    │       ├── contact.html        # Biểu mẫu liên hệ & kênh hỗ trợ
    │       ├── modals.html         # Hộp thoại chi tiết thiết bị & lightbox
    │       └── footer.html         # Chân trang & lưu ý pháp lý
    ├── js/                         # Bộ mã JavaScript
    │   ├── app.js                  # Tệp JS tổng hợp (được biên dịch tự động)
    │   └── modules/                # Các module chức năng tách rời
    │       ├── i18n.js             # Từ điển song ngữ toàn diện (Việt - Anh)
    │       ├── router.js           # Bộ điều hướng client-side & dynamic loader
    │       ├── demo_devices.js     # Quản lý bảng thiết bị & bộ lọc
    │       ├── demo_live.js        # Đồng bộ thời gian thực qua REST API
    │       ├── demo_traffic.js     # Vẽ biểu đồ sóng lưu lượng canvas
    │       ├── demo_alerts.js      # Hệ thống thông báo cảnh báo
    │       ├── demo_settings.js    # Cài đặt giao diện & thông số router
    │       └── ui_helpers.js       # Toast, lightbox, sao chép mã SHA-256
    ├── css/                        # Stylesheet, Dark Tech theme & Glassmorphism
    ├── downloads/                  # Thư mục chứa file cài đặt phân phối
    └── scripts/                    # Scripts build tự động hóa
        ├── build_html.py           # Ghép nối các component HTML thành index.html
        ├── build_js.py             # Ghép nối các module JS thành app.js
        └── build_all.py            # Trình biên dịch toàn bộ tài nguyên web
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

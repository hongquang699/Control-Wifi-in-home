# Hướng Dẫn Cài Đặt Network Manager (Installation Guide)

Tài liệu hướng dẫn cài đặt và triển khai hệ thống quản lý mạng **Network Manager v1.0.0** trên các hệ điều hành phổ biến: **Windows**, **Linux**, và **macOS**.

---

## 1. Yêu Cầu Hệ Thống

| Thành Phần | Yêu Cầu Tối Thiểu | Yêu Cầu Khuyên Dùng |
| :--- | :--- | :--- |
| **Hệ Điều Hành** | Windows 10/11 (64-bit), Ubuntu 22.04+, macOS 12+ | Windows 11 64-bit hoặc Linux Server x64 |
| **CPU** | Dual Core 1.8 GHz | Quad Core 2.5 GHz trở lên |
| **RAM** | 2 GB RAM | 4 GB RAM trở lên |
| **Dung Lượng Trống** | 250 MB | 1 GB |
| **Quyền Quản Trị** | Standard User (Quét cơ bản) | Administrator / Root (Tường lửa & Raw ARP) |
| **Công Cụ Bổ Trợ** | Native ARP + ICMP Ping (tích hợp sẵn) | Nmap 7.90+ (tùy chọn, tăng tốc quét dải lớn) |

---

## 2. Cài Đặt Trên Windows

### Cách 1: Sử dụng Bản Portable Executable (.exe) — Khuyên dùng
1. Tải gói `NetworkManager-v1.0.0-windows-x64.zip` từ trang [Tải xuống](#/download).
2. Giải nén vào thư mục bạn chọn (ví dụ `C:\Program Files\NetworkManager\` hoặc `D:\Tools\NetworkManager\`).
3. Khởi chạy:
   - **Chế độ chuẩn**: Nhấp đúp chuột vào `run.bat` hoặc `NetworkManager.exe`.
   - **Chế độ Administrator (Toàn quyền)**: Nhấp phải chuột vào `run_admin.bat` chọn **Run as administrator** để cho phép cấu hình Windows Host Firewall và gửi gói tin Nmap cấp thấp.

### Cách 2: Chạy Từ Mã Nguồn Python
```powershell
# 1. Clone repository hoặc giải nén mã nguồn
git clone https://github.com/hongquang699/Control-Wifi-in-home.git
cd Control-Wifi-in-home

# 2. Khởi tạo môi trường ảo Python 3.12
py -3.12 -m venv venv
.\venv\Scripts\activate

# 3. Cài đặt các gói phụ thuộc
pip install -r requirements.txt

# 4. Khởi chạy ứng dụng
python main.py
```

---

## 3. Cài Đặt Trên Linux (Ubuntu / Debian / Arch / Fedora)

1. Tải gói phát hành `NetworkManager-v1.0.0-linux-x64.tar.gz`.
2. Giải nén gói cài đặt:
   ```bash
   tar -xzf NetworkManager-v1.0.0-linux-x64.tar.gz
   cd NetworkManager
   ```
3. Cấp quyền thực thi và chạy:
   ```bash
   chmod +x network_manager
   sudo ./network_manager
   ```
   *Lưu ý: Chạy với `sudo` để kích hoạt bộ lọc gói tin raw socket ARP và khả năng cấu hình iptables/nftables.*

---

## 4. Cài Đặt Trên macOS (Apple Silicon M1/M2/M3 & Intel)

1. Tải tệp `NetworkManager-v1.0.0-darwin-arm64.dmg`.
2. Mở file `.dmg` và kéo thả biểu tượng **Network Manager** vào thư mục **Applications**.
3. Khởi chạy ứng dụng từ Launchpad hoặc Spotlight.
4. Trong lần chạy đầu tiên, cấp quyền Quét Mạng Cục Bộ (Local Network Access) khi hệ thống macOS hiển thị thông báo.

---

## 5. Xác Minh Tính Toàn Vẹn File (SHA-256 Checksum)

Trước khi cài đặt, bạn nên kiểm tra mã băm SHA-256 để đảm bảo tệp tải về không bị can thiệp:

```powershell
# Trên Windows PowerShell:
Get-FileHash NetworkManager-v1.0.0-windows-x64.zip -Algorithm SHA256

# Trên Linux / macOS:
sha256sum NetworkManager-v1.0.0-linux-x64.tar.gz
```
So sánh chuỗi kết quả với mã công bố trên trang [Tải xuống](#/download).

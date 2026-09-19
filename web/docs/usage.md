# Hướng Dẫn Sử Dụng Network Manager (User Guide)

Tài liệu chi tiết hướng dẫn vận hành các tính năng quản lý, giám sát và kiểm soát an ninh mạng trên hệ thống **Network Manager**.

---

## 1. Khởi Chạy & Quét Mạng Lần Đầu

1. **Khởi động**: Khi mở ứng dụng, hệ thống tự động xác định Card mạng (NIC) đang hoạt động, địa chỉ IP máy trạm, Router Gateway mặc định và tự động tính toán dải subnet (ví dụ: `192.168.1.0/24` hoặc `192.168.110.0/24`).
2. **Quét tự động**: Tiến trình quét nền tự động chạy và liệt kê tất cả các thiết bị đang trực tuyến.
3. **Quét thủ công**: Nhấp vào nút **"Quét mạng ngay (Scan Network)"** trên thanh công cụ để làm mới danh sách thiết bị bất cứ lúc nào.

---

## 2. Quản Lý Danh Sách Thiết Bị

Tại thẻ **"Thiết bị mạng (Devices)"**:
- **Xem thông số**: Hiển thị tên máy trạm (Hostname), IP, MAC, nhà sản xuất (Vendor qua OUI lookup), phân loại thiết bị, dải mạng phụ trách và trạng thái kết nối.
- **Tìm kiếm**: Gõ IP, MAC, Tên hoặc Vendor vào ô tìm kiếm để lọc tức thì.
- **Lọc theo dải mạng**: Chuyển đổi giữa dải *Wi-Fi Tổng (192.168.1.x)* và *Router Phụ (192.168.110.x)*.
- **Đặt tên gợi nhớ (Alias)**:
  1. Nhấp nút **"Chi tiết (Detail)"** trên dòng thiết bị tương ứng.
  2. Nhập tên dễ nhớ (ví dụ: *Laptop làm việc*, *Điện thoại của Nam*, *Camera Phòng Khách*).
  3. Nhấp **"Lưu thay đổi"**. Tên gợi nhớ sẽ được hiển thị ưu tiên trên toàn bộ hệ thống.

---

## 3. Xem Sơ Đồ Mạng Đa Tầng & Hop Path

1. Chuyển sang thẻ **"Sơ đồ mạng (Network Map)"**.
2. Hệ thống hiển thị cây phân cấp hình ảnh:
   ```text
   GLOBAL INTERNET
        │
   [ MODEM TỔNG ISP ] (192.168.1.1)
        ├── [ PC Quản Trị ]
        ├── [ iPhone 15 ]
        └── [ ROUTER PHỤ AP ] (192.168.110.1)
                 ├── [ Smart TV ]
                 └── [ Camera Ezviz ]
   ```
3. Mỗi nút biểu thị loại thiết bị, địa chỉ IP và trạng thái kết nối Online (xanh) hoặc Bị chặn (đỏ).

---

## 4. Kiểm Soát Truy Cập: Chặn & Bỏ Chặn Thiết Bị (Access Control)

### Chặn Thiết Bị (Block Device)
1. Trong bảng thiết bị hoặc hộp thoại chi tiết, nhấp **"Chặn (Block)"**.
2. Hộp thoại xác nhận xuất hiện kèm thông số IP và MAC cần chặn.
3. Khi nhấn xác nhận:
   - Hệ thống gửi lệnh chặn MAC Filtering/ACL tới Router Adapter (TP-Link / OpenWrt / MikroTik hoặc Mock Mode).
   - Thiết lập quy tắc chặn hai chiều Inbound & Outbound trên Windows Host Firewall của máy quản trị.
   - Thiết bị chuyển sang trạng thái **BLOCKED** và xuất hiện trong thẻ **Danh sách chặn**.

### Bỏ Chặn Thiết Bị (Unblock Device)
1. Truy cập thẻ **"Danh sách chặn (Blocked Devices)"**.
2. Nhấp **"Bỏ chặn (Unblock)"** tại thiết bị mong muốn.
3. Quy tắc chặn tại Router và Tường lửa sẽ được gỡ bỏ ngay lập tức, phục hồi kết nối bình thường.

---

## 5. Cấu Hình Router Adapter

1. Vào thẻ **"Cài đặt (Settings)"** -> Mục **"Cấu hình Router"**.
2. Chọn loại Router tương ứng:
   - **TP-Link**: Hỗ trợ Router TP-Link gia đình qua giao diện Web HTTP.
   - **OpenWrt**: Hỗ trợ thiết bị cài custom firmware OpenWrt qua LuCI / ubus JSON-RPC.
   - **MikroTik**: Hỗ trợ thiết bị RouterOS qua API Port 8728.
   - **Mock Router**: Chế độ thử nghiệm an toàn, mô phỏng hoàn chỉnh mà không can thiệp router thật.
3. Nhập Gateway IP, tên đăng nhập và mật khẩu.
4. Nhấp **"Kiểm tra kết nối Router"** để kiểm tra xác thực trước khi lưu.

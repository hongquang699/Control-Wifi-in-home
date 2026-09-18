"""
Hệ thống Đa ngôn ngữ (i18n / Internationalization): Tiếng Việt (vi) & Tiếng Anh (en).
"""

import json
import os
from typing import Dict, Optional
from PySide6.QtCore import QObject, Signal

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # ==================== VIETNAMESE (vi) ====================
    "vi": {
        # App & Header
        "app_title": "Network Manager - Quản lý & Giám sát Mạng Nội bộ",
        "app_brand": "NET MANAGER",
        "app_footer": "Network Manager v1.0\nGiám sát mạng an toàn",
        "status_ready": "Trạng thái: Trực tuyến (Sẵn sàng)",
        "status_scanning": "Trạng thái: Đang quét mạng...",
        "status_error": "Trạng thái: Lỗi quét",
        "ready_msg": "Sẵn sàng hoạt động.",
        "scanning_msg": "Đang thực hiện quét dải mạng...",
        "scan_success_msg": "Quét mạng thành công! Phát hiện {count} thiết bị.",
        "scan_error_title": "Lỗi Quét Mạng",
        "scan_error_body": "Không thể hoàn thành quét mạng:\n{error}",
        
        # Navigation
        "nav_dashboard": "Tổng quan",
        "nav_devices": "Thiết bị mạng",
        "nav_map": "Sơ đồ mạng",
        "nav_traffic": "Mức sử dụng mạng",
        "nav_blocked": "Danh sách chặn",
        "nav_settings": "Cài đặt",
        
        # Dashboard
        "dash_title": "Tổng quan Mạng (Network Dashboard)",
        "dash_scan_now": "Quét mạng ngay",
        "dash_scanning": "Đang quét mạng...",
        "card_total": "TỔNG THIẾT BỊ",
        "card_online": "TRỰC TUYẾN",
        "card_offline": "NGOẠI TUYẾN",
        "card_blocked": "ĐÃ BỊ CHẶN",
        "net_params_title": "Thông số Mạng Cục bộ",
        "net_param_iface": "• Card mạng: {val}",
        "net_param_ip": "• IP máy tính: {val}",
        "net_param_gw": "• Router Gateway: {val}",
        "net_param_subnet": "• Dải Subnet: {val} ({mask})",
        "net_param_dist": "• Phân loại online: {val}",
        "recent_events_title": "Nhật ký Sự kiện Mạng Gần đây",
        "col_time": "Thời gian",
        "col_event_type": "Loại sự kiện",
        "col_mac": "Địa chỉ MAC",
        "col_desc": "Nội dung",
        
        # Devices View
        "dev_title": "Quản lý Thiết bị Mạng (Connected Devices)",
        "dev_subtitle": "Danh sách tất cả thiết bị đã phát hiện trong mạng nội bộ ({count} thiết bị).",
        "search_placeholder": "Tìm theo IP, MAC, Tên, Vendor...",
        "subtab_all": "Tất cả dải mạng",
        "subtab_secondary": "📡 Router Phụ (192.168.110.x)",
        "subtab_primary": "🌐 Wi-Fi Tổng (192.168.1.x)",
        "filter_all": "Tất cả trạng thái",
        "filter_online": "Đang Online",
        "filter_offline": "Ngoại tuyến (Offline)",
        "filter_blocked": "Đang bị chặn",
        "col_name": "Tên thiết bị",
        "col_ip": "Địa chỉ IP",
        "col_vendor": "Hãng (Vendor)",
        "col_type": "Loại",
        "col_network": "Mạng kết nối",
        "col_conn_type": "Phương thức",
        "col_latency": "Độ trễ",
        "col_status": "Trạng thái",
        "col_blocked": "Bị chặn",
        "col_actions": "Thao tác",
        "btn_detail": "Chi tiết",
        "btn_block": "Chặn",
        "btn_unblock": "Bỏ chặn",
        "val_yes": "Có",
        "val_no": "Không",
        "val_online": "ONLINE",
        "val_offline": "OFFLINE",
        
        # Device Detail Modal
        "modal_title": "Chi tiết thiết bị - {ip} ({mac})",
        "sec_ident": "Thông tin Nhận dạng",
        "sec_network_route": "Thông tin Kết nối & Lộ trình Internet",
        "sec_admin": "Tùy chỉnh Quản trị",
        "sec_history": "Nhật ký Lịch sử Thiết bị",
        "lbl_alias": "Tên gợi nhớ (Alias):",
        "alias_placeholder": "Ví dụ: Laptop làm việc, Điện thoại của Nam...",
        "lbl_device_type": "Loại thiết bị:",
        "lbl_connected_network": "Mạng đang kết nối:",
        "lbl_conn_type": "Phương thức liên kết:",
        "lbl_gateway": "Gateway phụ trách:",
        "lbl_internet_status": "Trạng thái Internet:",
        "lbl_internet_route": "Lộ trình ra Internet (Hop Path):",
        "val_conn_wifi": "📶 Wi-Fi (Không dây)",
        "val_conn_ethernet": "🔌 Cáp LAN (Ethernet)",
        "val_conn_wan": "🌐 Cáp WAN/Quang",
        "val_internet_allowed": "🟢 Đang thông suốt (Có kết nối Internet)",
        "val_internet_blocked": "🔴 Bị chặn truy cập (Không có Internet)",
        "val_net_primary": "🌐 Wi-Fi Tổng (Modem ISP)",
        "val_net_secondary": "📡 Router Phụ (Ruijie/AP)",
        "dash_net_dist_title": "Phân bố Thiết bị theo Mạng & Kết nối",
        "dist_wifi": "Thiết bị Wi-Fi: {count}",
        "dist_ethernet": "Thiết bị Cáp LAN: {count}",
        "dist_primary": "Trên Wi-Fi Tổng: {count}",
        "dist_secondary": "Trên Router Phụ: {count}",
        "btn_save_changes": "Lưu thay đổi",
        "btn_toggle_block_yes": "Chặn kết nối thiết bị này (Block)",
        "btn_toggle_block_no": "Bỏ chặn thiết bị (Unblock)",
        "btn_close": "Đóng",
        "confirm_block_title": "Xác nhận chặn thiết bị",
        "confirm_block_msg": "CẢNH BÁO: Thiết bị {name} (MAC: {mac}, IP: {ip}) sẽ bị chặn khỏi mạng thông qua Router Adapter!\n\nBạn có chắc chắn muốn thực hiện không?",
        "confirm_unblock_title": "Xác nhận bỏ chặn",
        "confirm_unblock_msg": "Bạn có chắc muốn BỎ CHẶN thiết bị MAC {mac} ({ip}) không?",
        "save_success": "Đã lưu thông tin thiết bị!",
        
        # Network Map
        "map_title": "Sơ đồ Liên kết Mạng (Network Topology Map)",
        "map_desc": "Cấu trúc trực quan phân tầng từ Router Gateway đến từng nhóm thiết bị kết nối.",
        "btn_refresh_map": "Làm mới sơ đồ",
        "col_map_node": "Nút mạng / Tên thiết bị",
        "node_router": "[Router Gateway] {vendor} ({ip})",
        "node_subnet": "[Dải mạng LAN] {cidr}",
        "grp_pcs": "Máy tính & Laptop ({count})",
        "grp_phones": "Điện thoại & Máy tính bảng ({count})",
        "grp_iot": "Thiết bị thông minh ({count})",
        "grp_others": "Thiết bị khác & Server ({count})",
        
        # Traffic & Usage View
        "traffic_title": "Biểu đồ Mức sử dụng Mạng (Network Usage & Bandwidth)",
        "traffic_desc": "Theo dõi trực tiếp tốc độ tải về, tải lên và lưu lượng sử dụng theo thời gian thực.",
        "traffic_chart_title": "Biểu đồ Lưu lượng Thời gian thực (60s gần nhất)",
        "traffic_down_cur": "Tải về hiện tại",
        "traffic_up_cur": "Tải lên hiện tại",
        "traffic_down_peak": "Đỉnh tải về",
        "traffic_up_peak": "Đỉnh tải lên",
        "traffic_total_down": "TỔNG DỮ LIỆU TẢI VỀ",
        "traffic_total_up": "TỔNG DỮ LIỆU TẢI LÊN",
        "traffic_packets_stats": "Thống kê Gói tin & Lỗi đường truyền",
        "traffic_iface_select": "Card mạng theo dõi:",
        "traffic_all_ifaces": "Tất cả card mạng (Gộp)",
        "traffic_btn_pause": "Tạm dừng",
        "traffic_btn_resume": "Tiếp tục theo dõi",
        "traffic_btn_reset": "Đặt lại số liệu",
        "traffic_now": "Hiện tại",
        "traffic_waiting": "Đang đo lường và đồng bộ lưu lượng mạng...",
        "traffic_pkt_sent": "Gói tin gửi",
        "traffic_pkt_recv": "Gói tin nhận",
        "traffic_pkt_err": "Lỗi truyền (Err In/Out)",
        "traffic_pkt_drop": "Gói bị hủy (Drop In/Out)",
        "traffic_live_badge": "ĐANG THEO DÕI REALTIME",
        "traffic_paused_badge": "ĐÃ TẠM DỪNG",
        "dash_traffic_title": "Băng thông Mạng Thời gian thực",
        
        # Blocked View
        "blk_title": "Danh sách Thiết bị Bị chặn (Access Control Blacklist)",
        "blk_subtitle": "Tổng số thiết bị đang bị chặn: {count}",
        "blk_manual_title": "Chặn Thủ công Thiết bị Mới",
        "blk_manual_mac": "Địa chỉ MAC (vd: AA:BB:CC:DD:EE:FF)",
        "blk_manual_ip": "IP (Tùy chọn, vd: 192.168.1.50)",
        "blk_manual_reason": "Lý do chặn (vd: Thiết bị lạ, vi phạm nội quy...)",
        "btn_add_blacklist": "Thêm vào Blacklist",
        "err_invalid_mac": "Vui lòng nhập địa chỉ MAC hợp lệ!",
        "err_invalid_ip": "Địa chỉ IP không hợp lệ!",
        
        # Settings
        "set_title": "Cài đặt Hệ thống (System Settings)",
        "set_desc": "Tùy biến dải quét mạng, ngôn ngữ hiển thị và cấu hình Router Adapter.",
        "grp_scan_config": "Cấu hình Quét & Giám sát Mạng",
        "chk_autodetect": "Tự động nhận diện Card mạng & Subnet cục bộ",
        "chk_multisubnet": "Tự động quét tất cả các dải mạng (Wi-Fi Tổng & Router phụ / Multi-Subnet)",
        "custom_subnets_placeholder": "Một hoặc nhiều dải phân cách bởi dấu phẩy (vd: 192.168.110.0/24, 192.168.1.0/24)",
        "lbl_custom_subnet": "Dải Subnet tùy chỉnh:",
        "lbl_scan_interval": "Chu kỳ quét định kỳ:",
        "lbl_offline_thresh": "Ngưỡng đánh dấu Offline:",
        "lbl_nmap_path": "Đường dẫn Nmap.exe:",
        "grp_lang_config": "Ngôn ngữ Giao diện (Interface Language)",
        "lbl_language": "Chọn Ngôn ngữ:",
        "grp_router_config": "Cấu hình Router Quản trị (Block / Unblock Adapter)",
        "lbl_adapter_type": "Loại Router Adapter:",
        "lbl_router_host": "IP / Host Router:",
        "lbl_router_port": "Cổng Port kết nối:",
        "lbl_router_user": "Tài khoản quản trị:",
        "lbl_router_pass": "Mật khẩu router:",
        "btn_test_conn": "Kiểm tra Kết nối Router",
        "grp_sec_config": "Bảo mật & Tường lửa Cục bộ",
        "chk_firewall": "Kích hoạt Windows Firewall để chặn giao tiếp với thiết bị bị chặn",
        "chk_confirm": "Hiển thị hộp thoại xác nhận trước khi gửi lệnh Chặn",
        "btn_save_settings": "Lưu Cấu hình",
        "save_settings_success": "Đã lưu cài đặt hệ thống thành công!",
        "conn_success": "Kết nối Thành công",
        "conn_fail": "Kết nối Thất bại",
        "btn_browse": "📁 Duyệt...",
        "btn_reset_defaults": "Khôi phục mặc định",
        "router_mock_tip": "Chế độ Giả lập an toàn: Các lệnh chặn/bỏ chặn được mô phỏng an toàn trong bộ nhớ.",
        "sec_unit": "giây",
        "reset_defaults_confirm": "Bạn có chắc muốn đặt lại toàn bộ cài đặt về giá trị mặc định ban đầu?",
        "reset_defaults_success": "Đã khôi phục cài đặt mặc định thành công!",
        "card_lang_title": "Ngôn ngữ & Giao diện",
        "card_lang_sub": "Tùy chọn ngôn ngữ hiển thị trên toàn bộ ứng dụng (áp dụng tức thì).",
        "card_scan_title": "Cấu hình Quét & Giám sát Mạng",
        "card_scan_sub": "Thiết lập dải mạng IP quét tự động hoặc tùy chỉnh, chu kỳ quét và công cụ Nmap.",
        "card_router_title": "Bộ điều hợp Router Quản trị",
        "card_router_sub": "Cấu hình kết nối Router để quản lý chặn/bỏ chặn thiết bị trên Access Control List (ACL).",
        "card_sec_title": "Bảo mật & Tường lửa Cục bộ",
        "card_sec_sub": "Chính sách tường lửa máy chủ quản trị và quy tắc cảnh báo an toàn.",
        "hint_scan_interval": "Thời gian chờ giữa các chu kỳ quét tự động trong nền",
        "hint_offline_thresh": "Thời gian không nhận được phản hồi trước khi đánh dấu ngoại tuyến",
        "choose_nmap_title": "Chọn tập tin thực thi Nmap",
        "settings_synced": "Cấu hình đã sẵn sàng lưu",
        "conn_testing": "Đang kiểm tra...",
        "show_pass": "Hiện mật khẩu",
        "hide_pass": "Ẩn mật khẩu",
        "card_sec_firewall_hint": "Tạo quy tắc Windows Firewall để ngăn chặn mọi gói tin hai chiều với thiết bị bị đưa vào Blacklist.",
        "card_sec_confirm_hint": "Yêu cầu người dùng xác nhận lại qua hộp thoại trước khi thực thi ngắt kết nối thiết bị."
    },

    # ==================== ENGLISH (en) ====================
    "en": {
        # App & Header
        "app_title": "Network Manager - Local Network Management & Monitoring",
        "app_brand": "NET MANAGER",
        "app_footer": "Network Manager v1.0\nSecure Network Supervision",
        "status_ready": "Status: Online (Ready)",
        "status_scanning": "Status: Scanning network...",
        "status_error": "Status: Scan error",
        "ready_msg": "Ready.",
        "scanning_msg": "Scanning subnet in background...",
        "scan_success_msg": "Scan completed! Found {count} active devices.",
        "scan_error_title": "Network Scan Error",
        "scan_error_body": "Could not complete network scan:\n{error}",
        
        # Navigation
        "nav_dashboard": "Dashboard",
        "nav_devices": "Devices",
        "nav_map": "Network Map",
        "nav_traffic": "Network Usage",
        "nav_blocked": "Blocked List",
        "nav_settings": "Settings",
        
        # Dashboard
        "dash_title": "Network Dashboard",
        "dash_scan_now": "Scan Network Now",
        "dash_scanning": "Scanning...",
        "card_total": "TOTAL DEVICES",
        "card_online": "ONLINE",
        "card_offline": "OFFLINE",
        "card_blocked": "BLOCKED",
        "net_params_title": "Local Network Parameters",
        "net_param_iface": "• Network Interface: {val}",
        "net_param_ip": "• Host IP Address: {val}",
        "net_param_gw": "• Router Gateway: {val}",
        "net_param_subnet": "• Subnet CIDR: {val} ({mask})",
        "net_param_dist": "• Online Devices: {val}",
        "recent_events_title": "Recent Network Events Log",
        "col_time": "Timestamp",
        "col_event_type": "Event Type",
        "col_mac": "MAC Address",
        "col_desc": "Description",
        
        # Devices View
        "dev_title": "Connected Devices Management",
        "dev_subtitle": "All detected devices within the local network ({count} devices).",
        "search_placeholder": "Search by IP, MAC, Name, Vendor...",
        "subtab_all": "All Subnets",
        "subtab_secondary": "📡 Secondary Router (192.168.110.x)",
        "subtab_primary": "🌐 Main Wi-Fi / Modem (192.168.1.x)",
        "filter_all": "All Statuses",
        "filter_online": "Online",
        "filter_offline": "Offline",
        "filter_blocked": "Blocked",
        "col_name": "Device Name",
        "col_ip": "IP Address",
        "col_vendor": "Vendor",
        "col_type": "Type",
        "col_network": "Connected Network",
        "col_conn_type": "Connection Type",
        "col_latency": "Latency",
        "col_status": "Status",
        "col_blocked": "Blocked",
        "col_actions": "Actions",
        "btn_detail": "Details",
        "btn_block": "Block",
        "btn_unblock": "Unblock",
        "val_yes": "Yes",
        "val_no": "No",
        "val_online": "ONLINE",
        "val_offline": "OFFLINE",
        
        # Device Detail Modal
        "modal_title": "Device Details - {ip} ({mac})",
        "sec_ident": "Identity Information",
        "sec_network_route": "Connection Info & Internet Route",
        "sec_admin": "Administrative Customization",
        "sec_history": "Device Event History",
        "lbl_alias": "Custom Name (Alias):",
        "alias_placeholder": "E.g., Work Laptop, Alice's iPhone...",
        "lbl_device_type": "Device Type:",
        "lbl_connected_network": "Connected Network:",
        "lbl_conn_type": "Link Medium:",
        "lbl_gateway": "Assigned Gateway:",
        "lbl_internet_status": "Internet Access:",
        "lbl_internet_route": "Internet Hop Route:",
        "val_conn_wifi": "📶 Wi-Fi (Wireless)",
        "val_conn_ethernet": "🔌 Ethernet (LAN Cable)",
        "val_conn_wan": "🌐 Fiber / WAN Uplink",
        "val_internet_allowed": "🟢 Connected to Internet (Active)",
        "val_internet_blocked": "🔴 Blocked from Internet",
        "val_net_primary": "🌐 Main Wi-Fi (ISP Modem)",
        "val_net_secondary": "📡 Secondary Router (AP)",
        "dash_net_dist_title": "Network & Connection Distribution",
        "dist_wifi": "Wi-Fi Devices: {count}",
        "dist_ethernet": "Ethernet Devices: {count}",
        "dist_primary": "On Main Wi-Fi: {count}",
        "dist_secondary": "On Secondary Router: {count}",
        "btn_save_changes": "Save Changes",
        "btn_toggle_block_yes": "Block This Device from Network",
        "btn_toggle_block_no": "Unblock This Device",
        "btn_close": "Close",
        "confirm_block_title": "Confirm Block Device",
        "confirm_block_msg": "WARNING: Device {name} (MAC: {mac}, IP: {ip}) will be blocked from accessing the network via Router Adapter!\n\nDo you want to proceed?",
        "confirm_unblock_title": "Confirm Unblock Device",
        "confirm_unblock_msg": "Are you sure you want to UNBLOCK device MAC {mac} ({ip})?",
        "save_success": "Device details saved successfully!",
        
        # Network Map
        "map_title": "Network Topology Map",
        "map_desc": "Hierarchical visualization from Router Gateway down to connected device groups.",
        "btn_refresh_map": "Refresh Map",
        "col_map_node": "Network Node / Device",
        "node_router": "[Router Gateway] {vendor} ({ip})",
        "node_subnet": "[LAN Subnet] {cidr}",
        "grp_pcs": "Computers & Laptops ({count})",
        "grp_phones": "Phones & Tablets ({count})",
        "grp_iot": "Smart Home & IoT ({count})",
        "grp_others": "Servers & Others ({count})",
        
        # Traffic & Usage View
        "traffic_title": "Network Usage & Bandwidth",
        "traffic_desc": "Monitor live download/upload speeds and total data transfer in real time.",
        "traffic_chart_title": "Real-time Traffic History (Last 60s)",
        "traffic_down_cur": "Current Download",
        "traffic_up_cur": "Current Upload",
        "traffic_down_peak": "Peak Download",
        "traffic_up_peak": "Peak Upload",
        "traffic_total_down": "TOTAL RECEIVED DATA",
        "traffic_total_up": "TOTAL SENT DATA",
        "traffic_packets_stats": "Packet & Transmission Statistics",
        "traffic_iface_select": "Monitored Interface:",
        "traffic_all_ifaces": "All Interfaces (Combined)",
        "traffic_btn_pause": "Pause",
        "traffic_btn_resume": "Resume",
        "traffic_btn_reset": "Reset Stats",
        "traffic_now": "Now",
        "traffic_waiting": "Measuring and synchronizing network traffic...",
        "traffic_pkt_sent": "Packets Sent",
        "traffic_pkt_recv": "Packets Received",
        "traffic_pkt_err": "Errors (In/Out)",
        "traffic_pkt_drop": "Dropped (In/Out)",
        "traffic_live_badge": "LIVE MONITORING",
        "traffic_paused_badge": "PAUSED",
        "dash_traffic_title": "Real-time Network Bandwidth",
        
        # Blocked View
        "blk_title": "Access Control Blacklist",
        "blk_subtitle": "Total blocked devices: {count}",
        "blk_manual_title": "Manually Block New Device",
        "blk_manual_mac": "MAC Address (e.g. AA:BB:CC:DD:EE:FF)",
        "blk_manual_ip": "IP Address (Optional, e.g. 192.168.1.50)",
        "blk_manual_reason": "Block Reason (e.g. Unknown device, unauthorized...)",
        "btn_add_blacklist": "Add to Blacklist",
        "err_invalid_mac": "Please enter a valid MAC address!",
        "err_invalid_ip": "Invalid IP address format!",
        
        # Settings
        "set_title": "System Settings",
        "set_desc": "Customize network subnet, interface language, and Router Adapter configuration.",
        "grp_scan_config": "Network Scanning & Monitoring Configuration",
        "chk_autodetect": "Automatically detect network interface & local subnet",
        "chk_multisubnet": "Automatically scan all connected subnets (Main ISP Wi-Fi & Secondary Routers / Multi-Subnet)",
        "custom_subnets_placeholder": "One or more subnets separated by comma (e.g. 192.168.110.0/24, 192.168.1.0/24)",
        "lbl_custom_subnet": "Custom Subnet CIDR:",
        "lbl_scan_interval": "Scan Interval:",
        "lbl_offline_thresh": "Offline Threshold:",
        "lbl_nmap_path": "Nmap.exe Path:",
        "grp_lang_config": "Interface Language",
        "lbl_language": "Language:",
        "grp_router_config": "Router Management (Block / Unblock Adapter)",
        "lbl_adapter_type": "Router Adapter Type:",
        "lbl_router_host": "Router IP / Host:",
        "lbl_router_port": "Connection Port:",
        "lbl_router_user": "Admin Username:",
        "lbl_router_pass": "Admin Password:",
        "btn_test_conn": "Test Router Connection",
        "grp_sec_config": "Security & Local Host Firewall",
        "chk_firewall": "Enable Windows Firewall rules to block traffic to/from blocked devices",
        "chk_confirm": "Show confirmation dialog before sending Block command",
        "btn_save_settings": "Save Settings",
        "save_settings_success": "System settings saved successfully!",
        "conn_success": "Connection Successful",
        "conn_fail": "Connection Failed",
        "btn_browse": "📁 Browse...",
        "btn_reset_defaults": "Restore Defaults",
        "router_mock_tip": "Safe Mock Mode: Block/unblock commands are simulated safely in memory.",
        "sec_unit": "sec",
        "reset_defaults_confirm": "Are you sure you want to reset all settings to default values?",
        "reset_defaults_success": "Default settings restored successfully!",
        "card_lang_title": "Interface Language",
        "card_lang_sub": "Choose your preferred display language for the application (applies immediately).",
        "card_scan_title": "Network Scanner & Monitoring",
        "card_scan_sub": "Configure automatic or custom IP subnet scanning, intervals, and Nmap path.",
        "card_router_title": "Router Management Adapter",
        "card_router_sub": "Configure router connection to manage device blocking/unblocking via Access Control List (ACL).",
        "card_sec_title": "Security & Local Firewall",
        "card_sec_sub": "Host firewall integration and safety confirmation preferences.",
        "hint_scan_interval": "Delay between automatic background network scans",
        "hint_offline_thresh": "Inactivity duration before marking a device as Offline",
        "choose_nmap_title": "Select Nmap Executable",
        "settings_synced": "Configuration ready to save",
        "conn_testing": "Testing connection...",
        "show_pass": "Show password",
        "hide_pass": "Hide password",
        "card_sec_firewall_hint": "Configure Windows Firewall rules to block bidirectional traffic with blacklisted devices.",
        "card_sec_confirm_hint": "Prompt for user confirmation dialog before executing device block commands on the router."
    }
}

class TranslationManager(QObject):
    language_changed = Signal(str)
    _instance: Optional["TranslationManager"] = None

    def __init__(self):
        super().__init__()
        self.current_lang = "vi"
        self._load_saved_language()

    @classmethod
    def get_instance(cls) -> "TranslationManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_saved_language(self):
        config_path = "config/config.json"
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    self.current_lang = cfg.get("ui", {}).get("language", "vi")
            except Exception:
                self.current_lang = "vi"

    def set_language(self, lang: str):
        if lang in ("vi", "en") and lang != self.current_lang:
            self.current_lang = lang
            # Lưu lại vào config.json
            try:
                config_path = "config/config.json"
                if os.path.exists(config_path):
                    with open(config_path, "r", encoding="utf-8") as f:
                        cfg = json.load(f)
                    cfg.setdefault("ui", {})["language"] = lang
                    with open(config_path, "w", encoding="utf-8") as f:
                        json.dump(cfg, f, indent=2, ensure_ascii=False)
            except Exception:
                pass
            self.language_changed.emit(self.current_lang)

    def translate(self, key: str, **kwargs) -> str:
        dict_lang = TRANSLATIONS.get(self.current_lang, TRANSLATIONS["vi"])
        text = dict_lang.get(key, TRANSLATIONS["vi"].get(key, key))
        if kwargs:
            try:
                return text.format(**kwargs)
            except KeyError:
                return text
        return text

# Singleton instance & shorthand function
i18n = TranslationManager.get_instance()

def t(key: str, **kwargs) -> str:
    return i18n.translate(key, **kwargs)

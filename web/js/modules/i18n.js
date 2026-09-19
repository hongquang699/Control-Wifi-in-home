/**
 * Module Bản Địa Hóa & Từ Điển Song Ngữ (i18n & Mock Data)
 */
/**
 * Network Manager - Interactive Application & Router Engine
 * Supports 8-Page Routing, Bilingual Switching, Live Dashboard Simulation, Waveform Canvas, Checksum Copy
 */

// ==================== BILINGUAL TRANSLATION DICTIONARY ====================
const i18nData = {
  vi: {
    // Navigation & General
    nav_home: "Trang chủ",
    nav_about: "Giới thiệu",
    nav_features: "Tính năng",
    nav_dashboard: "Dashboard Demo",
    nav_download: "Tải xuống",
    nav_docs: "Tài liệu",
    nav_news: "Tin tức",
    nav_contact: "Liên hệ",
    nav_btn_download: "Tải bản v1.0",
    breadcrumb_home: "Trang chủ",

    // Hero Section
    hero_badge: "HỆ THỐNG QUẢN LÝ MẠNG TOÀN DIỆN V1.0.0",
    hero_support_sla: "Hỗ trợ kỹ thuật: Phản hồi < 2h",
    hero_title_1: "Giám Sát Toàn Diện,",
    hero_title_2: "Phân Tích Đa Tầng",
    hero_title_3: "& Kiểm Soát An Ninh Mạng",
    hero_desc: "Giải pháp quản trị mạng cục bộ tự động phát hiện 100% thiết bị LAN/WLAN, nhận diện phần cứng qua OUI, lập sơ đồ Internet Hop Path, giám sát băng thông thời gian thực và quản lý chặn thiết bị qua Router phần cứng.",
    hero_btn_download: "Tải xuống phần mềm (v1.0.0)",
    hero_btn_demo: "Trải nghiệm Dashboard Demo",
    badge_win: "Sẵn sàng cho Windows 10/11",
    badge_unix: "Sẵn sàng cho Linux & macOS",
    badge_portable: "Độc lập Không cần Python",
    badge_bilingual: "Song ngữ Việt - Anh",

    // Metrics Bar
    metric_subnets: "Phát hiện Subnet CIDR",
    metric_subnets_desc: "Tự động tính dải /24, /16",
    metric_speed: "Thời gian quét đa luồng",
    metric_speed_desc: "Nmap ARP + Native Ping song song",
    metric_oui: "Kho dữ liệu MAC OUI",
    metric_oui_desc: "Nhận diện Apple, Dell, Intel, IoT",
    metric_routers: "Router Adapter",
    metric_routers_desc: "TP-Link, OpenWrt, MikroTik, Mock",

    // Flow Diagram
    flow_title: "Sơ Đồ Hoạt Động Của Hệ Thống",
    flow_subtitle: "Mô hình luồng dữ liệu từ thiết bị mạng qua Agent, Server API đến giao diện Web Client",

    // Reviews & Testimonials
    testimonials_tag: "CUSTOMER TESTIMONIALS",
    testimonials_title: "Đánh Giá Thực Tế Từ Chuyên Gia Mạng",
    testimonials_subtitle: "Được tin tưởng bởi các kỹ sư hạ tầng mạng và quản trị viên hệ thống",

    // About Page
    about_title: "Giới Thiệu Hệ Thống Quản Lý Mạng",
    about_desc: "Tổng quan về mục tiêu, kiến trúc phân tầng 3 lớp và các công nghệ cốt lõi của Network Manager.",
    about_q1: "Hệ thống Network Manager là gì?",
    about_a1: "Network Manager là bộ giải pháp phần mềm quản trị và giám sát mạng nội bộ (LAN/WLAN) chuyên nghiệp. Khác với các công cụ quét IP thông thường, hệ thống tích hợp khả năng phân tích đa tầng (Multi-tier Topology), bóc tách rõ ràng giữa Modem Tổng ISP và Router Phụ, xác định phương thức liên kết Wi-Fi/LAN và cung cấp khả năng chặn thiết bị trực tiếp tại Router phần cứng.",
    about_case_title: "Các Trường Hợp Triển Khai Thực Tế (Case Studies)",
    about_case_1_title: "Chuỗi Cà Phê 3 Tầng",
    about_case_1_infra: "Hạ tầng: 1 Modem ISP + 3 Access Point",
    about_case_1_desc: "150+ khách kết nối đồng thời. Hệ thống phân tách dải IP từng tầng và khóa ngay các thiết bị tải lậu băng thông.",
    about_case_2_title: "Doanh Nghiệp Tech 50 Máy",
    about_case_2_infra: "Hạ tầng: Mạng nội bộ văn phòng",
    about_case_2_desc: "Nhân viên mang thiết bị lạ (BYOD). Hệ thống tự động đồng bộ tường lửa và cô lập máy lạ tức thì.",
    about_case_3_title: "Căn Hộ Smarthome 40+ IoT",
    about_case_3_infra: "Hạ tầng: Router phụ 192.168.110.x",
    about_case_3_desc: "Giám sát độ trễ camera Ezviz, công tắc ESP32 liên tục, vẽ sơ đồ hop route và báo động khi rớt mạng.",
    about_q2: "Mục Tiêu Của Hệ Thống",
    about_goal_1_title: "An Ninh Tuyệt Đối",
    about_goal_1_desc: "Phát hiện lập tức thiết bị lạ xâm nhập mạng Wi-Fi và phát cảnh báo an ninh tức thì.",
    about_goal_2_title: "Kiểm Soát 1 Cú Nhấp",
    about_goal_2_desc: "Gửi lệnh chặn MAC ACL trực tiếp đến Router TP-Link, OpenWrt, MikroTik.",
    about_goal_3_title: "Trực Quan Hóa Hoàn Toàn",
    about_goal_3_desc: "Lập bản đồ Internet Hop Path và biểu đồ sóng băng thông thời gian thực.",
    about_team_title: "Đội Ngũ Kỹ Sư Phát Triển (Core Team)",

    // Features Page
    features_title: "Tính Năng Hệ Thống Quản Lý Mạng",
    features_desc: "Đầy đủ 7 module chức năng phục vụ toàn diện công tác quản trị và an ninh mạng nội bộ.",
    feat_1_title: "1. Quản lý thiết bị (Device Management)",
    feat_1_desc: "Nhận diện IP, MAC, nhà sản xuất OUI, phân loại 6 nhóm thiết bị và cho phép gán tên gợi nhớ Alias.",
    feat_2_title: "2. Giám sát mạng (Network Monitoring)",
    feat_2_desc: "Tự động quét định kỳ dải mạng theo chu kỳ cấu hình, phát hiện tức thì biến động kết nối.",
    feat_3_title: "3. Kiểm tra trạng thái (Status Checking)",
    feat_3_desc: "Đo độ trễ phản hồi ping tính bằng ms, hiển thị trạng thái Online, Offline, Blocked trực quan.",
    feat_4_title: "4. Quản lý IP (Subnet & IP Allocation)",
    feat_4_desc: "Phân tách dải Wi-Fi Tổng 192.168.1.x và Router Phụ 192.168.110.x, phát hiện đổi IP bất thường.",
    feat_5_title: "5. Theo dõi băng thông (Traffic Tracking)",
    feat_5_desc: "Biểu đồ sóng động hiển thị tốc độ Upload / Download theo thời gian thực.",
    feat_6_title: "6. Cảnh báo an ninh (Real-time Alerts)",
    feat_6_desc: "Phát thông báo khi có thiết bị mới kết nối, ngắt kết nối hoặc vi phạm quy định mạng.",
    feat_7_title: "7. Nhật ký hoạt động (Audit Logs)",
    feat_7_desc: "Lưu vết toàn bộ sự kiện mạng vào cơ sở dữ liệu SQLite cục bộ, hỗ trợ truy xuất và kiểm toán an ninh.",

    // Downloads Page
    download_header_tag: "OFFICIAL DISTRIBUTION HUB",
    download_title: "Tải Xuống Phần Mềm",
    download_subtitle: "Bản phát hành chính thức ổn định, đã kiểm thử mã hóa SHA-256",
    download_win_desc: "Windows 10 / 11 (64-bit)",
    download_linux_desc: "Ubuntu, Debian, Fedora, Arch",
    download_mac_desc: "macOS 12.0+ (Apple Silicon M1-M4)",
    download_checksum_title: "Mã Băm Kiểm Tra Toàn Vẹn SHA-256",
    download_copy_btn: "Sao chép SHA-256",
    download_sys_req_title: "Yêu Cầu Hệ Thống Tối Thiểu",

    // Docs Page
    docs_title: "Tài Liệu Kỹ Thuật & Hướng Dẫn",
    docs_desc: "Cẩm nang hướng dẫn cài đặt, sử dụng, đặc tả API RESTful, 5 câu hỏi thường gặp và xử lý sự cố.",
    doc_tab_install: "1. Hướng dẫn cài đặt",
    doc_tab_usage: "2. Hướng dẫn sử dụng",
    doc_tab_api: "3. Đặc tả API RESTful",
    doc_tab_faq: "4. 5 Câu hỏi thường gặp (FAQs)",
    doc_tab_troubleshoot: "5. Xử lý lỗi",

    // News Page
    news_title: "Tin Tức & Cập Nhật Hệ Thống",
    news_desc: "Thông tin phát hành phiên bản mới, tính năng bổ sung và lộ trình phát triển.",
    news_roadmap_title: "Lộ Trình Phát Triển (Roadmap)",

    // Contact Page
    contact_title: "Liên Hệ & Hỗ Trợ Kỹ Thuật",
    contact_desc: "Đội ngũ kỹ thuật luôn sẵn sàng hỗ trợ cài đặt, cấu hình router và tiếp nhận phản hồi.",
    contact_channels_title: "Kênh Hỗ Trợ Chính Thức",
    contact_promise_title: "Cam Kết Phản Hồi:",
    contact_promise_1: "Phản hồi kỹ thuật trong vòng 2 giờ làm việc.",
    contact_promise_2: "Độ tin cậy hạ tầng: 99.98% Uptime SLA.",
    contact_office_title: "Văn Phòng Kỹ Thuật",
    contact_form_title: "Gửi Yêu Cầu Trực Tuyến",
    contact_lbl_name: "Họ và tên của bạn:",
    contact_lbl_email: "Địa chỉ email:",
    contact_lbl_subject: "Chủ đề cần hỗ trợ:",
    contact_lbl_msg: "Nội dung chi tiết:",
    contact_btn_send: "Gửi Yêu Cầu Hỗ Trợ",

    // Footer
    footer_tagline: "Hệ thống quản lý, giám sát và kiểm soát an ninh mạng nội bộ thế hệ mới. Tự động phát hiện 100% thiết bị, lập sơ đồ Internet Hop Path và kiểm soát truy cập cấp Router.",
    footer_col_nav: "Trang chính",
    footer_col_support: "Tài nguyên & Hỗ trợ",
    footer_disclaimer_title: "Lưu ý an ninh & Pháp lý:",
    footer_disclaimer: "Phần mềm được phát triển cho mục đích quản trị mạng được ủy quyền, giám sát an toàn hệ thống và học tập nghiên cứu trên hạ tầng thuộc quyền sở hữu. Mọi hành vi can thiệp trái phép đều bị nghiêm cấm.",
    footer_copyright: "© 2026 Network Manager. Bản quyền thuộc về Đội ngũ Kỹ sư Phát triển.",

    // Dashboard General
    demo_title: "Dashboard Quản Lý Mạng Minh Họa",
    demo_desc: "Bố cục Dashboard thực tế với Sidebar, chỉ số Online/Offline, CPU/RAM, biểu đồ sóng và thao tác Chặn/Bỏ chặn trực tiếp."
  },

  en: {
    // Navigation & General
    nav_home: "Home",
    nav_about: "About",
    nav_features: "Features",
    nav_dashboard: "Dashboard Demo",
    nav_download: "Downloads",
    nav_docs: "Documentation",
    nav_news: "News",
    nav_contact: "Contact",
    nav_btn_download: "Download v1.0",
    breadcrumb_home: "Home",

    // Hero Section
    hero_badge: "COMPREHENSIVE NETWORK MANAGEMENT SUITE V1.0.0",
    hero_support_sla: "Technical Support: SLA < 2h",
    hero_title_1: "Comprehensive Monitoring,",
    hero_title_2: "Multi-Tier Topology",
    hero_title_3: "& Network Access Control",
    hero_desc: "Enterprise-grade local network management suite: Automatically discovers 100% of devices, identifies hardware vendors via OUI, maps Internet hop routes, tracks real-time traffic, and enforces router-level blocking.",
    hero_btn_download: "Download Software (v1.0.0)",
    hero_btn_demo: "Explore Dashboard Demo",
    badge_win: "Windows 10/11 Ready",
    badge_unix: "Linux & macOS Ready",
    badge_portable: "Portable Zero-Python",
    badge_bilingual: "Bilingual EN / VI",

    // Metrics Bar
    metric_subnets: "Subnet CIDR Discovery",
    metric_subnets_desc: "Auto-resolves CIDR subnets",
    metric_speed: "Multithreaded Scan Speed",
    metric_speed_desc: "Parallel Nmap ARP & Ping",
    metric_oui: "MAC OUI Database",
    metric_oui_desc: "Identifies Apple, Dell, IoT",
    metric_routers: "Router Hardware",
    metric_routers_desc: "TP-Link, OpenWrt, MikroTik, Mock",

    // Flow Diagram
    flow_title: "System Architecture Flow",
    flow_subtitle: "Dataflow pipeline from network devices through Agent, Server API to Web Client",

    // Reviews & Testimonials
    testimonials_tag: "CUSTOMER TESTIMONIALS",
    testimonials_title: "Real Reviews From Network Engineers",
    testimonials_subtitle: "Trusted by infrastructure engineers and enterprise system administrators worldwide",

    // About Page
    about_title: "About Network Manager",
    about_desc: "Comprehensive overview of system objectives, 3-tier architecture, and core technologies.",
    about_q1: "What is Network Manager?",
    about_a1: "Network Manager is a professional-grade local network management suite. Unlike basic scanners, it performs multi-tier topology analysis, differentiating Primary Modems and Sub-Routers, mapping physical Wi-Fi/LAN links, and enabling hardware-level device blocking.",
    about_case_title: "Production Case Studies",
    about_case_1_title: "3-Floor Coffee Shop Chain",
    about_case_1_infra: "Infrastructure: 1 ISP Modem + 3 Access Points",
    about_case_1_desc: "150+ concurrent guest devices. Network Manager segregates per-floor IP ranges and immediately terminates unauthorized torrent downloads.",
    about_case_2_title: "50-Seat Tech Enterprise",
    about_case_2_infra: "Infrastructure: Corporate Office LAN",
    about_case_2_desc: "Staff bringing personal devices (BYOD). Automatic 2-way firewall synchronization isolates untrusted hosts in milliseconds.",
    about_case_3_title: "Smarthome with 40+ IoT Devices",
    about_case_3_infra: "Infrastructure: Sub-Router 192.168.110.x",
    about_case_3_desc: "Continuous latency tracking for Ezviz cameras and ESP32 relays with automated hop path failure alerts.",
    about_q2: "System Goals & Objectives",
    about_goal_1_title: "Zero-Trust Security",
    about_goal_1_desc: "Instant discovery of rogue Wi-Fi connections with real-time security alerts.",
    about_goal_2_title: "One-Click Enforcement",
    about_goal_2_desc: "Dispatches direct hardware MAC ACL block commands to TP-Link, OpenWrt, MikroTik.",
    about_goal_3_title: "Total Observability",
    about_goal_3_desc: "Maps complete Internet Hop Paths with real-time multi-stream bandwidth waveforms.",
    about_team_title: "Engineering Core Team",

    // Features Page
    features_title: "Comprehensive Features",
    features_desc: "Complete 7-module architecture covering all aspects of network administration and security.",
    feat_1_title: "1. Device Management",
    feat_1_desc: "Detects IP, MAC, hardware OUI vendor, classifies 6 device groups, and allows custom alias tagging.",
    feat_2_title: "2. Network Monitoring",
    feat_2_desc: "Automated periodic subnet scanning at configurable intervals to detect connection shifts instantly.",
    feat_3_title: "3. Status & Latency Checking",
    feat_3_desc: "Sub-millisecond ICMP ping latency measurement with clear Online, Offline, and Blocked indicators.",
    feat_4_title: "4. Subnet & IP Allocation",
    feat_4_desc: "Segregates Primary Wi-Fi (192.168.1.x) and Secondary Router (192.168.110.x) with IP conflict detection.",
    feat_5_title: "5. Real-Time Traffic Tracking",
    feat_5_desc: "Live dual-waveform bandwidth monitor with download and upload throughput meters.",
    feat_6_title: "6. Real-Time Security Alerts",
    feat_6_desc: "Instant notifications for rogue device joins, unauthorizations, or connection policy violations.",
    feat_7_title: "7. Audit Logging & Compliance",
    feat_7_desc: "Persists all network telemetry into an embedded SQLite database with CSV export and audit verification.",

    // Downloads Page
    download_header_tag: "OFFICIAL DISTRIBUTION HUB",
    download_title: "Download Software",
    download_subtitle: "Official stable releases, digitally verified with SHA-256 checksums",
    download_win_desc: "Windows 10 / 11 (64-bit)",
    download_linux_desc: "Ubuntu, Debian, Fedora, Arch",
    download_mac_desc: "macOS 12.0+ (Apple Silicon M1-M4)",
    download_checksum_title: "SHA-256 Integrity Verification",
    download_copy_btn: "Copy SHA-256",
    download_sys_req_title: "Minimum System Requirements",

    // Docs Page
    docs_title: "Documentation & Guides",
    docs_desc: "Complete manual covering installation, usage, REST API reference, FAQ, and troubleshooting.",
    doc_tab_install: "1. Installation Guide",
    doc_tab_usage: "2. User Manual",
    doc_tab_api: "3. REST API Specification",
    doc_tab_faq: "4. Frequently Asked Questions (FAQs)",
    doc_tab_troubleshoot: "5. Troubleshooting",

    // News Page
    news_title: "News & Announcements",
    news_desc: "Stay updated with the latest releases, roadmap milestones, and security enhancements.",
    news_roadmap_title: "Product Roadmap",

    // Contact Page
    contact_title: "Contact & Support",
    contact_desc: "Our engineering team is ready to assist with installation, router setup, and feedback.",
    contact_channels_title: "Official Support Channels",
    contact_promise_title: "Support SLA Guarantee:",
    contact_promise_1: "Technical inquiries answered within 2 business hours.",
    contact_promise_2: "Infrastructure reliability: 99.98% Uptime SLA.",
    contact_office_title: "Engineering Office",
    contact_form_title: "Send an Online Inquiry",
    contact_lbl_name: "Your Full Name:",
    contact_lbl_email: "Email Address:",
    contact_lbl_subject: "Subject / Topic:",
    contact_lbl_msg: "Detailed Message:",
    contact_btn_send: "Send Support Request",

    // Footer
    footer_tagline: "Next-generation local network management, topology mapping, and router-level access control suite. Automatically detects 100% of devices.",
    footer_col_nav: "Main Pages",
    footer_col_support: "Resources & Support",
    footer_disclaimer_title: "Security & Legal Notice:",
    footer_disclaimer: "Designed for authorized network administration, monitoring, and educational research on networks you own or administer. Unauthorized network scanning is prohibited.",
    footer_copyright: "© 2026 Network Manager. All rights reserved by Core Engineering Team.",

    // Dashboard General
    demo_title: "Network Management Dashboard Demo",
    demo_desc: "Production layout featuring Sidebar, Online/Offline metrics, CPU/RAM, wave chart, and live Block/Unblock actions."
  }
};

// ==================== MOCK DATA FOR DASHBOARD ====================
let demoDevices = [
  {
    id: 1,
    name: "Dell XPS 15 (Workstation)",
    ip: "192.168.1.102",
    mac: "38:B1:DB:54:A8:12",
    vendor: "Dell Inc.",
    type: "PC / Laptop",
    network: "Wi-Fi Tổng (192.168.1.x)",
    subnet: "primary",
    medium: "Wi-Fi",
    status: "ONLINE",
    latency: "2 ms"
  },
  {
    id: 2,
    name: "iPhone 15 Pro Max",
    ip: "192.168.1.115",
    mac: "BC:D1:D3:45:90:E2",
    vendor: "Apple, Inc.",
    type: "Smartphone / Tablet",
    network: "Wi-Fi Tổng (192.168.1.x)",
    subnet: "primary",
    medium: "Wi-Fi",
    status: "ONLINE",
    latency: "14 ms"
  },
  {
    id: 3,
    name: "Samsung Neo QLED 4K TV",
    ip: "192.168.110.45",
    mac: "64:1C:67:8A:23:4F",
    vendor: "Samsung Electronics",
    type: "IoT Smart Device",
    network: "Router Phụ (192.168.110.x)",
    subnet: "secondary",
    medium: "LAN",
    status: "ONLINE",
    latency: "5 ms"
  },
  {
    id: 4,
    name: "Ezviz C6N Security Cam",
    ip: "192.168.110.88",
    mac: "AC:BC:32:89:12:34",
    vendor: "Hangzhou Hikvision",
    type: "IoT Smart Device",
    network: "Router Phụ (192.168.110.x)",
    subnet: "secondary",
    medium: "Wi-Fi",
    status: "ONLINE",
    latency: "18 ms"
  },
  {
    id: 5,
    name: "ESP32 Smart Home Relay",
    ip: "192.168.110.99",
    mac: "24:6F:28:FE:19:6A",
    vendor: "Espressif Inc.",
    type: "IoT Smart Device",
    network: "Router Phụ (192.168.110.x)",
    subnet: "secondary",
    medium: "Wi-Fi",
    status: "ONLINE",
    latency: "9 ms"
  },
  {
    id: 6,
    name: "TP-Link Archer AX55 (Sub-Router)",
    ip: "192.168.1.2",
    mac: "50:D4:F7:2C:19:A1",
    vendor: "TP-Link Corporation",
    type: "Router / Gateway",
    network: "Wi-Fi Tổng (192.168.1.x)",
    subnet: "primary",
    medium: "LAN",
    status: "ONLINE",
    latency: "1 ms"
  },
  {
    id: 7,
    name: "MacBook Pro M2 (Nam)",
    ip: "192.168.1.189",
    mac: "3C:06:30:19:67:BC",
    vendor: "Apple, Inc.",
    type: "PC / Laptop",
    network: "Wi-Fi Tổng (192.168.1.x)",
    subnet: "primary",
    medium: "Wi-Fi",
    status: "OFFLINE",
    latency: "--"
  }
];

// ==================== UNIQUE PAGE TITLES (Item 11) ====================
const pageTitles = {
  vi: {
    home: "Network Manager - Quản Lý & Giám Sát Mạng Nội Bộ Chuyên Nghiệp",
    about: "Giới Thiệu Hệ Thống Network Manager | Kiến Trúc 3 Lớp & Công Nghệ",
    features: "Tính Năng Nổi Bật | Network Manager - Quản Lý Thiết Bị, Topo & QoS",
    dashboard: "Dashboard Demo Tương Tác | Network Manager Live Simulation",
    download: "Tải Xuống Phần Mềm Network Manager (Windows, Linux, macOS) | SHA-256",
    docs: "Tài Liệu Kỹ Thuật & 5 FAQs Hướng Dẫn | Network Manager Docs",
    news: "Tin Tức & Lịch Sử Phiên Bản v1.0.0 | Network Manager Updates",
    contact: "Liên Hệ Hỗ Trợ Kỹ Thuật SLA < 2h | Network Manager Support"
  },
  en: {
    home: "Network Manager - Enterprise Local Network Management Suite",
    about: "About Network Manager | 3-Tier Architecture & Technology Stack",
    features: "Comprehensive Features | Network Manager - Devices, Topology & QoS",
    dashboard: "Interactive Dashboard Demo | Network Manager Live Simulation",
    download: "Download Network Manager (Windows, Linux, macOS) | SHA-256 Verified",
    docs: "Technical Documentation & 5 FAQs | Network Manager Docs",
    news: "News & Release Notes v1.0.0 | Network Manager Updates",
    contact: "Contact & Technical Support SLA < 2h | Network Manager Support"
  }
};

let currentLang = localStorage.getItem("nm_lang") || "vi";
let activeDemoFilter = "all";
let demoSearchTerm = "";


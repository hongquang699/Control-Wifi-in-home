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
    nav_home: "Trang chủ",
    nav_about: "Giới thiệu",
    nav_features: "Tính năng",
    nav_dashboard: "Dashboard Demo",
    nav_download: "Tải xuống",
    nav_docs: "Tài liệu",
    nav_news: "Tin tức",
    nav_contact: "Liên hệ",
    nav_btn_download: "Tải bản v1.0",

    hero_badge: "HỆ THỐNG QUẢN LÝ MẠNG TOÀN DIỆN V1.0.0",
    hero_title_1: "Giám Sát Toàn Diện,",
    hero_title_2: "Phân Tích Đa Tầng",
    hero_title_3: "& Kiểm Soát An Ninh Mạng",
    hero_desc: "Giải pháp quản trị mạng cục bộ tự động phát hiện 100% thiết bị LAN/WLAN, nhận diện phần cứng qua OUI, lập sơ đồ Internet Hop Path, giám sát băng thông thời gian thực và quản lý chặn thiết bị qua Router phần cứng.",
    hero_btn_download: "Tải xuống phần mềm (v1.0.0)",
    hero_btn_demo: "Trải nghiệm Dashboard Demo",

    metric_subnets: "Phát hiện Subnet CIDR",
    metric_subnets_desc: "Tự động tính dải /24, /16",
    metric_speed: "Thời gian quét đa luồng",
    metric_speed_desc: "Nmap ARP + Native Ping song song",
    metric_oui: "Kho dữ liệu MAC OUI",
    metric_oui_desc: "Nhận diện Apple, Dell, Intel, IoT",
    metric_routers: "Router Adapter",
    metric_routers_desc: "TP-Link, OpenWrt, MikroTik, Mock",

    flow_title: "Sơ Đồ Hoạt Động Của Hệ Thống",
    flow_subtitle: "Mô hình luồng dữ liệu từ thiết bị mạng qua Agent, Server API đến giao diện Web Client",

    about_title: "Giới Thiệu Hệ Thống Quản Lý Mạng",
    about_desc: "Tổng quan về mục tiêu, kiến trúc phân tầng 3 lớp và các công nghệ cốt lõi của Network Manager.",
    about_q1: "Hệ thống Network Manager là gì?",
    about_a1: "Network Manager là bộ giải pháp phần mềm quản trị và giám sát mạng nội bộ (LAN/WLAN) chuyên nghiệp. Khác với các công cụ quét IP thông thường, hệ thống tích hợp khả năng phân tích đa tầng (Multi-tier Topology), bóc tách rõ ràng giữa Modem Tổng ISP và Router Phụ, xác định phương thức liên kết Wi-Fi/LAN và cung cấp khả năng chặn thiết bị trực tiếp tại Router phần cứng.",
    about_q2: "Mục Tiêu Của Hệ Thống",
    about_q3: "Kiến Trúc Hệ Thống (3 Lớp)",
    about_q4: "Công Nghệ Sử Dụng",

    features_title: "Tính Năng Hệ Thống Quản Lý Mạng",
    features_desc: "Đầy đủ 7 module chức năng phục vụ toàn diện công tác quản trị và an ninh mạng nội bộ.",

    demo_title: "Dashboard Quản Lý Mạng Minh Họa",
    demo_desc: "Bố cục Dashboard thực tế với Sidebar, chỉ số Online/Offline, CPU/RAM, biểu đồ sóng và thao tác Chặn/Bỏ chặn trực tiếp.",

    docs_title: "Tài Liệu Kỹ Thuật & Hướng Dẫn",
    docs_desc: "Cẩm nang hướng dẫn cài đặt, sử dụng, đặc tả API RESTful, FAQ và xử lý sự cố.",

    news_title: "Tin Tức & Cập Nhật Hệ Thống",
    news_desc: "Thông tin phát hành phiên bản mới, tính năng bổ sung và lộ trình phát triển.",

    contact_title: "Liên Hệ & Hỗ Trợ Kỹ Thuật",
    contact_desc: "Đội ngũ kỹ thuật luôn sẵn sàng hỗ trợ cài đặt, cấu hình router và tiếp nhận phản hồi.",

    footer_tagline: "Hệ thống quản lý, giám sát và kiểm soát an ninh mạng nội bộ thế hệ mới. Tự động phát hiện 100% thiết bị, lập sơ đồ Internet Hop Path và kiểm soát truy cập cấp Router.",
    footer_disclaimer: "Phần mềm được phát triển cho mục đích quản trị mạng được ủy quyền, giám sát an toàn hệ thống và học tập nghiên cứu trên hạ tầng thuộc quyền sở hữu. Mọi hành vi can thiệp trái phép đều bị nghiêm cấm."
  },

  en: {
    nav_home: "Home",
    nav_about: "About",
    nav_features: "Features",
    nav_dashboard: "Dashboard Demo",
    nav_download: "Downloads",
    nav_docs: "Documentation",
    nav_news: "News",
    nav_contact: "Contact",
    nav_btn_download: "Download v1.0",

    hero_badge: "COMPREHENSIVE NETWORK MANAGEMENT SUITE V1.0.0",
    hero_title_1: "Comprehensive Monitoring,",
    hero_title_2: "Multi-Tier Topology",
    hero_title_3: "& Network Access Control",
    hero_desc: "Enterprise-grade local network management suite: Automatically discovers 100% of devices, identifies hardware vendors via OUI, maps Internet hop routes, tracks real-time traffic, and enforces router-level blocking.",
    hero_btn_download: "Download Software (v1.0.0)",
    hero_btn_demo: "Explore Dashboard Demo",

    metric_subnets: "Subnet CIDR Discovery",
    metric_subnets_desc: "Auto-resolves CIDR subnets",
    metric_speed: "Multithreaded Scan Speed",
    metric_speed_desc: "Parallel Nmap ARP & Ping",
    metric_oui: "MAC OUI Database",
    metric_oui_desc: "Identifies Apple, Dell, IoT",
    metric_routers: "Router Hardware",
    metric_routers_desc: "TP-Link, OpenWrt, MikroTik, Mock",

    flow_title: "System Architecture Flow",
    flow_subtitle: "Dataflow pipeline from network devices through Agent, Server API to Web Client",

    about_title: "About Network Manager",
    about_desc: "Comprehensive overview of system objectives, 3-tier architecture, and core technologies.",
    about_q1: "What is Network Manager?",
    about_a1: "Network Manager is a professional-grade local network management suite. Unlike basic scanners, it performs multi-tier topology analysis, differentiating Primary Modems and Sub-Routers, mapping physical Wi-Fi/LAN links, and enabling hardware-level device blocking.",
    about_q2: "System Goals & Objectives",
    about_q3: "3-Tier System Architecture",
    about_q4: "Technologies & Stack",

    features_title: "Comprehensive Features",
    features_desc: "Complete 7-module architecture covering all aspects of network administration and security.",

    demo_title: "Network Management Dashboard Demo",
    demo_desc: "Production layout featuring Sidebar, Online/Offline metrics, CPU/RAM, wave chart, and live Block/Unblock actions.",

    docs_title: "Documentation & Guides",
    docs_desc: "Complete manual covering installation, usage, REST API reference, FAQ, and troubleshooting.",

    news_title: "News & Announcements",
    news_desc: "Stay updated with the latest releases, roadmap milestones, and security enhancements.",

    contact_title: "Contact & Support",
    contact_desc: "Our engineering team is ready to assist with installation, router setup, and feedback.",

    footer_tagline: "Next-generation local network management, topology mapping, and router-level access control suite. Automatically detects 100% of devices.",
    footer_disclaimer: "Designed for authorized network administration, monitoring, and educational research on networks you own or administer. Unauthorized network scanning is prohibited."
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


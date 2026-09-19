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

// ==================== INITIALIZATION ====================
document.addEventListener("DOMContentLoaded", () => {
  initRouter();
  applyLanguage(currentLang);
  setupLanguageSwitcher();
  setupMobileDrawer();
  setupDashboardDemo();
  setupDocsNavigation();
  setupContactForm();
  setupLightbox();
  setupDownloadTracking();
  initDemoWaveCanvas();
});

// ==================== CLIENT-SIDE ROUTER ====================
function initRouter() {
  const handleRoute = () => {
    let hash = window.location.hash.replace("#/", "").replace("#", "") || "home";
    
    // Allowed pages
    const validPages = ["home", "about", "features", "dashboard", "download", "docs", "news", "contact"];
    if (!validPages.includes(hash)) {
      hash = "home";
    }

    // Toggle pages
    document.querySelectorAll(".page-view").forEach(page => {
      if (page.id === `page-${hash}`) {
        page.classList.remove("hidden");
      } else {
        page.classList.add("hidden");
      }
    });

    // Update active navbar styles
    document.querySelectorAll(".nav-item").forEach(item => {
      const pageTarget = item.getAttribute("data-page");
      if (pageTarget === hash) {
        item.classList.add("bg-sky-500/10", "text-sky-400", "font-semibold");
        item.classList.remove("text-slate-300");
      } else {
        item.classList.remove("bg-sky-500/10", "text-sky-400", "font-semibold");
        item.classList.add("text-slate-300");
      }
    });

    // Dynamic document title update (Item 11)
    const title = (pageTitles[currentLang] && pageTitles[currentLang][hash]) || pageTitles[currentLang].home;
    document.title = title;

    // Google Analytics Event Tracking (Item 19)
    if (typeof gtag === "function") {
      gtag("event", "page_view", {
        page_title: title,
        page_path: window.location.hash || "#/home",
        page_location: window.location.href
      });
    }

    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  window.addEventListener("hashchange", handleRoute);
  handleRoute();
}

// ==================== BILINGUAL ENGINE ====================
function applyLanguage(lang) {
  currentLang = lang;
  localStorage.setItem("nm_lang", lang);
  const dict = i18nData[lang] || i18nData.vi;

  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.getAttribute("data-i18n");
    if (dict[key]) {
      el.textContent = dict[key];
    }
  });

  // Update dynamic document title for current page (Item 11)
  let currentHash = window.location.hash.replace("#/", "").replace("#", "") || "home";
  if (pageTitles[lang] && pageTitles[lang][currentHash]) {
    document.title = pageTitles[lang][currentHash];
  }

  const langLabel = document.getElementById("currentLangLabel");
  if (langLabel) {
    langLabel.textContent = lang === "vi" ? "🇻🇳 Tiếng Việt" : "🇬🇧 English";
  }

  renderDemoDevices();
}

function setupLanguageSwitcher() {
  const btn = document.getElementById("langToggleBtn");
  if (btn) {
    btn.addEventListener("click", () => {
      const next = currentLang === "vi" ? "en" : "vi";
      applyLanguage(next);
      showToast(next === "vi" ? "Đã chuyển sang Tiếng Việt" : "Switched to English");
    });
  }
}

// ==================== MOBILE DRAWER ====================
function setupMobileDrawer() {
  const btn = document.getElementById("mobileMenuBtn");
  const drawer = document.getElementById("mobileDrawer");
  if (!btn || !drawer) return;

  btn.addEventListener("click", () => {
    drawer.classList.toggle("hidden");
  });

  document.querySelectorAll(".mobile-nav-item").forEach(item => {
    item.addEventListener("click", () => {
      drawer.classList.add("hidden");
    });
  });
}

// ==================== DASHBOARD DEMO ====================
// ==================== DASHBOARD DEMO ENGINE ====================
let activeDevSubnetFilter = "all";
let devSearchTerm = "";
let currentModalDeviceId = null;
let isWaveAnimationPaused = false;
let activeAlertFilter = "all";

let demoAlertsData = [
  {
    id: "alt-1",
    level: "WARNING",
    title: "Phát hiện thiết bị mới kết nối",
    title_en: "New Device Joined Network",
    desc: "Thiết bị IP 192.168.1.115 (Apple iPhone 15 Pro) vừa gia nhập Wi-Fi Tổng qua cổng 802.11ax.",
    desc_en: "Device IP 192.168.1.115 (Apple iPhone 15 Pro) joined Primary Wi-Fi via 802.11ax.",
    time: "2026-09-19 08:45:12"
  },
  {
    id: "alt-2",
    level: "INFO",
    title: "Quét mạng định kỳ thành công",
    title_en: "Periodic Scan Completed",
    desc: "Đã quét 2 dải subnet 192.168.1.0/24 & 110.0/24. Phát hiện 7 thiết bị trực tuyến.",
    desc_en: "Scanned 2 subnets 192.168.1.0/24 & 110.0/24. Found 7 active devices.",
    time: "2026-09-19 09:15:00"
  },
  {
    id: "alt-3",
    level: "SUCCESS",
    title: "Tường lửa đồng bộ an toàn",
    title_en: "Firewall Synchronized",
    desc: "Các quy tắc chặn 2 chiều Inbound/Outbound của Windows Defender Firewall đang hoạt động tối ưu.",
    desc_en: "Bidirectional Inbound/Outbound Windows Firewall rules operating properly.",
    time: "2026-09-19 08:30:00"
  },
  {
    id: "alt-4",
    level: "INFO",
    title: "Giám sát lưu lượng khởi động",
    title_en: "Traffic Monitor Started",
    desc: "Thuật toán theo dõi băng thông thời gian thực và tạo biểu đồ sóng 60 giây đã kích hoạt.",
    desc_en: "Real-time bandwidth tracker and waveform generator initialized.",
    time: "2026-09-19 08:00:00"
  }
];

let demoLogsData = [
  {
    time: "2026-09-19 09:15:00",
    event_type: "SCAN_COMPLETED",
    ip: "192.168.1.0/24",
    mac: "Interface #1",
    desc: "Quét định kỳ 2 dải mạng thành công. 7 thiết bị trực tuyến, 0 lỗi."
  },
  {
    time: "2026-09-19 08:45:12",
    event_type: "DEVICE_JOINED",
    ip: "192.168.1.115",
    mac: "E4:5F:01:88:99:AA",
    desc: "Thiết bị Apple iPhone 15 Pro Max kết nối vào mạng Wi-Fi Tổng."
  },
  {
    time: "2026-09-19 08:30:00",
    event_type: "FIREWALL_SYNC",
    ip: "127.0.0.1",
    mac: "Host Windows",
    desc: "Đồng bộ quy tắc Windows Defender Firewall chặn 2 chiều Inbound/Outbound."
  },
  {
    time: "2026-09-19 08:14:20",
    event_type: "DEVICE_JOINED",
    ip: "192.168.110.88",
    mac: "AC:BC:32:89:12:34",
    desc: "Camera giám sát Ezviz C6N kết nối qua luồng RTSP Router Phụ."
  },
  {
    time: "2026-09-19 08:02:11",
    event_type: "DEVICE_LEFT",
    ip: "192.168.1.189",
    mac: "3C:06:30:19:67:BC",
    desc: "MacBook Pro M2 chuyển sang trạng thái ngủ (Sleep / Offline)."
  }
];

function setupDashboardDemo() {
  renderDemoDevices();
  renderFullDevicesTable();
  renderAlerts();
  renderLogs();
  fetchLiveApiData();
  setupDevicesFilter();
  setupAlertsFilter();
  loadSavedSettings();

  // Sidebar Tabs Switching (7 items matching screenshot)
  document.querySelectorAll(".demo-nav-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const tab = btn.getAttribute("data-demo-tab");
      switchDemoTab(tab);
    });
  });

  // Filters on Dashboard tab
  document.querySelectorAll(".demo-filter").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".demo-filter").forEach(b => {
        b.classList.remove("bg-sky-500/20", "text-sky-300", "border-sky-500/40");
        b.classList.add("bg-slate-900", "border-slate-800", "text-slate-400");
      });
      btn.classList.add("bg-sky-500/20", "text-sky-300", "border-sky-500/40");
      btn.classList.remove("bg-slate-900", "border-slate-800", "text-slate-400");

      activeDemoFilter = btn.getAttribute("data-filter");
      renderDemoDevices();
    });
  });

  // Search on Dashboard tab
  const searchInput = document.getElementById("demoSearchInput");
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      demoSearchTerm = e.target.value;
      renderDemoDevices();
    });
  }

  // Real-time Traffic Fluctuation Simulator (Every 2s)
  setInterval(() => {
    if (isWaveAnimationPaused) return;
    const downEl = document.getElementById("trafficLiveDown");
    const upEl = document.getElementById("trafficLiveUp");
    const demoDown = document.getElementById("demoDownloadSpeed");
    const demoUp = document.getElementById("demoUploadSpeed");
    
    const randomDown = (24.0 + (Math.random() * 2.2 - 1.1)).toFixed(1);
    const randomUp = (8.2 + (Math.random() * 0.8 - 0.4)).toFixed(1);

    if (downEl) downEl.textContent = `${randomDown} MB/s`;
    if (upEl) upEl.textContent = `${randomUp} MB/s`;
    if (demoDown) demoDown.textContent = `↓ ${randomDown} MB/s`;
    if (demoUp) demoUp.textContent = `↑ ${randomUp} MB/s`;
  }, 2000);
}

function switchDemoTab(tab) {
  if (!tab) return;
  
  // Highlight active sidebar button
  document.querySelectorAll(".demo-nav-btn").forEach(b => {
    if (b.getAttribute("data-demo-tab") === tab) {
      b.className = "demo-nav-btn w-full flex items-center gap-3 px-3 py-2.5 rounded-xl bg-sky-500/20 text-sky-300 font-semibold border border-sky-500/30 text-left";
    } else {
      b.className = "demo-nav-btn w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800/60 transition-all text-left";
    }
  });

  // Toggle tab panels
  document.querySelectorAll(".demo-tab-panel").forEach(panel => {
    panel.classList.add("hidden");
  });
  const targetId = "demoTab" + tab.charAt(0).toUpperCase() + tab.slice(1);
  const targetEl = document.getElementById(targetId);
  if (targetEl) {
    targetEl.classList.remove("hidden");
  }

  // Trigger tab-specific initialization
  if (tab === "devices") {
    renderFullDevicesTable();
  } else if (tab === "traffic") {
    initDemoWaveCanvas2();
    fetchLiveTraffic();
  } else if (tab === "logs") {
    renderLogs();
    fetchLiveLogs();
  } else if (tab === "alerts") {
    renderAlerts();
    fetchLiveAlerts();
  }
}

// ----------------------------------------------------
// TAB 2: DEVICES ENGINE
// ----------------------------------------------------
function setupDevicesFilter() {
  document.querySelectorAll(".dev-filter-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".dev-filter-btn").forEach(b => {
        b.classList.remove("bg-sky-500/20", "text-sky-300", "border-sky-500/40");
        b.classList.add("bg-slate-900", "border-slate-800", "text-slate-400");
      });
      btn.classList.add("bg-sky-500/20", "text-sky-300", "border-sky-500/40");
      btn.classList.remove("bg-slate-900", "border-slate-800", "text-slate-400");

      activeDevSubnetFilter = btn.getAttribute("data-dev-filter");
      renderFullDevicesTable();
    });
  });

  const input = document.getElementById("devSearchInput");
  if (input) {
    input.addEventListener("input", (e) => {
      devSearchTerm = e.target.value;
      renderFullDevicesTable();
    });
  }
}

function getDeviceIcon(type, name) {
  const lower = (type + " " + name).toLowerCase();
  if (lower.includes("phone") || lower.includes("iphone") || lower.includes("android")) return "📱";
  if (lower.includes("tv") || lower.includes("qled") || lower.includes("samsung")) return "📺";
  if (lower.includes("cam") || lower.includes("ezviz") || lower.includes("hikvision")) return "📹";
  if (lower.includes("router") || lower.includes("gateway") || lower.includes("tp-link")) return "📡";
  if (lower.includes("relay") || lower.includes("esp32") || lower.includes("iot")) return "🔌";
  return "💻";
}

function renderFullDevicesTable() {
  const tbody = document.getElementById("demoDevicesTableFull");
  if (!tbody) return;

  const countEl = document.getElementById("devFilterCountAll");
  if (countEl) countEl.textContent = demoDevices.length;

  let filtered = demoDevices.filter(d => {
    if (activeDevSubnetFilter === "primary" && d.subnet !== "primary") return false;
    if (activeDevSubnetFilter === "secondary" && d.subnet !== "secondary") return false;
    if (activeDevSubnetFilter === "blocked" && d.status !== "BLOCKED") return false;
    if (devSearchTerm.trim()) {
      const q = devSearchTerm.toLowerCase();
      return d.name.toLowerCase().includes(q) || d.ip.toLowerCase().includes(q) || d.mac.toLowerCase().includes(q) || d.vendor.toLowerCase().includes(q);
    }
    return true;
  });

  tbody.innerHTML = filtered.map(d => {
    const isBlocked = d.status === "BLOCKED";
    const statusBadge = d.status === "ONLINE"
      ? `<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">ONLINE</span>`
      : d.status === "BLOCKED"
      ? `<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30">BLOCKED</span>`
      : `<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-800 text-slate-400">OFFLINE</span>`;

    const btnBlockText = isBlocked ? (currentLang === "vi" ? "Bỏ chặn" : "Unblock") : (currentLang === "vi" ? "Chặn" : "Block");
    const btnBlockClass = isBlocked
      ? "bg-emerald-600/20 text-emerald-300 border-emerald-500/40 hover:bg-emerald-600/30"
      : "bg-rose-600/20 text-rose-300 border-rose-500/40 hover:bg-rose-600/30";

    const icon = getDeviceIcon(d.type, d.name);

    return `
      <tr class="hover:bg-slate-800/40 transition-colors">
        <td class="py-3 px-4 font-medium text-white">
          <div class="flex items-center gap-2.5">
            <span class="text-base p-1.5 rounded-lg bg-slate-900 border border-slate-800">${icon}</span>
            <div>
              <div class="font-bold text-white">${d.name}</div>
              <div class="text-[10px] text-slate-400">${d.type}</div>
            </div>
          </div>
        </td>
        <td class="py-3 px-4 font-mono text-sky-400 font-semibold">${d.ip}</td>
        <td class="py-3 px-4 font-mono text-slate-400 text-[11px]">${d.mac}</td>
        <td class="py-3 px-4 text-slate-300">${d.vendor}</td>
        <td class="py-3 px-4 font-mono text-[11px]">
          <div class="text-slate-300">${d.network}</div>
          <div class="text-[10px] text-slate-500">${d.medium === "Wi-Fi" ? "📶 Wi-Fi 5GHz" : "🔌 Dây LAN 1Gbps"}</div>
        </td>
        <td class="py-3 px-4 font-mono text-emerald-400 font-semibold">${d.latency || "2 ms"}</td>
        <td class="py-3 px-4">${statusBadge}</td>
        <td class="py-3 px-4 text-right">
          <div class="flex items-center justify-end gap-1.5">
            <button onclick="openDeviceModal(${d.id})" class="px-2.5 py-1 rounded-lg text-[11px] font-medium border border-slate-700 bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white transition-colors">
              Chi tiết
            </button>
            <button onclick="toggleDemoBlock(${d.id})" class="px-2.5 py-1 rounded-lg text-[11px] font-medium border transition-colors ${btnBlockClass}">
              ${btnBlockText}
            </button>
          </div>
        </td>
      </tr>
    `;
  }).join("");
}

window.simulateNetworkScan = function() {
  const btn = document.getElementById("btnScanNow");
  const spinner = document.getElementById("scanSpinner");
  const container = document.getElementById("scanProgressBarContainer");
  const bar = document.getElementById("scanProgressBar");
  const percentEl = document.getElementById("scanProgressPercent");
  const msgEl = document.getElementById("scanProgressMsg");

  if (!btn || !container) return;

  btn.disabled = true;
  btn.classList.add("opacity-60", "cursor-not-allowed");
  spinner.classList.add("animate-spin");
  container.classList.remove("hidden");

  const steps = [
    { p: 15, msg: "Nhận diện card mạng hoạt động (Wi-Fi 6 Intel AX200)..." },
    { p: 45, msg: "Gửi gói tin ARP Ping đa luồng trên dải 192.168.1.0/24..." },
    { p: 75, msg: "Quét dải phụ 192.168.110.0/24 & phân giải MAC OUI..." },
    { p: 100, msg: "Quét mạng hoàn tất! Phát hiện 7 thiết bị trực tuyến." }
  ];

  let currentStep = 0;
  const interval = setInterval(() => {
    if (currentStep < steps.length) {
      const s = steps[currentStep];
      bar.style.width = s.p + "%";
      percentEl.textContent = s.p + "%";
      msgEl.textContent = s.msg;
      currentStep++;
    } else {
      clearInterval(interval);
      setTimeout(() => {
        btn.disabled = false;
        btn.classList.remove("opacity-60", "cursor-not-allowed");
        spinner.classList.remove("animate-spin");
        container.classList.add("hidden");
        showToast(currentLang === "vi" ? "Quét mạng hoàn tất! Toàn bộ 7 thiết bị đã được đồng bộ." : "Scan completed! 7 devices synchronized.");
        renderDemoDevices();
        renderFullDevicesTable();
      }, 600);
    }
  }, 400);
};

window.openDeviceModal = function(id) {
  const d = demoDevices.find(item => item.id === id);
  if (!d) return;
  currentModalDeviceId = id;

  const modal = document.getElementById("deviceDetailModal");
  if (!modal) return;

  document.getElementById("modalDeviceIcon").textContent = getDeviceIcon(d.type, d.name);
  document.getElementById("modalDeviceName").textContent = d.name;
  document.getElementById("modalDeviceType").textContent = d.type;
  document.getElementById("modalDeviceIP").textContent = d.ip;
  document.getElementById("modalDeviceMAC").textContent = d.mac;
  document.getElementById("modalDeviceVendor").textContent = d.vendor;
  document.getElementById("modalDeviceNetwork").textContent = d.network;
  document.getElementById("modalDeviceMedium").textContent = d.medium === "Wi-Fi" ? "📶 Wi-Fi 5GHz (802.11ax)" : "🔌 Dây LAN 1Gbps (RJ45 Cat6)";
  document.getElementById("modalDeviceLatency").textContent = d.latency || "2 ms";
  
  const ports = d.subnet === "secondary" ? "554 (RTSP), 80 (HTTP), 1883 (MQTT)" : "80 (HTTP), 443 (HTTPS), 22 (SSH)";
  document.getElementById("modalDevicePorts").textContent = ports;
  
  const hopRoute = d.subnet === "secondary" 
    ? `${d.name} ➔ Router Phụ (192.168.110.1) ➔ Modem Tổng (192.168.1.1) ➔ WAN Gateway ➔ Internet`
    : `${d.name} ➔ Modem Tổng ISP (192.168.1.1) ➔ WAN Gateway ➔ Internet`;
  document.getElementById("modalDeviceHop").textContent = hopRoute;

  const btnBlock = document.getElementById("modalBtnToggleBlock");
  if (btnBlock) {
    if (d.status === "BLOCKED") {
      btnBlock.textContent = "Bỏ Chặn Thiết Bị Này";
      btnBlock.className = "px-4 py-2 rounded-xl bg-emerald-600/20 text-emerald-300 border border-emerald-500/40 hover:bg-emerald-600/30 text-xs font-semibold transition-all";
    } else {
      btnBlock.textContent = "Chặn Thiết Bị Này";
      btnBlock.className = "px-4 py-2 rounded-xl bg-rose-600/20 text-rose-300 border border-rose-500/40 hover:bg-rose-600/30 text-xs font-semibold transition-all";
    }
  }

  modal.classList.remove("hidden");
};

window.closeDeviceModal = function() {
  const modal = document.getElementById("deviceDetailModal");
  if (modal) modal.classList.add("hidden");
  currentModalDeviceId = null;
};

window.toggleModalBlock = function() {
  if (currentModalDeviceId !== null) {
    toggleDemoBlock(currentModalDeviceId);
    openDeviceModal(currentModalDeviceId);
  }
};

// ----------------------------------------------------
// TAB 3: NETWORKS & TOPOLOGY ENGINE
// ----------------------------------------------------
window.selectTopologyNode = function(nodeKey) {
  document.querySelectorAll(".topo-node").forEach(n => {
    n.classList.remove("ring-2", "ring-sky-400", "shadow-sky-500/30");
  });

  const selected = document.querySelector(`[data-node="${nodeKey}"]`);
  if (selected) {
    selected.classList.add("ring-2", "ring-sky-400", "shadow-sky-500/30");
  }

  const routeEl = document.getElementById("topoHopRouteText");
  const statusEl = document.getElementById("topoHopStatus");
  if (!routeEl || !statusEl) return;

  const nodeInfo = {
    internet: {
      route: "Internet Toàn Cầu ➔ Cáp Quang ISP (VNPT/Viettel/FPT) ➔ Cổng WAN Modem",
      status: "WAN Uplink • 1.2 Gbps Băng Thông",
      ip: "8.8.8.8"
    },
    modem: {
      route: "Modem Tổng ISP (192.168.1.1) ➔ Gateway ISP ➔ Internet Toàn Cầu",
      status: "1 Hop • 1 ms RTT (Trực Tuyến)",
      ip: "192.168.1.1"
    },
    subrouter: {
      route: "Router Phụ TP-Link (192.168.110.1) ➔ Modem Tổng (192.168.1.1) ➔ Internet",
      status: "1 Hop • 2 ms RTT (Gigabit LAN)",
      ip: "192.168.110.1"
    },
    macbook: {
      route: "MacBook Pro M2 (192.168.1.189) ➔ Wi-Fi Tổng (192.168.1.1) ➔ Internet",
      status: "1 Hop • 2 ms RTT (Wi-Fi 5GHz)",
      ip: "192.168.1.189"
    },
    iphone: {
      route: "iPhone 15 Pro (192.168.1.115) ➔ Wi-Fi Tổng (192.168.1.1) ➔ Internet",
      status: "1 Hop • 4 ms RTT (Wi-Fi 5GHz)",
      ip: "192.168.1.115"
    },
    tv: {
      route: "Samsung Smart 4K TV (192.168.110.45) ➔ Router Phụ (192.168.110.1) ➔ Modem Tổng ➔ Internet",
      status: "2 Hops • 5 ms RTT (Dây LAN)",
      ip: "192.168.110.45"
    },
    cam: {
      route: "Ezviz Cam C6N (192.168.110.88) ➔ Router Phụ (192.168.110.1) ➔ Modem Tổng ➔ Internet",
      status: "2 Hops • 12 ms RTT (Wi-Fi 2.4GHz)",
      ip: "192.168.110.88"
    },
    esp: {
      route: "ESP32 Relay (192.168.110.99) ➔ Router Phụ (192.168.110.1) ➔ Modem Tổng ➔ Internet",
      status: "2 Hops • 8 ms RTT (Wi-Fi 2.4GHz)",
      ip: "192.168.110.99"
    }
  };

  const info = nodeInfo[nodeKey] || nodeInfo.subrouter;
  routeEl.textContent = info.route;
  statusEl.textContent = info.status;

  const pingInput = document.getElementById("pingTargetInput");
  if (pingInput && info.ip) {
    pingInput.value = info.ip;
  }
};

window.runPingTest = function() {
  const input = document.getElementById("pingTargetInput");
  const output = document.getElementById("pingConsoleOutput");
  const spinner = document.getElementById("pingBtnSpinner");
  if (!input || !output) return;

  const target = input.value.trim() || "192.168.1.1";
  spinner.classList.add("animate-spin");
  output.innerHTML = `<div class="text-sky-400 font-bold">[PING] Bắt đầu gửi 4 gói tin ICMP (32 bytes) tới ${target}...</div>`;

  let packetIndex = 1;
  const timer = setInterval(() => {
    if (packetIndex <= 4) {
      const rtt = (1.2 + Math.random() * 2.5).toFixed(1);
      const ttl = target.startsWith("8.") || target.startsWith("1.") ? 116 : 64;
      const line = document.createElement("div");
      line.className = "text-slate-300";
      line.textContent = `Phản hồi từ ${target}: bytes=32 thời gian=${rtt}ms TTL=${ttl}`;
      output.appendChild(line);
      packetIndex++;
    } else {
      clearInterval(timer);
      spinner.classList.remove("animate-spin");
      const summary1 = document.createElement("div");
      summary1.className = "text-emerald-400 font-bold pt-1 border-t border-slate-800";
      summary1.textContent = `Thống kê Ping cho ${target}: Đã gửi = 4, Đã nhận = 4, Mất = 0 (0% loss)`;
      const summary2 = document.createElement("div");
      summary2.className = "text-slate-400";
      summary2.textContent = `Thời gian khứ hồi (RTT): Min = 1.2ms, Max = 3.6ms, Avg = 2.1ms`;
      output.appendChild(summary1);
      output.appendChild(summary2);
    }
  }, 300);
};

// ----------------------------------------------------
// TAB 4: TRAFFIC CONTROLS
// ----------------------------------------------------
window.toggleWaveAnimation = function() {
  isWaveAnimationPaused = !isWaveAnimationPaused;
  const icon = document.getElementById("wavePauseIcon");
  const text = document.getElementById("wavePauseText");
  if (icon && text) {
    if (isWaveAnimationPaused) {
      icon.textContent = "▶️";
      text.textContent = "Tiếp tục";
      showToast("Đã tạm dừng đồ thị sóng băng thông");
    } else {
      icon.textContent = "⏸️";
      text.textContent = "Tạm dừng";
      showToast("Đã kích hoạt lại đồ thị sóng băng thông");
    }
  }
};

// ----------------------------------------------------
// TAB 5: ALERTS ENGINE
// ----------------------------------------------------
function setupAlertsFilter() {
  document.querySelectorAll(".alert-filter-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".alert-filter-btn").forEach(b => {
        b.classList.remove("bg-sky-500/20", "text-sky-300", "border-sky-500/40");
        b.classList.add("bg-slate-900", "border-slate-800", "text-slate-400");
      });
      btn.classList.add("bg-sky-500/20", "text-sky-300", "border-sky-500/40");
      btn.classList.remove("bg-slate-900", "border-slate-800", "text-slate-400");

      activeAlertFilter = btn.getAttribute("data-alert-filter");
      renderAlerts();
    });
  });
}

function renderAlerts() {
  const el = document.getElementById("demoAlertsList");
  if (!el) return;

  const countTotal = document.getElementById("alertCountTotal");
  if (countTotal) countTotal.textContent = demoAlertsData.length;

  let filtered = demoAlertsData.filter(a => {
    if (activeAlertFilter === "all") return true;
    return a.level === activeAlertFilter;
  });

  if (filtered.length === 0) {
    el.innerHTML = `
      <div class="p-8 text-center text-slate-500 text-xs">
        <span>✅</span> Không có cảnh báo nào trong danh mục này. Hệ thống an toàn tuyệt đối.
      </div>
    `;
    return;
  }

  el.innerHTML = filtered.map(a => {
    const badgeClass = a.level === "CRITICAL" ? "bg-rose-500/20 text-rose-400 border-rose-500/30"
      : a.level === "WARNING" ? "bg-amber-500/20 text-amber-400 border-amber-500/30"
      : a.level === "SUCCESS" ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
      : "bg-sky-500/20 text-sky-400 border-sky-500/30";

    return `
      <div class="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-slate-800/20 transition-colors" id="alert-row-${a.id}">
        <div class="flex items-start gap-3">
          <span class="px-2 py-0.5 rounded text-[10px] font-bold border ${badgeClass}">${a.level}</span>
          <div>
            <div class="font-bold text-white text-xs">${currentLang === 'vi' ? a.title : a.title_en}</div>
            <div class="text-slate-400 text-[11px] mt-0.5">${currentLang === 'vi' ? a.desc : a.desc_en}</div>
            <div class="text-slate-500 text-[10px] font-mono mt-1">${a.time}</div>
          </div>
        </div>
        <div class="flex items-center gap-2 self-end sm:self-center">
          ${a.level === "CRITICAL" || a.level === "WARNING" ? `
            <button onclick="blockAlertAttacker('${a.id}')" class="px-2.5 py-1 rounded-lg text-[10px] font-bold border border-rose-500/40 bg-rose-500/20 text-rose-300 hover:bg-rose-500/30 transition-all">
              Chặn Kẻ Tấn Công
            </button>
          ` : ''}
          <button onclick="dismissAlert('${a.id}')" class="px-2.5 py-1 rounded-lg text-[10px] font-medium text-slate-400 hover:text-white bg-slate-900 border border-slate-800 hover:bg-slate-800 transition-all">
            Bỏ qua
          </button>
        </div>
      </div>
    `;
  }).join("");
}

window.simulateSecurityAlert = function() {
  const newAlert = {
    id: "alt-" + Date.now(),
    level: "CRITICAL",
    title: "Phát hiện quét cổng trái phép (Port Scan Attack)",
    title_en: "Port Scan Attack Detected",
    desc: "Thiết bị IP 192.168.1.205 (Rogue Device) đang quét dải cổng 20-1024 trên máy chủ nội bộ!",
    desc_en: "Rogue device IP 192.168.1.205 is scanning ports 20-1024 on local host!",
    time: new Date().toISOString().replace('T', ' ').substring(0, 19)
  };
  demoAlertsData.unshift(newAlert);
  renderAlerts();
  showToast("🚨 CẢNH BÁO: Phát hiện quét cổng trái phép từ IP 192.168.1.205!");
};

window.dismissAlert = function(id) {
  demoAlertsData = demoAlertsData.filter(a => a.id !== id);
  renderAlerts();
  showToast("Đã ẩn thông báo cảnh báo");
};

window.blockAlertAttacker = function(id) {
  showToast("🚫 ĐÃ GỬI LỆNH CHẶN KẺ TẤN CÔNG (IP 192.168.1.205) TỚI ROUTER & TƯỜNG LỬA!");
  dismissAlert(id);
};

window.clearAllAlerts = function() {
  demoAlertsData = [];
  renderAlerts();
  showToast("Đã đánh dấu xử lý toàn bộ cảnh báo an ninh mạng.");
};

// ----------------------------------------------------
// TAB 6: LOGS ENGINE & CSV EXPORT
// ----------------------------------------------------
function renderLogs() {
  const tbody = document.getElementById("demoLogsTableBody");
  if (!tbody) return;

  const typeFilter = document.getElementById("logTypeFilter") ? document.getElementById("logTypeFilter").value : "ALL";
  const searchInput = document.getElementById("logSearchInput");
  const keyword = searchInput ? searchInput.value.trim().toLowerCase() : "";

  let filtered = demoLogsData.filter(l => {
    if (typeFilter !== "ALL" && l.event_type !== typeFilter) return false;
    if (keyword) {
      const text = `${l.time} ${l.event_type} ${l.ip} ${l.mac} ${l.desc}`.toLowerCase();
      if (!text.includes(keyword)) return false;
    }
    return true;
  });

  if (filtered.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" class="py-6 text-center text-slate-500 font-sans text-xs">Không tìm thấy bản ghi sự kiện phù hợp.</td></tr>`;
    return;
  }

  tbody.innerHTML = filtered.map(l => {
    const isBlock = l.event_type.includes("BLOCK");
    const isJoin = l.event_type.includes("JOIN");
    const badgeClass = isBlock ? "bg-rose-500/20 text-rose-400 border-rose-500/30"
      : isJoin ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
      : "bg-sky-500/20 text-sky-400 border-sky-500/30";

    return `
      <tr class="hover:bg-slate-800/30 transition-colors">
        <td class="py-2.5 px-4 text-slate-400 font-mono text-[11px]">${l.time}</td>
        <td class="py-2.5 px-4">
          <span class="px-2 py-0.5 rounded text-[10px] font-bold border ${badgeClass}">
            ${l.event_type}
          </span>
        </td>
        <td class="py-2.5 px-4 text-sky-400 font-mono text-[11px]">${l.ip} <span class="text-slate-500">/</span> ${l.mac}</td>
        <td class="py-2.5 px-4 text-slate-300 font-sans text-xs">${l.desc}</td>
        <td class="py-2.5 px-4 text-right">
          <span class="text-[10px] text-slate-500 font-mono">AUDITED</span>
        </td>
      </tr>
    `;
  }).join("");
}

window.filterLogs = function() {
  renderLogs();
};

window.exportLogsToCSV = function() {
  let csvContent = "\uFEFFThời Gian,Loại Sự Kiện,Địa Chỉ IP,Địa Chỉ MAC,Mô Tả Chi Tiết\n";
  demoLogsData.forEach(l => {
    const descEscaped = `"${l.desc.replace(/"/g, '""')}"`;
    csvContent += `${l.time},${l.event_type},${l.ip},${l.mac},${descEscaped}\n`;
  });

  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.setAttribute("href", url);
  link.setAttribute("download", `network_audit_logs_${new Date().toISOString().substring(0, 10)}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  showToast(`Đã xuất ${demoLogsData.length} bản ghi nhật ký ra file CSV thành công!`);
};

window.clearLogsTable = function() {
  demoLogsData = [];
  renderLogs();
  showToast("Đã xóa sạch dữ liệu nhật ký sự kiện.");
};

// ----------------------------------------------------
// TAB 7: SETTINGS ENGINE
// ----------------------------------------------------
window.togglePasswordVisibility = function() {
  const input = document.getElementById("cfgRouterPass");
  const icon = document.getElementById("passToggleIcon");
  if (!input || !icon) return;

  if (input.type === "password") {
    input.type = "text";
    icon.textContent = "🙈";
  } else {
    input.type = "password";
    icon.textContent = "👁️";
  }
};

window.testRouterConnection = function() {
  const btn = document.getElementById("btnTestRouter");
  const spinner = document.getElementById("testRouterSpinner");
  const badge = document.getElementById("routerConnStatusBadge");
  const routerType = document.getElementById("cfgRouterType").value;
  const routerHost = document.getElementById("cfgRouterHost").value;

  if (!btn) return;
  btn.disabled = true;
  spinner.classList.add("animate-spin");
  badge.textContent = "⏳ Đang kết nối...";
  badge.className = "text-[10px] text-amber-400 font-mono px-2 py-0.5 rounded bg-amber-500/10 border border-amber-500/20";

  setTimeout(() => {
    btn.disabled = false;
    spinner.classList.remove("animate-spin");
    badge.textContent = `● Kết Nối Thành Công (${routerType.toUpperCase()} - 1.2ms)`;
    badge.className = "text-[10px] text-emerald-400 font-mono px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20";
    showToast(`Kết nối thành công tới Router ${routerHost} qua adapter ${routerType}!`);
  }, 750);
};

window.saveAllSettings = function() {
  const config = {
    router_type: document.getElementById("cfgRouterType").value,
    router_host: document.getElementById("cfgRouterHost").value,
    router_port: document.getElementById("cfgRouterPort").value,
    router_user: document.getElementById("cfgRouterUser").value,
    firewall_sync: document.getElementById("cfgFirewallSync").checked,
    auto_detect: document.getElementById("cfgAutoDetect").checked,
    scan_interval: document.getElementById("cfgIntervalRange").value,
    confirm_block: document.getElementById("cfgConfirmBlock").checked
  };

  localStorage.setItem("nm_demo_settings", JSON.stringify(config));
  showToast("💾 Đã lưu cấu hình hệ thống thành công vào bộ nhớ!");
};

window.resetDefaultSettings = function() {
  document.getElementById("cfgRouterType").value = "mock";
  document.getElementById("cfgRouterHost").value = "192.168.1.1";
  document.getElementById("cfgRouterPort").value = "80";
  document.getElementById("cfgRouterUser").value = "admin";
  document.getElementById("cfgRouterPass").value = "RouterAdmin@2026";
  document.getElementById("cfgFirewallSync").checked = true;
  document.getElementById("cfgAutoDetect").checked = true;
  document.getElementById("cfgIntervalRange").value = 60;
  document.getElementById("cfgIntervalValue").textContent = "60 giây";
  document.getElementById("cfgConfirmBlock").checked = true;

  localStorage.removeItem("nm_demo_settings");
  showToast("Đã khôi phục cài đặt mặc định của hệ thống.");
};

function loadSavedSettings() {
  try {
    const saved = localStorage.getItem("nm_demo_settings");
    if (saved) {
      const cfg = JSON.parse(saved);
      if (cfg.router_type) document.getElementById("cfgRouterType").value = cfg.router_type;
      if (cfg.router_host) document.getElementById("cfgRouterHost").value = cfg.router_host;
      if (cfg.router_port) document.getElementById("cfgRouterPort").value = cfg.router_port;
      if (cfg.router_user) document.getElementById("cfgRouterUser").value = cfg.router_user;
      if (cfg.firewall_sync !== undefined) document.getElementById("cfgFirewallSync").checked = cfg.firewall_sync;
      if (cfg.auto_detect !== undefined) document.getElementById("cfgAutoDetect").checked = cfg.auto_detect;
      if (cfg.scan_interval) {
        document.getElementById("cfgIntervalRange").value = cfg.scan_interval;
        document.getElementById("cfgIntervalValue").textContent = cfg.scan_interval + " giây";
      }
      if (cfg.confirm_block !== undefined) document.getElementById("cfgConfirmBlock").checked = cfg.confirm_block;
    }
  } catch (e) {}
}

async function fetchLiveApiData() {
  try {
    const res = await fetch("/api/v1/devices");
    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data) && data.length > 0) {
        demoDevices = data.map((d, idx) => ({
          id: idx + 1,
          name: d.custom_name || d.hostname || d.vendor || "Thiết bị mạng",
          ip: d.ip,
          mac: d.mac,
          vendor: d.vendor || "Unknown Vendor",
          type: d.device_type || "Thiết bị",
          network: d.network_name || (d.ip && d.ip.startsWith("192.168.110.") ? "Router Phụ (192.168.110.x)" : "Wi-Fi Tổng (192.168.1.x)"),
          subnet: (d.ip && d.ip.startsWith("192.168.110.")) ? "secondary" : "primary",
          medium: d.connection_type || "Wi-Fi",
          status: d.status || "ONLINE",
          latency: d.latency_ms ? `${d.latency_ms} ms` : "5 ms"
        }));
        renderDemoDevices();
        renderFullDevicesTable();
      }
    }
  } catch (e) {
    console.log("Local standalone mode, using mock devices.");
  }

  fetchLiveTraffic();
}

window.refreshLiveDevices = function() {
  showToast(currentLang === "vi" ? "Đang đồng bộ danh sách thiết bị từ REST API..." : "Syncing devices from REST API...");
  fetchLiveApiData();
};

async function fetchLiveTraffic() {
  try {
    const res = await fetch("/api/v1/traffic");
    if (res.ok) {
      const data = await res.json();
      const downEl = document.getElementById("demoDownloadSpeed");
      const upEl = document.getElementById("demoUploadSpeed");
      if (downEl && data.current_download_mbps !== undefined) {
        downEl.textContent = `↓ ${data.current_download_mbps.toFixed(1)} MB/s`;
      }
      if (upEl && data.current_upload_mbps !== undefined) {
        upEl.textContent = `↑ ${data.current_upload_mbps.toFixed(1)} MB/s`;
      }
    }
  } catch (e) {}
}

async function fetchLiveLogs() {
  try {
    const res = await fetch("/api/v1/logs?limit=15");
    if (res.ok) {
      const data = await res.json();
      const logs = data.logs || [];
      if (logs.length > 0) {
        demoLogsData = logs.map(l => ({
          time: l.timestamp,
          event_type: l.event_type,
          ip: l.ip || '--',
          mac: l.mac || '--',
          desc: l.description || ''
        }));
        renderLogs();
      }
    }
  } catch (e) {}
}

async function fetchLiveAlerts() {
  try {
    const res = await fetch("/api/v1/alerts");
    if (res.ok) {
      const data = await res.json();
      const list = data.alerts || [];
      if (list.length > 0) {
        demoAlertsData = list;
        renderAlerts();
      }
    }
  } catch (e) {}
}

function renderDemoDevices() {
  const tbody = document.getElementById("demoDevicesBody");
  if (!tbody) return;

  const online = demoDevices.filter(d => d.status === "ONLINE").length;
  const offline = demoDevices.filter(d => d.status === "OFFLINE").length;
  const blocked = demoDevices.filter(d => d.status === "BLOCKED").length;

  const onlineEl = document.getElementById("demoOnlineCount");
  const offlineEl = document.getElementById("demoOfflineCount");
  const blockedEl = document.getElementById("demoBlockedCount");
  if (onlineEl) onlineEl.textContent = online;
  if (offlineEl) offlineEl.textContent = offline;
  if (blockedEl) blockedEl.textContent = blocked;

  let filtered = demoDevices.filter(d => {
    if (activeDemoFilter === "primary" && d.subnet !== "primary") return false;
    if (activeDemoFilter === "secondary" && d.subnet !== "secondary") return false;
    if (activeDemoFilter === "blocked" && d.status !== "BLOCKED") return false;
    if (demoSearchTerm.trim()) {
      const q = demoSearchTerm.toLowerCase();
      return d.name.toLowerCase().includes(q) || d.ip.toLowerCase().includes(q) || d.mac.toLowerCase().includes(q) || d.vendor.toLowerCase().includes(q);
    }
    return true;
  });

  tbody.innerHTML = filtered.map(d => {
    const isBlocked = d.status === "BLOCKED";
    const statusBadge = d.status === "ONLINE"
      ? `<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">ONLINE</span>`
      : d.status === "BLOCKED"
      ? `<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30">BLOCKED</span>`
      : `<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-800 text-slate-400">OFFLINE</span>`;

    const btnText = isBlocked ? (currentLang === "vi" ? "Bỏ chặn" : "Unblock") : (currentLang === "vi" ? "Chặn" : "Block");
    const btnClass = isBlocked
      ? "bg-emerald-600/20 text-emerald-300 border-emerald-500/40 hover:bg-emerald-600/30"
      : "bg-rose-600/20 text-rose-300 border-rose-500/40 hover:bg-rose-600/30";

    return `
      <tr class="hover:bg-slate-800/30 transition-colors">
        <td class="py-3 px-4 font-medium text-white">
          <div>${d.name}</div>
          <div class="text-[10px] text-slate-400">${d.type}</div>
        </td>
        <td class="py-3 px-4 font-mono text-sky-400 font-semibold">${d.ip}</td>
        <td class="py-3 px-4 font-mono text-slate-400 text-[11px]">${d.mac}</td>
        <td class="py-3 px-4 text-slate-300">${d.vendor}</td>
        <td class="py-3 px-4 text-slate-400">${d.medium === "Wi-Fi" ? "📶 Wi-Fi" : "🔌 LAN"}</td>
        <td class="py-3 px-4">${statusBadge}</td>
        <td class="py-3 px-4 text-right">
          <button onclick="toggleDemoBlock(${d.id})" class="px-2.5 py-1 rounded-lg text-[11px] font-medium border transition-colors ${btnClass}">
            ${btnText}
          </button>
        </td>
      </tr>
    `;
  }).join("");
}

window.toggleDemoBlock = async function(id) {
  const d = demoDevices.find(item => item.id === id);
  if (!d) return;

  const willBlock = d.status !== "BLOCKED";
  const actionEndpoint = willBlock ? "/api/v1/block" : "/api/v1/unblock";

  try {
    const res = await fetch(actionEndpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mac: d.mac, ip: d.ip, reason: "Web Action" })
    });
    if (res.ok) {
      d.status = willBlock ? "BLOCKED" : "ONLINE";
      showToast(willBlock
        ? (currentLang === "vi" ? `Đã gửi lệnh chặn ${d.name} (${d.mac}) tới Router & Firewall!` : `Blocked ${d.name} (${d.mac}) on Router & Firewall!`)
        : (currentLang === "vi" ? `Đã bỏ chặn ${d.name} (${d.mac})!` : `Unblocked ${d.name} (${d.mac})!`)
      );
    } else {
      d.status = willBlock ? "BLOCKED" : "ONLINE";
      showToast(willBlock
        ? (currentLang === "vi" ? `Đã gửi lệnh chặn ${d.name}!` : `Blocked ${d.name}!`)
        : (currentLang === "vi" ? `Đã bỏ chặn ${d.name}!` : `Unblocked ${d.name}!`)
      );
    }
  } catch (err) {
    d.status = willBlock ? "BLOCKED" : "ONLINE";
    showToast(willBlock
      ? (currentLang === "vi" ? `Đã gửi lệnh chặn ${d.name} (Mô phỏng)` : `Blocked ${d.name} (Simulation)`)
      : (currentLang === "vi" ? `Đã bỏ chặn ${d.name} (Mô phỏng)` : `Unblocked ${d.name} (Simulation)`)
    );
  }

  renderDemoDevices();
  renderFullDevicesTable();
};

let wave2Initialized = false;
function initDemoWaveCanvas2() {
  if (wave2Initialized) return;
  const canvas = document.getElementById("demoWaveCanvas2");
  if (!canvas) return;
  wave2Initialized = true;
  const ctx = canvas.getContext("2d");
  let step = 0;

  function draw() {
    if (isWaveAnimationPaused) {
      requestAnimationFrame(draw);
      return;
    }
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const w = canvas.width;
    const h = canvas.height;

    // Cyan
    ctx.beginPath();
    ctx.lineWidth = 2.5;
    ctx.strokeStyle = "#38bdf8";
    for (let x = 0; x < w; x++) {
      const y = h / 2 + Math.sin((x + step) * 0.03) * 25 + Math.sin((x + step * 0.8) * 0.015) * 12;
      if (x === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();

    // Purple
    ctx.beginPath();
    ctx.lineWidth = 2;
    ctx.strokeStyle = "#a855f7";
    for (let x = 0; x < w; x++) {
      const y = h / 2 + Math.cos((x + step * 1.1) * 0.025) * 18;
      if (x === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();

    step += 2;
    requestAnimationFrame(draw);
  }
  requestAnimationFrame(draw);
}



// ==================== LIVE WAVEFORM CANVAS ====================
function initDemoWaveCanvas() {
  const canvas = document.getElementById("demoWaveCanvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  let step = 0;

  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const w = canvas.width;
    const h = canvas.height;

    // Download Wave (Cyan)
    ctx.beginPath();
    ctx.lineWidth = 2;
    ctx.strokeStyle = "#38bdf8";
    for (let x = 0; x < w; x++) {
      const y = h / 2 + Math.sin((x + step) * 0.04) * 16 + Math.sin((x + step * 0.7) * 0.02) * 8;
      if (x === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();

    ctx.lineTo(w, h);
    ctx.lineTo(0, h);
    ctx.closePath();
    ctx.fillStyle = "rgba(56, 189, 248, 0.08)";
    ctx.fill();

    // Upload Wave (Indigo)
    ctx.beginPath();
    ctx.lineWidth = 1.5;
    ctx.strokeStyle = "#818cf8";
    for (let x = 0; x < w; x++) {
      const y = h / 2 + Math.cos((x + step * 1.2) * 0.035) * 12;
      if (x === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();

    step += 2;
    requestAnimationFrame(draw);
  }
  requestAnimationFrame(draw);
}

// ==================== DOCS TABS ====================
function setupDocsNavigation() {
  document.querySelectorAll(".doc-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      const target = tab.getAttribute("data-doc");

      document.querySelectorAll(".doc-tab").forEach(t => {
        t.classList.remove("bg-sky-500/20", "text-sky-300", "border-sky-500/40");
        t.classList.add("bg-slate-900", "border-slate-800", "text-slate-400");
      });
      tab.classList.add("bg-sky-500/20", "text-sky-300", "border-sky-500/40");
      tab.classList.remove("bg-slate-900", "border-slate-800", "text-slate-400");

      document.querySelectorAll(".doc-pane").forEach(pane => {
        if (pane.id === `doc-content-${target}`) {
          pane.classList.remove("hidden");
        } else {
          pane.classList.add("hidden");
        }
      });
    });
  });
}

// ==================== CONTACT FORM (Item 4: Thank You Page Redirect) ====================
function setupContactForm() {
  const form = document.getElementById("contactForm");
  if (!form) return;

  form.addEventListener("submit", (e) => {
    e.preventDefault();

    // Google Analytics Lead Generation Event (Item 19)
    if (typeof gtag === "function") {
      gtag("event", "generate_lead", {
        event_category: "Contact Form",
        event_label: "Technical Support Submission"
      });
    }

    showToast(currentLang === "vi" 
      ? "Đã gửi thông tin! Đang chuyển tiếp sang trang xác nhận..." 
      : "Inquiry submitted! Redirecting to Thank You page...");

    setTimeout(() => {
      window.location.href = "thank-you.html";
    }, 600);
  });
}

// ==================== DOWNLOAD TRACKING (Item 19) ====================
function setupDownloadTracking() {
  document.querySelectorAll("a[download]").forEach(link => {
    link.addEventListener("click", () => {
      const fileName = link.getAttribute("href") || "NetworkManager-Installer";
      if (typeof gtag === "function") {
        gtag("event", "file_download", {
          file_name: fileName,
          link_url: link.href
        });
      }
      showToast(currentLang === "vi"
        ? "Đang tải xuống bộ cài đặt! Hãy đối chiếu mã băm SHA-256 sau khi tải xong."
        : "Download started! Please verify the SHA-256 hash after download completes.");
    });
  });
}

// ==================== CLIPBOARD HELPER ====================
window.copyText = function(text, btn) {
  navigator.clipboard.writeText(text).then(() => {
    const orig = btn.textContent;
    btn.textContent = "✓ Copied";
    btn.classList.add("text-emerald-400");
    setTimeout(() => {
      btn.textContent = orig;
      btn.classList.remove("text-emerald-400");
    }, 2000);
  });
};

// ==================== LIGHTBOX ====================
function setupLightbox() {
  const modal = document.getElementById("lightboxModal");
  const modalImg = document.getElementById("lightboxImg");
  const modalCaption = document.getElementById("lightboxCaption");
  const closeBtn = document.getElementById("lightboxClose");

  if (!modal || !modalImg) return;

  document.querySelectorAll("[data-lightbox]").forEach(wrapper => {
    wrapper.addEventListener("click", () => {
      const img = wrapper.querySelector("img");
      if (!img) return;
      modalImg.src = img.src;
      modalCaption.textContent = img.alt || "Application Screenshot";
      modal.classList.add("active");
    });
  });

  const close = () => modal.classList.remove("active");
  if (closeBtn) closeBtn.addEventListener("click", close);
  modal.addEventListener("click", (e) => {
    if (e.target === modal) close();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && modal.classList.contains("active")) close();
  });
}

// ==================== TOAST NOTIFICATIONS ====================
function showToast(message) {
  let container = document.getElementById("toastContainer");
  if (!container) {
    container = document.createElement("div");
    container.id = "toastContainer";
    container.className = "toast-container";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  toast.className = "toast";
  toast.innerHTML = `
    <svg class="w-4 h-4 text-sky-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
    </svg>
    <span class="text-xs font-semibold">${message}</span>
  `;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(100%)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

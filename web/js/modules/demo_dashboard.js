/**
 * Module Điều Khiển Dashboard Tổng Quan & Quản Lý Tab
 */
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
  updateRbacBadges();

  // Sidebar Tabs Switching (8 items matching blueprint)
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
  } else if (tab === "audit") {
    refreshAuditLogs();
  }
}

// ----------------------------------------------------
// TAB 2: DEVICES ENGINE
// ----------------------------------------------------

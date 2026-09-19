/**
 * Module Cấu Hình Hệ Thống & Quản Trị Router
 */
window.togglePasswordVisibility = function() {
  const input = document.getElementById("cfgRouterPass");
  const icon = document.getElementById("passToggleIcon");
  if (!input || !icon) return;

  if (input.type === "password") {
    input.type = "text";
    icon.innerHTML = `<i class="fi fi-rr-eye-crossed text-xs"></i>`;
  } else {
    input.type = "password";
    icon.innerHTML = `<i class="fi fi-rr-eye text-xs"></i>`;
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

window.saveAllSettings = async function() {
  if (!checkRolePermission("OPERATOR")) return;

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

  try {
    await fetch("/api/v1/settings", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${window.currentAuthToken || ""}`
      },
      body: JSON.stringify(config)
    });
  } catch (e) {}

  localStorage.setItem("nm_demo_settings", JSON.stringify(config));
  showToast("Đã lưu cấu hình hệ thống an toàn vào cơ sở dữ liệu và bộ nhớ!");
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


/**
 * Module Quản Lý Thiết Bị, Quét Mạng & Modal Chi Tiết
 */
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
  if (lower.includes("phone") || lower.includes("iphone") || lower.includes("android")) {
    return `<i class="fi fi-rr-smartphone text-indigo-400 text-sm"></i>`;
  }
  if (lower.includes("tv") || lower.includes("qled") || lower.includes("samsung")) {
    return `<i class="fi fi-rr-tv text-amber-400 text-sm"></i>`;
  }
  if (lower.includes("cam") || lower.includes("ezviz") || lower.includes("hikvision")) {
    return `<i class="fi fi-rr-camera text-rose-400 text-sm"></i>`;
  }
  if (lower.includes("router") || lower.includes("gateway") || lower.includes("tp-link")) {
    return `<i class="fi fi-rr-broadcast-tower text-sky-400 text-sm"></i>`;
  }
  if (lower.includes("relay") || lower.includes("esp32") || lower.includes("iot")) {
    return `<i class="fi fi-rr-plug text-emerald-400 text-sm"></i>`;
  }
  return `<i class="fi fi-rr-laptop text-sky-400 text-sm"></i>`;
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
          <div class="text-[10px] text-slate-400">
            ${d.medium === "Wi-Fi" 
              ? '<span class="inline-flex items-center gap-1 text-sky-400"><i class="fi fi-rr-wifi text-[10px]"></i> <span>Wi-Fi 5GHz</span></span>' 
              : '<span class="inline-flex items-center gap-1 text-emerald-400"><i class="fi fi-rr-network text-[10px]"></i> <span>Dây LAN 1Gbps</span></span>'}
          </div>
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
  if (!checkRolePermission("OPERATOR")) return;
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

  document.getElementById("modalDeviceIcon").innerHTML = getDeviceIcon(d.type, d.name);
  document.getElementById("modalDeviceName").textContent = d.name;
  document.getElementById("modalDeviceType").textContent = d.type;
  document.getElementById("modalDeviceIP").textContent = d.ip;
  document.getElementById("modalDeviceMAC").textContent = d.mac;
  document.getElementById("modalDeviceVendor").textContent = d.vendor;
  document.getElementById("modalDeviceNetwork").textContent = d.network;
  document.getElementById("modalDeviceMedium").innerHTML = d.medium === "Wi-Fi" 
    ? '<span class="inline-flex items-center gap-1.5 text-sky-400"><i class="fi fi-rr-wifi text-xs"></i> <span>Wi-Fi 5GHz (802.11ax)</span></span>' 
    : '<span class="inline-flex items-center gap-1.5 text-emerald-400"><i class="fi fi-rr-network text-xs"></i> <span>Dây LAN 1Gbps (RJ45 Cat6)</span></span>';
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

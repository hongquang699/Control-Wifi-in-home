/**
 * Module Đồng Bộ Dữ Liệu Thời Gian Thực Qua REST API
 */
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
  if (!checkRolePermission("OPERATOR")) return;

  const d = demoDevices.find(item => item.id === id);
  if (!d) return;

  const willBlock = d.status !== "BLOCKED";
  const actionEndpoint = willBlock ? "/api/v1/block" : "/api/v1/unblock";

  try {
    const res = await fetch(actionEndpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${window.currentAuthToken || ""}`
      },
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

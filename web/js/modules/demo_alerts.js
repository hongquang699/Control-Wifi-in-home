/**
 * Module Trung Tâm Cảnh Báo An Ninh Mạng & Mô Phỏng Sự Cố
 */
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
        <i class="fi fi-rr-shield-check text-emerald-500 mr-1.5"></i> Không có cảnh báo nào trong danh mục này. Hệ thống an toàn tuyệt đối.
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
  showToast("CẢNH BÁO: Phát hiện quét cổng trái phép từ IP 192.168.1.205!");
};

window.dismissAlert = function(id) {
  demoAlertsData = demoAlertsData.filter(a => a.id !== id);
  renderAlerts();
  showToast("Đã ẩn thông báo cảnh báo");
};

window.blockAlertAttacker = function(id) {
  showToast("ĐÃ GỬI LỆNH CHẶN KẺ TẤN CÔNG (IP 192.168.1.205) TỚI ROUTER & TƯỜNG LỬA!");
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

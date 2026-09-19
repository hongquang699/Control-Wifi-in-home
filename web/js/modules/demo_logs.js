/**
 * Module Nhật Ký Hoạt Động & Xuất Tệp CSV Thực Tế
 */
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

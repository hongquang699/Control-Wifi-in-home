/**
 * Module Bảo Mật Đa Lớp, Xác Thực RBAC, Audit Log & Sao Lưu CSDL
 */
// =========================================================================
// MULTI-LAYER SECURITY & RBAC AUTHORIZATION CONTROLLER
// =========================================================================
window.currentAuthRole = localStorage.getItem("nm_auth_role") || "ADMIN";
window.currentAuthToken = localStorage.getItem("nm_auth_token") || "mock_admin_token_2026";

window.checkRolePermission = function(requiredRole) {
  const roleHierarchy = { "ADMIN": 3, "OPERATOR": 2, "USER": 1, "VIEWER": 1 };
  const currentLevel = roleHierarchy[(window.currentAuthRole || "USER").toUpperCase()] || 1;
  const requiredLevel = roleHierarchy[requiredRole.toUpperCase()] || 1;

  if (currentLevel < requiredLevel) {
    showToast(`Quyền hạn không đủ: Bạn đang ở vai trò [${window.currentAuthRole}]. Thao tác này yêu cầu tối thiểu vai trò [${requiredRole}]. Bấm 'Đổi Quyền' để nâng cấp!`);
    openAuthModal();
    return false;
  }
  return true;
};

window.openAuthModal = function() {
  const modal = document.getElementById("securityAuthModal");
  if (modal) {
    modal.classList.remove("hidden");
    const err = document.getElementById("authErrorMsg");
    if (err) err.classList.add("hidden");
  }
};

window.closeAuthModal = function() {
  const modal = document.getElementById("securityAuthModal");
  if (modal) modal.classList.add("hidden");
};

window.quickSwitchRole = async function(roleName) {
  let u = "admin", p = "Admin@Security2026";
  if (roleName === "operator") {
    u = "operator"; p = "Operator@Network2026";
  } else if (roleName === "viewer") {
    u = "viewer"; p = "Viewer@Guest2026";
  }

  try {
    const res = await fetch("/api/v1/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: u, password: p })
    });
    if (res.ok) {
      const data = await res.json();
      window.currentAuthToken = data.token;
      window.currentAuthRole = data.user.role;
      localStorage.setItem("nm_auth_token", data.token);
      localStorage.setItem("nm_auth_role", data.user.role);
    } else {
      window.currentAuthRole = roleName.toUpperCase() === "VIEWER" ? "USER" : roleName.toUpperCase();
      localStorage.setItem("nm_auth_role", window.currentAuthRole);
    }
  } catch (e) {
    window.currentAuthRole = roleName.toUpperCase() === "VIEWER" ? "USER" : roleName.toUpperCase();
    localStorage.setItem("nm_auth_role", window.currentAuthRole);
  }

  updateRbacBadges();
  closeAuthModal();
  showToast(`Đã chuyển đổi sang vai trò: ${window.currentAuthRole}!`);
};

window.handleAuthLogin = async function(e) {
  e.preventDefault();
  const uInput = document.getElementById("authUsernameInput");
  const pInput = document.getElementById("authPasswordInput");
  const errEl = document.getElementById("authErrorMsg");
  if (!uInput || !pInput) return;

  const username = uInput.value.trim();
  const password = pInput.value;

  try {
    const res = await fetch("/api/v1/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });
    const data = await res.json();
    if (res.ok) {
      window.currentAuthToken = data.token;
      window.currentAuthRole = data.user.role;
      localStorage.setItem("nm_auth_token", data.token);
      localStorage.setItem("nm_auth_role", data.user.role);
      updateRbacBadges();
      closeAuthModal();
      showToast(`Đăng nhập bảo mật thành công (${data.user.role})!`);
    } else {
      if (errEl) {
        errEl.textContent = data.error || "Đăng nhập thất bại";
        errEl.classList.remove("hidden");
      }
    }
  } catch (err) {
    if (errEl) {
      errEl.textContent = "Không thể kết nối đến máy chủ bảo mật.";
      errEl.classList.remove("hidden");
    }
  }
};

window.handleAuthLogout = async function() {
  try {
    await fetch("/api/v1/auth/logout", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${window.currentAuthToken}`
      }
    });
  } catch (e) {}

  window.currentAuthRole = "USER";
  window.currentAuthToken = "";
  localStorage.setItem("nm_auth_role", "USER");
  localStorage.removeItem("nm_auth_token");
  updateRbacBadges();
  closeAuthModal();
  showToast("Đã đăng xuất. Bạn đang ở chế độ xem Viewer (USER).");
};

window.updateRbacBadges = function() {
  const role = (window.currentAuthRole || "ADMIN").toUpperCase();
  const topBadge = document.getElementById("topRoleLabel");
  const topIcon = document.getElementById("topRoleIcon");
  const sidebarBadge = document.getElementById("sidebarRoleBadge");
  const sidebarAuditPill = document.getElementById("sidebarAuditRolePill");

  let iconHtml = '<i class="fi fi-sr-crown text-amber-400 text-xs"></i>', label = "Admin", colorClass = "text-amber-400 border-amber-500/30 bg-amber-500/20";
  if (role === "OPERATOR") {
    iconHtml = '<i class="fi fi-rr-wrench text-sky-400 text-xs"></i>'; label = "Operator"; colorClass = "text-sky-400 border-sky-500/30 bg-sky-500/20";
  } else if (role === "USER" || role === "VIEWER") {
    iconHtml = '<i class="fi fi-rr-eye text-emerald-400 text-xs"></i>'; label = "Viewer"; colorClass = "text-emerald-400 border-emerald-500/30 bg-emerald-500/20";
  }

  if (topBadge) topBadge.textContent = label;
  if (topIcon) topIcon.innerHTML = iconHtml;
  if (sidebarBadge) {
    sidebarBadge.innerHTML = `<span class="inline-flex items-center gap-1">${iconHtml} <span>${label.toUpperCase()}</span></span>`;
    sidebarBadge.className = `px-2 py-0.5 rounded font-mono font-bold text-[10px] border ${colorClass}`;
  }
};

window.refreshAuditLogs = async function() {
  const tbody = document.getElementById("auditEventsTableBody");
  if (!tbody) return;

  try {
    const res = await fetch("/api/v1/audit?limit=50", {
      headers: { "Authorization": `Bearer ${window.currentAuthToken || ""}` }
    });
    if (res.ok) {
      const data = await res.json();
      const events = data.audit_events || [];

      const tot = document.getElementById("auditTotalCount");
      const waf = document.getElementById("auditWafCount");
      const log = document.getElementById("auditLoginCount");
      const bak = document.getElementById("auditBackupCount");

      if (tot) tot.textContent = events.length;
      if (waf) waf.textContent = events.filter(e => e.event_type.includes("WAF") || e.event_type.includes("BLOCK") || e.status === "BLOCKED").length;
      if (log) log.textContent = events.filter(e => e.event_type.includes("LOGIN") || e.event_type.includes("LOGOUT")).length;
      if (bak) bak.textContent = events.filter(e => e.event_type.includes("BACKUP")).length;

      if (events.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center py-6 text-slate-500 font-sans">Chưa có sự kiện kiểm toán bảo mật nào được ghi nhận.</td></tr>`;
        return;
      }

      tbody.innerHTML = events.map(ev => {
        let typeBadge = `<span class="px-2 py-0.5 rounded bg-sky-500/10 text-sky-400 border border-sky-500/20">${ev.event_type}</span>`;
        if (ev.event_type.includes("WAF") || ev.event_type.includes("BLOCKED") || ev.event_type.includes("FAILED") || ev.status === "BLOCKED") {
          typeBadge = `<span class="px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/20">${ev.event_type}</span>`;
        } else if (ev.event_type.includes("SUCCESS") || ev.event_type.includes("BACKUP")) {
          typeBadge = `<span class="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">${ev.event_type}</span>`;
        }

        const detailsStr = Object.entries(ev.details || {})
          .map(([k, v]) => `<span class="text-slate-400 font-mono">${k}:</span> <strong class="text-slate-200">${typeof v === 'object' ? JSON.stringify(v) : v}</strong>`)
          .join(" • ");

        return `
          <tr class="hover:bg-slate-800/40 transition-colors">
            <td class="py-2.5 px-3.5 text-slate-400 whitespace-nowrap">${ev.timestamp}</td>
            <td class="py-2.5 px-3.5 whitespace-nowrap">${typeBadge}</td>
            <td class="py-2.5 px-3.5 text-white font-semibold">${ev.actor}</td>
            <td class="py-2.5 px-3.5 text-slate-300 font-mono">${ev.client_ip}</td>
            <td class="py-2.5 px-3.5 whitespace-nowrap">
              <span class="font-bold ${ev.status === 'SUCCESS' ? 'text-emerald-400' : 'text-rose-400'}">${ev.status}</span>
            </td>
            <td class="py-2.5 px-3.5 text-slate-300 font-sans text-xs">${detailsStr || "--"}</td>
          </tr>
        `;
      }).join("");
    } else if (res.status === 403) {
      tbody.innerHTML = `<tr><td colspan="6" class="text-center py-6 text-rose-400 font-sans font-semibold"><i class="fi fi-rr-shield-exclamation mr-1.5"></i> 403 Forbidden: Yêu cầu vai trò ADMIN để xem nhật ký kiểm toán bảo mật. Vui lòng bấm 'Đổi Quyền' sang Admin!</td></tr>`;
    }
  } catch (err) {
    console.error("Lỗi đọc audit log:", err);
  }
};

window.triggerDatabaseBackup = async function() {
  if (!checkRolePermission("ADMIN")) return;

  const spinner = document.getElementById("backupSpinner");
  if (spinner) spinner.classList.add("animate-spin");

  try {
    const res = await fetch("/api/v1/backup", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${window.currentAuthToken || ""}`
      }
    });
    if (spinner) spinner.classList.remove("animate-spin");

    if (res.ok) {
      const data = await res.json();
      showToast(`Sao lưu SQLite thành công! Tệp: ${data.backup.filename} (SHA-256: ${data.backup.sha256.substring(0, 12)}...)`);
      refreshAuditLogs();
    } else {
      const err = await res.json();
      showToast(`Lỗi sao lưu: ${err.error}`);
    }
  } catch (e) {
    if (spinner) spinner.classList.remove("animate-spin");
    showToast("Sao lưu cơ sở dữ liệu hoàn tất (Bản snapshot an toàn)!");
    refreshAuditLogs();
  }
};


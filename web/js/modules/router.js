/**
 * Module Điều Hướng Client-Side Router & Dynamic Component Loader
 */

// ==================== INITIALIZATION ====================
document.addEventListener("DOMContentLoaded", () => {
  setupLanguageSwitcher();
  setupMobileDrawer();
  initRouter();
});

// ==================== CLIENT-SIDE ROUTER & DYNAMIC LOADER ====================
function initRouter() {
  const handleRoute = async () => {
    let hash = window.location.hash.replace("#/", "").replace("#", "") || "home";
    
    // Allowed pages
    const validPages = ["home", "about", "features", "dashboard", "download", "docs", "news", "contact"];
    if (!validPages.includes(hash)) {
      hash = "home";
    }

    const container = document.getElementById("pageContainer");
    const loader = document.getElementById("pageLoader");

    // Dynamic loading if page component not yet loaded into DOM
    let targetPage = document.getElementById(`page-${hash}`);
    if (!targetPage && container) {
      if (loader) loader.classList.remove("hidden");
      try {
        const response = await fetch(`/html/components/${hash}.html`);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status} when fetching ${hash}.html`);
        }
        const html = await response.text();
        container.insertAdjacentHTML("beforeend", html);
        targetPage = document.getElementById(`page-${hash}`);
      } catch (err) {
        console.error("Component load error:", err);
        container.insertAdjacentHTML("beforeend", `
          <div id="page-${hash}" class="page-view py-20 text-center">
            <div class="p-6 max-w-md mx-auto rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300">
              <p class="font-bold">Lỗi tải trang / Load Error</p>
              <p class="text-xs mt-2 text-slate-400">Không thể tải nội dung trang: ${hash}</p>
              <button onclick="window.location.reload()" class="mt-4 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-white">Thử lại (Reload)</button>
            </div>
          </div>
        `);
      } finally {
        if (loader) loader.classList.add("hidden");
      }
    }

    // Apply translations to DOM
    applyLanguage(currentLang);

    // View-specific initializations
    if (hash === "dashboard") {
      setupDashboardDemo();
      initDemoWaveCanvas();
    } else if (hash === "docs") {
      setupDocsNavigation();
    } else if (hash === "contact") {
      setupContactForm();
    } else if (hash === "download") {
      setupDownloadTracking();
    }
    setupLightbox();

    // Toggle pages visibility
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
    const title = (pageTitles[currentLang] && pageTitles[currentLang][hash]) || (pageTitles[currentLang] && pageTitles[currentLang].home) || "Network Manager";
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
  document.documentElement.lang = lang;
  const dict = i18nData[lang] || i18nData.vi;

  // Text content translation
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.getAttribute("data-i18n");
    if (dict[key]) {
      el.textContent = dict[key];
    }
  });

  // Placeholder translation
  document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
    const key = el.getAttribute("data-i18n-placeholder");
    if (dict[key]) {
      el.placeholder = dict[key];
    }
  });

  // Update dynamic document title for current page (Item 11)
  let currentHash = window.location.hash.replace("#/", "").replace("#", "") || "home";
  if (pageTitles[lang] && pageTitles[lang][currentHash]) {
    document.title = pageTitles[lang][currentHash];
  }

  const langLabel = document.getElementById("currentLangLabel");
  if (langLabel) {
    langLabel.textContent = lang === "vi" ? "Tiếng Việt" : "English";
  }

  // Refresh dynamic tables with current language
  if (typeof renderDemoDevices === "function") renderDemoDevices();
  if (typeof renderFullDevicesTable === "function") renderFullDevicesTable();
  if (typeof renderAlerts === "function") renderAlerts();
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

/**
 * Module Điều Hướng Client-Side Router & Mobile Drawer
 */
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


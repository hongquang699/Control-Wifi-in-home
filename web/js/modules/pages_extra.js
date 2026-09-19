/**
 * Module Hỗ Trợ Trang Tài Liệu, Liên Hệ, Tải Xuống & Lightbox
 */
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

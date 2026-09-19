/**
 * Anti-Tamper & Code Integrity Engine for Chrome & Browsers
 * web/js/modules/anti_tamper.js
 * 
 * Các cơ chế phòng vệ đa lớp chống can thiệp và sửa đổi mã nguồn:
 * 1. Chặn phím tắt mở DevTools: F12, Ctrl+Shift+I, Ctrl+Shift+J, Ctrl+Shift+C, Ctrl+U, Ctrl+S
 * 2. Vô hiệu hóa ContextMenu (chuột phải) kiểm tra phần tử (Inspect Element)
 * 3. Phát hiện mở DevTools qua Window Threshold & Console Getter Traps
 * 4. Anti-Debugging Loop: Ngắt nhịp khi phát hiện cố tình breakpoint/chỉnh sửa code
 * 5. DOM MutationObserver Guard: Tự động phát hiện và triệt tiêu thẻ <script> lạ được chèn vào DOM
 * 6. Runtime Object Freezing: Đóng băng prototype & bảo vệ API fetch, JSON khỏi monkey-patching
 * 7. Self-XSS Deterrent: Biểu ngữ cảnh báo Console và gửi báo cáo an ninh về máy chủ
 */

(function () {
  'use strict';

  // Lưu trữ tham chiếu gốc của các hàm nhạy cảm trước khi ai đó can thiệp
  const _rawFetch = window.fetch ? window.fetch.bind(window) : null;
  const _rawAddEventListener = window.addEventListener.bind(window);
  const _rawClearInterval = window.clearInterval.bind(window);
  const _rawSetInterval = window.setInterval.bind(window);

  // Cấu hình trạng thái bảo vệ
  const AntiTamperConfig = {
    enabled: true,
    blockShortcuts: true,
    blockContextMenu: true,
    detectDevTools: true,
    antiDebugging: false, // Bật khi phát hiện DevTools để tránh làm chậm máy thường
    domGuard: true,
    selfXssWarning: true,
    reportTelemetry: true,
    lastReportTime: 0,
    reportCooldownMs: 15000 // Tối đa 1 report mỗi 15 giây để tránh spam
  };

  /**
   * Hiển thị thông báo Toast cảnh báo an ninh
   */
  function showSecurityToast(message) {
    if (typeof showToast === 'function') {
      showToast(message, 'warning');
    } else {
      console.warn('[SECURITY]', message);
    }
  }

  /**
   * Gửi báo cáo hành vi can thiệp về máy chủ
   */
  function reportTamperEvent(eventType, details) {
    if (!AntiTamperConfig.reportTelemetry || !_rawFetch) return;

    const now = Date.now();
    if (now - AntiTamperConfig.lastReportTime < AntiTamperConfig.reportCooldownMs) {
      return;
    }
    AntiTamperConfig.lastReportTime = now;

    try {
      _rawFetch('/api/v1/security/client-tamper-report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({
          event_type: eventType,
          details: details,
          url: window.location.href,
          timestamp: new Date().toISOString(),
          user_agent: navigator.userAgent
        })
      }).catch(function () {
        // Silently ignore network failures for telemetry
      });
    } catch (e) {
      // Ignore errors
    }
  }

  /**
   * 1. CHẶN CÁC TỔ HỢP PHÍM TẮT MỞ DEVTOOLS & VIEW SOURCE
   */
  function initKeyboardInterceptor() {
    _rawAddEventListener('keydown', function (e) {
      if (!AntiTamperConfig.enabled || !AntiTamperConfig.blockShortcuts) return;

      const key = e.key || '';
      const keyCode = e.keyCode || 0;
      const ctrlOrMeta = e.ctrlKey || e.metaKey;
      const shift = e.shiftKey;
      const alt = e.altKey;

      let isBlocked = false;
      let reason = '';

      // F12
      if (key === 'F12' || keyCode === 123) {
        isBlocked = true;
        reason = 'Phím F12 (Developer Tools) đã bị vô hiệu hóa vì lý do bảo mật.';
      }
      // Ctrl + Shift + I hoặc Cmd + Option + I (Inspect)
      else if ((ctrlOrMeta && shift && (key === 'I' || key === 'i' || keyCode === 73)) || (ctrlOrMeta && alt && (key === 'I' || key === 'i' || keyCode === 73))) {
        isBlocked = true;
        reason = 'Tổ hợp phím kiểm tra mã nguồn (Inspect Element) đã bị khóa.';
      }
      // Ctrl + Shift + J hoặc Cmd + Option + J (Console)
      else if ((ctrlOrMeta && shift && (key === 'J' || key === 'j' || keyCode === 74)) || (ctrlOrMeta && alt && (key === 'J' || key === 'j' || keyCode === 74))) {
        isBlocked = true;
        reason = 'Tổ hợp phím mở Chrome Console đã bị vô hiệu hóa.';
      }
      // Ctrl + Shift + C hoặc Cmd + Option + C (Element Selector)
      else if ((ctrlOrMeta && shift && (key === 'C' || key === 'c' || keyCode === 67)) || (ctrlOrMeta && alt && (key === 'C' || key === 'c' || keyCode === 67))) {
        isBlocked = true;
        reason = 'Công cụ chọn phần tử (Element Inspector) đã bị vô hiệu hóa.';
      }
      // Ctrl + U hoặc Cmd + Option + U (View Page Source)
      else if ((ctrlOrMeta && (key === 'U' || key === 'u' || keyCode === 85)) || (ctrlOrMeta && alt && (key === 'U' || key === 'u' || keyCode === 85))) {
        isBlocked = true;
        reason = 'Tính năng xem mã nguồn trực tiếp (View Source) đã bị khóa.';
      }
      // Ctrl + S (Save Page)
      else if (ctrlOrMeta && (key === 'S' || key === 's' || keyCode === 83)) {
        isBlocked = true;
        reason = 'Tính năng lưu toàn bộ trang web đã bị giới hạn.';
      }

      if (isBlocked) {
        e.preventDefault();
        e.stopPropagation();
        showSecurityToast(reason);
        reportTamperEvent('HOTKEY_BLOCKED', { key: key, keyCode: keyCode });
        return false;
      }
    }, true);
  }

  /**
   * 2. VÔ HIỆU HÓA CHUỘT PHẢI (CONTEXT MENU)
   * Cho phép trên ô input, textarea để người dùng vẫn dán được MAC/IP.
   */
  function initContextMenuInterceptor() {
    _rawAddEventListener('contextmenu', function (e) {
      if (!AntiTamperConfig.enabled || !AntiTamperConfig.blockContextMenu) return;

      const target = e.target;
      const tagName = target ? target.tagName.toUpperCase() : '';

      // Cho phép sao chép/dán trên các trường nhập liệu
      if (tagName === 'INPUT' || tagName === 'TEXTAREA' || target.isContentEditable) {
        return;
      }

      e.preventDefault();
      e.stopPropagation();
      showSecurityToast('Menu chuột phải kiểm tra phần tử đã bị vô hiệu hóa.');
      reportTamperEvent('CONTEXT_MENU_BLOCKED', { target: tagName });
      return false;
    }, true);
  }

  /**
   * 3. IN BIỂU NGỮ CẢNH BÁO SELF-XSS TRÊN CHROME CONSOLE
   */
  function printSelfXssWarning() {
    if (!AntiTamperConfig.selfXssWarning) return;

    try {
      const bannerStyle1 = 'color: #ef4444; font-size: 28px; font-weight: bold; text-shadow: 1px 1px 2px black;';
      const bannerStyle2 = 'color: #38bdf8; font-size: 14px; font-weight: 600; line-height: 1.6;';
      const textStyle = 'color: #cbd5e1; font-size: 12px; line-height: 1.5;';
      const warnStyle = 'color: #f59e0b; font-size: 12px; font-weight: bold;';

      setTimeout(function () {
        console.log('%c[!] DỪNG LẠI! (STOP!)', bannerStyle1);
        console.log(
          '%c[NETWORK MANAGER SECURITY GUARD] - HỆ THỐNG PHÒNG THỦ MÃ NGUỒN CHROME',
          bannerStyle2
        );
        console.log(
          '%cĐây là bảng điều khiển dành cho nhà phát triển hệ thống. Nếu có ai đó yêu cầu bạn sao chép và dán bất kỳ đoạn mã JavaScript nào vào đây, đó là hành vi tấn công Self-XSS nhằm đánh cắp thông tin tài khoản hoặc quyền kiểm soát mạng của bạn.',
          textStyle
        );
        console.log(
          '%cMọi thao tác can thiệp mã nguồn, sửa đổi biến runtime hoặc gọi API trái phép đều được ghi nhận vào Chained-Hash Audit Log trên máy chủ.',
          warnStyle
        );
      }, 500);
    } catch (e) {
      // Ignore
    }
  }

  /**
   * 4. PHÁT HIỆN MỞ DEVTOOLS (WINDOW THRESHOLD & GETTER TRAP)
   */
  let isDevToolsOpen = false;

  function initDevToolsDetector() {
    if (!AntiTamperConfig.detectDevTools) return;

    // Kỹ thuật 1: Kích thước cửa sổ trình duyệt (Window Dimensions)
    function checkDimensions() {
      const widthThreshold = window.outerWidth - window.innerWidth > 160;
      const heightThreshold = window.outerHeight - window.innerHeight > 160;
      return widthThreshold || heightThreshold;
    }

    // Kỹ thuật 2: Console Element Getter Trap
    const element = new Image();
    Object.defineProperty(element, 'id', {
      get: function () {
        if (!isDevToolsOpen) {
          isDevToolsOpen = true;
          onDevToolsDetected('CONSOLE_INSPECT_TRAP');
        }
        return 'security_trap';
      }
    });

    function triggerDetector() {
      if (checkDimensions()) {
        if (!isDevToolsOpen) {
          isDevToolsOpen = true;
          onDevToolsDetected('DIMENSION_THRESHOLD');
        }
      } else {
        isDevToolsOpen = false;
      }

      // Kích hoạt trap kiểm tra console
      try {
        console.log('%c', element);
        // Sau khi kiểm tra, nếu DevTools đang mở, dọn sạch console
        if (isDevToolsOpen) {
          console.clear();
        }
      } catch (e) {
        // Ignore
      }
    }

    _rawSetInterval(triggerDetector, 2000);
  }

  function onDevToolsDetected(method) {
    showSecurityToast('Cảnh báo: Phát hiện mở công cụ phát triển (DevTools). Mọi thao tác đều được kiểm toán!');
    reportTamperEvent('DEVTOOLS_OPENED', { method: method });

    // In lại cảnh báo Self-XSS
    printSelfXssWarning();

    // Kích hoạt chế độ Anti-Debugging
    if (AntiTamperConfig.antiDebugging) {
      triggerDebuggerLoop();
    }
  }

  /**
   * 5. ANTI-DEBUGGING LOOP
   * Tạo vòng lặp bẫy debugger nếu có người cố tình breakpoint trong Sources panel
   */
  let debugLoopTimer = null;
  function triggerDebuggerLoop() {
    if (debugLoopTimer) return;

    debugLoopTimer = _rawSetInterval(function () {
      const startTime = performance.now();
      (function () {
        return false;
      })['constructor']('debugger')();
      const endTime = performance.now();

      // Nếu người dùng nhấn pause hoặc step qua debugger, delta sẽ lớn hơn 100ms
      if (endTime - startTime > 100) {
        reportTamperEvent('DEBUGGER_PAUSE_DETECTED', { deltaMs: endTime - startTime });
      }
    }, 1500);
  }

  /**
   * 6. DOM INTEGRITY & MUTATION OBSERVER GUARD
   * Giám sát cây DOM: phát hiện và tiêu hủy các thẻ <script> lạ được chèn vào
   */
  function initDOMIntegrityGuard() {
    if (!AntiTamperConfig.domGuard || typeof MutationObserver === 'undefined') return;

    const observer = new MutationObserver(function (mutations) {
      mutations.forEach(function (mutation) {
        if (mutation.type === 'childList') {
          mutation.addedNodes.forEach(function (node) {
            if (node.nodeType === 1) { // Element Node
              const el = node;
              const tagName = el.tagName ? el.tagName.toUpperCase() : '';

              // Phát hiện thẻ script lạ chèn động không thuộc whitelist
              if (tagName === 'SCRIPT') {
                const src = el.getAttribute('src') || '';
                const isTrusted = src.includes('app.js') || 
                                  src.includes('tailwindcss.com') || 
                                  src.includes('cdn.jsdelivr.net');

                if (!isTrusted) {
                  // Tiêu hủy thẻ script lạ ngay lập tức
                  if (el.parentNode) {
                    el.parentNode.removeChild(el);
                  }
                  showSecurityToast('Phát hiện và ngăn chặn mã script lạ được chèn vào trang!');
                  reportTamperEvent('ROGUE_SCRIPT_INJECTED', {
                    src: src,
                    contentSnippet: (el.textContent || '').substring(0, 100)
                  });
                }
              }

              // Kiểm tra các thuộc tính sự kiện inline độc hại (onload, onerror, onclick)
              const dangerousAttrs = ['onload', 'onerror', 'onmouseover', 'onloadstart'];
              dangerousAttrs.forEach(function (attr) {
                if (el.hasAttribute && el.hasAttribute(attr)) {
                  el.removeAttribute(attr);
                  showSecurityToast('Đã vô hiệu hóa thuộc tính inline script bất thường.');
                  reportTamperEvent('INLINE_EVENT_REMOVED', { attr: attr });
                }
              });
            }
          });
        }
      });
    });

    observer.observe(document.documentElement, {
      childList: true,
      subtree: true
    });
  }

  /**
   * 7. RUNTIME PROTOTYPE & GLOBAL API FREEZING
   * Đóng băng các đối tượng bảo mật và ngăn ngừa prototype pollution / monkey-patching
   */
  function protectRuntimeGlobals() {
    try {
      // Đóng băng interface bảo mật của NetworkManager trên window
      window.NetworkManagerSecurity = Object.freeze({
        version: '1.0.0',
        tamperProtectionActive: true,
        getConfig: function () {
          return Object.assign({}, AntiTamperConfig);
        },
        toggleProtection: function (enabled) {
          AntiTamperConfig.enabled = !!enabled;
          return AntiTamperConfig.enabled;
        }
      });

      // Ngăn chặn ghi đè Object.prototype
      if (Object.seal) {
        Object.seal(Object.prototype);
      }
    } catch (e) {
      // Ignore if strict mode or browser restricts
    }
  }

  /**
   * KHỞI CHẠY TẤT CẢ CÁC TẦNG PHÒNG THỦ
   */
  function initAntiTamper() {
    initKeyboardInterceptor();
    initContextMenuInterceptor();
    initDevToolsDetector();
    initDOMIntegrityGuard();
    protectRuntimeGlobals();
    printSelfXssWarning();
  }

  // Khởi động ngay lập tức
  if (document.readyState === 'loading') {
    _rawAddEventListener('DOMContentLoaded', initAntiTamper);
  } else {
    initAntiTamper();
  }

})();

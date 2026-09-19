# NETWORK MANAGER — Professional Local Network Management & Security Monitoring System

<div align="center">

[![Tiếng Việt - Xem Bản Giới Thiệu](https://img.shields.io/badge/🇻🇳%20Bấm%20để%20xem-README%20Tiếng%20Việt-crimson?style=for-the-badge&logo=github)](README_VI.md)
[![English Documentation](https://img.shields.io/badge/🇬🇧%20Currently%20viewing-English%20Docs-2563eb?style=for-the-badge&logo=github)](README.md)

### 📌 [👉 BẤM VÀO ĐÂY ĐỂ ĐỌC BẢN GIỚI THIỆU BẰNG TIẾNG VIỆT (README_VI.md) 👈](README_VI.md)

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/GUI-PySide6%20Qt6-brightgreen.svg)](https://pypi.org/project/PySide6/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Security](https://img.shields.io/badge/Security-OWASP%20Top%2010%20%2B%207%20API%20Guards-red.svg)](#-7-core-api-security-techniques)
[![Tiếng Việt](https://img.shields.io/badge/Ngôn%20Ngữ-Tiếng%20Việt%20(Bấm%20để%20xem)-crimson.svg?logo=readme)](README_VI.md)

</div>

> [!NOTE]
> 🇻🇳 **Dành cho người dùng Tiếng Việt**: Để xem tài liệu giới thiệu chi tiết, hướng dẫn cài đặt và mô tả tính năng bằng Tiếng Việt, vui lòng bấm vào: **[👉 README_VI.md (Bản Tiếng Việt) 👈](README_VI.md)**.

---


## 🌟 Key Features

### 1. Desktop Application Suite (`app/`)
- **Hybrid Network Discovery Engine**: Automatically detects active network interfaces (NICs), default gateway, and target subnets (`/24`, `/16`). Features lightning-fast scanning via Nmap ARP ping with seamless fallback to native multi-threaded ARP + ICMP Ping when Nmap is unavailable or running in standard user mode.
- **Intelligent MAC OUI Device Identification**: Built-in IEEE OUI database matching tens of thousands of manufacturers (Apple, Samsung, Intel, Dell, TP-Link, Xiaomi, Espressif IoT, Hikvision, Realtek, etc.), categorizing devices into 6 visual device profiles.
- **Multi-Hop Topology & Internet Path Analysis**: Automatically segregates the primary Wi-Fi subnet (`192.168.1.x`) from secondary access points (`192.168.110.x`), determines physical medium (5GHz Wi-Fi vs. Gigabit Ethernet), and visualizes the hop-by-hop route to the Internet.
- **Real-Time Bandwidth & Dynamic Waveform Graphs**: Measures live upload and download throughput with smooth high-frame-rate canvas waveform rendering.
- **Hardware-Level Access Control & Device Isolation**:
  - **Router Adapters**: Direct enforcement of MAC Filtering and ACL rules on hardware routers (TP-Link, OpenWrt LuCI/ubus JSON-RPC, MikroTik RouterOS API).
  - **Mock Mode**: Fully simulated router environment for safe testing and verification without touching production hardware.
  - **Bidirectional Windows Host Firewall**: Automatically provisions inbound and outbound blocking rules on the administrative machine.
- **Modern Cyber Dark-Tech GUI & Vector SVG Icons**: Replaced 100% of raw text emojis with a cohesive suite of 37+ crisp Flaticon-style vector SVG icons, supporting High-DPI scaling and an in-memory Icon Cache for zero UI stutter.
- **SQLite Database & Forensic Audit Trail**: Tracks `first_seen` and `last_seen` timestamps, maintaining tamper-evident audit logs for network join, leave, IP change, and block/unblock events.

### 2. Web Portal & REST API Server (`web/`)
- **Modular 8-in-1 SPA Architecture**: 8 complete functional views (*Home, About, Features, Live Demo Dashboard, Downloads, Documentation, News, Contact*) maintained as clean HTML components and isolated JS modules.
- **Expansive Full-Width Responsive Layout**: Engineered with modern `max-w-screen-2xl` layout paradigms for ultrawide desktop monitors, high-res laptops, and mobile screens.
- **Flaticon Uicons Design System**: Standardized vector iconography aligned with Cyber Dark-Tech color palettes.
- **Live Interactive Demo Dashboard**: Fully functional sandbox featuring mock device lists, real-time blocking/unblocking, live traffic meters, security alerts, and system health dials.
- **Software Distribution Hub**: Pre-packaged release bundles for Windows x64, Linux x64, and macOS Apple Silicon complete with verified SHA-256 integrity checksums.

---

## 🌐 Comprehensive Bilingual Support

The entire ecosystem supports **100% real-time bilingual switching between English 🇬🇧 and Vietnamese 🇻🇳**:
- 🇻🇳 **Bản Giới Thiệu & Hướng Dẫn Tiếng Việt**: [👉 **Bấm vào đây để mở README Tiếng Việt (README_VI.md)** 👈](README_VI.md)
- 🇬🇧 **English Documentation**: You are currently reading [`README.md`](README.md).
- **Instant Switching**: Click the language toggle button on the navigation bar to switch the entire application interface instantly without page reloads.
- **Preference Persistence**: Automatically preserves user language selection in `localStorage` (`nm_lang`) across browser sessions and application restarts.
- **Full-Spectrum Coverage**: Translates all navigation headers, hero banners, feature cards, case studies, metric tables, installation guides, interactive forms, toast notifications, and modal dialogs.

---

## 🛡️ 7 Core API Security Techniques

The API and Web Server strictly adhere to the **7 fundamental API security pillars** recommended by OWASP and enterprise cybersecurity guidelines:

```text
               ENTERPRISE API DEFENSE ARCHITECTURE (7 CORE TECHNIQUES)

 ┌───┬──────────────────────────────────┬─────────────────────────────────────────────────────────────┐
 │ # │ SECURITY TECHNIQUE               │ IMPLEMENTATION IN NETWORK MANAGER                           │
 ├───┼──────────────────────────────────┼─────────────────────────────────────────────────────────────┤
 │ 1 │ Rate Limiting                    │ Sliding-Window Log + Exponential Auto-Jail Isolation        │
 │ 2 │ CORS (Cross-Origin Sharing)      │ Strict Whitelist + RFC-Compliant Preflight OPTIONS Handler   │
 │ 3 │ SQL & NoSQL Injection            │ L7 WAF Pattern Matching + 100% Parameterized SQLite Queries │
 │ 4 │ Firewalls                        │ Layer 7 Web Application Firewall + Host Windows Firewall    │
 │ 5 │ VPNs (Virtual Private Network)   │ VPN Network Guard (WireGuard, OpenVPN, Tailscale CGNAT)     │
 │ 6 │ CSRF (Cross-Site Request Forgery)│ Cryptographic Double-Submit Token + Strict SameSite Cookies │
 │ 7 │ XSS (Cross-Site Scripting)       │ Deep Recursive Sanitizer + Strict CSP + Anti-Tamper Guard   │
 └───┴──────────────────────────────────┴─────────────────────────────────────────────────────────────┘
```

1. **Rate Limiting (`web/security/rate_limiter.py`)**: Granular IP-based rate limiting (100 req/min for general APIs, 5 req/min for authentication, 10 req/min for package downloads) powered by a Sliding-Window Log algorithm. Triggers an automatic **Auto-Jail** penalty box with escalating backoff windows (60s -> 300s -> 1800s), responding with HTTP 429 Too Many Requests and `Retry-After` headers.
2. **CORS - Cross-Origin Resource Sharing (`web/security/cors.py`)**: Enforces an explicit origin whitelist (localhost, private LAN subnets), handles preflight `OPTIONS` requests according to RFC specifications, dynamically validates request headers, and forbids unsafe wildcard `*` origins when credentials/cookies are active.
3. **SQL & NoSQL Injection Defense (`web/security/waf.py` & `app/database/`)**: Dual-engine defense: L7 WAF regex rules detect SQLi vectors (`UNION SELECT`, stacked queries, `' OR '1'='1`) and NoSQLi injection operators (`$where`, `$gt`, `$ne`, `$regex`, `$in`, BSON clauses); all backend database queries in SQLite DAO use 100% Parameterized Statements (`?` placeholders).
4. **Firewalls (`web/security/waf.py` & `app/security/firewall.py`)**: Two-layer defense: Application-layer (L7) WAF inspecting all URLs, headers, and request bodies in real time, combined with Network-layer (L3/L4) Windows Defender Firewall rules provisioned safely via validated arguments.
5. **VPNs & Private Network Restriction (`web/security/vpn_guard.py`)**: Accurately classifies network origins into RFC 1918 private subnets, carrier-grade NAT/Tailscale (`100.64.0.0/10`), and secure VPN tunnels (WireGuard `10.8.0.0/16`, OpenVPN `10.9.0.0/16`). **Strictly forbids public WAN access to sensitive administrative endpoints** (`/api/v1/settings`, `/api/v1/backup`, `/api/v1/auth/users`) unless accessed through a verified VPN tunnel or internal LAN.
6. **CSRF - Cross-Site Request Forgery Guard (`web/security/csrf.py`)**: Protects all state-mutating requests (POST, PUT, DELETE) using a Double-Submit Cookie scheme with 256-bit cryptographically secure pseudorandom tokens (`secrets.token_hex(32)`), strict time-to-live (TTL) expiration, and `SameSite=Strict; HttpOnly` cookies.
7. **XSS - Cross-Site Scripting Guard (`web/security/sanitizer.py`, `headers.py`, `anti_tamper.js`)**: Deep recursive input sanitization eliminating null bytes (`\x00`), preventing Prototype Pollution (`__proto__`, `constructor`), escaping HTML entities, enforcing a strict Content-Security-Policy (CSP) that bans `eval`, and executing a browser-side DOM MutationObserver that detects and purges unauthorized injected scripts.

---

## 🔒 Client-Side Anti-Tampering & Chrome DevTools Guard

To protect Web API keys, UI state, and prevent unauthorized client-side code modification via browser developer consoles:

- **DevTools Shortcut Lockout**: Intercepts and suppresses `F12`, `Ctrl+Shift+I` (Inspect Element), `Ctrl+Shift+J` (Console), `Ctrl+Shift+C` (Element Picker), `Ctrl+U` (View Source), and `Ctrl+S` (Save Page) with modern Cyber Dark-Tech security alerts.
- **Context Menu Restriction**: Disables the right-click inspect context menu across all static UI elements while intelligently preserving context menu actions inside text inputs and textareas for ease of copying/pasting IPs, MACs, and tokens.
- **Multi-Vector DevTools Detection**: Simultaneously monitors window dimension disparities (`outerWidth - innerWidth > 160px`), console getter traps, and executes periodic `console.clear()` purges.
- **Anti-Debugging Traps**: Leverages non-linear `debugger;` loops to detect breakpoint attachment and timing anomalies in browser developer tools.
- **DOM Integrity & MutationObserver**: Continuously monitors the DOM tree to immediately detect and destroy injected `<script>` tags, malicious event listeners, or inline DOM tampering.
- **Runtime Object Freezing**: Calls `Object.seal(Object.prototype)` and `Object.freeze(window.NetworkManagerSecurity)` to prevent monkey-patching of core runtime APIs (`window.fetch`, `JSON.parse`).
- **Security Telemetry**: Reports client-side tampering attempts to `/api/v1/security/client-tamper-report`, logging events into the backend tamper-evident chained-hash log.
- **Interactive UI Toggle**: Features an on/off control in the Settings panel for developers requiring local debugging.

---

## 📂 Project Directory Structure

The repository maintains a strictly clean, modular layout with zero rogue files at the root level:

```text
Control-wifi/
├── run_app.bat                     # 1-Click launcher for Desktop App
├── run_admin.bat                   # 1-Click launcher for Desktop App (Administrator rights)
├── serve_website.bat               # 1-Click launcher for Web & REST API Server (port 8080)
├── README.md                       # Primary English documentation
├── README_VI.md                    # Vietnamese documentation
├── NOTES.md                        # Technical engineering & operational notes
├── LICENSE                         # MIT License
│
├── app/                            # DESKTOP APPLICATION SUBSYSTEM (PYTHON / PYSIDE6)
│   ├── main.py                     # Primary entry point (GUI / CLI)
│   ├── requirements.txt            # Desktop dependencies
│   ├── NetworkManager.spec         # PyInstaller packaging configuration
│   ├── assets/                     # 37+ Vector SVG icons & application logos
│   ├── config/                     # Configuration files (config.json, routers.json)
│   ├── core/                       # Scanner engine, topology grapher, bandwidth meter, i18n
│   ├── data/                       # APPLICATION DATA STORAGE
│   │   ├── network.db              # SQLite database (devices, history, events)
│   │   └── logs/                   # Audit compliance & application runtime logs
│   │       ├── audit_compliance.log
│   │       └── network_manager.log
│   ├── database/                   # SQLite DAO layer (DeviceDAO, EventDAO, Database)
│   ├── gui/                        # PySide6 Cyber Dark-Tech user interface
│   ├── router/                     # Router adapters (TP-Link, OpenWrt, MikroTik, Mock)
│   ├── scripts/                    # Build scripts (build_app.py, package_zip.py)
│   ├── security/                   # DESKTOP SECURITY SUITE
│   │   ├── __init__.py             # Security facade export
│   │   ├── safe_exec.py            # Zero command injection, IP/MAC validators
│   │   ├── vault.py                # Hardware-bound credentials encryption (MachineGuid)
│   │   ├── rbac.py                 # Role-Based Access Control (Admin, Operator, Viewer)
│   │   ├── integrity.py            # HMAC-SHA256 file & DB integrity verifier
│   │   ├── arp_guard.py            # Anti-ARP poisoning & spoofing monitor
│   │   ├── firewall.py             # Bidirectional Windows Host Firewall manager
│   │   ├── blocker.py              # Multi-layer isolation coordinator
│   │   └── audit_logger.py         # Forensic compliance audit logger
│   ├── services/                   # OUI lookup service, background scheduler
│   ├── tests/                      # Test suites (test_all.py, test_app_security.py)
│   └── utils/                      # Network utilities & safe subprocess runners
│
└── web/                            # WEB PORTAL & REST API SERVER SUBSYSTEM
    ├── Dockerfile / docker-compose.yml
    ├── robots.txt / sitemap.xml
    ├── backend/                    # Multithreaded HTTP Server & REST API (/api/v1/...)
    │   ├── main.py                 # Web server entry point
    │   ├── server/                 # Request handler, CORS & static file server
    │   ├── api/                    # REST API routes (/devices, /stats, /security, ...)
    │   ├── middleware/             # Request dispatchers & security checks
    │   ├── services/               # Safe download service & audit streaming
    │   └── tests/                  # Test suites (test_web_security.py, test_security.py)
    ├── backups/                    # SQLite database snapshots
    ├── config/                     # Web server configuration
    ├── css/                        # Cyber Dark-Tech & Glassmorphism stylesheets
    ├── docs/                       # Technical API & installation markdown specifications
    ├── downloads/                  # Distribution packages (Windows, Linux, macOS)
    ├── html/                       # SPA components (8 pages) & index.html
    ├── images/                     # System logos & dashboard screenshots
    ├── js/                         # Modular JavaScript suite (anti_tamper, auth, router...)
    ├── logs/                       # Web audit logs (web/logs/audit/)
    ├── nginx/                      # Nginx reverse proxy configurations
    ├── scripts/                    # Automated build scripts (build_all.py)
    └── security/                   # WEB SECURITY SUITE (7 CORE API GUARDS)
        ├── __init__.py             # Security facade export
        ├── crypto.py               # PBKDF2-HMAC-SHA256 (600,000 rounds) & constant-time crypto
        ├── waf.py                  # OWASP Top 10 WAF (SQLi, NoSQLi, XSS, RCE, Bad Bots)
        ├── rate_limiter.py         # Sliding-Window Rate Limiter & Auto-Jail
        ├── headers.py              # Enterprise Security Headers (CSP, HSTS, XFO)
        ├── csrf.py                 # Anti-CSRF Guard (Double-Submit Token)
        ├── cors.py                 # CORS Manager with RFC preflight & origin whitelist
        ├── vpn_guard.py            # VPN Network Guard & private route restriction
        ├── sanitizer.py            # Deep Recursive Sanitizer & Prototype Pollution defense
        └── audit.py                # Chained-Hash Audit Logger (tamper-evident blockchain-style)
```

---

## 🚀 Installation & Quickstart

### Prerequisites
- **Operating System**: Windows 10/11 (64-bit), Linux (Ubuntu 22.04+, Debian, Fedora), or macOS (macOS 12+).
- **Python**: Version 3.12 or higher.
- **Nmap** *(Recommended)*: Download from [nmap.org](https://nmap.org/download.html) for hardware-accelerated ARP discovery.

### 1. Running the Desktop Application
```powershell
# Step 1: Create and activate a Python virtual environment
python -m venv venv
.\venv\Scripts\activate

# Step 2: Install required dependencies
pip install -r app/requirements.txt

# Step 3: Launch the Desktop application
python app/main.py
```
*Alternatively, double-click **`run_app.bat`** (or right-click **`run_admin.bat`** -> **Run as administrator** for full Windows Firewall and raw packet privileges).*

### 2. Running the Web Portal & REST API Server
```powershell
# Launch the server on port 8080
python web/backend/main.py 8080
```
*Or double-click **`serve_website.bat`** on Windows.*

Once started, open your web browser at: **`http://localhost:8080/`**

---

## 🛠️ Automated Build Pipeline

The web application is structured with a modern component-based architecture: edit individual components in `web/html/components/` and modules in `web/js/modules/`. Whenever you want to compile a production bundle:

```powershell
python web/scripts/build_all.py
```
The automated script will:
1. Parse and concatenate all HTML components into [`web/html/index.html`](web/html/index.html).
2. Bundle all JavaScript modules in dependency order into [`web/js/app.js`](web/js/app.js).
3. Validate markup structure, ensure zero dead code, and verify bilingual language keys.

---

## 🧪 Automated Testing Suite

The repository contains comprehensive unit test suites covering all discovery, database, router adapters, and security components:

```powershell
# 1. Desktop Application Test Suite (Discovery, DAO, Blocker, Topology, RBAC, Vault, Integrity)
.\venv\Scripts\python.exe -m unittest discover -s app/tests -p "test_*.py"
# Result: 16/16 PASS (100% OK)

# 2. Web Application & Security Test Suite (7 API Security Techniques, WAF, CORS, VPN, CSRF, RateLimit)
.\venv\Scripts\python.exe -m unittest discover -s web/backend/tests -p "test_*.py"
# Result: 23/23 PASS (100% OK)
```

---

## ⚖️ Legal Notice & Responsible Use

> [!IMPORTANT]
> **Network Manager** is designed solely for authorized local network administration, infrastructure security auditing, and academic research on networks owned or explicitly licensed to the operator. Port scanning, traffic interception, or device isolation on unauthorized external networks without prior written permission is strictly prohibited by law.

---

**© 2026 Network Manager Engineering Team. Released under the MIT License.**

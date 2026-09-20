# Technical Notes & Engineering Reference: Network Manager

This document provides in-depth technical notes, architectural diagrams, security implementation details, and operational guidance for developers and system operators working with the **Network Manager** ecosystem.

---

## 1. System Architecture & Component Interactions

Network Manager consists of two isolated yet interoperable subsystems:
1. **Desktop Client Subsystem (`app/`)**: High-privilege local agent executing network discovery, router ACL provisioning, Windows Host Firewall rules, and local SQLite data persistence.
2. **Web Portal & REST API Server (`web/`)**: High-performance HTTP server providing a modern Single Page Application (SPA), administrative REST API, live demo sandbox, and software distribution center.

```text
                                 SYSTEM OVERVIEW
 ┌──────────────────────────────────────────────────────────────────────────────────┐
 │                               DESKTOP SUBSYSTEM                                  │
 │                                                                                  │
 │  ┌──────────────┐      ┌─────────────────────────┐      ┌─────────────────────┐  │
 │  │  PySide6 GUI │ ───> │ Hybrid Discovery Engine │ ───> │ IEEE OUI Classifier │  │
 │  └──────────────┘      └─────────────────────────┘      └─────────────────────┘  │
 │         │                           │                              │             │
 │         v                           v                              v             │
 │  ┌──────────────┐      ┌─────────────────────────┐      ┌─────────────────────┐  │
 │  │ RBAC Guard   │ ───> │  Multi-Layer Blocker    │ ───> │ Hardware Credentials│  │
 │  │ (Permissions)│      │  (Router ACL + Firewall)│      │ Vault (MachineGuid) │  │
 │  └──────────────┘      └─────────────────────────┘      └─────────────────────┘  │
 └──────────────────────────────────────────────────────────────────────────────────┘
                                       │
                        Shared Network / Database Sync
                                       │
                                       v
 ┌──────────────────────────────────────────────────────────────────────────────────┐
 │                              WEB & API SUBSYSTEM                                 │
 │                                                                                  │
 │  ┌──────────────┐      ┌─────────────────────────┐      ┌─────────────────────┐  │
 │  │ Chrome Anti- │ ───> │ L7 Application WAF      │ ───> │ Sliding-Window Rate │  │
 │  │ Tamper Guard │      │ (SQLi, NoSQLi, XSS, RCE)│      │ Limiter & Auto-Jail │  │
 │  └──────────────┘      └─────────────────────────┘      └─────────────────────┘  │
 │         │                           │                              │             │
 │         v                           v                              v             │
 │  ┌──────────────┐      ┌─────────────────────────┐      ┌─────────────────────┐  │
 │  │ CORS Manager │ ───> │ VPN & Network Guard     │ ───> │ Chained-Hash Audit  │  │
 │  │ (RFC Preflt) │      │ (Tailscale / RFC 1918)  │      │ Trail (Blockchain)  │  │
 │  └──────────────┘      └─────────────────────────┘      └─────────────────────┘  │
 └──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Deep Dive: The 7 Core API Security Techniques

The Web API layer incorporates a multi-tiered security defense covering all 7 standard cybersecurity principles:

### 1. Rate Limiting (`web/security/rate_limiter.py`)
- **Algorithm**: In-memory Sliding-Window Log tracking millisecond-accurate timestamps per client IP.
- **Configured Thresholds**:
  - General API endpoints: 100 requests per minute.
  - Authentication endpoints (`/api/v1/auth/*`): 5 requests per minute.
  - Package download endpoints (`/downloads/*`): 10 requests per minute.
- **Auto-Jail Mechanism**: Consecutive rate-limit or WAF violations automatically ban the offending IP. Initial penalty: 60 seconds; subsequent violations double exponentially up to 1800 seconds. Responses return HTTP `429 Too Many Requests` with `Retry-After`.

### 2. Cross-Origin Resource Sharing (CORS) (`web/security/cors.py`)
- **Origin Validation**: Strict whitelist containing loopback origins (`http://localhost:*`, `http://127.0.0.1:*`) and private subnets (`192.168.*`, `10.*`).
- **Preflight Support**: Handles HTTP `OPTIONS` requests conforming to RFC specifications with `Access-Control-Allow-Methods`, `Access-Control-Allow-Headers`, and `Access-Control-Max-Age`.
- **Credential Protection**: When `Access-Control-Allow-Credentials: true` is active, wildcards (`*`) are prohibited; the exact vetted Origin is echoed back.

### 3. SQL & NoSQL Injection Protection (`web/security/waf.py` & `app/database/`)
- **L7 Inspection**: WAF inspects query parameters, path strings, and request bodies for SQL signatures (`UNION SELECT`, `' OR '1'='1`, `INFORMATION_SCHEMA`, stacked queries) and MongoDB / NoSQL injection operators (`$where`, `$gt`, `$ne`, `$regex`, `$in`, `$or`, `$exists`, `$nin`).
- **DAO Enforcement**: 100% of SQLite database queries in `DeviceDAO`, `EventDAO`, and `Database` utilize parameterized statements with `?` placeholders. String formatting into SQL statements is prohibited.

### 4. Firewalls (`web/security/firewall.py` & `app/security/firewall.py`)
- **Application-Layer (L7)**: In-memory IP whitelist/blacklist with CIDR subnet matching support. Malicious bots (`sqlmap`, `nikto`, `wpscan`, `dirbuster`) are dropped before reaching application routes.
- **Host-Layer (L3/L4)**: Windows Defender Firewall interface executing `netsh advfirewall firewall` rules through `safe_run_command` with parameterized arguments and zero `shell=True`.

### 5. Virtual Private Networks (VPNs) & Route Guard (`web/security/vpn_guard.py`)
- **Subnet Classification**: Recognizes RFC 1918 private subnets (`192.168.0.0/16`, `10.0.0.0/8`, `172.16.0.0/12`), Carrier-Grade NAT / Tailscale networks (`100.64.0.0/10`), and common VPN subnets (WireGuard `10.8.0.0/16`, OpenVPN `10.9.0.0/16`).
- **Protected Endpoints**: Administrative routes (`/api/v1/settings`, `/api/v1/backup`, `/api/v1/auth/users`) are inaccessible from public WAN IPs unless connected via a verified VPN tunnel.

### 6. Cross-Site Request Forgery (CSRF) (`web/security/csrf.py`)
- **Double-Submit Cookie Pattern**: Generates 256-bit entropy tokens (`secrets.token_hex(32)`).
- **Enforcement**: State-changing methods (`POST`, `PUT`, `DELETE`, `PATCH`) must supply a matching `X-CSRF-Token` header.
- **Cookie Flags**: Cookies are marked `SameSite=Strict`, `HttpOnly`, and scoped to root path `/`.

### 7. Cross-Site Scripting (XSS) (`web/security/sanitizer.py`, `headers.py`)
- **Deep Recursive Sanitization**: Traverses nested JSON objects and URL encoded forms, stripping null bytes (`\x00`), escaping HTML characters (`<`, `>`, `"`, `'`, `&`), and rejecting prototype pollution vectors (`__proto__`, `constructor`).
- **Content Security Policy (CSP)**: Strict policy disabling `eval()`, restricting script execution to approved origins, and enforcing `X-Content-Type-Options: nosniff` and `X-Frame-Options: DENY`.

---

## 3. Client-Side Anti-Tampering & Chrome DevTools Guard

The browser client implements multiple layers of runtime defense:

| Mechanism | Implementation File | Details |
|---|---|---|
| **Shortcut Lockout** | `web/js/modules/anti_tamper.js` | Suppresses `F12`, `Ctrl+Shift+I/J/C`, `Ctrl+U`, `Ctrl+S` on Windows/Linux and `Cmd+Option+I/J/C/U` on macOS. |
| **Context Menu Guard** | `web/js/modules/anti_tamper.js` | Disables right-click inspect menu across the DOM, while maintaining right-click accessibility for text inputs and textareas. |
| **DevTools Detection** | `web/js/modules/anti_tamper.js` | Compares window inner/outer dimensions, utilizes console getter traps, and issues periodic `console.clear()`. |
| **Anti-Debugging Trap** | `web/js/modules/anti_tamper.js` | Uses timing deltas across asynchronous `debugger;` loops to detect breakpoint attachments. |
| **DOM Mutation Observer** | `web/js/modules/anti_tamper.js` | Observes the DOM tree and purges unauthorized injected `<script>` elements. |
| **Runtime Freezing** | `web/js/modules/anti_tamper.js` | Seals and freezes `Object.prototype` and `window.NetworkManagerSecurity` against monkey-patching. |
| **Telemetry Reporting** | `web/backend/api/routes.py` | Sends client-side tampering detections to `/api/v1/security/client-tamper-report` for chained-hash audit logging. |

---

## 4. Hardware-Bound Credentials Vault (`app/security/vault.py`)

Router credentials stored on disk are encrypted using keys bound to the physical host:
1. **Entropy Harvesting**: Queries Windows Registry for `HKLM\SOFTWARE\Microsoft\Cryptography\MachineGuid`.
2. **Key Derivation**: Feeds the hardware GUID, CPU model string, and a 32-byte salt into **PBKDF2-HMAC-SHA256** across 100,000 iterations.
3. **AES-GCM Authenticated Encryption**: Plaintext passwords are encrypted with AES-256-GCM.
4. **Portability Protection**: If an adversary copies `routers.json` to another machine, the derived key will mismatch, causing decryption failure and raising an integrity alert.

---

## 5. Chained-Hash Audit Logger (`web/security/audit.py`)

All security events (logins, blocked MACs, rate limits, WAF triggers, tamper telemetry) are recorded in a blockchain-inspired chained log:

$$\text{Hash}_n = \text{SHA256}(\text{Timestamp}_n \parallel \text{Event}_n \parallel \text{IP}_n \parallel \text{Hash}_{n-1})$$

- **Tamper Detection**: The built-in `verify_log_integrity()` function audits the cryptographic link between consecutive entries.
- **Forensic Guarantee**: Any modification, insertion, or truncation of historical log records breaks the mathematical hash chain and is immediately flagged.

---

## 6. Directory Layout & Path Anchoring Guidelines

To prevent stray files during development or runtime:
- **Application Root**: All Python path anchors should use `Path(__file__).resolve().parent...` rather than relative working directory paths (`os.getcwd()`).
- **Database & Logs**:
  - Desktop database: [`app/data/network.db`](file:///c:/Users/HOA%20BINH/Control-wifi/app/data/network.db)
  - Desktop audit log: [`app/data/logs/audit_compliance.log`](file:///c:/Users/HOA%20BINH/Control-wifi/app/data/logs/audit_compliance.log)
  - Web audit log: [`web/logs/audit/audit_chain.log`](file:///c:/Users/HOA%20BINH/Control-wifi/web/logs/audit/)
- **Testing Cleanliness**: Automated tests must use `try...finally` with `gc.collect()` before removing SQLite databases on Windows to avoid `PermissionError: [WinError 32] The process cannot access the file because it is being used by another process`.

---

## 7. Operational & Troubleshooting Reference

| Symptom | Root Cause | Resolution |
|---|---|---|
| **ARP Scan returns only Gateway** | Non-administrator privilege without Nmap installed. | Install Nmap 7.90+ or launch application with `run_admin.bat`. |
| **HTTP 429 Too Many Requests** | Exceeded request limit or triggered Auto-Jail. | Wait 60 seconds for jail timer expiration or whitelist IP in `web/security/rate_limiter.py`. |
| **HTTP 403 Forbidden on `/settings`** | Accessing sensitive admin route from a non-VPN WAN IP. | Connect via local LAN or trusted VPN tunnel (WireGuard / Tailscale). |
| **DevTools opens with repeated debugger pauses** | Anti-Tamper Guard is active. | Disable the toggle in Web Settings or run with local debug flag in development. |
| **Windows SQLite test file lock** | Open connection handle held by Python GC on Windows. | Explicitly close cursor/connection and call `import gc; gc.collect()` before `os.remove()`. |

---

## 8. Enterprise Defense-in-Depth Enhancements (Phase 2 Upgrade)

### Desktop Application Hardening
- **Memory Zeroization (`app/security/zeroize.py`)**: Overwrites physical byte buffers with null bytes (`0x00`) immediately after consuming plaintext router passwords or session tokens. Implemented as a RAII context manager (`with SecureBuffer(...) as buf:`).
- **Process Integrity & Anti-Hook Guard (`app/security/process_guard.py`)**: Checks Windows PEB `BeingDebugged` and `CheckRemoteDebuggerPresent`. Enumerates active DLL modules in process address space via `psapi.EnumProcessModules` to detect injected hooks (Frida, Detours, Cheat Engine, MinHook).
- **DNS Guard (`app/security/dns_guard.py`)**: Inspects adapter DNS configurations via PowerShell WMI cmdlets. Classifies addresses into Trusted Public DNS (Cloudflare, Google, Quad9), Private Gateway, and flags unknown public IPs as potential Rogue DNS / DHCP Hijacking.
- **Emergency Host Quarantine (`app/security/firewall.py`)**: Instant firewall isolation mode blocking 100% of non-loopback inbound and outbound traffic except the local gateway management address.

### Web Server & REST API Hardening
- **Advanced WAF Expansion (`web/security/waf.py`)**: Inspects query strings, bodies, and key HTTP headers (`User-Agent`, `Referer`, `X-Forwarded-For`) for:
  - **SSRF**: Cloud metadata IPs (`169.254.169.254`, `metadata.google.internal`, Alibaba/Tencent metadata).
  - **SSTI**: Jinja2/Mako/Twig template injection expressions (`{{...}}`, `#{...}`).
  - **JNDI / Log4j**: Remote codebase lookup patterns (`${jndi:ldap...}`, `${jndi:rmi...}`).
  - **Protocol Wrappers**: Dangerous wrapper protocols (`php://`, `gopher://`, `dict://`, `file:///etc/`).
- **Account Lockout Manager (`web/security/account_lockout.py`)**: Enforces username-based lockout (5 failed attempts -> 15-minute freeze), defeating distributed botnets rotating source IP addresses.
- **Request Size & MIME Guard (`web/security/request_guard.py`)**: Restricts request payloads to 2MB (HTTP 413) and enforces valid API MIME types (HTTP 415), preventing memory exhaustion attacks.
- **Data Masking Engine (`web/security/data_masker.py`)**: Recursively traverses outbound API JSON structures and scrubs passwords, secrets, and private keys into `********`.
- **Extended Security Headers (`web/security/headers.py`)**: Enforces `Permissions-Policy` (disabling camera, mic, geolocation), `Cross-Origin-Embedder-Policy: credentialless`, and `X-Permitted-Cross-Domain-Policies: none`.

---

## 9. Multi-Layer Anti-DoS & Anti-DDoS Architecture (`web/security/dos_guard.py`)

The Web Server and REST API subsystem incorporate an enterprise-grade, four-layer Anti-DoS/DDoS defense engine operating prior to HTTP request routing:

```text
 Inbound TCP Connection
           │
           ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ Layer 1: L4/L7 Connection Shield                            │
 │ - Max concurrent connections per IP: 15                     │
 │ - Global concurrent server connections: 128                 │
 │ - Loopback exemption (127.0.0.1, ::1)                       │
 └──────────────────────────────┬──────────────────────────────┘
                                │ PASS
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ Layer 2: Slowloris & Socket Timeout Mitigation              │
 │ - Strict per-socket timeout: 5.0 seconds                    │
 │ - Drops slow HTTP header trickles immediately               │
 └──────────────────────────────┬──────────────────────────────┘
                                │ PASS
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ Layer 3: Micro-Burst Throttler                              │
 │ - Max 25 requests per 2.0-second sliding window             │
 │ - Immediate 60-second Blackhole quarantine upon burst       │
 └──────────────────────────────┬──────────────────────────────┘
                                │ PASS
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ Layer 4: Adaptive Under-Attack Mode & SHA-256 PoW           │
 │ - System-wide RPS threshold: 60.0 requests/sec              │
 │ - Issues cryptographic SHA-256 Proof-of-Work challenge      │
 │ - Defeats distributed botnets by consuming client CPU       │
 └─────────────────────────────────────────────────────────────┘
```

---

## 10. 100-Request Firewall Limit & Automated 1,000-Request IP Ban Bot

To defend against automated scraping, brute-forcing, and volumetric HTTP floods, Network Manager establishes a two-phase rate enforcement and bot-banning pipeline:

### 1. 100-Request Firewall Quota & Cooldown Warning Page (`web/html/429.html`)
- **Quota**: Strictly enforces a maximum of **100 requests per 60-second sliding window** per individual IP address.
- **Smart Client Discrimination (`handler.py -> is_html_client()`)**:
  - **Browser Clients** (`Accept: text/html`): Dynamically renders and serves [`web/html/429.html`](web/html/429.html) (HTTP 429 Too Many Requests).
  - **API Clients** (`/api/*` or `Accept: application/json`): Returns structured JSON 429 error payload with standard `Retry-After` header.
- **Page Capabilities**:
  - Cyberpunk Dark Tech Glassmorphic styling with Amber glow accents.
  - Live JavaScript countdown timer (`<span id="countdown">60</span>s`) and dynamic progress bar.
  - Automatic page reload upon timer expiration.
  - Injects client IP and firewall telemetry directly into DOM.
  - Provides instant `[Try Again Now]` and `[Back to Home]` action triggers.

### 2. Automated IP Ban Bot (`web/security/ip_ban_bot.py`)
- **Cumulative Traffic Telemetry**: Tracks the lifetime request volume from each non-loopback IP address (`_cumulative_requests`).
- **Auto-Ban Trigger**: Once an IP crosses the threshold of **1,000 requests**:
  1. **Immediate Application Ban**: The bot marks the IP as banned in memory and writes to persistent storage [`web/data/banned_ips.json`](web/data/banned_ips.json) with incident metadata, request count, and expiration timestamp.
  2. **OS Kernel Drop (Windows Host Firewall)**: On Windows operating systems, the bot issues a privileged `netsh advfirewall firewall add rule name="NetManager_BotBan_{IP}_IN" dir=in action=block remoteip={IP}` rule, dropping packets directly in the kernel network stack before socket allocation.
  3. **Forensic Audit Logging**: Records a `CRITICAL` audit record in the blockchain-style chained-hash audit trail (`web/logs/audit/audit.log`).
  4. **Dedicated 403 Banned Webpage (`web/html/banned.html`)**: Subsequent visits from the banned IP receive HTTP 403 Forbidden displaying incident ID, violation details, and administrator unlock instructions.
  5. **Administrative Unban**: Administrators can instantly restore an IP via the console or administrative API:
     ```python
     from web.security.ip_ban_bot import ip_ban_bot
     ip_ban_bot.unban_ip("192.168.1.55")
     ```

---

## 11. Test Coverage & Verification Matrix

The test suite consists of **72 comprehensive, automated unit tests** passing with 100% success rate:

```powershell
# Desktop Application Test Suite (31 tests)
.\venv\Scripts\python.exe -m unittest discover -s app/tests -p "test_*.py"
# Ran 31 tests in 3.7s -> OK

# Web Server & Security Test Suite (41 tests)
.\venv\Scripts\python.exe -m unittest discover -s web/backend/tests -p "test_*.py"
# Ran 41 tests in 1.3s -> OK

# Combined Verification: 72/72 PASS (100% SUCCESS)
```

---

**Network Manager Engineering Documentation — Updated 2026 (v2.0.0 Cyberpunk Edition)**



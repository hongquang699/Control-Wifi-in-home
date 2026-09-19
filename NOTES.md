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

**Network Manager Engineering Documentation — Updated 2026**

# Network Manager Installation Guide

Comprehensive setup and deployment guide for **Network Manager v2.0.0** across **Windows**, **Linux**, and **macOS**.

---

## 1. System Requirements

| Component | Minimum Specification | Recommended Specification |
| :--- | :--- | :--- |
| **Operating System** | Windows 10/11 (64-bit), Ubuntu 22.04+, macOS 12+ | Windows 11 64-bit or Linux Server x64 |
| **CPU** | Dual Core 1.8 GHz | Quad Core 2.5 GHz or higher |
| **RAM** | 2 GB RAM | 4 GB RAM or higher |
| **Storage** | 250 MB free space | 1 GB SSD space |
| **Privilege Level** | Standard User (Basic Discovery) | Administrator / Root (Firewall & Raw ARP) |
| **Auxiliary Tools** | Native ARP + ICMP Ping (Built-in) | Nmap 7.90+ (Optional, accelerates subnet scans) |

---

## 2. Installation on Windows

### Option 1: Standalone Portable Executable (.exe) — Recommended
1. Download `NetworkManager-v2.0.0-windows-x64.zip` from the [Downloads Page](#/download).
2. Extract the archive to your target directory (e.g., `C:\Tools\NetworkManager\`).
3. Launch:
   - **Standard Mode**: Double-click `run.bat` or `NetworkManager.exe`.
   - **Administrator Mode (Full Access)**: Right-click `run_admin.bat` and choose **Run as administrator** to permit Windows Host Firewall rule creation and low-level Nmap raw socket execution.

### Option 2: Run From Python Source Code
```powershell
# 1. Clone repository
git clone https://github.com/hongquang699/Control-Wifi-in-home.git
cd Control-Wifi-in-home

# 2. Initialize Python 3.12 Virtual Environment
python -m venv venv
.\venv\Scripts\activate

# 3. Install dependencies
pip install -r app/requirements.txt

# 4. Launch Desktop application
python app/main.py
```

---

## 3. Installation on Linux (Ubuntu / Debian / Fedora / Arch)

1. Download the release archive `NetworkManager-v2.0.0-linux-x64.tar.gz`.
2. Extract the bundle:
   ```bash
   tar -xzf NetworkManager-v2.0.0-linux-x64.tar.gz
   cd NetworkManager
   ```
3. Grant execution permissions and run with sudo for raw socket access:
   ```bash
   chmod +x network_manager
   sudo ./network_manager
   ```

---

## 4. Running the Web Portal & REST API Server

```powershell
# Start HTTP Server on port 8080
python web/backend/main.py 8080
```
*Or execute `serve_website.bat`.*

Navigate your web browser to: **`http://localhost:8080/`**

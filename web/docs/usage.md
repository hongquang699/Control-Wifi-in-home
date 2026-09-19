# Network Manager User Guide

Detailed operational manual for network discovery, topology visualization, and access control with **Network Manager**.

---

## 1. Startup & Initial Network Discovery

1. **Initialization**: On startup, Network Manager inspects active network interface cards (NICs), determines the local host IP, resolves the default router gateway, and calculates the target subnet range (e.g., `192.168.1.0/24` or `192.168.110.0/24`).
2. **Automated Discovery**: The background discovery engine automatically catalogs all responsive hosts, collecting IP, MAC, and IEEE vendor information.
3. **Manual Refresh**: Click **"Scan Network"** on the main toolbar to trigger an immediate discovery cycle.

---

## 2. Managing Network Devices

Within the **"Devices"** tab:
- **Telemetry Inspection**: View hostname, IP address, MAC address, vendor profile (OUI), hardware medium (Wi-Fi vs Ethernet), network zone, and status (`ONLINE`, `OFFLINE`, `BLOCKED`).
- **Real-Time Filtering**: Search by IP, MAC, hostname, or vendor substring.
- **Subnet Segmentation**: Toggle between the *Primary Wi-Fi (`192.168.1.x`)* and *Secondary Access Point (`192.168.110.x`)* zones.
- **Device Aliasing**:
  1. Click **"Detail"** on any device row.
  2. Input a friendly name (e.g., *Work Laptop*, *Living Room Smart TV*, *Security Camera 01*).
  3. Click **"Save Changes"**. The custom alias is persisted and prioritized across the UI.

---

## 3. Multi-Hop Network Topology Map

1. Navigate to the **"Network Map"** tab.
2. Inspect the hierarchical tree visualizer:
   ```text
   GLOBAL INTERNET
        │
   [ PRIMARY GATEWAY ROUTER ] (192.168.1.1)
        ├── [ Admin PC ]
        ├── [ Mobile Device ]
        └── [ SECONDARY AP ROUTER ] (192.168.110.1)
                 ├── [ Smart TV ]
                 └── [ IoT Camera ]
   ```
3. Each node dynamically reflects connection quality, ping latency, and isolation status.

---

## 4. Access Control: Blocking & Unblocking Devices

### Blocking a Device
1. Click **"Block"** in the device table or detail dialog.
2. Confirm the isolation request in the prompt.
3. The engine executes:
   - MAC Filtering / ACL push to the configured Router Adapter (TP-Link, OpenWrt, MikroTik, or Mock).
   - Inbound and Outbound host firewall isolation rules on the admin workstation.
   - Status changes to **BLOCKED** and transitions to the **"Blocked Devices"** tab.

### Unblocking a Device
1. Open the **"Blocked Devices"** tab.
2. Click **"Unblock"** on the target device.
3. Isolation rules are purged from the router and firewall, restoring connectivity.

---

## 5. Router Adapter Configuration

1. Open **"Settings"** -> **"Router Configuration"**.
2. Select your router adapter type:
   - **TP-Link**: Consumer Wi-Fi routers via HTTP Web management.
   - **OpenWrt**: Devices running OpenWrt firmware via LuCI / ubus JSON-RPC.
   - **MikroTik**: RouterOS appliances via API port 8728.
   - **Mock Router**: Full simulation mode for safe evaluation.
3. Enter the Gateway IP, administrator username, and password.
4. Click **"Test Connection"** to verify authentication before saving.

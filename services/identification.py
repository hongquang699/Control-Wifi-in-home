"""
Dịch vụ nhận diện Vendor và Phân loại loại thiết bị (Device Type) qua MAC OUI và Hostname.
"""

import re
from typing import Tuple
from utils.validators import normalize_mac

# Danh mục OUI phổ biến (3 octets đầu)
OUI_DATABASE = {
    # Apple
    "00:03:93": "Apple", "00:05:02": "Apple", "00:0A:27": "Apple", "00:0A:95": "Apple",
    "00:0D:93": "Apple", "00:11:24": "Apple", "00:14:51": "Apple", "00:16:CB": "Apple",
    "00:17:F2": "Apple", "00:19:E3": "Apple", "00:1B:63": "Apple", "00:1C:B3": "Apple",
    "00:1D:4F": "Apple", "00:1E:52": "Apple", "00:1F:5B": "Apple", "00:21:E9": "Apple",
    "00:22:41": "Apple", "00:23:12": "Apple", "00:23:32": "Apple", "00:23:6C": "Apple",
    "00:24:36": "Apple", "00:25:00": "Apple", "00:25:4B": "Apple", "00:26:08": "Apple",
    "00:26:4A": "Apple", "00:26:B0": "Apple", "00:CD:FE": "Apple", "04:0C:CE": "Apple",
    "18:65:90": "Apple", "28:CF:E9": "Apple", "3C:07:54": "Apple", "40:B3:95": "Apple",
    "48:43:7C": "Apple", "54:26:96": "Apple", "60:F4:45": "Apple", "70:56:81": "Apple",
    "80:EA:96": "Apple", "8C:85:90": "Apple", "98:01:A7": "Apple", "A4:C3:61": "Apple",
    "AC:BC:32": "Apple", "B8:78:26": "Apple", "C8:69:CD": "Apple", "DC:A9:04": "Apple",
    "E0:C9:7A": "Apple", "F0:18:98": "Apple", "F4:F1:5A": "Apple", "FC:25:3F": "Apple",
    
    # Samsung
    "00:07:AB": "Samsung", "00:09:18": "Samsung", "00:12:47": "Samsung", "00:15:99": "Samsung",
    "00:16:6C": "Samsung", "00:17:C9": "Samsung", "00:1A:8A": "Samsung", "00:1D:25": "Samsung",
    "00:21:4C": "Samsung", "00:23:39": "Samsung", "00:24:90": "Samsung", "08:37:3D": "Samsung",
    "14:49:E0": "Samsung", "18:3B:D2": "Samsung", "24:4B:03": "Samsung", "2C:4D:54": "Samsung",
    "30:07:4D": "Samsung", "34:23:87": "Samsung", "38:01:46": "Samsung", "40:4E:36": "Samsung",
    "4C:BC:48": "Samsung", "50:56:A8": "Samsung", "5C:A3:9D": "Samsung", "64:1C:AE": "Samsung",
    "78:47:1D": "Samsung", "84:25:DB": "Samsung", "8C:77:12": "Samsung", "94:65:2D": "Samsung",
    "A8:7C:01": "Samsung", "B4:07:F9": "Samsung", "C0:BD:D1": "Samsung", "D0:22:BE": "Samsung",
    "E4:58:B8": "Samsung", "EC:1F:72": "Samsung", "F8:04:2E": "Samsung",
    
    # Xiaomi
    "00:9E:C8": "Xiaomi", "04:CF:8C": "Xiaomi", "18:59:36": "Xiaomi", "28:6C:07": "Xiaomi",
    "34:80:B3": "Xiaomi", "3C:BD:3E": "Xiaomi", "50:8F:4C": "Xiaomi", "58:44:98": "Xiaomi",
    "64:09:80": "Xiaomi", "74:23:44": "Xiaomi", "78:02:F8": "Xiaomi", "7C:49:EB": "Xiaomi",
    "8C:BE:BE": "Xiaomi", "98:FA:E3": "Xiaomi", "A4:C4:94": "Xiaomi", "AC:C1:EE": "Xiaomi",
    "B0:E2:35": "Xiaomi", "C4:0B:D4": "Xiaomi", "D4:97:0B": "Xiaomi", "F4:F5:24": "Xiaomi",

    # TP-Link
    "00:0A:EB": "TP-Link", "00:14:78": "TP-Link", "00:19:E0": "TP-Link", "00:21:27": "TP-Link",
    "00:23:CD": "TP-Link", "00:25:86": "TP-Link", "14:75:90": "TP-Link", "14:CF:92": "TP-Link",
    "1C:3B:F3": "TP-Link", "20:0C:C8": "TP-Link", "30:B5:C2": "TP-Link", "3C:46:D8": "TP-Link",
    "40:31:3C": "TP-Link", "50:3E:AA": "TP-Link", "50:C7:BF": "TP-Link", "54:AF:97": "TP-Link",
    "60:32:B1": "TP-Link", "64:56:01": "TP-Link", "70:4F:57": "TP-Link", "74:05:A5": "TP-Link",
    "84:16:F9": "TP-Link", "90:F6:52": "TP-Link", "A0:F3:C1": "TP-Link", "B0:95:75": "TP-Link",
    "C0:25:E9": "TP-Link", "C4:6E:1F": "TP-Link", "D4:6E:0E": "TP-Link", "E8:48:B8": "TP-Link",
    "EC:08:6B": "TP-Link", "F4:EC:38": "TP-Link",

    # Intel
    "00:02:B3": "Intel", "00:03:47": "Intel", "00:04:23": "Intel", "00:07:E9": "Intel",
    "00:0E:0C": "Intel", "00:13:02": "Intel", "00:13:E8": "Intel", "00:15:00": "Intel",
    "00:16:76": "Intel", "00:19:D1": "Intel", "00:1B:21": "Intel", "00:1C:BF": "Intel",
    "00:1D:E0": "Intel", "00:1E:64": "Intel", "00:1F:3B": "Intel", "00:21:5C": "Intel",
    "00:22:FB": "Intel", "00:23:14": "Intel", "00:24:D7": "Intel", "00:26:C6": "Intel",
    "3C:F8:62": "Intel", "48:51:B7": "Intel", "4C:1D:96": "Intel", "58:91:CF": "Intel",
    "68:05:CA": "Intel", "74:70:FD": "Intel", "80:86:F2": "Intel", "8C:8D:28": "Intel",
    "94:E6:F7": "Intel", "A0:36:BC": "Intel", "AC:74:09": "Intel", "B4:96:91": "Intel",

    # Espressif (ESP8266/ESP32 IoT)
    "18:FE:34": "Espressif (IoT)", "24:0A:C4": "Espressif (IoT)", "24:62:AB": "Espressif (IoT)",
    "24:6F:28": "Espressif (IoT)", "24:B2:DE": "Espressif (IoT)", "2C:F4:32": "Espressif (IoT)",
    "30:AE:A4": "Espressif (IoT)", "3C:61:05": "Espressif (IoT)", "3C:71:BF": "Espressif (IoT)",
    "48:3F:DA": "Espressif (IoT)", "48:55:19": "Espressif (IoT)", "5C:CF:7F": "Espressif (IoT)",
    "60:01:94": "Espressif (IoT)", "68:C6:3A": "Espressif (IoT)", "84:0D:8E": "Espressif (IoT)",
    "84:F3:EB": "Espressif (IoT)", "A4:CF:12": "Espressif (IoT)", "AC:67:B2": "Espressif (IoT)",
    "B4:E6:2D": "Espressif (IoT)", "C4:4F:33": "Espressif (IoT)", "CC:50:E3": "Espressif (IoT)",
    "D8:A0:1D": "Espressif (IoT)", "DC:4F:22": "Espressif (IoT)",

    # Realtek
    "00:07:0E": "Realtek", "00:0B:2F": "Realtek", "00:18:4D": "Realtek", "00:26:18": "Realtek",
    "00:E0:4C": "Realtek", "40:8D:5C": "Realtek", "50:3E:AA": "Realtek", "52:54:00": "Realtek/QEMU",
    "74:D0:2B": "Realtek", "80:EA:07": "Realtek", "88:25:2C": "Realtek", "B8:97:5A": "Realtek",

    # Dell & HP
    "00:14:22": "Dell", "00:18:8B": "Dell", "00:19:B9": "Dell", "00:21:70": "Dell",
    "00:22:19": "Dell", "00:24:E8": "Dell", "00:26:B9": "Dell", "18:03:73": "Dell",
    "00:08:02": "HP", "00:0E:7F": "HP", "00:11:0A": "HP", "00:16:35": "HP", "00:17:A4": "HP",
    "00:1B:78": "HP", "00:1E:0B": "HP", "00:21:5A": "HP", "00:22:64": "HP", "00:24:81": "HP",

    # MikroTik, Cisco, Ubiquiti, Huawei
    "00:0C:42": "MikroTik", "48:8F:5A": "MikroTik", "64:D1:54": "MikroTik", "74:4D:28": "MikroTik",
    "B8:69:F4": "MikroTik", "C4:AD:34": "MikroTik", "CC:2D:E0": "MikroTik", "D4:01:C3": "MikroTik",
    "00:00:0C": "Cisco", "00:01:42": "Cisco", "00:01:43": "Cisco", "00:01:63": "Cisco",
    "00:27:22": "Ubiquiti", "04:18:D6": "Ubiquiti", "24:A4:3C": "Ubiquiti", "68:72:51": "Ubiquiti",
    "78:8A:20": "Ubiquiti", "80:2A:A8": "Ubiquiti", "DC:9F:DB": "Ubiquiti", "F0:9F:C2": "Ubiquiti",
    "00:18:82": "Huawei", "00:1E:10": "Huawei", "00:25:9E": "Huawei", "04:25:28": "Huawei",

    # Raspberry Pi
    "B8:27:EB": "Raspberry Pi", "DC:A6:32": "Raspberry Pi", "E4:5F:01": "Raspberry Pi",
    "28:CD:C1": "Raspberry Pi", "D8:3A:DD": "Raspberry Pi"
}

class DeviceIdentifier:
    @staticmethod
    def identify_vendor(mac: str) -> str:
        """Nhận diện hãng sản xuất qua 3 cặp ký tự đầu của MAC."""
        if not mac:
            return "Unknown"
        mac_norm = normalize_mac(mac)
        parts = mac_norm.split(":")
        if len(parts) >= 3:
            prefix = ":".join(parts[:3])
            if prefix in OUI_DATABASE:
                return OUI_DATABASE[prefix]
        return "Unknown"

    @staticmethod
    def classify_device(ip: str, mac: str, hostname: str, vendor: str, is_gateway: bool = False) -> Tuple[str, str]:
        """
        Xác định vendor và phân loại thiết bị:
        Trả về (vendor, device_type)
        Device types: 'Router', 'Phone', 'PC', 'IoT', 'Printer', 'Server', 'Unknown'
        """
        # Xác định vendor nếu chưa có
        if not vendor or vendor == "Unknown":
            vendor = DeviceIdentifier.identify_vendor(mac)

        # 1. Router / Gateway
        if is_gateway or ip.endswith(".1") or "router" in hostname.lower() or "gateway" in hostname.lower():
            return vendor, "Router"

        # 2. Heuristic theo Vendor và Hostname
        host_lower = hostname.lower()
        vendor_lower = vendor.lower()

        if any(w in host_lower for w in ["iphone", "ipad", "android", "galaxy", "pixel", "xiaomi", "redmi", "oppo", "vivo", "realme"]):
            return vendor, "Phone"

        if any(w in host_lower for w in ["desktop", "laptop", "pc", "thinkpad", "macbook", "surface", "msi", "asus", "dell", "hp"]):
            return vendor, "PC"

        if "espressif" in vendor_lower or "iot" in vendor_lower or any(w in host_lower for w in ["esp_", "tasmota", "shelly", "cam", "camera", "tuya", "sonoff", "smart"]):
            return vendor, "IoT"

        if any(w in host_lower for w in ["print", "printer", "epson", "canon", "brother"]):
            return vendor, "Printer"

        if any(w in host_lower for w in ["server", "nas", "synology", "qnap", "proxmox", "truenas", "unraid"]):
            return vendor, "Server"

        # Theo vendor
        if "apple" in vendor_lower:
            # Apple có thể là iPhone hoặc Mac
            return vendor, "Phone" if ("iphone" in host_lower or "ipad" in host_lower) else "PC"
        if "samsung" in vendor_lower:
            return vendor, "Phone"
        if "xiaomi" in vendor_lower:
            return vendor, "Phone"
        if "intel" in vendor_lower or "dell" in vendor_lower or "hp" in vendor_lower:
            return vendor, "PC"
        if "raspberry" in vendor_lower:
            return vendor, "IoT"
        if any(v in vendor_lower for v in ["tp-link", "mikrotik", "cisco", "ubiquiti", "huawei"]):
            return vendor, "Router"

        return vendor, "Unknown"

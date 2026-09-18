"""
Module quét mạng cục bộ đa dải (Multi-Subnet Scanner) bằng Nmap XML & Native Fallback.
Hỗ trợ tự động phát hiện và quét đồng thời cả Wi-Fi Tổng (Modem ISP) và các Router/AP Wi-Fi phụ.
"""

import xml.etree.ElementTree as ET
import os
import shutil
import ipaddress
import concurrent.futures
from typing import List, Dict, Optional, Callable, Union
from core.device import Device
from core.network import NetworkManagerCore, NetworkInterface
from core.logger import logger
from services.identification import DeviceIdentifier
from utils.command import run_cmd
from utils.network_utils import ping_host, get_arp_table, resolve_hostname
from utils.validators import is_valid_ipv4, normalize_mac, is_valid_mac

class NetworkScanner:
    def __init__(self, nmap_path: Optional[str] = None):
        self.nmap_path = self._find_nmap(nmap_path)
        self.current_interface = NetworkManagerCore.get_default_interface()

    def _find_nmap(self, custom_path: Optional[str] = None) -> Optional[str]:
        if custom_path and os.path.isfile(custom_path):
            return custom_path
        
        default_paths = [
            r"C:\Program Files (x86)\Nmap\nmap.exe",
            r"C:\Program Files\Nmap\nmap.exe",
        ]
        for p in default_paths:
            if os.path.isfile(p):
                return p
                
        which_nmap = shutil.which("nmap")
        if which_nmap:
            return which_nmap
            
        return None

    def detect_active_subnets(self) -> List[str]:
        """
        Tự động phát hiện tất cả các dải subnet liên quan trong mạng gia đình:
        1. Subnet của card mạng máy tính (ví dụ: 192.168.110.0/24)
        2. Subnet của Modem/Wi-Fi Tổng (ví dụ: 192.168.1.0/24 nếu 192.168.1.1 phản hồi)
        3. Các dải thông dụng khác (192.168.0.0/24)
        """
        subnets = []
        if not self.current_interface:
            self.current_interface = NetworkManagerCore.get_default_interface()

        if self.current_interface and self.current_interface.cidr:
            subnets.append(self.current_interface.cidr)

        # Kiểm tra sự tồn tại của modem/router tổng ở các dải phổ biến
        upstream_gateways = ["192.168.1.1", "192.168.0.1", "10.0.0.1"]
        for gw in upstream_gateways:
            # Nếu gateway này chưa nằm trong subnet đã có
            already_in = False
            for s in subnets:
                try:
                    if ipaddress.IPv4Address(gw) in ipaddress.IPv4Network(s, strict=False):
                        already_in = True
                        break
                except Exception:
                    pass
            if already_in:
                continue

            # Ping thử gateway
            is_up, _ = ping_host(gw, timeout_ms=300)
            if is_up:
                parts = gw.split(".")
                candidate_subnet = f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
                if candidate_subnet not in subnets:
                    subnets.append(candidate_subnet)
                    logger.info(f"Phát hiện thêm dải mạng upstream/Wi-Fi tổng: {candidate_subnet} (Gateway: {gw})")

        return subnets

    def scan_subnet(
        self,
        subnet: Optional[Union[str, List[str]]] = None,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> List[Device]:
        """
        Quét dải mạng (hoặc danh sách nhiều dải mạng).
        """
        if not self.current_interface:
            self.current_interface = NetworkManagerCore.get_default_interface()

        # Chuẩn hóa danh sách các subnet cần quét
        target_subnets: List[str] = []
        if isinstance(subnet, list):
            target_subnets = [s.strip() for s in subnet if s.strip()]
        elif isinstance(subnet, str) and subnet.strip():
            # Hỗ trợ phân tách bằng dấu phẩy, chấm phẩy hoặc khoảng trắng
            import re
            parts = re.split(r"[,;\s]+", subnet.strip())
            target_subnets = [p for p in parts if "/" in p or is_valid_ipv4(p)]
        
        if not target_subnets:
            target_subnets = self.detect_active_subnets()

        subnets_str = ", ".join(target_subnets)
        logger.info(f"Bắt đầu quét đa dải mạng: {subnets_str}")
        if progress_callback:
            progress_callback(10, f"Đang quét dải: {subnets_str}...")

        devices: List[Device] = []

        if self.nmap_path:
            try:
                if progress_callback:
                    progress_callback(30, "Đang thực hiện quét Nmap đa dải...")
                devices = self._scan_with_nmap(target_subnets)
            except Exception as e:
                logger.warning(f"Quét Nmap thất bại ({e}), chuyển sang chế độ quét Native ARP...")
                devices = []

        if not devices:
            if progress_callback:
                progress_callback(40, "Đang quét bằng phương thức Native ARP + Ping...")
            for s in target_subnets:
                devices.extend(self._scan_with_arp_ping(s, progress_callback))

        # Hậu xử lý: định danh, gắn thông tin máy tính quản trị và gateway
        local_ip = self.current_interface.ip if self.current_interface else ""
        local_mac = self._get_local_mac()

        if progress_callback:
            progress_callback(85, "Đang định danh thiết bị...")

        # Loại bỏ trùng lặp nếu có
        seen_ips = set()
        unique_devices: List[Device] = []

        for dev in devices:
            if dev.ip in seen_ips:
                continue
            seen_ips.add(dev.ip)

            # Máy cục bộ (localhost)
            if dev.ip == local_ip:
                if local_mac:
                    dev.mac = local_mac
                if not dev.custom_name:
                    dev.custom_name = "Máy tính Quản trị (Máy này)"

            # Kiểm tra Gateway
            is_local_gw = (dev.ip == (self.current_interface.gateway if self.current_interface else ""))
            is_main_modem = (dev.ip in ("192.168.1.1", "192.168.0.1") and not is_local_gw)

            if is_local_gw:
                if not dev.custom_name:
                    dev.custom_name = "Router Wi-Fi Phụ (Cục bộ)"
            elif is_main_modem:
                if not dev.custom_name:
                    dev.custom_name = "Modem / Wi-Fi Tổng (GPON ONT)"
                if dev.vendor == "Unknown":
                    dev.vendor = "ISP Modem"

            vendor, dev_type = DeviceIdentifier.classify_device(
                dev.ip, dev.mac, dev.hostname, dev.vendor, is_gateway=(is_local_gw or is_main_modem)
            )
            dev.vendor = vendor
            dev.device_type = dev_type

            # Tự động gán thông tin Mạng kết nối và Cách thức kết nối Internet
            from core.topology import NetworkTopologyHelper
            net_info = NetworkTopologyHelper.get_network_info(dev.ip)
            dev.network_name = net_info["network_name"]
            dev.connection_type = NetworkTopologyHelper.infer_connection_type(
                ip=dev.ip,
                mac=dev.mac,
                device_type=dev_type,
                vendor=vendor,
                is_local_pc=(dev.ip == local_ip)
            )

            unique_devices.append(dev)

        if progress_callback:
            progress_callback(100, f"Hoàn tất. Phát hiện {len(unique_devices)} thiết bị trên các mạng.")

        logger.info(f"Hoàn thành quét đa mạng: tìm thấy {len(unique_devices)} thiết bị.")
        return unique_devices

    def _scan_with_nmap(self, subnets: List[str]) -> List[Device]:
        """Quét đồng thời nhiều subnet bằng Nmap XML."""
        cmd = [self.nmap_path, "-sn", "-n"] + subnets + ["-oX", "-"]
        code, stdout, stderr = run_cmd(cmd, timeout=60)
        
        if code != 0 or not stdout.strip():
            raise RuntimeError(f"Nmap error (code {code}): {stderr}")

        devices: List[Device] = []
        try:
            root = ET.fromstring(stdout)
            for host in root.findall("host"):
                status = host.find("status")
                if status is None or status.get("state") != "up":
                    continue

                ip = ""
                mac = ""
                vendor = "Unknown"
                hostname = ""
                latency = 0.0

                for addr in host.findall("address"):
                    addr_type = addr.get("addrtype")
                    if addr_type == "ipv4":
                        ip = addr.get("addr", "")
                    elif addr_type == "mac":
                        mac = normalize_mac(addr.get("addr", ""))
                        vendor = addr.get("vendor", "Unknown")

                # Với các host được định tuyến từ subnet khác (không có Layer 2 ARP response)
                if ip and not mac:
                    mac = self._ip_to_pseudo_mac(ip)

                # Latency
                times = host.find("times")
                if times is not None and times.get("srtt"):
                    try:
                        latency = round(float(times.get("srtt")) / 1000.0, 2)
                    except ValueError:
                        latency = 0.0

                if ip and is_valid_ipv4(ip):
                    devices.append(Device(
                        ip=ip,
                        mac=mac,
                        hostname=hostname,
                        vendor=vendor,
                        latency_ms=latency,
                        status="ONLINE"
                    ))
        except ET.ParseError as e:
            logger.error(f"Lỗi parse XML từ Nmap: {e}")
            raise

        return devices

    def _ip_to_pseudo_mac(self, ip: str) -> str:
        """Tạo địa chỉ MAC hợp lệ (Locally Administered) cho thiết bị từ subnet khác."""
        try:
            octets = [int(x) for x in ip.split(".")]
            return f"02:00:{octets[0]:02X}:{octets[1]:02X}:{octets[2]:02X}:{octets[3]:02X}"
        except Exception:
            return "02:00:00:00:00:00"

    def _scan_with_arp_ping(
        self,
        subnet: str,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> List[Device]:
        devices: List[Device] = []
        try:
            network = ipaddress.IPv4Network(subnet, strict=False)
            hosts = [str(ip) for ip in network.hosts()]
        except Exception:
            hosts = []

        target_hosts = hosts[:254] if len(hosts) > 254 else hosts

        def do_ping(ip_str):
            ping_host(ip_str, timeout_ms=300)

        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            executor.map(do_ping, target_hosts)

        arp_entries = get_arp_table()
        for entry in arp_entries:
            ip = entry["ip"]
            mac = entry["mac"]
            is_up, latency = ping_host(ip, timeout_ms=400)
            if is_up:
                devices.append(Device(
                    ip=ip,
                    mac=mac,
                    latency_ms=latency,
                    status="ONLINE"
                ))

        return devices

    def _get_local_mac(self) -> str:
        ps_cmd = "Get-NetAdapter | Where-Object { $_.Status -eq 'Up' } | Select-Object -First 1 MacAddress | ConvertTo-Json"
        code, stdout, _ = run_cmd(["powershell", "-NoProfile", "-Command", ps_cmd], timeout=3)
        if code == 0 and "MacAddress" in stdout:
            import json
            try:
                data = json.loads(stdout)
                return normalize_mac(data.get("MacAddress", ""))
            except Exception:
                pass
        return ""

"""
Module phân tích cấu trúc mạng và lộ trình kết nối Internet (Network Topology & Internet Route Helper).
Hỗ trợ nhận diện mạng đang kết nối (Wi-Fi Tổng vs Router Phụ), phương thức kết nối vật lý (Wi-Fi vs LAN vs WAN),
và chuỗi các trạm trung chuyển (hops) từ thiết bị ra mạng Internet toàn cầu.
"""

from typing import Dict, List, Optional

class NetworkTopologyHelper:
    @staticmethod
    def get_network_info(ip: str, current_gateway: str = "192.168.110.1") -> Dict[str, str]:
        """
        Xác định thông tin dải mạng và gateway phụ trách thiết bị.
        Dựa trên quy hoạch địa chỉ IP mạng nội bộ.
        """
        parts = ip.split(".")
        if len(parts) != 4:
            return {
                "network_key": "other",
                "network_name": "Mạng Không Xác Định",
                "network_badge": "❓ Mạng Khác",
                "gateway_ip": current_gateway,
                "subnet_cidr": "Unknown",
                "is_primary": False,
                "is_secondary": False
            }

        prefix_24 = f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
        
        # Subnet 192.168.1.x hoặc 192.168.0.x (thường là Modem / Wi-Fi Tổng GPON của ISP)
        if parts[0] == "192" and parts[1] == "168" and parts[2] in ("1", "0"):
            gw = f"{parts[0]}.{parts[1]}.{parts[2]}.1"
            return {
                "network_key": "primary",
                "network_name": "Wi-Fi Tổng (Modem ISP)",
                "network_badge": "🌐 Wi-Fi Tổng",
                "gateway_ip": gw,
                "subnet_cidr": prefix_24,
                "is_primary": True,
                "is_secondary": False
            }
        
        # Subnet 192.168.110.x hoặc subnet cục bộ của máy tính quản trị
        if parts[0] == "192" and parts[1] == "168" and parts[2] == "110":
            return {
                "network_key": "secondary",
                "network_name": "Router Phụ (Ruijie / AP Tầng)",
                "network_badge": "📡 Router Phụ",
                "gateway_ip": "192.168.110.1",
                "subnet_cidr": prefix_24,
                "is_primary": False,
                "is_secondary": True
            }

        # Các dải mạng khác
        return {
            "network_key": "lan",
            "network_name": f"Mạng LAN ({prefix_24})",
            "network_badge": f"💻 LAN {parts[2]}.x",
            "gateway_ip": f"{parts[0]}.{parts[1]}.{parts[2]}.1",
            "subnet_cidr": prefix_24,
            "is_primary": False,
            "is_secondary": False
        }

    @staticmethod
    def infer_connection_type(
        ip: str,
        mac: str = "",
        device_type: str = "Unknown",
        vendor: str = "Unknown",
        is_local_pc: bool = False
    ) -> str:
        """
        Tự động phân loại phương thức kết nối mạng vật lý:
        - 'Wi-Fi': Thiết bị di động, IoT, Camera, Smart TV, Laptop không dây.
        - 'Ethernet': Máy tính bàn, Server, Máy in mạng, hoặc máy đang cắm cáp LAN.
        - 'WAN': Router/Modem gateway.
        """
        # Nếu là Router hoặc Gateway chính
        if ip in ("192.168.1.1", "192.168.0.1", "192.168.110.1") or device_type == "Router":
            return "WAN"

        # Nếu là máy tính cục bộ đang chạy chương trình này
        if is_local_pc:
            return "Ethernet"

        dev_type_lower = device_type.lower()
        vendor_lower = vendor.lower()

        # Điện thoại, tablet, smart home IoT, camera luôn dùng Wi-Fi
        if any(k in dev_type_lower for k in ["phone", "mobile", "iot", "camera", "tv"]):
            return "Wi-Fi"

        # Nhà sản xuất chip Wi-Fi / IoT đặc trưng
        if any(v in vendor_lower for v in ["espressif", "tuya", "apple", "samsung", "xiaomi"]):
            return "Wi-Fi"

        # Server, Máy in, hoặc thiết bị mạng chuyên dụng thường cắm cáp Ethernet
        if any(k in dev_type_lower for k in ["server", "printer"]):
            return "Ethernet"

        # PC/Laptop: Nếu dải 192.168.1.x của Wi-Fi tổng -> thường là thiết bị bắt Wi-Fi
        if ip.startswith("192.168.1."):
            return "Wi-Fi"

        return "Wi-Fi"

    @staticmethod
    def get_internet_route(
        ip: str,
        connection_type: str = "Wi-Fi",
        custom_name: str = "",
        blocked: bool = False
    ) -> List[Dict[str, str]]:
        """
        Tính toán chuỗi các trạm (hops) dẫn truyền từ thiết bị ra Internet toàn cầu.
        """
        net_info = NetworkTopologyHelper.get_network_info(ip)
        route: List[Dict[str, str]] = []

        host_icon = "📱" if connection_type == "Wi-Fi" else ("🔌" if connection_type == "Ethernet" else "💻")
        route.append({
            "name": custom_name or ip,
            "role": "Thiết bị đầu cuối (Host)",
            "ip": ip,
            "medium": connection_type,
            "status": "BLOCKED" if blocked else "ACTIVE",
            "icon": host_icon
        })

        if blocked:
            route.append({
                "name": "Tường lửa / ACL Router",
                "role": "Chặn truy cập Internet",
                "ip": net_info["gateway_ip"],
                "medium": "Bị ngắt kết nối",
                "status": "BLOCKED",
                "icon": "⛔"
            })
            return route

        # 2. Nếu nằm ở dải Router Phụ (192.168.110.x)
        if net_info["is_secondary"]:
            route.append({
                "name": "Router Wi-Fi Phụ (Ruijie)",
                "role": "Gateway Cục bộ & Điểm phát Wi-Fi",
                "ip": "192.168.110.1",
                "medium": "Cáp LAN / Uplink WAN",
                "status": "ACTIVE",
                "icon": "📡"
            })
            route.append({
                "name": "Modem / Wi-Fi Tổng GPON",
                "role": "Modem Nhà mạng ISP (NAT Tổng)",
                "ip": "192.168.1.1",
                "medium": "Cáp quang GPON / AON",
                "status": "ACTIVE",
                "icon": "🌐"
            })
        elif net_info["is_primary"]:
            # Nằm trực tiếp trên Wi-Fi Tổng (192.168.1.x)
            if ip != "192.168.1.1":
                route.append({
                    "name": "Modem / Wi-Fi Tổng GPON",
                    "role": "Modem Nhà mạng ISP (Gateway Trực tiếp)",
                    "ip": "192.168.1.1",
                    "medium": "Cáp quang GPON / AON",
                    "status": "ACTIVE",
                    "icon": "🌐"
                })
        else:
            # Subnet khác
            route.append({
                "name": f"Gateway ({net_info['gateway_ip']})",
                "role": "Router Gateway",
                "ip": net_info["gateway_ip"],
                "medium": "Định tuyến IP",
                "status": "ACTIVE",
                "icon": "🔀"
            })

        # 3. Trạm cuối: Internet Toàn cầu
        route.append({
            "name": "Internet Toàn Cầu",
            "role": "Mạng Toàn Cầu (WAN)",
            "ip": "0.0.0.0/0",
            "medium": "ISP Trực tuyến",
            "status": "ACTIVE",
            "icon": "🌍"
        })

        return route

"""
Điểm khởi động ứng dụng Network Manager (Entry Point).
Hỗ trợ cả giao diện đồ họa PySide6 và chế độ quét dòng lệnh CLI.
"""

import sys
import argparse

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from gui.app import MainWindow
from services.discovery import NetworkDiscoveryService
from core.network import NetworkManagerCore
from core.logger import logger

def run_cli_scan(subnet=None):
    """Chế độ quét CLI nhanh qua dòng lệnh."""
    print("=" * 65)
    print("      NETWORK MANAGER - CÔNG CỤ QUÉT & GIÁM SÁT MẠNG CỤC BỘ")
    print("=" * 65)
    
    iface = NetworkManagerCore.get_default_interface()
    if iface:
        print(f"[*] Card mạng: {iface.alias}")
        print(f"[*] IP máy trạm: {iface.ip}")
        print(f"[*] Router Gateway: {iface.gateway}")
    
    from core.scanner import NetworkScanner
    scanner = NetworkScanner()
    detected_subnets = scanner.detect_active_subnets()
    target_subnets = subnet or (", ".join(detected_subnets))
    print(f"[*] Dải Subnet quét: {target_subnets}")
    print("-" * 65)
    print("[*] Đang thực hiện quét dải mạng (vui lòng chờ vài giây)...")

    service = NetworkDiscoveryService(scanner=scanner)
    devices = service.run_discovery(subnet=target_subnets)

    print(f"\n[+] Kết quả: Tìm thấy {len(devices)} thiết bị đang hoạt động:")
    print("-" * 65)
    print(f"{'IP Address':<16} {'MAC Address':<18} {'Trạng thái':<10} {'Loại':<10} {'Tên / Vendor'}")
    print("-" * 65)
    for dev in devices:
        name = dev.custom_name or dev.hostname or dev.vendor
        print(f"{dev.ip:<16} {dev.mac:<18} {dev.status:<10} {dev.device_type:<10} {name}")
    print("-" * 65)
    print("[+] Dữ liệu đã được cập nhật vào SQLite: data/network.db")

def main():
    parser = argparse.ArgumentParser(description="Network Manager - Quản lý và Giám sát Mạng Nội bộ")
    parser.add_argument("--cli", action="store_true", help="Chạy quét mạng ở chế độ dòng lệnh CLI")
    parser.add_argument("--subnet", type=str, help="Dải subnet tùy chỉnh (vd: 192.168.1.0/24 hoặc nhiều dải cách nhau bởi dấu phẩy)")
    args = parser.parse_args()

    if args.cli:
        run_cli_scan(subnet=args.subnet)
        return

    # Khởi động giao diện PySide6
    app = QApplication(sys.argv)
    app.setApplicationName("Network Manager")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("SecurityNetworkTools")

    # Áp dụng font chữ chuẩn hệ thống
    font = app.font()
    font.setFamily("Segoe UI")
    font.setPointSize(10)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()

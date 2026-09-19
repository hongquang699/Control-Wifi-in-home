"""
Script tự động đóng gói ứng dụng Network Manager thành file chạy độc lập (.exe trên Windows).
"""

import os
import sys
import shutil
import subprocess

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def build():
    # Đảm bảo thư mục làm việc luôn là thư mục gốc của dự án
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)

    print("=" * 60)
    print("   ĐANG ĐÓNG GÓI NETWORK MANAGER THÀNH WINDOWS EXECUTABLE")
    print("=" * 60)

    # 1. Đảm bảo các thư mục tồn tại
    os.makedirs("config", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)

    # 1.5 Đảm bảo tiến trình cũ đã đóng
    try:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/F", "/IM", "NetworkManager.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["taskkill", "/F", "/IM", "nmap.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

    # 2. Xóa các build cũ nếu có
    for folder in ["build", "dist"]:
        if os.path.exists(folder):
            print(f"[*] Dọn dẹp thư mục cũ: {folder}...")
            shutil.rmtree(folder, ignore_errors=True)

    # 3. Lệnh chạy PyInstaller
    # Sử dụng dấu chấm phẩy ';' làm data separator trên Windows
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=NetworkManager",
        "--windowed",                 # Không hiện cửa sổ console đen khi mở GUI
        "--onedir",                   # Tạo gói thư mục độc lập chạy ổn định nhất
        "--icon=assets/logo.ico",     # Biểu tượng ứng dụng chính thức
        "--add-data=config;config",   # Đính kèm thư mục cấu hình
        "--add-data=assets;assets",   # Đính kèm thư mục logo và assets
        "--hidden-import=PySide6",
        "--hidden-import=requests",
        "--hidden-import=psutil",
        "--hidden-import=security",
        "--hidden-import=services",
        "--hidden-import=core",
        "--hidden-import=database",
        "--hidden-import=router",
        "--clean",
        "-y",
        "main.py"
    ]

    print("[*] Thực thi PyInstaller:", " ".join(cmd))
    proc = subprocess.run(cmd)

    if proc.returncode != 0:
        print("[!] Đóng gói thất bại với mã lỗi:", proc.returncode)
        return False

    # 4. Sao chép thêm config và tạo thư mục data trong dist/NetworkManager
    dist_dir = os.path.join("dist", "NetworkManager")
    if os.path.exists(dist_dir):
        # Đảm bảo có thư mục config, assets và data bên cạnh file .exe
        target_config = os.path.join(dist_dir, "config")
        target_assets = os.path.join(dist_dir, "assets")
        target_data = os.path.join(dist_dir, "data", "logs")
        os.makedirs(target_config, exist_ok=True)
        os.makedirs(target_assets, exist_ok=True)
        os.makedirs(target_data, exist_ok=True)

        for cfg_file in ["config.json", "routers.json"]:
            src = os.path.join("config", cfg_file)
            dst = os.path.join(target_config, cfg_file)
            if os.path.exists(src):
                shutil.copy2(src, dst)

        if os.path.exists("assets"):
            shutil.copytree("assets", target_assets, dirs_exist_ok=True)

        db_src = os.path.join("data", "network.db")
        if os.path.exists(db_src):
            shutil.copy2(db_src, os.path.join(dist_dir, "data", "network.db"))

        # Sao chép file run.bat và README vào thư mục dist
        readme_src = "README.md" if os.path.exists("README.md") else os.path.join("..", "README.md")
        if os.path.exists(readme_src):
            shutil.copy2(readme_src, os.path.join(dist_dir, "README.md"))
        if os.path.exists("run.bat"):
            shutil.copy2("run.bat", os.path.join(dist_dir, "run.bat"))

        print("\n" + "=" * 60)
        print("[+] ĐÓNG GÓI THÀNH CÔNG!")
        print(f"[+] Ứng dụng đã sẵn sàng tại: {os.path.abspath(dist_dir)}")
        print(f"[+] File thực thi: {os.path.abspath(os.path.join(dist_dir, 'NetworkManager.exe'))}")
        print("=" * 60)
        return True
    else:
        print("[!] Không tìm thấy thư mục đầu ra:", dist_dir)
        return False

if __name__ == "__main__":
    success = build()
    sys.exit(0 if success else 1)

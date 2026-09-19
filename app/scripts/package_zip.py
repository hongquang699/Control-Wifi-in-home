import os
import sys
import zipfile
import hashlib

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def package():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    dist_dir = os.path.join(base_dir, "app", "dist", "NetworkManager")
    out_zip = os.path.join(base_dir, "web", "downloads", "windows", "NetworkManager-v1.0.0-windows-x64.zip")
    
    if not os.path.exists(dist_dir):
        print("[!] Không tìm thấy thư mục build:", dist_dir)
        return False
        
    os.makedirs(os.path.dirname(out_zip), exist_ok=True)
    print(f"[*] Đang nén {dist_dir} -> {out_zip}...")
    
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(dist_dir):
            for f in files:
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, os.path.dirname(dist_dir))
                zf.write(full_path, rel_path)
                
    size_mb = os.path.getsize(out_zip) / (1024 * 1024)
    hasher = hashlib.sha256()
    with open(out_zip, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    sha256 = hasher.hexdigest()
    
    print(f"[+] Hoàn tất! Kích thước: {size_mb:.1f} MB")
    print(f"[+] SHA256: {sha256}")
    return sha256

if __name__ == "__main__":
    package()

"""
Dịch vụ kiểm tra và cập nhật phiên bản ứng dụng tự động (Auto-Updater Service).
Kiểm tra bản phát hành mới nhất từ GitHub Repository hongquang699/Control-Wifi-in-home.
"""

import json
import urllib.request
import urllib.error
import re
from dataclasses import dataclass
from typing import Optional, Tuple
from core.logger import logger

CURRENT_VERSION = "2.0.0"
GITHUB_REPO = "hongquang699/Control-Wifi-in-home"
GITHUB_API_LATEST_RELEASE = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
GITHUB_REPO_URL = f"https://github.com/{GITHUB_REPO}"


@dataclass
class UpdateInfo:
    current_version: str
    latest_version: str
    is_update_available: bool
    release_name: str
    release_notes: str
    download_url: str
    published_at: str
    error_message: Optional[str] = None


def parse_version(ver_str: str) -> Tuple[int, ...]:
    """Phân tích chuỗi phiên bản (vd: 'v2.0.0', '2.1.0-beta') thành tuple số nguyên so sánh được."""
    if not ver_str:
        return (0, 0, 0)
    # Loại bỏ tiền tố 'v' hoặc 'ver'
    clean = re.sub(r"^[vV\s]+", "", ver_str.strip())
    # Lấy các nhóm số phân tách bởi dấu chấm
    parts = re.findall(r"\d+", clean)
    if not parts:
        return (0, 0, 0)
    return tuple(int(p) for p in parts[:3])


class UpdateChecker:
    """Bộ kiểm tra phiên bản mới từ GitHub Release."""

    def __init__(self, current_version: str = CURRENT_VERSION, repo: str = GITHUB_REPO):
        self.current_version = current_version
        self.repo = repo
        self.api_url = f"https://api.github.com/repos/{repo}/releases/latest"

    def check_for_updates(self, timeout: int = 4) -> UpdateInfo:
        """
        Gửi yêu cầu kiểm tra phiên bản mới qua GitHub REST API.
        An toàn, không làm crash ứng dụng khi mất kết nối mạng.
        """
        req = urllib.request.Request(
            self.api_url,
            headers={
                "User-Agent": f"NetworkManager-Updater/{self.current_version}",
                "Accept": "application/vnd.github.v3+json"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    tag_name = data.get("tag_name", "").strip()
                    latest_ver = tag_name.lstrip("vV") if tag_name else self.current_version
                    
                    cur_tuple = parse_version(self.current_version)
                    latest_tuple = parse_version(latest_ver)

                    is_newer = latest_tuple > cur_tuple
                    release_name = data.get("name") or f"Bản phát hành {tag_name}"
                    body = data.get("body", "Không có thông tin thay đổi chi tiết.").strip()
                    html_url = data.get("html_url") or f"https://github.com/{self.repo}/releases"
                    published = data.get("published_at", "")

                    return UpdateInfo(
                        current_version=self.current_version,
                        latest_version=latest_ver,
                        is_update_available=is_newer,
                        release_name=release_name,
                        release_notes=body,
                        download_url=html_url,
                        published_at=published,
                        error_message=None
                    )
        except urllib.error.HTTPError as e:
            if e.code == 404:
                # Chưa có release chính thức trên GitHub, người dùng đang ở bản mới nhất
                logger.info(f"[Updater] Không tìm thấy GitHub Release (404). Bản hiện tại {self.current_version} là mới nhất.")
                return UpdateInfo(
                    current_version=self.current_version,
                    latest_version=self.current_version,
                    is_update_available=False,
                    release_name=f"Network Manager v{self.current_version} Cyberpunk Edition",
                    release_notes="Hệ thống đang hoạt động ở bản dựng phát triển mới nhất.",
                    download_url=f"https://github.com/{self.repo}",
                    published_at="",
                    error_message=None
                )
            logger.warning(f"[Updater] GitHub API HTTP error: {e.code}")
            return self._fallback_offline(f"HTTP {e.code}")
        except Exception as e:
            logger.warning(f"[Updater] Không thể kết nối tới máy chủ cập nhật: {e}")
            return self._fallback_offline(str(e))

    def _fallback_offline(self, err_msg: str) -> UpdateInfo:
        return UpdateInfo(
            current_version=self.current_version,
            latest_version=self.current_version,
            is_update_available=False,
            release_name=f"Network Manager v{self.current_version}",
            release_notes="Không thể kết nối máy chủ kiểm tra cập nhật (Kiểm tra kết nối Internet).",
            download_url=f"https://github.com/{self.repo}",
            published_at="",
            error_message=err_msg
        )

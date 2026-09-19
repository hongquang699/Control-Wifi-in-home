@echo off
chcp 65001 >nul
title Network Manager (Launch Desktop App)
cd /d "%~dp0"

echo [*] Đang khởi chạy ứng dụng Network Manager từ thư mục app/...
if exist "app\run.bat" (
    call "app\run.bat" %*
) else (
    echo [ERROR] Không tìm thấy tệp app\run.bat!
    pause
)

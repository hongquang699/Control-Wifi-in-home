@echo off
chcp 65001 >nul
title Network Manager - Launch Website Server
cd /d "%~dp0"

echo [*] Đang khởi chạy hệ thống Web từ thư mục web/...
if exist "web\serve_website.bat" (
    call "web\serve_website.bat" %*
) else (
    echo [ERROR] Không tìm thấy tệp web\serve_website.bat!
    pause
)

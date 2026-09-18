@echo off
chcp 65001 >nul
title Network Manager - Quản lý & Giám sát Mạng Nội bộ
cd /d "%~dp0"

if exist "dist\NetworkManager\NetworkManager.exe" (
    echo [INFO] Đang khởi động ứng dụng NetworkManager.exe...
    start "" "dist\NetworkManager\NetworkManager.exe" %*
) else if exist "venv\Scripts\python.exe" (
    echo [INFO] Đang khởi động Network Manager từ virtualenv...
    start "" "venv\Scripts\pythonw.exe" main.py %*
) else (
    echo [INFO] Đang khởi động Network Manager bằng Python hệ thống...
    python main.py %*
)

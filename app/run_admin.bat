@echo off
chcp 65001 >nul
title Network Manager (Run as Administrator)
cd /d "%~dp0"

:: Kiểm tra xem đã có quyền Administrator chưa
net session >nul 2>&1
if %errorLevel% == 0 (
    goto :runApp
) else (
    echo ================================================================
    echo   YÊU CẦU QUYỀN QUẢN TRỊ VIÊN (ADMINISTRATOR)
    echo   Quyền Admin giúp Tường lửa (Firewall) và Nmap hoạt động tốt nhất.
    echo ================================================================
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

:runApp
cd /d "%~dp0"
if exist "dist\NetworkManager\NetworkManager.exe" (
    echo [INFO] Đang khởi động NetworkManager.exe với quyền Admin...
    start "" "dist\NetworkManager\NetworkManager.exe"
) else if exist "..\dist\NetworkManager\NetworkManager.exe" (
    echo [INFO] Đang khởi động NetworkManager.exe với quyền Admin...
    start "" "..\dist\NetworkManager\NetworkManager.exe"
) else if exist "venv\Scripts\python.exe" (
    echo [INFO] Đang khởi động qua Virtualenv với quyền Admin...
    start "" "venv\Scripts\pythonw.exe" main.py
) else if exist "..\venv\Scripts\python.exe" (
    echo [INFO] Đang khởi động qua Virtualenv gốc với quyền Admin...
    start "" "..\venv\Scripts\pythonw.exe" main.py
) else (
    echo [INFO] Đang khởi động qua Python hệ thống...
    start "" pythonw main.py
)
exit /b

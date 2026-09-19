@echo off
chcp 65001 > nul
title Network Manager - Web & REST API Server
cd /d "%~dp0"

echo =======================================================
echo   NETWORK MANAGER - MÁY CHỦ WEB & REST API
echo =======================================================
echo.

set PY_EXE=
if exist "..\venv\Scripts\python.exe" (
    set PY_EXE=..\venv\Scripts\python.exe
) else (
    where python >nul 2>&1
    if %errorlevel% equ 0 set PY_EXE=python
)

if not "%PY_EXE%"=="" (
    echo [OK] Đã tìm thấy Python (%PY_EXE%).
    echo [*] Khởi chạy máy chủ Web & REST API tại cổng 8080...
    echo [*] Đang mở trình duyệt web: http://localhost:8080
    start http://localhost:8080
    echo [*] Nhấn Ctrl+C để dừng máy chủ khi hoàn tất.
    echo.
    if exist "backend\main.py" (
        "%PY_EXE%" backend\main.py 8080
    ) else (
        "%PY_EXE%" -m http.server 8080
    )
) else (
    echo [!] Không tìm thấy Python trong môi trường.
    echo [*] Đang mở trực tiếp tệp html\index.html bằng trình duyệt mặc định...
    start "" "html\index.html"
)
pause

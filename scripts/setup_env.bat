@echo off
chcp 65001 >nul
title Setup Network Manager Environment
cd /d "%~dp0.."

echo ================================================================
echo    CÀI ĐẶT MÔI TRƯỜNG & THƯ VIỆN CHO NETWORK MANAGER
echo ================================================================

:: 1. Kiểm tra Python
where py >nul 2>&1
if %errorLevel% == 0 (
    set "PY_CMD=py -3.12"
) else (
    where python >nul 2>&1
    if %errorLevel% == 0 (
        set "PY_CMD=python"
    ) else (
        echo [LỖI] Không tìm thấy Python trên máy tính. Vui lòng cài đặt Python 3.12+ từ python.org!
        pause
        exit /b 1
    )
)

:: 2. Khởi tạo venv nếu chưa có
if not exist "venv\Scripts\python.exe" (
    echo [*] Đang tạo môi trường ảo (venv)...
    %PY_CMD% -m venv venv
)

:: 3. Cài đặt các gói phụ thuộc
echo [*] Đang cài đặt các thư viện cần thiết từ requirements.txt...
venv\Scripts\python.exe -m pip install -r requirements.txt
venv\Scripts\python.exe -m pip install pyinstaller

echo.
echo ================================================================
echo [THÀNH CÔNG] Môi trường đã sẵn sàng! 
echo Bạn có thể chạy "run.bat" để mở ứng dụng.
echo ================================================================
pause

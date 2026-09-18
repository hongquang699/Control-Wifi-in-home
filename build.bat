@echo off
chcp 65001 >nul
title Build Network Manager Windows Executable
cd /d "%~dp0"

echo ================================================================
echo    TIẾN HÀNH ĐÓNG GÓI NETWORK MANAGER THÀNH ỨNG DỤNG WINDOWS
echo ================================================================

if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe build_app.py
) else (
    python build_app.py
)

pause

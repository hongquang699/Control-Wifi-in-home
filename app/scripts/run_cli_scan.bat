@echo off
chcp 65001 >nul
title Network Manager - Quét Mạng CLI
cd /d "%~dp0.."

echo ================================================================
echo         NETWORK MANAGER - TIẾN HÀNH QUÉT MẠNG NHANH
echo ================================================================

if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe main.py --cli
) else (
    python main.py --cli
)

echo.
echo ================================================================
echo Quá trình quét hoàn tất. Nhấn phím bất kỳ để đóng cửa sổ.
pause >nul

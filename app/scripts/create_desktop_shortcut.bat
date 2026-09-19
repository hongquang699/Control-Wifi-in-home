@echo off
chcp 65001 >nul
title Tạo Shortcut Desktop cho Network Manager
cd /d "%~dp0.."

echo ================================================================
echo      ĐANG TẠO LỐI TẮT (SHORTCUT) RA MÀN HÌNH DESKTOP...
echo ================================================================

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0create_shortcut.ps1"

echo.
echo [HOÀN TẤT] Bạn có thể mở ứng dụng bằng biểu tượng "Network Manager" trên Desktop!
echo.
pause

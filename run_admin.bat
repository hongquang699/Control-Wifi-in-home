@echo off
chcp 65001 >nul
title Network Manager (Run App as Administrator)
cd /d "%~dp0"

if exist "app\run_admin.bat" (
    call "app\run_admin.bat" %*
) else (
    echo [ERROR] Không tìm thấy tệp app\run_admin.bat!
    pause
)

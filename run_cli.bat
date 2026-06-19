@echo off
title Ultimate Dork — CLI
cd /d "%~dp0"
echo.
echo Usage examples:
echo   python ultimate-dork.py --dork "inurl:.php?id="
echo   python ultimate-dork.py --dork "inurl:.php?id=" --scan
echo   python ultimate-dork.py --dork "inurl:.php?id=" --proxy 127.0.0.1:8080
echo   python ultimate-dork.py --help
echo.
set /p CMD=Enter your dork (or press Enter to show --help):
if "%CMD%"=="" (
    python ultimate-dork.py --help
) else (
    python ultimate-dork.py --dork "%CMD%"
)
echo.
pause

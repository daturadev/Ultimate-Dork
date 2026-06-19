@echo off
title Ultimate Dork — GUI
cd /d "%~dp0"
python gui.py
if errorlevel 1 (
    echo.
    echo [!] Error launching GUI. Have you run setup.bat yet?
    pause
)

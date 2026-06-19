@echo off
title Ultimate Dork — Setup
echo.
echo  ==========================================
echo   Ultimate Dork v2.0 — Windows Setup
echo  ==========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [!] Python not found. Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo [*] Python found:
python --version
echo.

:: Install pip deps
echo [*] Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [!] pip install failed. Check your internet connection.
    pause
    exit /b 1
)
echo.

:: Fetch camoufox Firefox binary (one-time download ~100 MB)
echo [*] Fetching camoufox Firefox binary (one-time download, ~100 MB)...
python -m camoufox fetch
if errorlevel 1 (
    echo [!] camoufox fetch failed. Try running manually:
    echo     python -m camoufox fetch
    pause
    exit /b 1
)
echo.

echo  ==========================================
echo   Setup complete!
echo   Run the GUI with:  python gui.py
echo   Run the CLI with:  python ultimate-dork.py --help
echo  ==========================================
echo.
pause

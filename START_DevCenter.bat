@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo        DevCenter starten
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] Python nicht gefunden!
    echo Bitte Python 3.10+ installieren.
    echo.
    pause
    exit /b 1
)

echo Starte Anwendung...
echo.
python main.py

if errorlevel 1 (
    echo.
    echo [FEHLER] Anwendung mit Fehler beendet.
    pause
)

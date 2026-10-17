@echo off
REM Update - Check for and install app updates

echo.
echo Impeccable Setup App Updater
echo ============================
echo.

REM Auto-apply pending update if exists
if exist "%~dp0apply_update.bat" (
    echo Applying pending update...
    call "%~dp0apply_update.bat"
    echo.
)

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found.
    goto :end
)

python "%~dp0update.py"

:end
echo.
echo Press any key to close...
pause >nul

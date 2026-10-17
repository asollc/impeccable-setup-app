@echo off
REM Auto-apply pending update if exists
if exist "%~dp0apply_update.bat" (
    echo Applying pending update...
    call "%~dp0apply_update.bat"
    echo.
)
REM Pack and Send - Zip website changes for Gigi to push live
REM Drag your project folder onto this file

echo.
echo Pack and Send to Gigi
echo =====================
echo.

if "%~1"=="" (
    echo Drag your project folder onto this window and press Enter,
    echo or type/paste the path:
    echo.
    set /p PROJECT_PATH="Project path: "
) else (
    set "PROJECT_PATH=%~1"
)

set "PROJECT_PATH=%PROJECT_PATH:"=%"

echo.
echo Project: %PROJECT_PATH%
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.6+ from https://python.org
    goto :end
)

REM Check for updates
echo Checking for updates...
python "%~dp0update.py"
echo.
REM Auto-apply if update was just staged
if exist "%~dp0apply_update.bat" (
    echo Applying staged update...
    call "%~dp0apply_update.bat"
    echo.
)

if not exist "%PROJECT_PATH%" (
    echo ERROR: Path does not exist: %PROJECT_PATH%
    goto :end
)

echo.
python "%~dp0send.py" "%PROJECT_PATH%"

:end
echo.
echo Press any key to close...
pause >nul

@echo off
REM Download a project and set up live mode
REM Usage: download.bat <url> [project-name]

echo.
echo Download Project and Setup
echo ==========================
echo.

if "%~1"=="" (
    echo Paste the project download URL:
    echo.
    set /p DOWNLOAD_URL="URL: "
    echo.
    set /p PROJECT_NAME="Project name (optional): "
) else (
    set "DOWNLOAD_URL=%~1"
    set "PROJECT_NAME=%~2"
)

set "DOWNLOAD_URL=%DOWNLOAD_URL:"=%"
set "PROJECT_NAME=%PROJECT_NAME:"=%"

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found.
    goto :end
)

REM Check for updates
echo Checking for updates...
python "%~dp0update.py"
echo.

if "%PROJECT_NAME%"=="" (
    python "%~dp0download.py" "%DOWNLOAD_URL%"
) else (
    python "%~dp0download.py" "%DOWNLOAD_URL%" "%PROJECT_NAME%"
)

:end
echo.
echo Press any key to close...
pause >nul

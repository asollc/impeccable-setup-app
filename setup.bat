@echo off
REM Impeccable Live Mode Setup - Windows Launcher
REM Drag a project folder or zip onto this file, or run it and paste the path

echo.
echo Impeccable Live Mode Setup
echo ==========================
echo.

if "%~1"=="" (
    echo Drag your project folder or zip file onto this window and press Enter,
    echo or type/paste the path:
    echo.
    set /p PROJECT_PATH="Project path: "
) else (
    set "PROJECT_PATH=%~1"
)

REM Remove surrounding quotes if present
set "PROJECT_PATH=%PROJECT_PATH:"=%"

echo.
echo Project: %PROJECT_PATH%
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.6+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation.
    goto :end
)

REM Check for updates
echo Checking for updates...
python "%~dp0update.py"
echo.

REM Check if the project path exists
if not exist "%PROJECT_PATH%" (
    echo ERROR: Path does not exist: %PROJECT_PATH%
    goto :end
)

echo Running setup...
echo.
python "%~dp0setup.py" "%PROJECT_PATH%"
if errorlevel 1 (
    echo.
    echo ERROR: Setup failed with exit code %errorlevel%
)

:end
echo.
echo Press any key to close...
pause >nul

@echo off
REM ============================================================
REM Paper Blogger - Installer Build Script
REM ============================================================
REM Requires: Inno Setup 6.x with ISCC.exe in PATH
REM   or installed at default location
REM ============================================================

setlocal

echo.
echo ========================================
echo  Paper Blogger Installer Build
echo ========================================
echo.

REM --- Locate ISCC.exe ---
where ISCC.exe >nul 2>&1
if %ERRORLEVEL%==0 (
    set "ISCC=ISCC.exe"
    goto :found
)

REM Check default Inno Setup 6 install locations
set "ISCC_CANDIDATE=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if exist "%ISCC_CANDIDATE%" (
    set "ISCC=%ISCC_CANDIDATE%"
    goto :found
)

set "ISCC_CANDIDATE=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if exist "%ISCC_CANDIDATE%" (
    set "ISCC=%ISCC_CANDIDATE%"
    goto :found
)

echo [ERROR] ISCC.exe not found.
echo.
echo Please install Inno Setup 6 from:
echo   https://jrsoftware.org/isdl.php
echo.
echo Or add ISCC.exe to your PATH.
pause
exit /b 1

:found
echo [INFO] Using: %ISCC%
echo.

REM --- Verify PyInstaller build exists ---
set "DIST_DIR=%LOCALAPPDATA%\paper_blogger_build\dist\paper_blogger"
if not exist "%DIST_DIR%\paper_blogger.exe" (
    echo [ERROR] PyInstaller build not found at:
    echo   %DIST_DIR%
    echo.
    echo Run pyinstaller\build.bat or pyinstaller\secure_build.bat first.
    pause
    exit /b 1
)

echo [INFO] PyInstaller dist found: %DIST_DIR%
echo.

REM --- Create output directory ---
if not exist "%~dp0output" mkdir "%~dp0output"

REM --- Build installer ---
echo [BUILD] Compiling installer...
echo.

"%ISCC%" "%~dp0paper_blogger_installer.iss"

if %ERRORLEVEL%==0 (
    echo.
    echo ========================================
    echo  BUILD SUCCESSFUL
    echo ========================================
    echo.
    echo Installer: %~dp0output\setup_paper_blogger.exe
    echo.
    explorer "%~dp0output"
) else (
    echo.
    echo [ERROR] Build failed with error code %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)

pause

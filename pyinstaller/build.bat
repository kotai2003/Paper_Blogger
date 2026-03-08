@echo off
chcp 65001 >nul 2>&1
echo ============================================
echo  Paper Blogger - PyInstaller Build
echo ============================================
echo.

cd /d "%~dp0"

REM PyInstaller がインストールされているか確認
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] PyInstaller が見つかりません
    echo   pip install pyinstaller
    pause
    exit /b 1
)

REM OneDrive ロック回避: ビルド出力をローカルフォルダに配置
set "BUILD_OUT=%LOCALAPPDATA%\paper_blogger_build"

echo [1/4] 既存プロセスの終了...
taskkill /F /IM paper_blogger.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo [2/4] クリーンアップ...
if exist "%BUILD_OUT%\dist" rd /s /q "%BUILD_OUT%\dist" >nul 2>&1
if exist "%BUILD_OUT%\build" rd /s /q "%BUILD_OUT%\build" >nul 2>&1
if not exist "%BUILD_OUT%" mkdir "%BUILD_OUT%"

echo [3/4] ビルド開始...
echo   出力先: %BUILD_OUT%\dist\paper_blogger\
python -m PyInstaller paper_blogger.spec --clean --noconfirm --distpath "%BUILD_OUT%\dist" --workpath "%BUILD_OUT%\build"

if errorlevel 1 (
    echo.
    echo [ERROR] ビルドに失敗しました
    pause
    exit /b 1
)

echo [4/4] ビルド完了
echo.
echo ============================================
echo  出力先: %BUILD_OUT%\dist\paper_blogger\
echo  実行:   paper_blogger.exe
echo ============================================
echo.

REM 出力フォルダを開く
explorer "%BUILD_OUT%\dist\paper_blogger"

pause

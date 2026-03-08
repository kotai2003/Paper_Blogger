@echo off
chcp 65001 >nul 2>&1
echo ============================================
echo  Paper Blogger - Secure Build
echo  Cython + PyInstaller
echo ============================================
echo.

cd /d "%~dp0\.."

REM --- 前提チェック ---
python -c "import Cython" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Cython が見つかりません
    echo   pip install cython
    pause
    exit /b 1
)

python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] PyInstaller が見つかりません
    echo   pip install pyinstaller
    pause
    exit /b 1
)

REM --- ビルド出力先（OneDrive ロック回避） ---
set "BUILD_OUT=%LOCALAPPDATA%\paper_blogger_build"

echo [1/5] 既存プロセスの終了...
taskkill /F /IM paper_blogger.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo [2/5] 前回の .pyd / build 成果物をクリーンアップ...
if exist "%BUILD_OUT%\dist" rd /s /q "%BUILD_OUT%\dist" >nul 2>&1
if exist "%BUILD_OUT%\build" rd /s /q "%BUILD_OUT%\build" >nul 2>&1
if not exist "%BUILD_OUT%" mkdir "%BUILD_OUT%"
REM Cython の build ディレクトリ削除
if exist build rd /s /q build >nul 2>&1
REM 既存 .pyd を削除（再コンパイル用）
for /R %%f in (*.pyd) do (
    echo   [DEL] %%f
    del /f "%%f" >nul 2>&1
)

echo.
echo [3/5] Cython コンパイル (.py → .pyd)...
echo ============================================
python build_tools/setup_cython.py build_ext --inplace

if errorlevel 1 (
    echo.
    echo [ERROR] Cython コンパイルに失敗しました
    pause
    exit /b 1
)

REM Cython build ディレクトリ削除
if exist build rd /s /q build >nul 2>&1

echo.
echo [4/5] PyInstaller ビルド...
echo ============================================
cd /d "%~dp0"
python -m PyInstaller secure_gui.spec --clean --noconfirm --distpath "%BUILD_OUT%\dist" --workpath "%BUILD_OUT%\build"

if errorlevel 1 (
    echo.
    echo [ERROR] PyInstaller ビルドに失敗しました
    pause
    exit /b 1
)

echo.
echo [5/5] コンパイル済み .pyd をソースから削除...
cd /d "%~dp0\.."
for /R %%f in (*.pyd) do (
    echo   [DEL] %%f
    del /f "%%f" >nul 2>&1
)

echo.
echo ============================================
echo  Secure Build Complete
echo ============================================
echo.
echo  出力先: %BUILD_OUT%\dist\paper_blogger\
echo.
echo  保護レイヤー:
echo    [OK] Cython .pyd (ネイティブバイナリ)
echo    [OK] optimize=2 (docstring/assert削除)
echo    [OK] UPX圧縮
echo    [OK] console=False
echo    [OK] ソースコード .py は配布物に含まれません
echo.

explorer "%BUILD_OUT%\dist\paper_blogger"

pause

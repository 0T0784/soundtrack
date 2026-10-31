
@echo off
chcp 65001 > nul

cd /d "%~dp0"

echo ==========================
echo Python Script Launcher
echo ==========================
echo.

python make_tracks.py

set "RESULT=%ERRORLEVEL%"

echo.
echo ==========================

if %RESULT% EQU 0 (
    echo [SUCCESS] 正常に終了しました。
) else (
    echo [ERROR] エラーが発生しました。
    echo 終了コード: %RESULT%
)

echo ==========================
echo.
pause

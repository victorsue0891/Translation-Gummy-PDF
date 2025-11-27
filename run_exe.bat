@echo off
chcp 65001 >nul
echo ==========================================
echo PDF 翻譯工具 - EXE 測試
echo ==========================================
echo.

if not exist "dist\PDF翻譯工具.exe" (
    echo [錯誤] 找不到 EXE 檔案
    echo 請先執行 build_exe.bat 進行編譯
    echo.
    pause
    exit /b 1
)

echo 檔案資訊：
dir "dist\PDF翻譯工具.exe" | findstr "PDF翻譯工具"
echo.

echo [啟動] 正在執行 PDF翻譯工具.exe ...
echo 請稍候，首次啟動可能需要 10-20 秒
echo.

start "" "dist\PDF翻譯工具.exe"

echo.
echo ✓ 已啟動 EXE 程式
echo.
echo 如果視窗沒有出現，請檢查：
echo 1. 防毒軟體是否阻擋
echo 2. 防火牆設定
echo 3. 系統相容性（需要 Windows 10/11）
echo.

pause

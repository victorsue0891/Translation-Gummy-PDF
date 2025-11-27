@echo off
chcp 65001 >nul
echo ==========================================
echo PDF 翻譯工具 - GUI 版本
echo ==========================================
echo.
echo 正在啟動...
echo.

python pdf_translator_gui.py

if %errorlevel% neq 0 (
    echo.
    echo [錯誤] 程式執行失敗
    echo.
    echo 請確認：
    echo 1. 已安裝 Python 3.x
    echo 2. 已安裝必要套件：
    echo    pip install PyMuPDF googletrans==3.1.0a0
    echo.
    pause
)

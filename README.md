# PDF Translator CLI

一個強大的PDF翻譯命令行工具，可以將PDF文件翻譯成多種語言，同時完整保留原始的圖片、排版和格式。

## 功能特點

✅ **保留原始格式** - 完整保留PDF的所有圖片、排版和視覺元素  
✅ **多語言支持** - 支持Google Translate的所有語言  
✅ **雙翻譯引擎** - 可選擇 Google Translate 或 Ollama LLM (Gemma2:9b)  
✅ **靈活的頁面選擇** - 可以翻譯整個文檔或指定頁面範圍  
✅ **進度追蹤** - 提供詳細的進度信息（可選）  
✅ **批量處理** - 適合處理大型PDF文檔

## 系統需求

- **Python 版本**: 3.10, 3.11, 或 3.12
  - ⚠️ **不支援 Python 3.13+**（因為 `googletrans==3.1.0a0` 依賴的 `httpx` 需要已被移除的 `cgi` 模組）

- **翻譯引擎** (擇一):
  - **Google Translate** (預設): 需要網路連線
  - **Ollama LLM**: 需要本機安裝並執行 Ollama，並下載 Gemma2:9b 模型
    ```bash
    # 安裝 Ollama: https://ollama.ai
    # 下載模型
    ollama pull gemma2:9b
    # 啟動 Ollama
    ollama serve
    ```

## 安裝依賴

### 方法 1：使用 uv（推薦）

```bash
# 安裝 uv（如果尚未安裝）
pip install uv

# 同步專案依賴
uv sync
```

### 方法 2：使用 pip

```bash
pip install PyMuPDF googletrans==3.1.0a0 requests
```

## 使用方法

### 基本用法

#### 使用 uv（推薦）
```bash
uv run pdf_translator.py input.pdf output.pdf
```

#### 使用 python
```bash
python pdf_translator.py input.pdf output.pdf
```

### 進階用法

#### 1. 翻譯為簡體中文
```bash
# 使用 uv
uv run pdf_translator.py input.pdf output.pdf --lang zh-CN

# 或使用 python
python pdf_translator.py input.pdf output.pdf --lang zh-CN
```

#### 2. 翻譯為其他語言
```bash
# 日文
uv run pdf_translator.py input.pdf output.pdf --lang ja

# 韓文
uv run pdf_translator.py input.pdf output.pdf --lang ko

# 法文
uv run pdf_translator.py input.pdf output.pdf --lang fr
```

#### 3. 只翻譯指定頁面
```bash
# 翻譯第1-10頁
uv run pdf_translator.py input.pdf output.pdf --pages "1-10"

# 翻譯多個不連續的頁面範圍
uv run pdf_translator.py input.pdf output.pdf --pages "1-10,15,20-25,50-60"
```

#### 4. 啟用詳細輸出
```bash
uv run pdf_translator.py input.pdf output.pdf -v
# 或
uv run pdf_translator.py input.pdf output.pdf --verbose
```

#### 5. 使用 Ollama 翻譯（本機 LLM）
```bash
# 確保 Ollama 已啟動：ollama serve
# 並且已下載模型：ollama pull gemma2:9b

uv run pdf_translator.py input.pdf output.pdf --engine ollama

# 結合其他選項
uv run pdf_translator.py input.pdf output.pdf --engine ollama --lang zh-CN -v
```

## 命令行參數

| 參數 | 簡寫 | 說明 | 預設值 |
|------|------|------|--------|
| `input` | - | 輸入PDF文件路徑 | 必需 |
| `output` | - | 輸出PDF文件路徑 | 必需 |
| `--lang` | `-l` | 目標語言代碼 | zh-TW |
| `--pages` | `-p` | 要翻譯的頁面範圍 | 全部頁面 |
| `--engine` | `-e` | 翻譯引擎：`google` 或 `ollama` | google |
| `--verbose` | `-v` | 顯示詳細輸出 | 關閉 |
| `--version` | - | 顯示版本信息 | - |
| `--help` | `-h` | 顯示幫助信息 | - |

## 支持的語言代碼

常用語言代碼：
- `zh-TW` - 繁體中文
- `zh-CN` - 簡體中文
- `en` - 英文
- `ja` - 日文
- `ko` - 韓文
- `fr` - 法文
- `de` - 德文
- `es` - 西班牙文
- `pt` - 葡萄牙文
- `ru` - 俄文

更多語言代碼請參考 [Google Translate 語言列表](https://cloud.google.com/translate/docs/languages)

## 使用範例

### 範例 1：翻譯英文電子書為繁體中文
```bash
# 使用 uv
uv run pdf_translator.py "The_Pathless_Path.pdf" "The_Pathless_Path(zh-TW).pdf"

# 或使用 python
python pdf_translator.py "The_Pathless_Path.pdf" "The_Pathless_Path(zh-TW).pdf"
```

### 範例 2：翻譯學術論文的前20頁
```bash
uv run pdf_translator.py "research_paper.pdf" "research_paper_zh.pdf" --pages "1-20" -v
```

### 範例 3：翻譯特定章節
```bash
# 假設第3-5章在第30-80頁
uv run pdf_translator.py "textbook.pdf" "textbook_chapter3-5.pdf" --pages "30-80"
```

## 處理時間估算

翻譯速度取決於：
- PDF的頁數和文字密度
- 網路連線速度
- Google Translate API 的回應時間

大致估算：
- 小型PDF（50頁）：約10-15分鐘
- 中型PDF（100頁）：約20-30分鐘
- 大型PDF（200頁）：約40-60分鐘

## 注意事項

1. **網路連線**：需要穩定的網路連線以訪問Google Translate API
2. **API限制**：Google Translate可能有使用限制，大量翻譯時請注意
3. **字體顯示**：使用內建CJK字體，中文顯示效果良好
4. **文件大小**：翻譯後的PDF文件可能會增大（約2-3倍）
5. **備份原檔**：建議先備份原始PDF文件

## 測試

執行測試套件：
```bash
python test_cli.py
```

## 技術細節

- **PDF處理**：使用 PyMuPDF (fitz) 進行PDF讀取和修改
- **翻譯引擎**：使用 Google Translate API (googletrans)
- **字體支持**：使用內建CJK字體（china-ss, china-s, cjk）
- **文字處理**：通過redact覆蓋原文，再插入翻譯文字

## 限制

- 某些特殊PDF格式可能無法完美處理
- 圖片中的文字無法翻譯（僅翻譯可提取的文字）
- 複雜的排版可能需要手動調整

## 版本歷史

### v1.0 (2024-11-26)
- 初始版本發布
- 支持多語言翻譯
- 支持頁面範圍選擇
- 完整保留圖片和排版

## 授權

MIT License

## 貢獻

歡迎提交Issue和Pull Request！

## 常見問題

**Q: 為什麼翻譯後的PDF變大了？**  
A: 因為嵌入了中文字體數據，這是確保中文正確顯示所必需的。

**Q: 可以離線使用嗎？**  
A: 可以！使用 Ollama 引擎可以完全離線翻譯：
```bash
uv run python pdf_translator.py input.pdf output.pdf -l zh-TW -e ollama
```

**Q: 支持掃描版PDF嗎？**  
A: 不支持。本工具只能翻譯可提取的文字，掃描版PDF需先進行OCR處理。

**Q: 翻譯質量如何？**  
A: 
- Google Translate：快速、穩定，適合一般翻譯
- Ollama LLM：更自然、可自訂，但速度較慢

**Q: 有 GUI 圖形介面版本嗎？**  
A: 有！請參考 `README_GUI.md` 或執行 `run_gui.bat`

**Q: 可以編譯成獨立的 EXE 檔案嗎？**  
A: 可以！執行 `build_exe.bat` 即可編譯 GUI 版本成 EXE，詳見 `EXE_使用說明.md`

## 相關文件

- **GUI 版本使用說明**: `README_GUI.md`
- **EXE 版本使用說明**: `EXE_使用說明.md`
- **翻譯引擎比較**: `TRANSLATION_ENGINES.md`
- **專案完整指南**: `FULL_PROJECT_GUIDE.md`
- **專案摘要**: `PROJECT_SUMMARY.md`

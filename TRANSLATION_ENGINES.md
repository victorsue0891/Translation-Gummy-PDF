# 翻譯引擎使用說明

PDF 翻譯工具現在支援兩種翻譯引擎，您可以根據需求選擇：

## 🌐 Google Translate (預設)

### 優點
- ✅ 無需安裝額外軟體
- ✅ 翻譯質量穩定
- ✅ 支援多種語言
- ✅ 使用簡單

### 缺點
- ❌ 需要網路連線
- ❌ 可能有 API 使用限制
- ❌ 翻譯速度較慢 (每段延遲 0.5 秒)

### 使用方法

#### CLI
```bash
# 預設使用 Google Translate
uv run pdf_translator.py input.pdf output.pdf

# 或明確指定
uv run pdf_translator.py input.pdf output.pdf --engine google
```

#### GUI
1. 啟動 GUI 程式
2. 在「翻譯引擎」下拉選單選擇 "google (Google Translate)"
3. 其他步驟照常進行

---

## 🤖 Ollama LLM (本機 AI)

使用本機運行的大型語言模型 (Gemma2:9b) 進行翻譯。

### 優點
- ✅ 離線可用（不需網路）
- ✅ 無 API 限制
- ✅ 隱私保護（數據不外傳）
- ✅ 翻譯速度較快 (每段延遲 0.1 秒)
- ✅ 可能有更好的上下文理解

### 缺點
- ❌ 需要安裝 Ollama
- ❌ 需要下載大型模型（約 5GB）
- ❌ 需要較好的硬體配置
- ❌ 首次生成較慢（模型載入）

### 系統需求
- **RAM**: 建議 16GB 以上
- **儲存空間**: 至少 10GB 可用空間
- **CPU/GPU**: 較新的處理器或支援的顯卡

### 安裝步驟

#### 1. 安裝 Ollama
訪問 https://ollama.ai 下載並安裝適合您作業系統的版本

**Windows**: 下載 `.exe` 安裝程式並執行

**macOS**: 
```bash
brew install ollama
```

**Linux**:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### 2. 下載模型
```bash
ollama pull gemma2:9b
```

這將下載約 5GB 的模型文件，請確保網路連線穩定。

#### 3. 啟動 Ollama 服務
```bash
ollama serve
```

保持此終端視窗開啟，Ollama 將在背景運行。

### 使用方法

#### CLI
```bash
# 確保 Ollama 已啟動
ollama serve  # 在另一個終端

# 使用 Ollama 翻譯
uv run pdf_translator.py input.pdf output.pdf --engine ollama

# 結合其他選項
uv run pdf_translator.py input.pdf output.pdf --engine ollama --lang zh-CN -v
```

#### GUI
1. 啟動 Ollama: `ollama serve`
2. 啟動 GUI 程式
3. 在「翻譯引擎」下拉選單選擇 "ollama (Ollama LLM - Gemma2:9b)"
4. 其他步驟照常進行

---

## 📊 效能比較

| 特性 | Google Translate | Ollama LLM |
|------|-----------------|------------|
| 網路需求 | 必需 | 不需要 |
| 安裝難度 | 簡單 | 中等 |
| 翻譯速度 | 中等 (0.5s/段) | 快速 (0.1s/段) |
| 翻譯質量 | 穩定 | 良好 |
| 硬體需求 | 低 | 中高 |
| 隱私性 | 數據外傳 | 完全本地 |
| 使用限制 | 可能有 | 無 |
| 成本 | 免費但有限制 | 免費無限制 |

## 🔧 疑難排解

### Google Translate 問題

**問題**: 顯示 "googletrans not installed"
```bash
# 解決方法
pip install googletrans==3.1.0a0
# 或
uv sync
```

**問題**: 翻譯失敗或速度很慢
- 檢查網路連線
- 可能遇到 API 限制，稍後再試
- 考慮使用 Ollama 引擎

### Ollama 問題

**問題**: "Cannot connect to Ollama"
```bash
# 確認 Ollama 是否運行
ollama list

# 如果沒有運行，啟動它
ollama serve
```

**問題**: "Model not found"
```bash
# 下載模型
ollama pull gemma2:9b

# 確認模型已安裝
ollama list
```

**問題**: 翻譯很慢或記憶體不足
- 確認系統有足夠 RAM (建議 16GB+)
- 關閉其他佔用記憶體的程式
- 考慮使用較小的模型或 Google Translate

## 💡 建議

### 何時使用 Google Translate
- 偶爾翻譯小型文件
- 不介意網路連線
- 硬體配置較低
- 快速上手

### 何時使用 Ollama
- 經常翻譯大量文件
- 需要離線工作
- 重視隱私
- 有足夠的硬體資源
- 願意投入時間設置

---

## 📞 支援

如有問題或建議，請在 GitHub Issues 中回報。

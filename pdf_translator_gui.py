# -*- coding: utf-8 -*-
"""
PDF翻譯工具 - Windows GUI版本
支持文件選擇、進度顯示和即時翻譯
"""

import fitz
import os
import time
import shutil
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

class PDFTranslatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF 翻譯工具 - GUI 版本")
        self.root.geometry("700x720")
        self.root.resizable(False, False)
        
        # 設置視窗圖示（如果有的話）
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        self.translator = None
        self.is_translating = False
        self.input_file = None
        self.output_file = None
        self.engine = 'google'  # 'google' or 'ollama'
        self.ollama_model = None  # 將在 setup_translator 時自動檢測
        
        self.setup_ui()
        self.setup_translator()
    
    def setup_ui(self):
        """建立使用者介面"""
        # 標題區域
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="📄 PDF 翻譯工具",
            font=("Microsoft JhengHei", 20, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=15)
        
        # 主要內容區域
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 輸入檔案選擇
        input_frame = tk.LabelFrame(
            main_frame,
            text="1. 選擇輸入檔案",
            font=("Microsoft JhengHei", 10, "bold"),
            padx=10,
            pady=10
        )
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.input_path_var = tk.StringVar()
        input_entry = tk.Entry(
            input_frame,
            textvariable=self.input_path_var,
            font=("Consolas", 9),
            state="readonly"
        )
        input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        input_btn = tk.Button(
            input_frame,
            text="瀏覽...",
            command=self.select_input_file,
            font=("Microsoft JhengHei", 9),
            width=10,
            bg="#3498db",
            fg="white",
            cursor="hand2"
        )
        input_btn.pack(side=tk.RIGHT)
        
        # 輸出檔案選擇
        output_frame = tk.LabelFrame(
            main_frame,
            text="2. 選擇輸出位置",
            font=("Microsoft JhengHei", 10, "bold"),
            padx=10,
            pady=10
        )
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.output_path_var = tk.StringVar()
        output_entry = tk.Entry(
            output_frame,
            textvariable=self.output_path_var,
            font=("Consolas", 9),
            state="readonly"
        )
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        output_btn = tk.Button(
            output_frame,
            text="瀏覽...",
            command=self.select_output_file,
            font=("Microsoft JhengHei", 9),
            width=10,
            bg="#3498db",
            fg="white",
            cursor="hand2"
        )
        output_btn.pack(side=tk.RIGHT)
        
        # 選項設定
        options_frame = tk.LabelFrame(
            main_frame,
            text="3. 翻譯設定",
            font=("Microsoft JhengHei", 10, "bold"),
            padx=10,
            pady=10
        )
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 語言選擇
        lang_frame = tk.Frame(options_frame)
        lang_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            lang_frame,
            text="目標語言：",
            font=("Microsoft JhengHei", 9)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.lang_var = tk.StringVar(value="zh-TW")
        lang_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.lang_var,
            values=["zh-TW (繁體中文)", "zh-CN (簡體中文)", "en (English)", "ja (日本語)", "ko (한국어)"],
            state="readonly",
            width=30,
            font=("Microsoft JhengHei", 9)
        )
        lang_combo.pack(side=tk.LEFT)
        lang_combo.current(0)
        
        # 翻譯引擎選擇
        engine_frame = tk.Frame(options_frame)
        engine_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            engine_frame,
            text="翻譯引擎：",
            font=("Microsoft JhengHei", 9)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.engine_var = tk.StringVar(value="google")
        self.engine_combo = ttk.Combobox(
            engine_frame,
            textvariable=self.engine_var,
            values=["google (Google Translate)", "ollama (Ollama LLM)"],
            state="readonly",
            width=30,
            font=("Microsoft JhengHei", 9)
        )
        self.engine_combo.pack(side=tk.LEFT)
        self.engine_combo.current(0)
        self.engine_combo.bind('<<ComboboxSelected>>', self.on_engine_changed)
        
        # Ollama 模型選擇（初始隱藏）
        self.ollama_model_frame = tk.Frame(options_frame)
        
        tk.Label(
            self.ollama_model_frame,
            text="Ollama 模型：",
            font=("Microsoft JhengHei", 9)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.ollama_model_var = tk.StringVar()
        self.ollama_model_combo = ttk.Combobox(
            self.ollama_model_frame,
            textvariable=self.ollama_model_var,
            state="readonly",
            width=30,
            font=("Microsoft JhengHei", 9)
        )
        self.ollama_model_combo.pack(side=tk.LEFT, padx=(0, 5))
        
        # 重新整理按鈕
        self.refresh_models_btn = tk.Button(
            self.ollama_model_frame,
            text="🔄",
            command=self.refresh_ollama_models,
            font=("Microsoft JhengHei", 9),
            width=3,
            cursor="hand2"
        )
        self.refresh_models_btn.pack(side=tk.LEFT)
        
        # 頁面範圍
        pages_frame = tk.Frame(options_frame)
        pages_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            pages_frame,
            text="頁面範圍：",
            font=("Microsoft JhengHei", 9)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.pages_var = tk.StringVar()
        pages_entry = tk.Entry(
            pages_frame,
            textvariable=self.pages_var,
            font=("Consolas", 9),
            width=32
        )
        pages_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Label(
            pages_frame,
            text="(留空=全部，例：1-10,15,20-25)",
            font=("Microsoft JhengHei", 8),
            fg="gray"
        ).pack(side=tk.LEFT)
        
        # 進度顯示區域
        progress_frame = tk.LabelFrame(
            main_frame,
            text="4. 翻譯進度",
            font=("Microsoft JhengHei", 10, "bold"),
            padx=10,
            pady=10
        )
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 狀態文字
        self.status_var = tk.StringVar(value="等待開始...")
        status_label = tk.Label(
            progress_frame,
            textvariable=self.status_var,
            font=("Microsoft JhengHei", 9),
            fg="#2c3e50"
        )
        status_label.pack(pady=(0, 10))
        
        # 進度條
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            length=600
        )
        self.progress_bar.pack(pady=(0, 10))
        
        # 詳細資訊顯示區域
        detail_frame = tk.Frame(progress_frame)
        detail_frame.pack(fill=tk.X)
        
        scrollbar = tk.Scrollbar(detail_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.detail_text = tk.Text(
            detail_frame,
            height=6,
            font=("Consolas", 8),
            yscrollcommand=scrollbar.set,
            state="disabled",
            bg="#f8f9fa",
            relief=tk.FLAT
        )
        self.detail_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
        scrollbar.config(command=self.detail_text.yview)
        
        # 開始翻譯按鈕
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.translate_btn = tk.Button(
            button_frame,
            text="開始翻譯",
            command=self.start_translation,
            font=("Microsoft JhengHei", 11, "bold"),
            bg="#27ae60",
            fg="white",
            height=2,
            cursor="hand2"
        )
        self.translate_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.stop_btn = tk.Button(
            button_frame,
            text="停止",
            command=self.stop_translation,
            font=("Microsoft JhengHei", 11),
            bg="#e74c3c",
            fg="white",
            height=2,
            state="disabled",
            cursor="hand2"
        )
        self.stop_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
    
    def setup_translator(self):
        """初始化翻譯器"""
        if self.engine == 'google':
            try:
                from googletrans import Translator
                self.translator = Translator()
                self.log_detail("✓ Google Translate 引擎已就緒")
            except ImportError:
                messagebox.showerror(
                    "錯誤",
                    "未安裝 googletrans 套件\n請執行：pip install googletrans==3.1.0a0"
                )
            except Exception as e:
                self.log_detail(f"✗ Google Translate 初始化失敗：{e}")
        elif self.engine == 'ollama':
            try:
                import requests
                # 使用用戶選擇的模型
                selected_model = self.ollama_model_var.get()
                
                if selected_model:
                    # 驗證模型存在
                    response = requests.get('http://localhost:11434/api/tags', timeout=5)
                    if response.status_code == 200:
                        models_data = response.json()
                        models = models_data.get('models', [])
                        model_names = [m.get('name', '') for m in models]
                        
                        if selected_model in model_names:
                            self.ollama_model = selected_model
                            self.translator = True  # 標記為已就緒
                            self.log_detail(f"✓ Ollama 引擎已就緒 (model: {self.ollama_model})")
                        else:
                            messagebox.showerror(
                                "錯誤",
                                f"模型 {selected_model} 不存在\n請重新選擇或下載模型"
                            )
                            self.translator = None
                    else:
                        messagebox.showerror(
                            "錯誤",
                            "Ollama 伺服器未回應\n請確認 Ollama 已啟動（ollama serve）"
                        )
                        self.translator = None
                else:
                    messagebox.showwarning(
                        "警告",
                        "請選擇一個 Ollama 模型"
                    )
                    self.translator = None
            except ImportError:
                messagebox.showerror(
                    "錯誤",
                    "未安裝 requests 套件\n請執行：pip install requests"
                )
            except Exception as e:
                messagebox.showerror(
                    "錯誤",
                    f"無法連接到 Ollama：{e}\n請確認 Ollama 已啟動（ollama serve）"
                )
                self.translator = None
    
    def on_engine_changed(self, event=None):
        """當翻譯引擎變更時"""
        engine_str = self.engine_var.get()
        if engine_str.startswith('google'):
            self.engine = 'google'
            # 隱藏 Ollama 模型選擇器
            self.ollama_model_frame.pack_forget()
        elif engine_str.startswith('ollama'):
            self.engine = 'ollama'
            # 顯示 Ollama 模型選擇器
            self.ollama_model_frame.pack(fill=tk.X, pady=5, after=self.engine_combo.master)
            # 刷新模型列表
            self.refresh_ollama_models()
        
        self.translator = None
        self.setup_translator()
    
    def refresh_ollama_models(self):
        """刷新 Ollama 模型列表"""
        try:
            import requests
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                models = models_data.get('models', [])
                
                if models:
                    model_names = [model.get('name', '') for model in models if model.get('name')]
                    self.ollama_model_combo['values'] = model_names
                    
                    # 自動選擇第一個模型
                    if model_names:
                        # 優先選擇包含 gemma 的模型
                        selected_model = None
                        for model_name in model_names:
                            if 'gemma' in model_name.lower():
                                selected_model = model_name
                                break
                        
                        if not selected_model:
                            selected_model = model_names[0]
                        
                        self.ollama_model_var.set(selected_model)
                        self.ollama_model = selected_model
                        self.log_detail(f"✓ 找到 {len(model_names)} 個 Ollama 模型")
                    else:
                        self.log_detail("✗ 未找到 Ollama 模型")
                        messagebox.showwarning(
                            "警告",
                            "未找到可用的 Ollama 模型\n請先下載模型：ollama pull gemma2:9b"
                        )
                else:
                    self.log_detail("✗ 未找到 Ollama 模型")
                    messagebox.showwarning(
                        "警告",
                        "未找到可用的 Ollama 模型\n請先下載模型：ollama pull gemma2:9b"
                    )
            else:
                messagebox.showerror(
                    "錯誤",
                    "無法連接到 Ollama\n請確認 Ollama 已啟動（ollama serve）"
                )
        except ImportError:
            messagebox.showerror(
                "錯誤",
                "未安裝 requests 套件\n請執行：pip install requests"
            )
        except Exception as e:
            messagebox.showerror(
                "錯誤",
                f"無法連接到 Ollama：{e}\n請確認 Ollama 已啟動（ollama serve）"
            )
    
    def select_input_file(self):
        """選擇輸入檔案"""
        filename = filedialog.askopenfilename(
            title="選擇要翻譯的 PDF 檔案",
            filetypes=[("PDF 檔案", "*.pdf"), ("所有檔案", "*.*")]
        )
        if filename:
            self.input_file = filename
            self.input_path_var.set(filename)
            self.log_detail(f"✓ 已選擇輸入檔案：{os.path.basename(filename)}")
            
            # 自動設定輸出檔名
            if not self.output_file:
                path = Path(filename)
                output_name = f"{path.stem}_translated{path.suffix}"
                output_path = path.parent / output_name
                self.output_file = str(output_path)
                self.output_path_var.set(str(output_path))
    
    def select_output_file(self):
        """選擇輸出檔案"""
        filename = filedialog.asksaveasfilename(
            title="選擇輸出檔案位置",
            defaultextension=".pdf",
            filetypes=[("PDF 檔案", "*.pdf"), ("所有檔案", "*.*")]
        )
        if filename:
            self.output_file = filename
            self.output_path_var.set(filename)
            self.log_detail(f"✓ 已設定輸出位置：{os.path.basename(filename)}")
    
    def log_detail(self, message):
        """記錄詳細資訊"""
        self.detail_text.config(state="normal")
        self.detail_text.insert(tk.END, f"{message}\n")
        self.detail_text.see(tk.END)
        self.detail_text.config(state="disabled")
        self.root.update_idletasks()
    
    def update_status(self, message):
        """更新狀態訊息"""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def update_progress(self, value):
        """更新進度條"""
        self.progress_bar['value'] = value
        self.root.update_idletasks()
    
    def start_translation(self):
        """開始翻譯"""
        # 驗證輸入
        if not self.input_file or not os.path.exists(self.input_file):
            messagebox.showwarning("警告", "請選擇有效的輸入檔案")
            return
        
        if not self.output_file:
            messagebox.showwarning("警告", "請指定輸出檔案位置")
            return
        
        if not self.translator:
            messagebox.showerror("錯誤", "翻譯引擎未就緒")
            return
        
        # 禁用按鈕
        self.translate_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.is_translating = True
        
        # 清空詳細資訊
        self.detail_text.config(state="normal")
        self.detail_text.delete(1.0, tk.END)
        self.detail_text.config(state="disabled")
        
        # 在新執行緒中執行翻譯
        thread = threading.Thread(target=self.translate_pdf)
        thread.daemon = True
        thread.start()
    
    def stop_translation(self):
        """停止翻譯"""
        self.is_translating = False
        self.update_status("正在停止...")
        self.log_detail("✗ 使用者已取消翻譯")
    
    def translate_pdf(self):
        """執行PDF翻譯（在背景執行緒中）"""
        try:
            # 解析語言代碼
            lang_code = self.lang_var.get().split()[0]
            
            # 開始處理
            self.update_status("正在讀取 PDF 檔案...")
            self.update_progress(0)
            self.log_detail("="*60)
            self.log_detail(f"輸入檔案：{os.path.basename(self.input_file)}")
            self.log_detail(f"輸出檔案：{os.path.basename(self.output_file)}")
            self.log_detail(f"目標語言：{lang_code}")
            self.log_detail("="*60)
            
            # 讀取PDF
            doc = fitz.open(self.input_file)
            total_pages = len(doc)
            
            # 解析頁面範圍
            pages_str = self.pages_var.get().strip()
            if pages_str:
                page_range = self._parse_page_range(pages_str, total_pages)
                self.log_detail(f"✓ 將翻譯第 {pages_str} 頁")
            else:
                page_range = range(total_pages)
                self.log_detail(f"✓ 將翻譯全部 {total_pages} 頁")
            
            # 提取文字
            self.update_status(f"正在提取文字 (0/{len(page_range)})...")
            pages_data = []
            
            for idx, page_num in enumerate(page_range):
                if not self.is_translating:
                    raise Exception("使用者取消")
                
                page = doc[page_num]
                blocks = page.get_text("dict")["blocks"]
                
                texts = []
                for block in blocks:
                    if block["type"] == 0:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                if span["text"].strip() and len(span["text"].strip()) > 1:
                                    texts.append({
                                        'page_num': page_num,
                                        'bbox': span["bbox"],
                                        'text': span["text"],
                                        'size': span["size"],
                                        'color': span.get("color", 0)
                                    })
                
                pages_data.append((page_num, texts))
                progress = (idx + 1) / len(page_range) * 20
                self.update_progress(progress)
                self.update_status(f"正在提取文字 ({idx + 1}/{len(page_range)})...")
            
            total_texts = sum(len(texts) for _, texts in pages_data)
            self.log_detail(f"✓ 已提取 {total_texts} 個文字區塊")
            doc.close()
            
            # 翻譯文字
            self.update_status("正在翻譯文字...")
            translated_count = 0
            
            for page_idx, (page_num, page_texts) in enumerate(pages_data):
                if not self.is_translating:
                    raise Exception("使用者取消")
                
                for item in page_texts:
                    if not self.is_translating:
                        raise Exception("使用者取消")
                    
                    try:
                        if self.engine == 'google':
                            result = self.translator.translate(item['text'], dest=lang_code)
                            item['translated'] = result.text
                            time.sleep(0.5)
                        elif self.engine == 'ollama':
                            item['translated'] = self._translate_with_ollama(item['text'], lang_code)
                            time.sleep(0.1)
                    except Exception as e:
                        self.log_detail(f"✗ 翻譯失敗：{item['text'][:20]}... ({e})")
                        item['translated'] = item['text']
                    
                    translated_count += 1
                    progress = 20 + (translated_count / total_texts * 60)
                    self.update_progress(progress)
                    self.update_status(f"正在翻譯 ({translated_count}/{total_texts})...")
            
            self.log_detail(f"✓ 已完成 {translated_count} 個文字區塊的翻譯")
            
            # 創建輸出PDF
            self.update_status("正在建立輸出檔案...")
            if os.path.exists(self.output_file):
                os.remove(self.output_file)
            shutil.copy2(self.input_file, self.output_file)
            
            doc = fitz.open(self.output_file)
            
            # 應用翻譯
            self.update_status("正在套用翻譯...")
            success = 0
            
            for page_idx, (page_num, page_texts) in enumerate(pages_data):
                if not self.is_translating:
                    raise Exception("使用者取消")
                
                page = doc[page_num]
                
                # 覆蓋原文
                for item in page_texts:
                    page.add_redact_annot(fitz.Rect(item['bbox']), fill=(1, 1, 1))
                page.apply_redactions()
                
                # 插入翻譯
                for item in page_texts:
                    if not self.is_translating:
                        raise Exception("使用者取消")
                    
                    translated = item['translated']
                    bbox = item['bbox']
                    size = item['size']
                    color = item['color']
                    
                    if color:
                        r = ((color >> 16) & 0xFF) / 255.0
                        g = ((color >> 8) & 0xFF) / 255.0
                        b = (color & 0xFF) / 255.0
                        text_color = (r, g, b)
                    else:
                        text_color = (0, 0, 0)
                    
                    adjusted_size = max(size * 0.7, 6)
                    baseline_y = bbox[1] + size * 0.75
                    
                    # 使用內建CJK字體
                    for fontname in ["china-ss", "china-s", "cjk"]:
                        try:
                            rc = page.insert_text(
                                (bbox[0], baseline_y),
                                translated,
                                fontname=fontname,
                                fontsize=adjusted_size,
                                color=text_color
                            )
                            if rc > 0:
                                success += 1
                                break
                        except:
                            continue
                
                progress = 80 + ((page_idx + 1) / len(pages_data) * 15)
                self.update_progress(progress)
                self.update_status(f"正在套用翻譯 ({page_idx + 1}/{len(pages_data)} 頁)...")
            
            self.log_detail(f"✓ 已成功套用 {success}/{total_texts} 個翻譯")
            
            # 保存
            self.update_status("正在儲存檔案...")
            self.update_progress(95)
            doc.saveIncr()
            doc.close()
            
            output_size = os.path.getsize(self.output_file) / (1024*1024)
            
            # 完成
            self.update_progress(100)
            self.update_status("翻譯完成！")
            self.log_detail("="*60)
            self.log_detail(f"✓ 翻譯完成！")
            self.log_detail(f"✓ 輸出檔案：{self.output_file}")
            self.log_detail(f"✓ 檔案大小：{output_size:.2f} MB")
            self.log_detail(f"✓ 成功翻譯：{success}/{total_texts} 個文字區塊")
            self.log_detail("="*60)
            
            # 顯示完成訊息
            self.root.after(0, lambda: messagebox.showinfo(
                "完成",
                f"翻譯完成！\n\n已翻譯 {success}/{total_texts} 個文字區塊\n輸出檔案：{os.path.basename(self.output_file)}"
            ))
            
        except Exception as e:
            error_msg = str(e)
            self.log_detail(f"✗ 錯誤：{error_msg}")
            self.update_status(f"錯誤：{error_msg}")
            self.root.after(0, lambda: messagebox.showerror("錯誤", f"翻譯失敗：{error_msg}"))
        
        finally:
            # 恢復按鈕狀態
            self.root.after(0, lambda: self.translate_btn.config(state="normal"))
            self.root.after(0, lambda: self.stop_btn.config(state="disabled"))
            self.is_translating = False
    
    def _parse_page_range(self, pages_str, total_pages):
        """解析頁面範圍字符串"""
        page_set = set()
        for part in pages_str.split(','):
            part = part.strip()
            if '-' in part:
                start, end = part.split('-')
                start = int(start) - 1
                end = int(end)
                page_set.update(range(start, min(end, total_pages)))
            else:
                page_num = int(part) - 1
                if 0 <= page_num < total_pages:
                    page_set.add(page_num)
        return sorted(page_set)
    
    def _translate_with_ollama(self, text, lang_code):
        """使用 Ollama 翻譯文本"""
        if not text or len(text.strip()) < 2:
            return text
        
        try:
            import requests
            
            # 根據目標語言設定提示詞
            lang_names = {
                'zh-TW': '繁體中文',
                'zh-CN': '简体中文',
                'en': 'English',
                'ja': '日本語',
                'ko': '한국어',
                'fr': 'français',
                'de': 'Deutsch',
                'es': 'español',
                'pt': 'português',
                'ru': 'русский'
            }
            target_lang_name = lang_names.get(lang_code, lang_code)
            
            # 優化提示詞，使用更明確的指示
            prompt = f"""You are a professional translator. Translate the following text to {target_lang_name}.
Rules:
- Only provide the translation
- Do not include any explanations, notes, or the original text
- Maintain the original meaning and tone
- Keep proper nouns and technical terms appropriate

Text to translate:
{text}

Translation:"""
            
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': self.ollama_model,
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'temperature': 0.3,  # 降低隨機性，提高準確性
                        'top_p': 0.9
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                translated = result.get('response', '').strip()
                
                # 清理可能的多餘內容
                # 移除可能的引號或標記
                if translated:
                    # 移除開頭和結尾的引號
                    translated = translated.strip('"\'')
                    # 如果翻譯結果包含"Translation:"等標籤，移除它
                    if translated.lower().startswith('translation:'):
                        translated = translated[12:].strip()
                    # 移除可能的換行符號
                    translated = translated.strip()
                
                return translated if translated and translated != text else text
            else:
                self.log_detail(f"✗ Ollama API 錯誤：HTTP {response.status_code}")
                return text
        except Exception as e:
            self.log_detail(f"✗ Ollama 翻譯錯誤：{e}")
            return text

def main():
    root = tk.Tk()
    app = PDFTranslatorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

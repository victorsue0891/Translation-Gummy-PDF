# -*- coding: utf-8 -*-
"""
PDF翻譯工具 - CLI版本
支持命令行參數和多種翻譯選項
"""

import fitz
import os
import time
import shutil
import sys
import argparse

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

class PDFTranslatorCLI:
    def __init__(self, input_pdf, output_pdf, target_lang='zh-TW', pages=None, verbose=False, engine='google'):
        self.input_pdf = input_pdf
        self.output_pdf = output_pdf
        self.target_lang = target_lang
        self.pages = pages
        self.verbose = verbose
        self.engine = engine  # 'google' or 'ollama'
        self.translator = None
        self.ollama_model = None  # 將在 setup_translator 時自動檢測
        
    def log(self, message, force=False):
        """輸出日誌信息"""
        if self.verbose or force:
            print(message)
    
    def setup_translator(self):
        """設置翻譯器"""
        if self.engine == 'google':
            try:
                from googletrans import Translator
                self.translator = Translator()
                self.log("   [OK] Google Translator ready", force=True)
                return True
            except ImportError:
                print("   [ERROR] googletrans not installed")
                print("   Please run: pip install googletrans==3.1.0a0")
                return False
            except Exception as e:
                print(f"   [ERROR] {e}")
                return False
        elif self.engine == 'ollama':
            try:
                import requests
                # 獲取可用的模型列表
                response = requests.get('http://localhost:11434/api/tags', timeout=5)
                if response.status_code == 200:
                    models_data = response.json()
                    models = models_data.get('models', [])
                    
                    if models:
                        # 優先選擇 gemma 系列模型
                        self.ollama_model = None
                        for model in models:
                            model_name = model.get('name', '')
                            if 'gemma' in model_name.lower():
                                self.ollama_model = model_name
                                break
                        
                        # 如果沒有 gemma 模型，使用第一個可用模型
                        if not self.ollama_model and models:
                            self.ollama_model = models[0].get('name', '')
                        
                        if self.ollama_model:
                            self.log(f"   [OK] Ollama ready (model: {self.ollama_model})", force=True)
                            return True
                        else:
                            print("   [ERROR] No Ollama models found")
                            print("   Please download a model: ollama pull gemma2:9b")
                            return False
                    else:
                        print("   [ERROR] No Ollama models found")
                        print("   Please download a model: ollama pull gemma2:9b")
                        return False
                else:
                    print("   [ERROR] Ollama not responding")
                    return False
            except ImportError:
                print("   [ERROR] requests not installed")
                print("   Please run: pip install requests")
                return False
            except Exception as e:
                print(f"   [ERROR] Cannot connect to Ollama: {e}")
                print("   Please make sure Ollama is running (ollama serve)")
                return False
        else:
            print(f"   [ERROR] Unknown engine: {self.engine}")
            return False
    
    def translate_text(self, text):
        """翻譯文本"""
        if not text or len(text.strip()) < 2:
            return text
        
        if self.engine == 'google':
            try:
                result = self.translator.translate(text, dest=self.target_lang)
                time.sleep(0.5)
                return result.text
            except Exception as e:
                self.log(f"   [WARNING] Translation failed: {e}")
                return text
        elif self.engine == 'ollama':
            return self._translate_with_ollama(text)
        else:
            return text
    
    def _translate_with_ollama(self, text):
        """使用 Ollama 翻譯文本"""
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
            target_lang_name = lang_names.get(self.target_lang, self.target_lang)
            
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
                if translated:
                    # 移除開頭和結尾的引號
                    translated = translated.strip('"\'')
                    # 如果翻譯結果包含"Translation:"等標籤，移除它
                    if translated.lower().startswith('translation:'):
                        translated = translated[12:].strip()
                    # 移除可能的換行符號
                    translated = translated.strip()
                
                time.sleep(0.1)  # 較短的延遲
                return translated if translated and translated != text else text
            else:
                self.log(f"   [WARNING] Ollama translation failed: {response.status_code}")
                return text
        except Exception as e:
            self.log(f"   [WARNING] Ollama translation error: {e}")
            return text
    
    def process(self):
        """處理PDF"""
        print("\n" + "="*70)
        print("PDF Translation Tool - CLI Version")
        print("="*70)
        
        # 檢查輸入文件
        if not os.path.exists(self.input_pdf):
            print(f"\n[ERROR] Input file not found: {self.input_pdf}")
            return False
        
        file_size = os.path.getsize(self.input_pdf) / (1024*1024)
        print(f"\nInput:  {self.input_pdf} ({file_size:.2f} MB)")
        print(f"Output: {self.output_pdf}")
        print(f"Target language: {self.target_lang}")
        
        if not self.setup_translator():
            return False
        
        try:
            # 讀取PDF
            self.log("\n[1/4] Reading PDF and extracting text...", force=True)
            doc = fitz.open(self.input_pdf)
            total_pages = len(doc)
            
            # 確定要處理的頁面範圍
            if self.pages:
                page_range = self._parse_page_range(self.pages, total_pages)
                self.log(f"   Processing pages: {page_range}", force=True)
            else:
                page_range = range(total_pages)
                self.log(f"   Processing all {total_pages} pages", force=True)
            
            pages_data = []
            for page_num in page_range:
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
                
                if self.verbose:
                    print(f"   Progress: {(len(pages_data))/len(page_range)*100:.1f}%", end='\r')
            
            total_texts = sum(len(texts) for _, texts in pages_data)
            print(f"\n   Extracted {total_texts} text segments from {len(page_range)} pages")
            doc.close()
            
            # 翻譯
            self.log("\n[2/4] Translating text...", force=True)
            translated_count = 0
            for _, page_texts in pages_data:
                for item in page_texts:
                    item['translated'] = self.translate_text(item['text'])
                    translated_count += 1
                    if self.verbose or translated_count % 100 == 0:
                        print(f"   Progress: {translated_count/total_texts*100:.1f}% ({translated_count}/{total_texts})", end='\r')
            print(f"\n   Translation completed")
            
            # 創建輸出PDF
            self.log("\n[3/4] Creating output PDF...", force=True)
            if os.path.exists(self.output_pdf):
                os.remove(self.output_pdf)
            shutil.copy2(self.input_pdf, self.output_pdf)
            
            doc = fitz.open(self.output_pdf)
            
            # 應用翻譯
            self.log("\n[4/4] Applying translations...", force=True)
            success = 0
            
            for page_num, page_texts in pages_data:
                page = doc[page_num]
                
                # 覆蓋原文
                for item in page_texts:
                    page.add_redact_annot(fitz.Rect(item['bbox']), fill=(1, 1, 1))
                page.apply_redactions()
                
                # 插入翻譯
                for item in page_texts:
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
                
                if self.verbose:
                    print(f"   Progress: {(len([p for p, _ in pages_data if p <= page_num]))/len(pages_data)*100:.1f}%", end='\r')
            
            print(f"\n   Successfully applied {success}/{total_texts} translations")
            
            # 保存
            self.log("\n   Saving PDF...", force=True)
            doc.saveIncr()
            doc.close()
            
            output_size = os.path.getsize(self.output_pdf) / (1024*1024)
            
            print("\n" + "="*70)
            print("Translation completed successfully!")
            print(f"\nOutput file: {self.output_pdf} ({output_size:.2f} MB)")
            print(f"Translated: {success}/{total_texts} text segments")
            print("="*70 + "\n")
            return True
            
        except Exception as e:
            print(f"\n[ERROR] {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return False
    
    def _parse_page_range(self, pages_str, total_pages):
        """解析頁面範圍字符串，例如 '1-10,15,20-25'"""
        page_set = set()
        for part in pages_str.split(','):
            part = part.strip()
            if '-' in part:
                start, end = part.split('-')
                start = int(start) - 1  # 轉換為0-based索引
                end = int(end)
                page_set.update(range(start, min(end, total_pages)))
            else:
                page_num = int(part) - 1
                if 0 <= page_num < total_pages:
                    page_set.add(page_num)
        return sorted(page_set)

def main():
    parser = argparse.ArgumentParser(
        description='PDF Translation Tool - Translate PDF files while preserving images and layout',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Translate entire PDF to Traditional Chinese
  python pdf_translator.py input.pdf output.pdf
  
  # Translate to Simplified Chinese
  python pdf_translator.py input.pdf output.pdf --lang zh-CN
  
  # Translate only specific pages
  python pdf_translator.py input.pdf output.pdf --pages "1-10,15,20-25"
  
  # Translate with verbose output
  python pdf_translator.py input.pdf output.pdf -v
        """
    )
    
    parser.add_argument('input', help='Input PDF file path')
    parser.add_argument('output', help='Output PDF file path')
    parser.add_argument(
        '--lang', '-l',
        default='zh-TW',
        help='Target language code (default: zh-TW for Traditional Chinese)'
    )
    parser.add_argument(
        '--pages', '-p',
        help='Page range to translate (e.g., "1-10,15,20-25")'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--engine', '-e',
        choices=['google', 'ollama'],
        default='google',
        help='Translation engine: google (default) or ollama (requires Ollama running locally)'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='PDF Translator CLI v1.0'
    )
    
    args = parser.parse_args()
    
    # 創建翻譯器並執行
    translator = PDFTranslatorCLI(
        args.input,
        args.output,
        target_lang=args.lang,
        pages=args.pages,
        verbose=args.verbose,
        engine=args.engine
    )
    
    success = translator.process()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

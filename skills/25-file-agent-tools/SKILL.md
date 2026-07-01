---
name: file-agent-tools
description: 檔案處理 Agent 工具包（Word/Excel/PPT/PDF 自動化），包含 Python 自動化套件一鍵安裝指引與「痛點 ➔ 一句話 Prompt」對應表。
---

# 🛠️ 檔案處理 Agent 工具包 (File Agent Tools)

本技能整合三師爸 Sense Bar 《AI Agent 基本功 EP03》的精華。它能協助 AI Agent（如 Claude Code, Codex, Antigravity, OpenCode 等）快速安裝 Word/Excel/PPT/PDF 及其他自動化處理套件，並提供教師與辦公室常見痛點的「一句話 Prompt 對照表」，讓 AI 真正發揮「手腳」功能來批次處理本機檔案。

---

## 🎯 給 Agent 的自動安裝指令（請照做）

當使用者載入本技能並要求進行安裝時，請依序執行：

1. **確認環境**：偵測本機作業系統與 Python／pip 版本（`python --version`、`pip --version`）。
2. **安裝 Python 套件**：執行下方「核心安裝指令」。安裝前先告知使用者你要裝什麼。
3. **處理系統相依**：依作業系統，提示或執行下方「系統相依套件」的安裝（Tesseract OCR, Poppler, ffmpeg）。
4. **驗證匯入**：執行驗證指令，回報每個套件是否 import 成功，並列出失敗清單。
5. **最終回報**：給使用者一份結構化清單：✅ 成功 / ⚠️ 需手動處理（系統相依）/ ❌ 失敗與原因。

### 📦 核心安裝指令

```bash
pip install python-docx docxcompose openpyxl xlsxwriter pandas python-pptx pypdf PyMuPDF pdfplumber pdf2image reportlab fpdf2 pillow matplotlib qrcode markitdown ocrmypdf docx2pdf edge-tts yt-dlp youtube-transcript-api
```
*Windows 平台請額外追加安裝：*
```bash
pip install pywin32
```

### ⚙️ 系統相依套件（非 pip，安裝後請重開終端機以更新 PATH）

*   **Tesseract OCR**（`ocrmypdf` 需要）：
    *   **Windows**：`winget install UB-Mannheim.TesseractOCR` (繁中包需下載 [`chi_tra.traineddata`](https://github.com/tesseract-ocr/tessdata_best/raw/main/chi_tra.traineddata) 放置於 `Tesseract-OCR\tessdata\` 目錄中)
    *   **macOS**：`brew install tesseract tesseract-lang`
*   **Poppler**（`pdf2image` 需要）：
    *   **Windows**：`winget install oschwartz10612.Poppler`
    *   **macOS**：`brew install poppler`
*   **ffmpeg**（`yt-dlp` 與音訊處理需要）：
    *   **Windows**：`winget install Gyan.FFmpeg`
    *   **macOS**：`brew install ffmpeg`
*   **Microsoft Office**（`docx2pdf` 轉換需要）：需本機已安裝 MS Office，或使用 LibreOffice。

### ✅ 驗證匯入指令

```bash
python -c "import docx, docxcompose, openpyxl, xlsxwriter, pandas, pptx, pypdf, fitz, pdfplumber, pdf2image, reportlab, fpdf, PIL, matplotlib, qrcode, markitdown, ocrmypdf; print('✅ 全部核心套件匯入成功')"
```

---

## 📋 痛點 ➔ 一句話 Prompt 對照表

您可以將以下「一句話」複製貼給您的 AI Agent，它將會依據對應的 Python 套件自動生成程式碼並為您執行檔案處理：

### 📄 Word 篇
*   **套印獎狀／通知單／成績單** ➔ *「讀這份班級名單 Excel，套進這個獎狀 Word 模板，每人產一份並存成 PDF」* (使用 `python-docx` + `openpyxl`)
*   **出考卷（學生卷／教師卷分開）** ➔ *「把這些題目做成 Word，產出『學生卷（無答案）』和『教師卷（含詳解）』兩份」* (使用 `python-docx`)
*   **講義合併與轉 PDF** ➔ *「把這資料夾的 Word 講義依檔名順序合併成一份，再另存成 PDF」* (使用 `docxcompose`)

### 📊 Excel 篇
*   **成績計算與排名標紅** ➔ *「讀 grades.xlsx，算總分與排名，不及格標紅，各班平均放最後一列，存成新檔」* (使用 `openpyxl` + `xlsxwriter` / `pandas`)
*   **段考成績分析** ➔ *「分析這份答題明細，畫出各題答對率長條圖和全班分數分布圖」* (使用 `pandas` + `matplotlib`)
*   **總成績單拆成各班／各生** ➔ *「把這份全校成績表，依『班級』欄拆成一個班一個 Excel 檔」* (使用 `openpyxl`)

### 📑 PowerPoint 篇
*   **教材大綱轉簡報** ➔ *「把這份教材大綱，每個重點做成一頁投影片，套用這個範本」* (使用 `python-pptx`)
*   **圖片整批轉單字卡簡報** ➔ *「把這資料夾的圖片，每張做成一頁投影片，下方加檔名當標題」* (使用 `python-pptx` + `pillow`)
*   **統一字型與加校徽/浮水印** ➔ *「把這份 PPT 全部字型改成標楷體，每頁右下角加上這張校徽」* (使用 `python-pptx`)

### 📕 PDF 篇
*   **PDF 合併與抽取頁面** ➔ *「把這些 PDF 合併成一份，並把第 5～8 頁單獨抽出來另存」* (使用 `pypdf` + `PyMuPDF`)
*   **PDF 加浮水印** ➔ *「幫這份 PDF 每頁加上淡灰色浮水印『302 班 期中複習』」* (使用 `pypdf` + `reportlab`)
*   **掃描講義 OCR 辨識** ➔ *「把這份掃描 PDF 做 OCR，變成可以複製文字的 PDF」* (使用 `ocrmypdf`)

### 🧰 其他常用小工具
*   **連結批次轉 QR Code** ➔ *「把這 5 個連結各生一張 QR Code，貼到學習單」* (使用 `qrcode` + `pillow`)
*   **抓 YouTube 字幕逐字稿** ➔ *「抓這支 YouTube 影片的字幕，整理成逐字稿」* (使用 `youtube-transcript-api`)
*   **講稿轉免費中文語音** ➔ *「把這份講稿轉成中文語音 mp3，語速慢一點」* (使用 `edge-tts`)
*   **PDF/PPT 轉 Markdown** ➔ *「把這份 PDF/PPT 轉成 Markdown」* (使用 `markitdown`)

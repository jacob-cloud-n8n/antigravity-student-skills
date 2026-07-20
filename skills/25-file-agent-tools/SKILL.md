---
name: file-agent-tools
description: 檔案處理 Agent 工具包（Word/Excel/PPT/PDF 自動化），包含 Windows PowerShell 核心 uv 套件一鍵安裝與「痛點 ➔ 一句話 Prompt」對應表。
---

# 🛠️ 檔案處理 Agent 工具包 (File Agent Tools)

本技能整合三師爸 Sense Bar 《AI Agent 基本功 EP03》的精華。它能協助 AI Agent（如 Claude Code, Codex, Antigravity, OpenCode 等）快速且安全地安裝 Word/Excel/PPT/PDF 及其他自動化處理套件，並提供教師與辦公室常見痛點的「一句話 Prompt 對照表」，讓 AI 真正發揮「手腳」功能來批次處理本機檔案。

---

## 🎯 給 Agent 的必要安裝規則（請照做）

當使用者要求「依這份檔案安裝」時，請遵守：

1. **只在本 repo 內工作**：以本技能所在資料夾為專案根目錄，不要搜尋其他磁碟或其他 Agent 的資料夾。
2. **只執行核心安裝**：不要安裝選用工具與系統工具，除非使用者明確點名用途。
3. **不要使用全域 `pip install`**：核心套件安裝到本 repo 的 `.venv`，避免污染使用者原有全域 Python。
4. **不要逐項上網研究**：套件與版本交給 `uv` 解析；不要為每個套件另開網頁、產生長篇計畫或重複說明。
5. **最多重試一次**：失敗時先回報原始錯誤與建議，不要反覆改指令、重裝或自動改用系統管理員權限。
6. **不自動切換執行環境**：Windows、WSL、沙盒是不同環境；不要為了安裝而自行改用 WSL、Docker 或另一個 Agent。

---

## 🚀 核心安裝步驟（預設只做這段）

在專案根目錄執行：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\install_windows.ps1"
```

安裝腳本會自動完成：
1. 找到 `uv`；若沒有，透過 WinGet 安裝官方 `astral-sh.uv`。
2. 以 Python 3.12 建立本 repo 專用的 `.venv`；本機沒有 3.12 時由 `uv` 下載。
3. 依 `requirements-core.txt` 一次安裝核心套件。
4. 執行 `verify_core.py`；只做一次匯入驗證並回報結果。

### ✅ 核心必裝套件

這一組涵蓋研習最常見的 Word、Excel、PowerPoint、PDF、圖片、圖表、QR Code 與教材轉 Markdown：

| 套件 | 用途 |
|------|------|
| `python-docx` | 生成／讀寫 Word |
| `openpyxl` | 讀寫與格式化 Excel |
| `python-pptx` | 生成／改寫 PowerPoint |
| `pypdf` | PDF 合併、拆分、浮水印 |
| `PyMuPDF` (fitz) | PDF 抽文字、抽頁、轉圖片 |
| `reportlab` | 生成 PDF 與浮水印圖層 |
| `pillow` | 圖片裁切、去白邊、合成 |
| `matplotlib` | 產生統計圖表 |
| `qrcode[pil]` | 產生 QR Code |
| `markitdown[pdf,docx,pptx,xlsx]` | 將 PDF／Word／PPT／Excel 轉成 Markdown |

---

## 📋 痛點 ➔ 一句話 Prompt 對照表

您可以將以下「一句話」複製貼給您的 AI Agent，它將會依據對應的 Python 套件自動生成程式碼並為您執行檔案處理：

### 📄 Word 篇
*   **套印獎狀／通知單／成績單** ➔ *「讀這份班級名單 Excel，套進這個獎狀 Word 模板，每人產一份並存成 PDF」* (使用 `python-docx` + `openpyxl`)
*   **出考卷（學生卷／教師卷分開）** ➔ *「把這些題目做成 Word，產出『學生卷（無答案）』和『教師卷（含詳解）』兩份」* (使用 `python-docx`)
*   **講義合併與轉 PDF** ➔ *「把這資料夾的 Word 講義依檔名順序合併成一份，再另存成 PDF」* (使用 `python-docx` 或彙整工具)

### 📊 Excel 篇
*   **成績計算與排名標紅** ➔ *「讀 grades.xlsx，算總分與排名，不及格標紅，各班平均放最後一列，存成新檔」* (使用 `openpyxl` + `matplotlib` / `pandas`)
*   **段考成績分析** ➔ *「分析這份答題明細，畫出各題答對率長條圖和全班分數分布圖」* (使用 `openpyxl` + `matplotlib`)
*   **總成績單拆成各班／各生** ➔ *「把這份全校成績表，依『班級』欄拆成一個班一個 Excel 檔」* (使用 `openpyxl`)

### 📑 PowerPoint 篇
*   **教材大綱轉簡報** ➔ *「把這份教材大綱，每個重點做成一頁投影片，套用這個範本」* (使用 `python-pptx`)
*   **圖片整批轉單字卡簡報** ➔ *「把這資料夾的圖片，每張做成一頁投影片，下方加檔名當標題」* (使用 `python-pptx` + `pillow`)
*   **統一字型與加校徽/浮水印** ➔ *「把這份 PPT 全部字型改成標楷體，每頁右下角加上這張校徽」* (使用 `python-pptx`)

### 📕 PDF 篇
*   **PDF 合併與抽取頁面** ➔ *「把這些 PDF 合併成一份，並把第 5～8 頁單獨抽出來另存」* (使用 `pypdf` + `PyMuPDF`)
*   **PDF 加浮水印** ➔ *「幫這份 PDF 每頁加上淡灰色浮水印『302 班 期中複習』」* (使用 `pypdf` + `reportlab`)

### 🧰 其他常用小工具
*   **連結批次轉 QR Code** ➔ *「把這 5 個連結各生一張 QR Code，貼到學習單」* (使用 `qrcode` + `pillow`)
*   **PDF/PPT 轉 Markdown** ➔ *「把這份 PDF/PPT 轉成 Markdown」* (使用 `markitdown`)

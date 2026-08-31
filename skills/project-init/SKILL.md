---
name: project-init
description: 專案初始化（三層級自動偵測）。當使用者說「初始化專案」「專案初始化」「開新專案」「建立專案藍圖」「幫我 init 專案」等要為當前資料夾建立專案基礎建設的請求時，請使用此技能。依這台電腦的工具鏈自動建到最高可用層級：L1 本地（AGENTS.md + handoff.md）→ L2 GitHub（git + 私有 repo）→ L3 詳細筆記（Obsidian 或 docs/工作筆記.md）；若使用者明確要建立學員第二大腦，則登記共用二腦路徑並沿用其工作日誌。
---

# 專案初始化（三層級自動偵測）

## 設計理念

一套技能、三個層級。**這台電腦裝了什麼工具，就自動建到哪個層級**——不用問使用者「你要第幾層級」。三層資訊的定位與讀取頻率不同：

| 層級 | 平台 | 建立的東西 | 讀取時機 |
|------|------|-----------|---------|
| L1 本地 | 專案資料夾（建議放 Google 雲端硬碟等同步資料夾，跨電腦靠它） | `AGENTS.md`（專案藍圖）＋`handoff.md`（交接檔） | **每個 session 都讀** |
| L2 GitHub | 私有 repo | git 版本控制＋雲端備份 | 指定才讀 |
| L3 筆記 | Obsidian vault，或專案內 `docs/工作筆記.md` | 詳細筆記（決策原因、踩坑細節） | 有需要才讀 |

> 為什麼藍圖叫 `AGENTS.md` 而不是 `CLAUDE.md`？AGENTS.md 是跨 Agent 開放標準——Claude Code、Codex、Gemini CLI、OpenCode 都讀得懂，換 Agent 不用改檔案。

## 層級偵測（初始化看「這台電腦」有什麼）

依序檢查，決定本次能建到第幾層級：

1. **L1**：無條件可建。
2. **L2**：跑 `gh auth status`，已登入 GitHub CLI → 可建。
3. **L3**：Obsidian MCP 工具可用 → 建在 vault；不可用 → 建在專案內 `docs/工作筆記.md`（跟著 L1/L2 同步，不會遺失）。

檢查完先告訴使用者：「這台電腦可初始化至第 N 層級（L3 形式：Obsidian／docs）」，再開始執行。

## 初始化 SOP（依序執行）

### L1：本地藍圖（永遠執行）

1. **掃描資料夾現況**：列出既有檔案。若已有 `AGENTS.md` 或 `handoff.md` → **停下來問使用者**：覆蓋、或只補缺口（預設只補缺口，不覆蓋既有檔案）。
2. **詢問使用者**：專案名稱、一句話目標、關鍵時程（沒有就留白，不要硬編）。
3. **建立 `AGENTS.md`**：以 `templates/agents.template.md` 為底填入實際內容；「資料夾結構」區塊由掃描結果自動生成。
4. **建立 `handoff.md`**：以 `templates/handoff.template.md` 為底，「目前做到哪」填「專案初始化完成」。更新者填「Agent 名 @ 電腦名」：
   - macOS / Linux：`hostname`
   - Windows PowerShell：`$env:COMPUTERNAME`
5. 若專案路徑在雲端同步資料夾（路徑含「雲端硬碟」「My Drive」「Dropbox」「iCloud」等）→ 提醒使用者確認同步 App 的同步圖示已打勾（檔案要真的上雲端，換電腦才拿得到）。

### 選配：登記學員第二大腦

只有使用者明確要求「建立／啟用第二大腦」，或目前資料夾已同時存在 `Clippings/`、`知識庫/`、`創作庫/`、`工作日誌/` 時才執行：

1. 以目前資料夾作為唯一共用第二大腦根目錄；內容增加時在各層依專案分類，不為每個專案另建 repo。
2. 使用 `student-second-brain` 的專案範本，只補缺少的資料夾、索引、日誌和 `AGENTS.md` 二腦區塊；不得覆蓋既有內容。
3. 將 `工作日誌/log.md` 登記為 L3 詳細筆記，避免另建一份重複的 `docs/工作筆記.md`。
4. Obsidian 是建議安裝的閱讀介面，不是啟用條件；沒有 Obsidian 仍可完成本機二腦初始化。
5. 不在初始化時建立每日排程、呼叫付費 API 或加入 embeddings／向量資料庫。

沒有明確要求且未偵測到完整結構時，維持原初始化流程，不主動把普通專案改造成第二大腦。

### L2：GitHub（gh 已登入才做，否則跳過並註明）

6. **git 初始化**：
   ```bash
   git init
   git config user.name "<使用者 GitHub 帳號>"    # 可由 gh api user --jq .login 取得
   git config user.email "<使用者 email>"
   ```
   Windows 且專案在 Google 雲端硬碟內 → 加跑 `git config windows.appendAtomically false`（GDrive＋git 的已知坑，Mac 不需要）。
7. **建立 `.gitignore`**：
   ```gitignore
   # 敏感檔（絕不入庫）
   .env
   .env.*
   *.key
   credentials.*

   # 依賴與編譯輸出
   node_modules/
   dist/
   build/

   # 系統與暫存
   .DS_Store
   Thumbs.db
   desktop.ini
   ~$*
   *.tmp
   ```
8. **初始 commit**：`git status` 逐一確認沒有混入敏感檔，再**逐一 `git add` 新建檔案**（不用 `git add .`）→ `git commit -m "chore: 初始化專案 <專案名稱>"`。
9. **建立私有 repo**：問使用者偏好的英文 repo 名，然後：
   ```bash
   gh repo create <帳號>/<repo-name> --private --source=. --push
   ```
   預設一律 **private**，使用者明說才轉公開。
10. **回填 `AGENTS.md`** 同步層級表的 GitHub 欄（repo 網址）。

### L3：詳細筆記（依偵測結果二擇一）

11. 建立詳細筆記，兩種形式同結構；若上一節已登記學員第二大腦，沿用 `工作日誌/log.md` 並跳過另建：
    - **有 Obsidian MCP**：在 vault 根目錄建與專案資料夾**同名**的資料夾，內建 `專案工作流程.md`。
    - **無 Obsidian**：在專案內建 `docs/工作筆記.md`（跟著 git／雲端資料夾同步）。
    內容包含：專案背景與詳細脈絡、決策紀錄（為什麼這樣做）、🕳️ 踩坑筆記、🗓️ 最近更動紀錄表格（第一行寫今天的初始化）。
12. **回填 `AGENTS.md`** 同步層級表的 L3 欄（筆記位置）。

### 回報

```
🏗️ 本專案初始化至第 N 層級
✅ L1 本地：AGENTS.md ＋ handoff.md
✅ L2 GitHub：<帳號>/<repo>（私有）
✅ L3 筆記：<Obsidian 路徑｜docs/工作筆記.md>
⚠️ 未建的層級：<原因。例：這台電腦沒登入 gh——之後登入後說「補建 L2」即可>
```

## 不該做的事

- ❌ 未經確認就覆蓋既有的 `AGENTS.md`／`handoff.md`（既有專案只補缺口）
- ❌ 電腦沒 gh／Obsidian 時報錯中斷（正確行為：跳過該層級、回報中註明原因）
- ❌ 把 `.env`、API key 之類敏感檔 commit 進 git
- ❌ 預設建 public repo
- ❌ 初始提交用 `git add .`（先 `git status` 逐一確認）

## 注意事項

- 所有訊息與檔案內容使用**繁體中文**。
- 初始化完成後，日常循環交給搭檔技能：**開工（startup）讀、收工（shutdown）寫**。
- 跨電腦接續的原理：L1 檔案靠同步資料夾、L2 靠 git push/pull，兩者互為備援。

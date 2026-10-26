# 憑證：Zen key、n8n Header Auth、Google 服務帳戶、試算表

> 依 2026-10 實際操作整理（n8n 2.40.7）。所有密鑰都只貼進 n8n 憑證頁，不貼進對話、不存成檔案、不截圖。
> 各家後台會改版，畫面路徑以學員當下看到的為準；不同時請他截圖（遮住密鑰）再往下。
> 本課實測走的是 n8n API；「在 n8n 畫面上匯入範本、選憑證、按執行」的畫面流程尚未逐步實測，畫面不同就截圖。

## 一、OpenCode Zen key

1. 到 https://opencode.ai/auth 登入，建立一把 API key，名稱取好認的（例：`n8n-line-助理`）。
2. 複製後直接到第二節貼進 n8n。

## 二、n8n 的兩個 Header Auth 憑證（LINE、Zen）

n8n → Credentials → Create → 搜尋 **Header Auth**，建兩個（每個都有 Name、Value 兩欄）：

| 憑證名稱（建議） | Name | Value |
|---|---|---|
| `LINE 官方帳號` | `Authorization` | `Bearer ` ＋ LINE 的 Channel access token |
| `Zen AI` | `Authorization` | `Bearer ` ＋ Zen key |

- `Bearer` 和密鑰之間有**一個空格**。
- 範本匯入後不會自動帶憑證，要**打開節點、在憑證下拉選單手動選**：
  - 關卡 1～5 的 `LINE 回覆 API` 節點 → 選 LINE 憑證。
  - 關卡 4、5 的 `呼叫 Zen AI` 節點 → 選 Zen 憑證。

## 三、Google 服務帳戶（給關卡 0、3、4、5 讀寫試算表）

為什麼用服務帳戶：學員只要把試算表「共用」給一個 email，不用每個人做 Google 登入授權。

1. Google Cloud Console → 選（或建）一個專案。
2. **先啟用 Google Sheets API**：API 程式庫搜尋 Google Sheets API → 啟用。
   - ⚠️ 沒啟用時，n8n 憑證頁的「連線測試」照樣會成功，但實際讀寫試算表會回 403「Sheets API 未啟用」。
3. IAM 與管理 → 服務帳戶 → 建立：名稱例如 `n8n-line-sheets`；**授予角色這一步什麼都不選**，直接完成。
4. 點進該帳戶 → 金鑰 → 新增金鑰 → JSON，瀏覽器會下載一個 `.json`。
5. n8n → Credentials → Create → 搜尋 **Google Service Account API**（搜「Google Sheets」只會出現 OAuth2，不是這個）：
   - **Service Account Email**：JSON 裡 `client_email` 的值（先填這欄）。
   - **Private Key**：⛔ **不要手動從 JSON 複製**——手動複製會把換行變成 `\n` 字樣，n8n 會報「secretOrPrivateKey must be an asymmetric key」。改用本技能附的小程式，它會把私鑰以正確格式放進剪貼簿、畫面不顯示金鑰：
     1. 開「終端機」（Mac：在 Spotlight 搜「終端機」）。
     2. 輸入 `python3 `（後面留一個空格），把本技能 `scripts/copy_private_key.py` 檔案拖進視窗，再打一個空格，把下載的 JSON 檔也拖進視窗，按 Enter。
     3. 看到「格式 OK」後回到 n8n，點 Private Key 欄 → 全選（Mac ⌘A／Windows Ctrl+A）→ 貼上（⌘V／Ctrl+V）→ Save，看到 **Connection tested successfully**。
     - Windows：小程式會改用系統的 `clip` 放進剪貼簿——**本課只在 Mac 實測過，Windows 未驗證**，失敗請找老師。
   - Impersonate a User、Set up for use in HTTP Request node：保持關閉。
6. 收尾：清空剪貼簿（Mac 在終端機執行 `pbcopy < /dev/null`；Windows 隨便複製一段無關文字蓋掉即可），**下載的 JSON 丟垃圾桶**——它等同密碼。

## 四、試算表（只做一步，其餘自動）

1. 開一張**空白** Google 試算表，取好名字。
2. 右上角「共用」→ 加入服務帳戶 email（第三節的 `client_email`）→ 權限「編輯者」→ 傳送（建議取消「通知使用者」；畫面以實際為準）。
3. 在 n8n 匯入 `templates/level0-setup-sheet.json`（課程範本 0｜建立 LINE 助理試算表）：
   - 打開「貼上試算表網址」節點，把試算表完整網址貼到 `spreadsheetUrl`。
   - 四個 Google Sheets 節點（確保有問答分頁、初始化問答分頁、確保有紀錄分頁、初始化紀錄分頁）都選 Google 服務帳戶憑證。
   - 按一次「執行 workflow」，最後一個節點會顯示「已建立：問答、紀錄」。
   - 它會建好分頁「問答」（關鍵字、回覆＋一列範例）與「紀錄」（時間、使用者訊息、回覆、是否待人工）。
   - 新試算表若有預設分頁（如「工作表1」），留著即可，範本不會刪它（全新空白表的情況本課未實測）。
   - 兩個分頁都已存在時再執行，會顯示「兩個分頁都已存在，未變更」，不覆蓋既有資料（實測過）。只有其中一個已存在的情況本課未實測。
   - 服務帳戶不能自己開新試算表（實測回 403，原因未證實），所以「開空白表＋共用」這一步一定由學員做。
4. 之後學員只要在「問答」分頁加自己的關鍵字與回覆；「紀錄」由關卡 5 自動寫入。
5. 試算表會存客人訊息：**不要設成「知道連結的人都能檢視」**。

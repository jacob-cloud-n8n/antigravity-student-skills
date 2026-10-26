---
name: line-assistant-setup
description: 帶學員把「n8n LINE 官方助理」五關範本接上真的帳號與憑證：LINE Messaging API token、OpenCode Zen key、Google 服務帳戶與試算表，最後用手機傳一句話驗收。當使用者說「幫我串 LINE 助理」「設定 LINE 官方帳號」「n8n 接 LINE」「建 Google 服務帳戶」「試算表要怎麼接 n8n」「LINE 助理沒反應」時使用。不涵蓋：架設 n8n 本身、LINE 簽章驗證、正式上線前的資安檢查。
---

# LINE 官方助理：帳號與憑證設定

帶學員把五關範本（`templates/level0`～`level5`）接上自己的 LINE 官方帳號、AI 與 Google 試算表。學員是非工程師，**一次只給一個動作**，做完看到畫面再給下一步。

## 成功標準

1. 學員用手機傳一句話給自己的官方帳號，收到助理回覆（證據：學員的聊天截圖）。
2. 三把密鑰都只存在 n8n 憑證頁，**沒有出現在對話、截圖、檔案或 GitHub**。
3. 試算表的分頁與表頭是「關卡 0 建表」自動建的，學員沒有手動輸入表頭。
4. 學員說得出：要升下一關，先停用上一關。

## 開場必講兩件事

- **密鑰不給 agent 看**：token、key、私鑰都直接貼進 n8n 憑證頁。學員若傳來含密鑰的截圖，請他到後台重新發行那把密鑰，舊的作廢。
- **資料流向**：關卡 4、5 會把客人訊息送到 AI（範本預設模型 `glm-5.3`）。選模型前，當天到 https://opencode.ai/docs/zen/ 的 Privacy 節確認該模型不在「會保留或拿去訓練」的例外清單；清單會變，不要靠記憶。

## 流程（照順序，一步一確認）

| 步驟 | 學員做什麼 | 細節 |
|---|---|---|
| 1 | 建 LINE 官方帳號、開 Messaging API、發 token | [references/line-account.md](references/line-account.md) |
| 2 | 申請 OpenCode Zen key | [references/credentials.md](references/credentials.md) 第一節 |
| 3 | 在 n8n 建兩個 Header Auth 憑證（LINE、Zen） | [references/credentials.md](references/credentials.md) 第二節 |
| 4 | 匯入關卡 1、綁 LINE 憑證、啟用 | 範本在 `templates/`。n8n 新增 workflow → 右上角選單 Import from File（畫面路徑未實測）；打開 `LINE 回覆 API` 節點選 LINE 憑證；匯入後預設未啟用，要手動切成啟用 |
| 5 | LINE 後台填 Webhook 網址、Verify、關自動回應 | [references/line-account.md](references/line-account.md) 第三節 |
| 6 | **手機傳一句話**，收到回覆＝關卡 1 打通 | 沒回覆 → [references/troubleshooting.md](references/troubleshooting.md) |
| 7 | 啟用 Sheets API → 建 Google 服務帳戶 → 建 n8n 憑證 | [references/credentials.md](references/credentials.md) 第三節 |
| 8 | 開一張**空白**試算表、共用給服務帳戶，跑「關卡 0 建表」 | [references/credentials.md](references/credentials.md) 第四節 |
| 9 | 依序升級關卡 2～5，每關手機測一次 | 升級前先停用上一關；關卡 3～5 的 `讀取 FAQ 試算表`（讀的是「問答」分頁）與關卡 5 的 `寫入對話紀錄` 都要貼同一張試算表網址、選服務帳戶憑證 |

## 規矩

- **一次只啟用一關**：五關共用同一個 webhook 路徑 `line-assistant`，LINE 端網址設一次就好，但同時只能有一關是啟用狀態。
- **先用模擬訊息判斷 token 對不對**：還沒動手機之前，可以在 n8n 用假的 LINE 事件測。LINE 回 **400 Invalid reply token**＝token 正確（只是回覆碼是假的）；回 **401**＝token 貼錯。
- **動手前先核對帳號**：官方帳號在不同後台顯示的名稱可能不同，改設定前先核對左上角的 @ID 是不是這次要用的那個。
- **看不到畫面就不給步驟**：各家後台會改版，學員畫面跟本技能不同時，請他截圖（遮住密鑰）再往下。

## 不做的事

- 不替學員架 n8n；n8n 已經有（課堂提供或自己架好）才用本技能。
- 不做 LINE 簽章驗證（進階選修，另議）。
- 不把任何密鑰寫進檔案、對話或 repo。

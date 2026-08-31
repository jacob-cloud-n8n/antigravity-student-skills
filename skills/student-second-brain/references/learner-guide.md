# 學員使用指南

只有在向學員介紹第二大腦、安裝 Obsidian、提供常用說法或理念來源時讀取本檔。

## 一句話理解

第二大腦不是某個軟體，而是一個固定的本機資料夾：原始資料有入口、AI 整理後有位置、成果不只留在聊天裡、下次可以從日誌接著做。

## Obsidian 的定位

Obsidian **不是必要條件，但建議安裝**。第二大腦本體是 Markdown 檔案；Obsidian 負責：

- 舒服地閱讀與搜尋 Markdown。
- 顯示 `[[雙向連結]]`、反向連結和關係圖。
- 讓學員在 AI 修改內容時同步瀏覽與檢查。
- 透過 Web Clipper 把網頁轉成 Markdown 原始資料。

沒有安裝 Obsidian 時，Codex 與一般檔案管理器仍可使用整套流程。

官方資源：

- Obsidian 下載：https://obsidian.md/download
- Obsidian Web Clipper：https://obsidian.md/zh/clipper

若使用 Web Clipper，目標資料夾應設為 `Clippings/<專案名稱>`，不要直接存進 `知識庫`。

## 理念與參考

- Andrej Karpathy，LLM Wiki 原始提案：https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- 參考影片（14:30 起的自動更新與 Agent 規則）：https://youtu.be/hOJsRc9Ju7k?t=870

Karpathy 原文描述的是一種可調整的模式，不是一套必須照抄的固定架構。本學員版採用：不可變原始來源、AI 維護知識、AGENTS.md 規則、index、append-only log、收錄／查詢／健檢；另外加入創作庫、工作接續與資料告知流程。

## 常用說法

學員不需要背斜線指令，直接說：

- 「初始化我的第二大腦。」
- 「把這份資料收進二腦，放在＿＿專案。」
- 「整理這份資料，並保留來源。」
- 「查詢我對＿＿知道什麼，請附來源。」
- 「把剛才的成果保存起來。」
- 「檢查第二大腦有沒有重複、過期或來源不明。」
- 「開工。」
- 「收工。」

## 建議學習順序

1. 先建資料夾並放入一份真實但適合交給 AI 的資料。
2. 比較「沒讀二腦」與「讀過二腦」的回答差異。
3. 完成一次收錄、整理、保存成果、收工、隔天開工。
4. 使用一至兩週後再決定是否安裝 Web Clipper、Git 或每週提醒。

不建議一開始就加入 embeddings、向量資料庫或每日自動排程。

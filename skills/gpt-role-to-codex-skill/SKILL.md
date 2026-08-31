---
name: gpt-role-to-codex-skill
description: 把 ChatGPT 自訂 GPT、ChatGPT 專案裡的顧問／指導員角色，或 Gemini Gem 轉成可安裝的 Codex Skill。當使用者說「把 GPT 搬到 Codex」「把顧問角色匯入」「Gem 轉 Skill」「昨晚沒轉完角色」「Instructions 要怎麼轉」時使用。可接受貼上的文字、匯出檔、附件或截圖；會分離角色規則、知識資料、示範案例與平台專屬功能，建立 SKILL.md 並驗證。不是用來搬移整個帳號、完整聊天紀錄或秘密金鑰。
---

# GPT／Gem 角色轉 Codex Skill

把使用者在 ChatGPT 或 Gemini 已調好的顧問、教練、指導員角色，整理成可重複使用的 Codex Skill。對非技術學員使用日常語言，不要求他們先懂檔案格式。

## 先說清楚一件事

`Instructions` 是角色的「工作說明與規則」，不是 ChatGPT 裡建立的資料夾。

- 自訂 GPT：通常包含 Instructions、Knowledge、Conversation starters、Actions。
- ChatGPT 專案：通常包含 Project instructions、專案檔案與代表性對話。
- Gemini Gem：通常包含 Instructions、上傳檔案與平台擴充功能。

只取得 Instructions 也能先建立可用的文字型 Skill；其他資料可以之後補進來。

## 成功標準

完成時必須同時符合：

1. 角色在 Codex 中的任務、語氣、流程、限制與輸出格式清楚可執行。
2. 參考資料與操作規則分離，避免把大量知識塞進 `SKILL.md`。
3. ChatGPT／Gemini 專屬功能被明列為「已轉換」「需替代連接」「無法直接搬移」。
4. 不複製 API key、密碼、Cookie、私人連結或不必要個資。
5. 至少以三個代表性情境檢查觸發、行為與邊界。

## 工作流程

### 1. 收件，不考學生

先接受使用者手上現有的任何材料：貼文、文件、JSON、截圖或口述皆可。不要一開始要求完整匯出。

若資料不足，只追問會改變結果的項目，最多三題：

1. 請貼上或上傳角色的 Instructions；找不到時可傳設定畫面截圖。
2. 這個角色要「自己到處用」還是「只在目前專案用」？未指定時，顧問／指導員預設為個人 Skill。
3. 希望它叫什麼名字？名稱明顯時直接推定，不再追問。

若使用者不知道去哪裡找資料，提供對應平台的簡短指引；需要空白收件表時才讀取 `references/intake-template.md`。

### 2. 建立轉換清單

先把來源整理成下列四類，並用簡短表格向使用者說明：

| 類別 | 放置位置 | 處理原則 |
|---|---|---|
| 角色規則 | `SKILL.md` | 保留任務、流程、語氣、限制、輸出格式；改寫成可執行指令 |
| 知識資料 | `references/` | 只放長篇或需要按需讀取的內容；保留來源與日期 |
| 示範案例 | `references/examples.md` 或 `SKILL.md` | 留下少量能界定品質的輸入／輸出特徵，不大量複製聊天 |
| 平台功能 | 遷移報告 | Actions、瀏覽、Drive／Gmail 等先盤點；只有現有工具真的可替代才標成已接上 |

不要把整段舊對話直接當 Instructions。只提取跨情境仍成立的偏好、決策規則與好案例；一次性的聊天內容不要搬。

### 3. 安全與相容性檢查

寫檔前檢查：

- 發現 API key、token、密碼、Cookie、私人憑證時停止複製，改成環境變數名稱或「待連接」說明。
- 發現學生、客戶、病患或其他個資時，只保留完成角色所需的最小資訊；測試案例改用虛構資料。
- 不宣稱已搬移聊天記憶、帳號設定、付費功能或平台內建工具。
- Actions、外部 API、Gmail、Drive、Notion 等能力必須逐項對照目前可用的 connector、plugin、MCP 或 CLI。沒有實際連接與測試，就標示「需另接」。
- 遇到醫療、法律、財務等高風險角色，把查證、來源與人工覆核要求寫入限制。

### 4. 決定安裝範圍

- **個人 Skill（預設）**：適合顧問、教練、指導員等跨專案角色。標準位置為 `$HOME/.agents/skills/<skill-name>/`。
- **專案 Skill**：只服務某門課或某個 repo。放在專案根目錄 `.agents/skills/<skill-name>/`。

若環境另有既定 Skill 目錄或團隊規則，遵循該環境規範。不要覆蓋同名 Skill；先比較既有內容，再讓使用者選擇更新或改名。

### 5. 產生 Skill

建立 kebab-case 英文名稱，只用小寫英文字母、數字與連字號。資料夾名稱必須與 frontmatter 的 `name` 相同。

最小結構：

```text
<skill-name>/
└── SKILL.md
```

內容較多時才增加：

```text
<skill-name>/
├── SKILL.md
└── references/
    ├── source-profile.md
    └── examples.md
```

`SKILL.md` 必須包含：

- YAML frontmatter：`name`、`description`。
- description 同時寫清楚「做什麼」與「何時觸發」。
- 角色目標、工作流程、輸出格式、限制與拒絕範圍。
- 對 references 的精準讀取條件；沒有必要就不要建立空資料夾。

改寫原始 Instructions 時：

- 保留使用者真正需要的行為，不逐字保留平台話術。
- 把模糊人格形容詞改成可觀察行為。例如「很有耐心」改成「一次只問一題，先用白話解釋，再給範例」。
- 把固定回覆格式寫成小模板；不要把每次都不同的內容硬編進去。
- 不替使用者捏造經歷、專業資格、知識來源或工具能力。
- `SKILL.md` 保持精簡；長篇背景、教材與案例移到 references。

### 6. 驗證

若環境有 Skill validator，執行它。無 validator 時至少檢查：

- `SKILL.md` 存在，frontmatter 可解析。
- `name` 與資料夾同名，description 包含觸發情境。
- 所有相對連結指向存在的檔案。
- 新檔沒有真實秘密值與不必要個資。

再用三種情境做行為驗收：

1. **典型任務**：角色應依指定流程完成工作。
2. **資訊不足**：角色應問必要問題，不自行腦補。
3. **越界要求**：角色應遵守限制，並指出可行替代方案。

驗收看行為特徵，不要求逐字一致。若任一情境失敗，修正 Skill 後重測。

## 交件格式

完成後用白話回報：

```markdown
✅ 已建立：<skill-name>
📍 安裝位置：<完整路徑>
📦 已轉換：角色規則／知識資料／示範案例
🔌 需另接：<沒有就寫「無」>
🧪 驗證：結構檢查 + 3 個情境通過／未通過項目

在 Codex 中可以這樣叫它：
「請使用 <skill-name> 幫我……」
```

若尚未寫入檔案，只能稱為「轉換草稿」，不可說已安裝。

## 不該做的事

- 不要求使用者先找到「ChatGPT 資料夾」；Instructions 本來就不是資料夾。
- 不把整個 ChatGPT／Gemini 帳號、全部聊天紀錄或模型能力說成可一鍵匯入。
- 不因缺少 Knowledge 檔就卡住；先完成 instruction-only 版本。
- 不把第三方 Actions 的秘密值寫進 Skill。
- 不把平台功能名稱原封不動搬過來，卻沒有對應工具與測試。
- 不為了看起來完整而建立沒內容的 scripts、assets 或 references。

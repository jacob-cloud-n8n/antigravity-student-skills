# 第二大腦專案範本

只有在初始化第二大腦或修補缺少的核心檔案時讀取。先掃描既有內容，只取需要的區塊；不得整份覆蓋已有的 `AGENTS.md`、`handoff.md`、索引或日誌。

## AGENTS.md 整合區塊

將下列區塊合併到既有 `AGENTS.md`；沒有該檔時才建立最小版。

```markdown
## 第二大腦

- 狀態：啟用
- 類型：學員共用二腦
- 原始資料：`Clippings/`
- 整理知識：`知識庫/`
- 創作成果：`創作庫/`
- 工作日誌：`工作日誌/log.md`
- 知識索引：`知識庫/index.md`

### 使用約定

- Clippings 原始資料只讀，不靜默改寫。
- 知識與成果寫入前先預覽，取得確認後才保存。
- 知識頁保留來源；推測、衝突與待確認事項明確標示。
- 工作日誌只能追加；handoff.md 保持精簡，供下一次開工接續。
- 個資與內部資料先告知並提供代號化選項；使用者確認有權且接受風險後才繼續。
- API key、token、密碼、私鑰、Cookie、驗證碼與助記詞禁止收錄。
```

## handoff.md

```markdown
# 工作交接

## ⏯️ 目前做到哪

- 第二大腦初始化完成。

## 🚦 目前狀態

- 可開始放入第一份 Clippings。

## ➡️ 下一步

1. 選一份真實且適合交給 AI 的資料。
2. 說「把這份資料收進二腦」。

## ⚠️ 注意事項

- 尚未建立的專案分類會在第一次需要時再建立。

## 🕐 最後更新

- 日期：<YYYY-MM-DD>
- 更新者：<Agent @ 電腦名>
```

## 知識庫/index.md

```markdown
# 知識庫索引

> AI 查詢時先讀本頁，再深入相關知識；不要一開始重讀全部 Clippings。

## 共用

目前尚無知識頁。

## 專案

第一次整理專案資料時再建立分類。
```

索引項目格式：

```markdown
- [[頁面名稱]] — 一句話摘要；更新：YYYY-MM-DD；來源：N 份
```

## 工作日誌/log.md

```markdown
# 第二大腦工作日誌

> Append only：只在底部追加，不改寫既有紀錄。

## [<YYYY-MM-DD>] init | 建立第二大腦

- 建立最小資料夾、索引與開工／收工接續規則。
```

後續紀錄標題格式：

```markdown
## [YYYY-MM-DD] ingest | <來源名稱>
## [YYYY-MM-DD] query | <問題摘要>
## [YYYY-MM-DD] lint | <檢查範圍>
## [YYYY-MM-DD] output | <成果名稱>
```

## 知識頁 metadata

```markdown
---
title: <主題>
project: <專案或共用>
type: knowledge
status: active
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources:
  - <Clippings 相對路徑或公開網址>
---
```

若學員確認使用未代號化的個人／內部資料，再加入：

```yaml
privacy_decision: user-confirmed-original-data
```

不要把敏感內容本身複製進 metadata 或工作日誌。

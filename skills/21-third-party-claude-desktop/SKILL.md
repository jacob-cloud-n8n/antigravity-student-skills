---
name: third-party-claude-desktop
description: 透過 CC Switch 將第三方模型（DeepSeek / Kimi）接入 Claude Desktop 的完整懶人包。當使用者要求「DeepSeek 接入 Claude Desktop」「Kimi 接入 Claude Desktop」「用第三方模型跑 Claude Desktop」時使用。
version: 1.1.0
author: MiCode
tags: [deepseek, kimi, claude-desktop, cc-switch, proxy, api, third-party]
---

# 第三方模型 × Claude Desktop 接入懶人包

透過 CC Switch 本地代理，將 DeepSeek / Kimi 等第三方模型接入 Claude Desktop，實現以第三方模型驅動 Claude Desktop 介面。

## 適用情境與觸發條件

當使用者說「DeepSeek 接入 Claude Desktop」、「Kimi 接入 Claude Desktop」、「用第三方模型跑 Claude Desktop」、「CC Switch 設定 DeepSeek」或「換掉 Claude 的模型」時，自動載入此技能。

## 運作原理

```
Claude Desktop (Anthropic API 格式)
    ↓ CC Switch 本地代理 (127.0.0.1:15721)
    ↓ 自動轉換為目標模型的 Anthropic 格式
DeepSeek / Kimi API (各自的 Anthropic 端點)
```

Claude Desktop 只認識三種模型角色（Sonnet / Opus / Haiku），CC Switch 負責將這些角色映射到實際的第三方模型。

## 前置需求

| 項目 | 說明 |
|------|------|
| macOS | 12 (Monterey) 以上 |
| Claude Desktop | 從 [claude.ai/download](https://claude.ai/download) 下載安裝 |
| CC Switch | 從 [GitHub Releases](https://github.com/farion1231/cc-switch/releases/latest) 下載 DMG 安裝 |
| API Key | 從對應平台取得（見下方模型表） |

## 支援模型一覽

| 模型 | Anthropic 端點 | API Key 取得 | 備註 |
|------|---------------|-------------|------|
| **DeepSeek V4 Pro** | `https://api.deepseek.com/anthropic` | [platform.deepseek.com](https://platform.deepseek.com) | 最強能力，適合複雜任務 |
| **DeepSeek V4 Flash** | `https://api.deepseek.com/anthropic` | 同上 | 速度優先，適合日常問答 |
| **Kimi K2.5** | `https://api.moonshot.cn/anthropic` | [platform.moonshot.cn](https://platform.moonshot.cn) | 多模態理解，256K 上下文 |
| **Kimi K2.7 Code** | `https://api.moonshot.cn/anthropic` | 同上 | Coding 專用模型 |

> 💡 CC Switch 會自動在 Endpoint 後補上 `/v1/messages`，填入基礎網址即可。

> ⚠️ 只有提供 Anthropic 相容端點的模型才能接入 Claude Desktop。僅支援 OpenAI 格式的模型無法直接使用。

> ⚠️ **重要**：不要手動編輯 `~/Library/Application Support/Claude-3p/configLibrary/` 裡的 JSON 設定檔。CC Switch 有自己的狀態管理，手動修改會導致衝突或崩潰。所有設定都透過 CC Switch 介面操作。

## 安裝步驟

### Step 1：安裝 CC Switch

```bash
# 方法 A：Homebrew（推薦）
brew install --cask cc-switch

# 方法 B：手動下載 DMG
# 從 https://github.com/farion1231/cc-switch/releases/latest 下載 macOS DMG
# 拖入 Applications 即可
```

### Step 2：新增 Provider

1. 開啟 CC Switch
2. 左側選擇 **Claude Desktop** 應用
3. 點右上角 **`+`** 新增 Provider
4. Preset 下拉選選擇模型（DeepSeek / Kimi）
5. 填入 **API Key**
6. 確認 Endpoint（見上方模型表）
7. 點 **Add**

### Step 3：設定 Model Mapping（模型映射）

1. 在 Provider 上點 **Edit**（鉛筆圖示）
2. 確認 **需要模型對應**（Needs model mapping）已開啟
3. 在 **模型映射** 區塊填入：

#### DeepSeek 配置

| 模型角色 | 選單顯示名稱 | 實際請求模型 |
|----------|-------------|-------------|
| Sonnet | DeepSeek V4 Pro | `deepseek-v4-pro` |
| Opus | DeepSeek V4 Pro Max | `deepseek-v4-pro` |
| Haiku | DeepSeek V4 Flash | `deepseek-v4-flash` |

#### Kimi 配置

| 模型角色 | 選單顯示名稱 | 實際請求模型 |
|----------|-------------|-------------|
| Sonnet | Kimi K2.5 | `kimi-k2.5` |
| Opus | Kimi K2.7 Code | `kimi-k2.7-code` |
| Haiku | Kimi K2.5 | `kimi-k2.5` |

> 💡 Opus 和 Haiku 留空會自動沿用 Sonnet 的模型。如果只有一種模型，只填 Sonnet 即可。

4. 點 **Save**

### Step 4：啟用代理與路由

1. 到 **Settings → 路由**
2. 確認 **本地路由** 狀態為「執行中」
3. 確認 **路由總開關** 已開啟
4. **路由啟用** 區塊中，**Claude Desktop** 開關打開

> 💡 第 5 項「在主頁面顯示本地路由開關」只需首次設定時開啟，之後不用再改。

### Step 5：啟用 Provider

1. 回到 Claude Desktop 頁面
2. 在 Provider 上點 **Enable**
3. **完全退出 Claude Desktop**（Cmd+Q）
4. 重新開啟 Claude Desktop

## 驗證

在 Claude Desktop 輸入：`請問你的模型是什麼？`

如果回覆提到對應的模型名稱，表示接入成功。

## 切換模型

在 CC Switch 裡可以新增多個 Provider（DeepSeek + Kimi），要切換時：

1. 在 CC Switch 裡選擇要使用的 Provider
2. 點 **Enable**
3. 重啟 Claude Desktop

## 常見問題

### Q：顯示「currently unavailable」但可以正常對話？

這是 CC Switch 健康檢查的警告，**不影響實際使用**。代理轉發正常即可忽略。

### Q：顯示「Can't reach 127.0.0.1:15721」？

CC Switch 代理沒有啟動。打開 CC Switch → Settings → 路由 → 開啟路由總開關。

### Q：模型選擇器有兩個同名選項？

因為 Sonnet 和 Opus 都映射到同一個模型。可以在 CC Switch 裡把其中一個的「選單顯示名稱」改不同名稱。

### Q：回覆說自己是 Claude 而不是第三方模型？

正常現象。第三方模型在 Anthropic 格式下會回報為 Claude 模型名稱，但實際運算的是第三方模型。

### Q：要切換回 Claude 官方模型？

1. 在 CC Switch 裡選擇 **Claude Desktop Official** provider
2. 點 **Enable**
3. 重啟 Claude Desktop

### Q：可以同時用多個第三方模型嗎？

可以。在 CC Switch 裡新增多個 Provider，要切換時 Enable 對應的 Provider 即可。但每次切換都需要重啟 Claude Desktop。

## 注意事項

- CC Switch 必須保持開啟，關閉後 Claude Desktop 無法連接第三方模型
- 此設定僅影響 Claude Desktop，不影響 Claude Code CLI
- API 費用依各平台官方定價計算
- 切換 Provider 後必須重啟 Claude Desktop（不支援熱重載）
- **不要手動編輯** `configLibrary/` 裡的 JSON 設定檔，所有操作都透過 CC Switch 介面完成

## 系統支援

| 系統 | Claude Desktop | CC Switch | 3P 設定寫入 |
|------|---------------|-----------|------------|
| macOS | ✅ | ✅ | ✅ |
| Windows | ✅ | ✅ | ✅ |
| Linux | ❌ | ✅ | ❌ |

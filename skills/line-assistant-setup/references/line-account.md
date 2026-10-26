# LINE 官方帳號與 Messaging API

> 依 2026-10 實際操作整理。後台會改版；學員畫面不同時，以實際畫面為準，請他截圖（遮住密鑰）再判斷。

## 一、建官方帳號

1. 到 LINE Official Account Manager（https://manager.line.biz/）建立官方帳號，方案選免費的「輕用量」即可。
2. **帳號名稱不能含「LINE」字樣**，會被擋下。
3. 記下帳號的 **@ID**（例：`@abc1234`）。之後所有後台都用 @ID 核對，不要只看名稱——同一個帳號在不同後台顯示的名稱可能不一樣。

## 二、開 Messaging API、發 token

1. 官方帳號後台 → 設定 → Messaging API → 啟用，選或建立一個 Provider。
2. 到 LINE Developers（https://developers.line.biz/console/）→ 該 Provider → 這個帳號的 channel → **Messaging API** 分頁。
3. 拉到最下面 **Channel access token (long-lived)** → **Issue**。
4. 這串 token 只貼進 n8n 憑證頁（見 credentials.md 第二節），不要複製到其他地方。

⚠️ Basic settings 分頁的 **Channel secret** 也是密鑰。截圖時不要拍到；若不小心外流，按 Reissue 重新發行。

## 三、Webhook 與自動回應

前提：n8n 裡關卡 1 已綁好 LINE 憑證並**啟用**。

1. 在 n8n 打開關卡 1 的 Webhook 節點，複製 **Production URL**（路徑是 `/webhook/line-assistant`）。
   - ⛔ 不要用 Test URL（`/webhook-test/...`）：測試時會動，正式啟用後就沒反應。
2. LINE Developers → Messaging API 分頁 → **Webhook settings** → Edit，貼上網址 → Update。
3. 打開 **Use webhook**，按 **Verify**，要看到 **Success**。
4. 回官方帳號後台（manager.line.biz）→ 先核對左上角 @ID 是對的帳號 → **自動回應訊息**頁（入口名稱可能隨改版不同，找不到就截圖） → 把預設那則（通常是「感謝您的訊息！」）的「使用」開關關掉。
   - 不關的話，同一句話會被回兩次（一次是 LINE 自動回應、一次是你的助理）。
5. 用手機傳一句話給官方帳號（例：「營業時間」），收到助理回覆＝打通。

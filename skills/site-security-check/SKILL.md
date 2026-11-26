---
name: site-security-check
description: 幫網站主人對「自己的網站」做一次被動、低流量的基本資安健檢（連線與網域、不該公開的檔案、跨網域存取、安全標頭），用白話報告結果與下一步找誰修。當使用者說「檢查我的網站安全」「網站資安健檢」「幫我看我的網站有沒有漏洞」「我網站的 .env 有沒有外洩」「我網站的憑證什麼時候到期」時使用。
version: 1.0.0
author: 小牧人工作室
tags: [security, website, 資安健檢, https, dns, cors, 網站主人自查]
---

# 網站資安基本健檢（網站主人自查版）

幫小店老闆、上班族檢查**自己的網站**有沒有幾個最常見、最容易出事的設定問題。
全程只做「看一眼」等級的檢查：少量一般網頁請求與 DNS 查詢，不攻擊、不猜密碼、不灌流量。
最後產出一份看得懂的報告，每一項都寫清楚「要不要緊」和「拿去問網站工程師的一句話」。

---

## 第 0 步：範圍閘門（必做，沒過就不准動手）

Agent 在送出任何請求之前，**一定要先做完下面三件事**：

1. **問網域**：「請告訴我要檢查的網址，例如 `shop.example.com.tw`。」
   - 把使用者給的內容整理成單純網域（拿掉 `https://`、路徑、結尾斜線），唸回去給使用者確認。
2. **要求授權確認**：請使用者明確回覆這句話（或意思相同的話）：
   > 「這是我擁有，或我有書面授權可以檢查的網站。」
   - 使用者沒有確認、語氣含糊（「應該是吧」「朋友的」「競爭對手的」），**一律不動手**，請對方先取得網站主人的書面同意。
3. **講清楚法律風險**：告訴使用者——對別人的網站做這類檢查，在台灣可能觸犯**刑法第 358 條以下的妨害電腦使用罪**（刑法第三十六章）。就算只是「看看」，沒有授權也不要做。

**範圍規則（整個流程都適用）**：
- 一次只檢查使用者給的**那一個網域**。
- **不做子網域列舉**（子網域＝`www.`、`api.` 這類掛在主網域前面的網址），不查憑證公開紀錄去挖其他網址，不碰第三方網域（金流、CDN、外部字型等）。
- 如果使用者給的是 `example.com`，而網站其實在 `www.example.com`，要**先問**：「也要一起檢查 `www.example.com` 嗎？它也是你的嗎？」確認後才算在範圍內。
- 轉址到其他網域時，只記錄「轉去哪裡」，**不跟過去檢查**。

---

## 流量與禮貌規則

- **只用**：少量 `GET`／`HEAD` 網頁請求（就是瀏覽器平常打開網頁的那種請求）、`dig` DNS 查詢、`openssl s_client` 看一次憑證。
- **不做**：暴力猜測、大量路徑字典、漏洞利用、繞過登入、注入測試（往表單或網址塞惡意字串）、跑掃描器批次掃描、下載整個 `.git` 或整份備份檔。
- **每個網頁請求之間停 1 秒**（`sleep 1`）。
- **總請求數上限 40 次**（網頁請求＋DNS 查詢合計）。照本流程大約 25～30 次。Agent 要自己記數，到上限就停。
- 收到 `429`（請求太多）或連續 `403`（被防火牆擋）：**立刻停**，報告「網站有防護擋下檢查」，**不要換方法繞過**。
- 每個請求都設逾時：`--max-time 10`。

先設定兩個變數，後面指令都會用到：

```bash
D="使用者確認過的網域"          # 例：shop.example.com.tw
UA="site-security-check (owner self-check)"
```

---

## 第一類：連線與網域

### 1-1　HTTPS 強制轉址
HTTPS＝網址前面的鎖頭，代表你和網站之間的資料有加密，別人在中間偷看不到。

```bash
curl -s -o /dev/null --max-time 10 -A "$UA" -w '%{http_code} → %{redirect_url}\n' "http://$D/"
sleep 1
```
判讀：
- 🟢 回 `301`／`308`（或 `302`），且轉到 `https://` 同一個網域。
- 🟡 有轉，但轉到別的網域或先轉到另一個 http 網址。
- 🔴 回 `200`：沒加密的版本也能正常瀏覽，客人在咖啡廳 Wi-Fi 上填的資料可能被偷看。

### 1-2　憑證到期日
憑證＝網站的「身分證」，過期時瀏覽器會跳出大紅色警告，客人會直接嚇跑。

```bash
echo | openssl s_client -connect "$D:443" -servername "$D" 2>/dev/null \
  | openssl x509 -noout -enddate -issuer
```
沒有 `openssl` 時的替代法（也能看到到期日）：
```bash
curl -svI --max-time 10 -A "$UA" "https://$D/" 2>&1 | grep -iE 'expire date|issuer'
sleep 1
```
選用、需另外安裝：`testssl.sh`（例如 `brew install testssl`）能看得更細（加密方式強弱等），**但沒有它也能完成本健檢**。若使用者已裝，只跑一次 `testssl.sh --fast "$D"`，不要批次重跑。

判讀：🟢 還有 30 天以上；🟡 剩 14～30 天；🔴 剩不到 14 天、已過期，或憑證上的名字跟網域對不起來。
小提醒：多數架站平台（Wix、Shopify、SHOPLINE、Cloudflare 等）會自動續約，到期日很近通常代表自動續約壞了。

### 1-3　HSTS
HSTS＝網站告訴瀏覽器「以後一律用加密連線來找我」，防止被人騙回沒加密的版本。

```bash
curl -sI --max-time 10 -A "$UA" "https://$D/" > /tmp/ssc_headers.txt   # 這份標頭後面 4 類共用
grep -i 'strict-transport-security' /tmp/ssc_headers.txt
sleep 1
```
判讀：🟢 有，且 `max-age` 至少 `31536000`（一年）；🟡 沒有或時間很短。這項**不會單獨列 🔴**——缺 HSTS 是「加強防護沒做」，不是已經破洞。

### 1-4　寄信冒名防護：SPF、DMARC、DKIM
這三個 DNS 設定決定**別人能不能假冒你的網域寄信**。例如詐騙集團用 `service@你的網域` 寄「付款失敗請重新刷卡」給你的客人。
- **SPF**：公告「哪些主機可以代表我寄信」。
- **DKIM**：每封信蓋上數位印章，收信方可以驗章。
- **DMARC**：告訴收信方「驗不過的信要怎麼處理」（不管、丟垃圾桶、直接退回）。

```bash
dig +short TXT "$D" | grep -i 'v=spf1'
dig +short TXT "_dmarc.$D"
for s in google default selector1 selector2 k1; do      # 只查 5 個常見印章名稱
  r=$(dig +short TXT "$s._domainkey.$D"); [ -n "$r" ] && echo "DKIM 找到：$s"
done
```
⚠️ 網站若是子網域（例如 `shop.example.com`），寄信設定通常放在主網域（`example.com`）：子網域查不到時，**先問使用者主網域也是不是他的**，確認後把上面三行的 `$D` 換成主網域再查一次（只查 DNS，不對主網域發網頁請求）。DMARC 沒設在子網域時，收信方會沿用主網域的設定。

判讀：
- SPF：🟢 有，結尾是 `-all` 或 `~all`；🔴 結尾是 `+all`（等於任何人都能用你的名義寄信）；🟡 沒有 SPF。
- DMARC：🟢 `p=quarantine` 或 `p=reject`；🟡 `p=none`（只觀察、不擋）或完全沒有。
- DKIM：🟢 有找到；🟡 這 5 個名稱都沒找到——**不代表一定沒設**，印章名稱每家郵件服務不同，請到郵件服務後台確認。
- 這網域**完全不寄信**的話，建議設 `v=spf1 -all` 加 `p=reject`，直接宣告「我不寄信，冒名的一律退」。
- 只看設定**不等於**證明真的能被冒用（收信端如 Gmail 還有自己的過濾）。本健檢只報設定，不寄任何測試信。

---

## 第二類：不該公開的檔案

網站上線時，有時會不小心把設定檔、版本紀錄、備份一起放上去，任何人知道網址就能下載。

### 2-0　先量「找不到的頁面長什麼樣」（防誤報用）
很多現代網站（SPA，單頁式網站）**任何網址都會回首頁**，狀態碼一樣是 `200`。所以「回 200」不等於檔案存在，要比對內容。

```bash
probe() {  # $1=路徑  $2=這種檔案應有的內容特徵（正規表示式）
  resp=$(curl -s --max-time 10 -A "$UA" -r 0-65535 --max-filesize 2000000 \
         -w '\n__META__%{http_code} %{size_download} %{content_type}' "https://$D$1")
  meta=${resp##*__META__}; body=${resp%__META__*}
  hits=$(printf '%s' "$body" | grep -cE "$2")
  page=$(printf '%s' "$body" | head -c 400 | grep -ciE '<!doctype|<html')
  echo "$1 → $meta｜特徵行數=$hits｜像一般網頁=$page"
  unset resp body; sleep 1
}
probe "/ssc-not-exist-$RANDOM" 'x^'      # 基準：記下它的大小與類型
```
⛔ `probe` **刻意只印統計數字，不印檔案內容**。不要改成會把內容印出來的寫法。

### 2-1　固定檢查清單（共 12 條，不得自行加長）

```bash
probe "/.env"            '^[A-Za-z_][A-Za-z0-9_]*='
probe "/.env.production" '^[A-Za-z_][A-Za-z0-9_]*='
probe "/.env.local"      '^[A-Za-z_][A-Za-z0-9_]*='
probe "/.git/HEAD"       '^ref: '
probe "/.git/config"     '^\[core\]'
probe "/wp-config.php.bak" 'DB_PASSWORD|DB_NAME'
probe "/config.php.bak"  '\$[a-z_]+ *='
for f in /backup.zip /backup.sql /db.sql /site.zip /www.zip; do  # 備份檔只看標頭，不下載
  curl -sI --max-time 10 -A "$UA" "https://$D$f" | grep -iE '^HTTP|content-type|content-length' | tr '\n' ' '
  echo " ← $f"; sleep 1
done
```
白話：`.env`＝放密碼與金鑰的設定檔；`.git`＝程式的完整修改紀錄，拿到它常等於拿到整份原始碼。

判讀（**三個條件都要看**）：
- 🔴 **確定外洩**：狀態 `200` 或 `206`（`206`＝只取了前段，因為我們刻意只讀前 64KB；**兩者都代表檔案存在**）、「像一般網頁=0」、而且「特徵行數 ≥1」（例如 `.git/HEAD` 有 `ref:`、`.env` 有 `KEY=VALUE` 格式的行）。
- 🔴 **備份檔疑似外洩**：狀態 `200`，類型是 `application/zip`、`application/octet-stream`、`application/sql` 之類，且大小明顯不是網頁。
- 🟢 回 `404`／`403`，或回 `200`／`206` 但「像一般網頁=1」且大小跟 2-0 基準差不多（SPA 全站回首頁，不算外洩）。
- 🟡 回 `200`／`206`、不像網頁、但特徵對不上：標「無法判定」，請工程師親自看一眼。

### 2-2　JS 原始碼對照檔（source map，`.map`）
`.map` 檔原本是給工程師除錯用的，會把壓縮過的程式還原成可讀的原始碼。公開放著，等於把網站程式的設計圖交給所有人。

```bash
home=$(curl -s --max-time 10 -A "$UA" "https://$D/"); sleep 1
js=$(printf '%s' "$home" | grep -oE "src=[\"'][^\"']+\.js[\"']" | sed -E "s/^src=[\"']//;s/[\"']$//" | grep -vE '^(https?:)?//' | head -3)
printf '%s\n' "$js" | while read -r j; do   # 只取本站最多 3 支 JS，外部網域的跳過（逐行讀，zsh／bash 都適用）
  [ -z "$j" ] && continue
  p="/${j#/}"; p="${p#/./}"; [ "${p#/}" = "$p" ] && p="/$p"   # 補成「/路徑」
  curl -sI --max-time 10 -A "$UA" "https://$D$p.map" | grep -iE '^HTTP|content-type' | tr '\n' ' '
  echo " ← $j.map"; sleep 1
done
```
判讀：🔴 `.map` 回 `200` 且類型是 `application/json`（或 `octet-stream`）；🟢 `404`／`403` 或回的是網頁。
提醒工程師：**重新部署不會修好它**，檔名會變但新的 `.map` 可能照樣公開；要在建置設定裡關掉產生 `.map`，並清除 CDN 快取。
⛔ 找到也**不要下載 `.map` 內容來還原原始碼**，記錄「找到」即可。

### ⛔ 找到疑似外洩檔時的處理（硬規則）
1. **不要把檔案內容印在報告或對話裡**，包括密碼、金鑰、資料庫位址、片段也不行。只寫：「找到 `/.env`，含 N 行設定」（N 就是特徵行數）。
2. **不要再往下挖**：不下載整個 `.git`、不打開備份檔、不拿裡面的金鑰去試。
3. 立刻提醒使用者：「**請把這個檔案裡所有的密碼和金鑰全部換掉**（金流、寄信、資料庫、雲端服務都算），不是只把檔案刪掉——檔案可能早就被別人下載過了。」
4. 請工程師同時檢查網站存取紀錄，看這個網址以前有沒有被別人讀過。

---

## 第三類：跨網域存取（CORS）

CORS＝網站設定「哪些別的網站可以用你訪客的身分，來讀你網站上的資料」。設錯時，壞人做一個網頁，你的客人一打開，就可能在客人不知情下讀走他在你網站上的會員資料。

```bash
curl -s -o /dev/null -D - --max-time 10 -A "$UA" -H 'Origin: https://evil.example' "https://$D/" \
  | grep -i '^access-control-allow'
sleep 1
```
（如果使用者**自己提供**一個會員或 API 網址，例如 `/api/me`，可以對那一個網址再做一次同樣的請求；不要自己猜 API 路徑。）

判讀：
- 🔴 回 `Access-Control-Allow-Origin: https://evil.example`（把我們假造的來源原樣反射回來）**而且** `Access-Control-Allow-Credentials: true`。
- 🟡 有反射來源，但沒有 `Allow-Credentials: true`：目前讀不到登入後的資料，但設定太寬鬆。
- 🟢 沒有任何 `Access-Control-Allow-*` 標頭，或只允許自家網域，或是 `*`（`*` 時瀏覽器不會附帶登入身分；公開資料才用 `*` 沒問題）。
- 注意：`curl` 本身不受 CORS 限制，所以這只是「設定看起來有問題」，最終要請工程師用瀏覽器確認。本健檢**不做**瀏覽器實際讀取測試。

---

## 第四類：安全標頭快速表（只列有無，不嚇人）

用 1-3 存下的 `/tmp/ssc_headers.txt`，**不用再發請求**：

```bash
for h in content-security-policy x-frame-options x-content-type-options referrer-policy; do
  grep -qi "^$h:" /tmp/ssc_headers.txt && echo "有  $h" || echo "沒有 $h"
done
grep -qi 'frame-ancestors' /tmp/ssc_headers.txt && echo "有  frame-ancestors（在 CSP 裡）"
rm -f /tmp/ssc_headers.txt
```

| 標頭 | 白話作用 | 沒有時 |
|------|----------|--------|
| CSP（Content-Security-Policy） | 規定網頁只能載入哪些來源的程式，降低被塞惡意程式的傷害 | 🟡 |
| X-Frame-Options 或 CSP 的 frame-ancestors | 禁止別人把你的網頁偷偷嵌進他的網頁，騙客人點按鈕 | 🟡 |
| X-Content-Type-Options | 叫瀏覽器不要亂猜檔案類型 | 🟡 |
| Referrer-Policy | 客人點出去時，少透露你網站的網址細節 | 🟡 |

這四項有就 🟢、沒有就 🟡，**一律不列 🔴**。用架站平台（Wix、Shopify 等）的話很多標頭不能自己改，寫「平台管理，可詢問客服」即可。

---

## 報告格式

先給一句總結（例：「共檢查 14 項：🔴 1 項、🟡 4 項、🟢 9 項，總請求 27 次」），再用表格：

| 項目 | 狀態 | 白話說明 | 給網站工程師的一句修法 |
|------|------|----------|------------------------|
| HTTPS 強制轉址 | 🟢 正常 | 打 http 會自動轉到加密版 | — |
| 憑證到期日 | 🟡 建議 | 還剩 21 天到期 | 請確認憑證自動續約有在運作 |
| /.env | 🔴 要修 | 找到，含 12 行設定（內容未顯示） | 立即從網站移除並封鎖 `.env` 存取，所有金鑰全部更換 |
| DMARC | 🟡 建議 | 有設，但只觀察不擋冒名信 | 觀察兩週無誤後把 `p=none` 改成 `p=quarantine` |

狀態只用三種：**🔴 要修**（現在就可能出事）／**🟡 建議**（加強防護）／**🟢 正常**。

最後一段「**下一步找誰**」，依項目分類指給使用者：
- 憑證、HTTPS、安全標頭、外洩檔案、CORS → 架網站的工程師，或架站平台客服。
- SPF、DKIM、DMARC → 管網域 DNS 的人（網域註冊商後台）＋你用的郵件服務（如 Google Workspace）。
- 有任何 🔴 外洩檔 → **先換金鑰，再找人修**，順序不能反。

---

## 做不到的事（報告結尾一定要寫）

- 這是**基本健檢**，只看最常見的幾個設定，**不等於完整的滲透測試**（滲透測試＝請專業資安人員在授權下模擬駭客實際攻擊）。
- **結果全綠不代表沒有漏洞。** 程式邏輯錯誤、後台密碼太弱、外掛有漏洞、員工被釣魚等，本健檢都看不到。
- 不檢查子網域、不檢查網站用到的第三方服務、不登入會員區。
- 網站有防火牆擋下時，部分項目會是「無法判定」，不代表安全。
- 網站存放客戶個資或有線上金流的，建議定期委託專業資安廠商做完整檢測。

---

## 出處

本技能改寫自 [elementalsouls/Claude-BugHunter](https://github.com/elementalsouls/Claude-BugHunter)（commit `08965e25`）的 `hunt-tls-network`、`hunt-source-leak`、`hunt-cors` 三個技能，原內容以 CC BY 4.0 授權（https://creativecommons.org/licenses/by/4.0/ ）。
本版**已大幅改寫與刪減**：刪除所有攻擊性、主動利用與大範圍掃描的內容，只留網站主人自查用的被動檢查，並改寫成台灣繁體中文白話版。本版**非原作者背書**，如有錯誤由小牧人工作室負責。

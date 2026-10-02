---
name: code-animation
description: "用程式逐格渲染 15–60 秒的解說／宣傳短片（HTML＋Playwright＋ffmpeg）。先用引導問答釐清目的、內容、平台比例、片長、畫風（幾何資訊／動態文字／手繪線條／角色插畫，附預覽圖）、配色與背景音樂，產出製作單給使用者確認，再照範本施工並機械驗收。適用於新聞整理、方法說明、方案介紹、課堂教材；不適用於實拍剪輯、AI 生成影片、旁白配音。Windows／Mac 皆可。"
---

# 程式動畫短片

用程式「一格一格畫」出影片：每一格都由 `render(t)` 依秒數決定，所以畫面精準、可重現，字幕、音效能對到同一格。

## 第一次使用（每台電腦一次）

```bash
python3 scripts/doctor.py        # 檢查 Python、Playwright、ffmpeg、素材庫；缺什麼會告訴你怎麼裝
python3 scripts/fetch_assets.py  # 下載函式庫、字型、音效與角色到本機素材庫（約 30 MB，可重複執行）
```
Windows 若沒有 `python3` 指令，改用 `python` 或 `py`。

## 工作流程（agent 照做）

0. **引導問答**：照 `references/intake.md` 一題一題問（目的 → 內容 → 平台 → 片長 → 畫風 → 配色 → 音樂 → 交件）。畫風那題要給使用者看 `references/styles/` 的預覽圖。
1. **製作單**：把答案寫成 `brief.json`，**念給使用者確認後才開工**。無頭派工時用預設值補齊，並記在 `defaults_used`。
2. **時間軸**：先寫事件表（哪一秒發生什麼），再寫畫面。用 120 BPM 對拍：1 拍＝0.5 秒、1 小節＝2 秒，重要事件放在拍點上。
3. **複製範本**：把 `templates/` 整個複製到你的專案資料夾（`kit.js` 要跟場景檔放在一起），挑畫風對應的範本改：
   `geo.html`（幾何資訊）／`motion.html`（動態文字）／`sketch.html`（手繪線條）／`peeps.html`（角色插畫）。
4. **抽關鍵格**：`python3 scripts/render.py 場景.html --still 0 3 7.5 12 --param palette=dark --size 1080x1350`，打開截圖看。
5. **配樂**（要的話）：改 `templates/score.js`，事件秒數讀同一份時間軸。
6. **出片**：
   ```bash
   TONE_SCORE=score.js python3 scripts/render.py 場景.html out.mp4 --music scripts/tone_render.py --param palette=dark --size 1080x1350
   ```
   Windows PowerShell 設環境變數：`$env:TONE_SCORE="score.js"`。自備音樂改用 `--audio 音樂.mp3`；不要音樂就兩個都不加。
7. **機械驗收**：`python3 scripts/check.py 場景.html --brief brief.json --wav 場景-music.wav --timeline 場景-timeline.json --mp4 out.mp4`
8. **逐格目視**：每 1.5 秒抽一格拼成總覽（`ffmpeg -i out.mp4 -vf "select='not(mod(n\,45))',scale=300:-1,tile=8x3" -frames:v 1 總覽.png`），逐格看。
9. **交件**：附上（a）用了哪些預設值（b）哪些句子是你新寫的、不是原稿裡的——請使用者認可（c）沒驗到的項目（配樂聽感、手機實機）。

## 說故事：起承轉合

| 段 | 做什麼 | 例 |
|---|---|---|
| 起（0–4 秒） | 不放標題，直接開在衝突或問題；**第 0 格就要有字**（平台常拿第一格當封面） | 「交給 AI 的事，誰來驗收？」 |
| 承 | 每個重點**用一個畫面演出來**，同一個主角符號（游標、角色）貫穿全片 | 時鐘轉一圈打勾／價格條縮短／路徑分岔 |
| 轉 | 全片最重的一記視覺＋音效，帶出你的主張 | 閘門落下：「一個做，一個驗」 |
| 合 | 把開頭的意象拿回來問觀眾，接**唯一一個**行動 | 「你的流程，哪一關沒人驗？」→ 私訊關鍵字 |

- **演出來，不是排出來**：只有文字依序淡入＝簡報放映，觀眾會滑走。
- **畫面要補字幕沒說的資訊**，不是把字幕再畫一次。
- **觀眾要帶走價值**：只報消息會被按讚、不會被找。
- **只做程式畫得好的東西**：排版、幾何、資料圖、精準同步。⛔ 不要用程式手刻人物（火柴人在手機上像草稿）——要人物用角色插畫畫風。
- **焦點色只給一樣東西**：轉折句、價格或行動按鈕。

## 技術規則（都是實測踩過的）

- ⛔ 畫面只能由 `render(t)` 決定：不得用 `setTimeout`、`requestAnimationFrame`、CSS transition——逐格會不可重現。
- ⛔ GSAP 時間軸要**預跑一次**：`tl.progress(1, true).progress(0, true)`，被補間的屬性先用 `gsap.set` 寫明初始值；否則先跳到後面再倒回會畫錯。
- ⛔ `window.render = t => { tl.seek(t); }` **一定要加大括號**；不加會把整個時間軸物件回傳給渲染器，卡死。
- 角色檔名：站姿 `standing-N`（30 張）、坐姿 `sitting-N`（14 張）、半身 `N`（49 張），編號不連號——先開素材庫 `open-peeps-svg/` 看圖再挑。
- Tone.js：MetalSynth 離線渲染會報錯（用 NoiseSynth＋高通做 hi-hat）；單音合成器不能排在第 0 秒。配樂不是逐位元可重現（白噪音隨機），渲一次存 wav。
- 渲染器會用本機 `127.0.0.1` 的小伺服器提供素材（瀏覽器的 `fetch` 不支援 `file://`）。
- 場景沒回報就緒時，渲染器會印出頁面錯誤——先讀錯誤，不要重跑。
- 中文斷行用手動 `<br>` 在標點後斷；`text-wrap: balance` 會從詞中間切開。
- 量退出碼不要接管線（`… | head` 量到的是 head 的退出碼）。

## 驗收清單

- [ ] 原稿裡一字不改的句子、數字、價格：`check.py` 逐字比對全在（0 條＝沒驗，不是通過）
- [ ] 新寫的句子已列給使用者認可；沒有編造數字或承諾
- [ ] 禁用項 0 命中；需目視的禁用項已看過
- [ ] 每句關鍵字完整出現後停留 ≥1.5 秒
- [ ] 第 0 格有字（封面）；換場沒有全黑格（用交叉淡化）
- [ ] 主角沒有穿過不該穿的東西（例如閘門落下前就越過閘門）
- [ ] 音效事件點音量躍升 ≥1.5 倍；響度約 -16 LUFS、峰值 ≤ -1 dBFS
- [ ] 交件時明說沒驗到的：配樂聽感（agent 聽不到）、手機實機觀看

## 工具與授權

| 東西 | 授權 | 用途 |
|---|---|---|
| GSAP 3.15（含 SplitText／MorphSVG／DrawSVG／MotionPath／CustomEase） | 免費商用；禁止用於與 Webflow 競爭的視覺動畫編輯器 | 動態文字、變形、轉場 |
| Tone.js 15.1 | MIT | 程式合成配樂 |
| Noto Sans TC、Inter | SIL Open Font License | 字型 |
| Kenney 音效（介面／撞擊／數位／短配樂） | CC0 | 音效點綴 |
| Open Peeps 角色 | CC0 | 角色插畫 |
| 範例資料庫（475 支 Opus 5.5 影片提示詞） | MIT（`references/opus55-videos/LICENSE`） | 找參考作品 |

函式庫與素材都由 `fetch_assets.py` 從官方來源下載並驗證雜湊，不隨本技能散布。
評估過但暫不採用的工具（Remotion、HyperFrames、Lottie 等）與「碰到什麼情況再重新評估」：`references/tools.md`。

## 檔案地圖

```
scripts/    doctor.py 環境檢查｜fetch_assets.py 下載素材｜render.py 渲染｜tone_render.py 配樂｜check.py 驗收｜asset_server.py
templates/  kit.js 共用工具｜geo／motion／sketch／peeps.html 四種畫風範本｜score.js 配樂範本｜music.py 純 numpy 配樂（備用）
references/ intake.md 引導問答｜styles/ 畫風預覽圖｜tools.md 工具評估｜assets.json 素材清單｜library-audit.md｜opus55-videos/ 範例資料庫
```

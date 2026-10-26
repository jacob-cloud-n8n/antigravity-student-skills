---
name: code-animation
description: "用程式逐格渲染 15–110 秒的解說／宣傳短片（HTML＋Playwright＋ffmpeg）。先用引導問答釐清目的、內容、平台比例、片長、畫風（幾何資訊／動態文字／手繪線條／角色插畫，附預覽圖）、配色與聲音（背景配樂或選配中文 TTS 旁白＋逐句字幕），產出製作單給使用者確認，再照範本施工並機械驗收。適用於新聞整理、原理解說、方法說明、方案介紹、課堂教材；不適用於實拍剪輯、AI 生成影片。Windows／Mac 皆可。"
---

# 程式動畫短片

用程式「一格一格畫」出影片：每一格都由 `render(t)` 依秒數決定，所以畫面精準、可重現，字幕、旁白、音效能對到同一格。

## 第一次使用（每台電腦一次）

```bash
python3 scripts/doctor.py        # 檢查 Python、Playwright、ffmpeg、素材庫與選配套件（Pillow／fonttools／edge-tts）
python3 scripts/fetch_assets.py  # 下載函式庫、字型、音效與角色到本機素材庫（約 30 MB，可重複執行）
```
Windows 若沒有 `python3` 指令，改用 `python` 或 `py`。

## 工作流程（agent 照做）

0. **引導問答**：照 `references/intake.md` 一題一題問（目的 → 內容 → 平台 → 片長 → 畫風 → 配色 → 音樂／旁白 → 交件）。畫風那題要給使用者看 `references/styles/` 的預覽圖。
1. **製作單**：把答案寫成 `brief.json`，**念給使用者確認後才開工**。無頭派工時用預設值補齊，並記在 `defaults_used`。
2. **時間軸（配樂對拍 或 旁白驅動擇一）**：
   - **配樂對拍（預設）**：先寫事件表（哪一秒發生什麼），用 120 BPM 對拍（1 拍＝0.5 秒、1 小節＝2 秒），重要事件放在拍點上。
   - **中文旁白驅動（選配，原理解說／教學片適用）**：
     1. 寫 `SCRIPT.md`（每段 `## Line 1`、`## Line 2`…，**旁白裡的數字寫成國字如「零點八一秒」**，TTS 才不會唸錯；畫面數字照常寫阿拉伯數字）。
     2. 跑 `python3 scripts/edge_tts_voice.py --project . --voice zh-TW-HsiaoChenNeural` 產生 `assets/voice/raw/NN.wav`（先試聽前兩句確認口音與語速）。
     3. 跑 `python3 scripts/voice_meta.py --project .`：自動裁頭尾靜音、用 `ffmpeg silencedetect` 偵測停頓並按字數比例將 `SCRIPT.md` 的繁中子句對齊到語音區段（**字幕文字直接取自 `SCRIPT.md`、不經 Whisper ASR 轉寫，避免語音辨識簡體字或同音錯字；子句時間為啟發式對齊**），輸出 `audio_meta.json`（含全片累加時間 `clauses_flat`）與合併好的 `narration.wav`。場景 HTML 即可讀取子句秒數排動畫，並用 `KIT.caption(ctx, t, clauses)` 畫出逐子句高亮字幕。
     4. **破音字／英文品牌名唸錯修復（不牽動分鏡時間軸）**：片子做好才發現某個詞唸錯，不要只剪單字拼接（停頓點不同會切斷字尾）。用同一聲音換拼法（如 `Road-ster` 或同音同調字）重抽整句放進 `assets/voice/fix/cand/NN_A.wav`…，跑 `python3 scripts/fix_voice.py --project . audition --line N --clauses 0 1` 串成試聽檔給使用者用耳朵選；選好後跑 `python3 scripts/fix_voice.py --project . apply --line N --take NN_A`，它會將整句以 `atempo` 等比伸縮回原本的 `speech_s` 秒數（建議重抽長度誤差在 ±15% 內以免聽感失真）、對齊 LUFS 響度並重算該句內子句時間與 `narration.wav`——各段 `duration_s` 與全片累積起訖秒數保持不變，不必重調動畫時間軸。
3. **複製範本**：把 `templates/` 整個複製到你的專案資料夾（`kit.js` 要跟場景檔放在一起），挑畫風對應的範本改：
   `geo.html`（幾何資訊）／`motion.html`（動態文字）／`sketch.html`（手繪線條）／`peeps.html`（角色插畫）。
4. **抽關鍵格**：`python3 scripts/render.py 場景.html --still 0 3 7.5 12 --param palette=dark --size 1080x1350`，打開截圖看。
5. **配樂**（選配樂路線時）：改 `templates/score.js`，事件秒數讀同一份時間軸。
6. **字型瘦身（選配，定稿後最後一步）**：若需將場景打包上傳或加速多工載入，跑 `python3 scripts/subset_fonts.py --scan 場景.html --out NotoSansTC.subset.woff2`，只保留片中實際用到的中文字（12–17 MB → 約 150–300 KB，小 98%）。**任何改字之後都要重跑**。
7. **出片**：
   ```bash
   # 配樂路線
   TONE_SCORE=score.js python3 scripts/render.py 場景.html out.mp4 --music scripts/tone_render.py --param palette=dark --size 1080x1350
   # 旁白或自備音檔路線
   python3 scripts/render.py 場景.html out.mp4 --audio narration.wav --param palette=dark --size 1920x1080
   ```
   Windows PowerShell 設環境變數：`$env:TONE_SCORE="score.js"`。不要聲音就兩個都不加。
8. **機械驗收**：`python3 scripts/check.py 場景.html --brief brief.json --wav 場景-music.wav --timeline 場景-timeline.json --mp4 out.mp4`
9. **落定時刻 Contact Sheet 目視（`sheet.py`）**：
   ```bash
   python3 scripts/sheet.py --video out.mp4 --timeline 場景-timeline.json --out sheets
   # 若為旁白片，可傳 --timeline audio_meta.json（自動取每個子句結束前 0.15 秒落定畫面）
   ```
   它會在**每個時間軸節拍後 `+0.3s`（動作剛落定的瞬間）**截圖，並縮成 **360px 寬（模擬手機動態牆實際觀看尺寸）** 拼成 4×2 檢查表 `sheets/beats-1.png`。逐張打開親眼檢查。
10. **交件**：附上（a）用了哪些預設值（b）哪些句子是你新寫的、不是原稿裡的——請使用者認可（c）引用數字哪些是官方宣稱、哪些是估算（d）沒驗到的項目（配樂／旁白聽感、手機實機）。

## 說故事：起承轉合

| 段 | 做什麼 | 例 |
|---|---|---|
| 起（0–4 秒） | 不放標題，直接開在衝突或問題；**第 0 格就要有字**（平台常拿第一格當封面） | 「交給 AI 的事，誰來驗收？」 |
| 承 | 每個重點**用一個畫面演出來**，同一個主角符號（游標、角色、共用 SVG）貫穿全片 | 時鐘轉一圈打勾／價格條縮短／路徑分岔 |
| 轉 | 全片最重的一記視覺＋音效，帶出你的主張 | 閘門落下：「一個做，一個驗」 |
| 合 | 把開頭的意象拿回來問觀眾，接**唯一一個**行動 | 「你的流程，哪一關沒人驗？」→ 私訊關鍵字 |

- **演出來，不是排出來**：只有文字依序淡入＝簡報放映，觀眾會滑走。
- **畫面要補字幕沒說的資訊**，不是把字幕再畫一次。
- **每個數字在畫面上標明性質**：「官方宣稱」／「實測報導」／「估算」；英制單位用一行小字交代公制換算。
- **觀眾要帶走價值**：只報消息會被按讚、不會被找。
- **只做程式畫得好的東西**：排版、幾何、資料圖、精準同步。⛔ 不要用程式手刻人物（火柴人在手機上像草稿）——要人物用角色插畫畫風。
- **焦點色只給一樣東西**：轉折句、答案、關鍵數字或行動按鈕。

## 技術規則（都是實測踩過的）

- ⛔ 畫面只能由 `render(t)` 決定：不得用 `setTimeout`、`requestAnimationFrame`、CSS transition——逐格會不可重現。
- ⛔ GSAP 時間軸要**預跑一次**：`tl.progress(1, true).progress(0, true)`，被補間的屬性先用 `gsap.set` 寫明初始值；否則先跳到後面再倒回會畫錯。
- ⛔ `window.render = t => { tl.seek(t); }` **一定要加大括號**；不加會把整個時間軸物件回傳給渲染器，卡死。
- **遮罩旋轉揭示**：外層 `overflow: hidden`，內層文字帶旋轉（如 `rotation: 3 → 0`）時，從 `yPercent: 100` 起跳會露出一角（中文字比英文字高更明顯），**起點必須設 `yPercent: 135`**。
- **計數器與長條圖同步**：計數器用 GSAP `power2.out`（三次方 `1-(1-t)^3`）或 `power3.out`（四次方 `1-(1-t)^4`）時，長條格子的出現時間**不得用 stagger 的 ease**（stagger ease 管起跑時間分配，會變先慢後快、方向相反），必須用計數器 ease 的**反函數**算：呼叫 `KIT.invEase2(y)`（即 `1 - Math.cbrt(1 - y)`，對應 `power2.out`）或 `KIT.invEase3(y)`（`1 - Math.pow(1 - y, 0.25)`，對應 `power3.out`）。若有旁白，數字動畫要在唸到該子句後 **0.5 秒內**數完。
- **SVG 描線動畫**：路徑做 dash 描線（從 0 開始畫）時，**`stroke-linecap` 一律用 `butt`**——用 `square` 在長度 0 時仍會畫出一個小方點。
- **旋轉容器動畫**：斜放的圖形（如斜邊上的正方形），外層容器只負責固定 `rotate(...)`，GSAP 動畫只動裡面的子元素；直接對外層做 GSAP 位移／縮放會把旋轉蓋掉。
- **繁體中文排版與閱讀停留**：
  - 中文展示字不設負字距（`letter-spacing: 0` 至 `0.02em`），`line-height: 1.15–1.25`，一行不超過約 12 個字；中文沒有真斜體，重點用**焦點色＋粗體**。
  - 每個要讓人讀的狀態落定後都要停住：短句至少停 **1.5 秒**，超過 6 個字每多 4 個字加 **0.25 秒**，結尾句至少停 **2.0 秒**。拿不準時，停久一點、動少一點。
  - 中文斷行用手動 `<br>` 在標點後斷；`text-wrap: balance` 會從詞中間切開。
- **多 Sub-agent 平行做多格時的防走鐘規則**：
  1. 跨格重複出現的主角（車、人、儀器）先畫成**唯一一個共用 SVG**，固定各部件 `id` 與座標，所有 worker 原封不動 inline 貼上、只准等比縮放。
  2. 相鄰格接續同一畫面（如同一把刻度尺）時，先做完那格回報的精確像素座標，立刻轉給下一格照抄。
  3. 英文數字字型排在 CJK 字型前面（如 `"Inter", "TC", sans-serif`），避免各格數字長相不同。
- 角色檔名：站姿 `standing-N`（30 張）、坐姿 `sitting-N`（14 張）、半身 `N`（49 張），編號不連號——先開素材庫 `open-peeps-svg/` 看圖再挑。
- Tone.js：MetalSynth 離線渲染會報錯（用 NoiseSynth＋高通做 hi-hat）；單音合成器不能排在第 0 秒。配樂不是逐位元可重現（白噪音隨機），渲一次存 wav。
- 渲染器會用本機 `127.0.0.1` 的小伺服器提供素材（瀏覽器的 `fetch` 不支援 `file://`）。
- 場景沒回報就緒時，渲染器會印出頁面錯誤——先讀錯誤，不要重跑。
- 量退出碼不要接管線（`… | head` 量到的是 head 的退出碼）。

## 驗收清單

- [ ] 原稿裡一字不改的句子、數字、價格：`check.py` 逐字比對全在（0 條＝沒驗，不是通過）
- [ ] 新寫的句子已列給使用者認可；沒有編造數字或承諾；畫面數字已標明「宣稱／實測／估算」
- [ ] 禁用項 0 命中；需目視的禁用項已看過
- [ ] 用 `sheet.py` 產出節拍落定時刻（360px 手機寬度）Contact Sheet 並逐格看過：無遮罩切字、無重疊、手機寬度字仍清晰、全部繁體字形與全形標點
- [ ] 每句關鍵字完整出現後停留 ≥1.5 秒（長句每多 4 字 +0.25 秒）
- [ ] 第 0 格有字（封面）；換場沒有全黑格（用交叉淡化或物件延續）
- [ ] 主角沒有穿過不該穿的東西（例如閘門落下前就越過閘門）
- [ ] 音效事件點音量躍升 ≥1.5 倍；響度約 -16 LUFS（旁白片約 -14 LUFS）、峰值 ≤ -1 dBFS
- [ ] 交件時明說沒驗到的：配樂／旁白口音與情緒聽感（agent 聽不到，由使用者耳朵決定）、手機實機觀看

## 工具與授權

| 東西 | 授權 | 用途 |
|---|---|---|
| GSAP 3.15（含 SplitText／MorphSVG／DrawSVG／MotionPath／CustomEase） | 免費商用；禁止用於與 Webflow 競爭的視覺動畫編輯器 | 動態文字、變形、轉場 |
| Tone.js 15.1 | MIT | 程式合成配樂 |
| Noto Sans TC、Inter | SIL Open Font License | 字型 |
| Kenney 音效（介面／撞擊／數位／短配樂） | CC0 | 音效點綴 |
| Open Peeps 角色 | CC0 | 角色插畫 |
| 範例資料庫（475 支 Opus 5.5 影片提示詞） | MIT（`references/opus55-videos/LICENSE`） | 找參考作品 |
| `sheet.py`／`subset_fonts.py`／`voice_meta.py`／`fix_voice.py`／`edge_tts_voice.py` 及動態設計品味規則 | 改編自 `mathruffian-dot/claude-motion-explainer`（MIT，commit `d868d7c1d71590b00174ebb76ef172b33aeddec2`）與 `whaleyxbt/claude-motion`（MIT）；完整授權全文與對照表見 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) | 落定時刻 Contact Sheet、中文字型瘦身、免 Whisper 停頓對齊字幕、等比伸縮換句 |
| `edge-tts`（選配旁白套件） | 套件 GPL-3.0；呼叫 Microsoft 線上語音服務（**商業發布前請自行確認微軟服務條款**） | 免 GPU 台灣口音中文旁白合成 |

函式庫與素材都由 `fetch_assets.py` 從官方來源下載並驗證雜湊，不隨本技能散布。
評估過但暫不採用的工具（Remotion、HyperFrames、Lottie、Breeze TTS 2 等）與「碰到什麼情況再重新評估」：`references/tools.md`。

## 檔案地圖

```
THIRD_PARTY_NOTICES.md  第三方改編來源、Blob SHA 對照與完整 MIT 授權聲明
scripts/    doctor.py 環境檢查｜fetch_assets.py 下載素材｜render.py 渲染｜tone_render.py 配樂｜check.py 驗收｜sheet.py 落定時刻 360px 檢查表｜subset_fonts.py 中文字型瘦身｜edge_tts_voice.py 中文 TTS 合成｜voice_meta.py 免 Whisper 子句停頓對齊｜fix_voice.py 唸錯字等比伸縮換句｜asset_server.py
templates/  kit.js 共用工具（含 invEase2/3 反函數與 caption 字幕高亮）｜geo／motion／sketch／peeps.html 四種畫風範本｜score.js 配樂範本｜music.py 純 numpy 配樂（備用）
references/ intake.md 引導問答｜styles/ 畫風預覽圖｜tools.md 工具評估｜assets.json 素材清單｜library-audit.md｜opus55-videos/ 範例資料庫
```

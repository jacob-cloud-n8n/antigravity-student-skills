# 程式動畫工具評估

> 查證日 2026-10-02（研究 subagent 只讀官方頁與 npm registry 中繼資料，未安裝任何東西）。
> Claude 獨立抽查 2 條：GSAP 全外掛免費商用（gsap.com/licensing）、Open Peeps 為 CC0（openpeeps.com）——皆相符。其餘為 subagent 申報。
> 授權與版本會變：**導入前當次重查**，不要信這份的日期之後的狀態。
> 〔官〕＝官方文件／registry；〔推〕＝推論。

## 導入狀態（2026-10-02）

GSAP、Tone.js、Kenney、Open Peeps 已導入並實測，用法與授權見 `SKILL.md`「工具與授權」與「技術規則」。

## 結論

現行管線（HTML＋`render(t)`＋Playwright 逐格）跟 HyperFrames／Remotion 是**同一種架構**，不必換框架。最划算的升級是在現有 `render(t)` 裡加料：

| 順序 | 工具 | 解哪個痛點 | 第一個試作 |
|---|---|---|---|
| 1 | **GSAP**（含 SplitText／MorphSVG／DrawSVG／MotionPath／CustomEase） | 緩動、逐字動畫、路徑變形、遮罩轉場 | 時間軸設 `paused:true`，每格 `tl.seek(t)`；把一支舊片標題改逐字進場＋一個圖示變形，同一個 t 抽 5 格比對確定性 |
| 2 | **Open Peeps**（CC0 模組化手繪角色 SVG） | 角色從火柴人升到插畫等級 | 一個角色「困惑 → 想通」：換表情、手臂擺動；深色底要把線條反白，只上單一焦點色 |
| 3 | **Kenney 音效**（CC0）＋**Tone.js `Offline`**（MIT） | 配樂音色陽春 | 轉場加 whoosh／click；配樂改 PolySynth＋殘響，與正弦波版 A/B |

## 總表

| 工具 | 逐格確定性 | 商用授權 | 導入成本 |
|---|---|---|---|
| GSAP 3.15 | 可〔官 `seek()`〕 | 免費含外掛〔官〕；禁用於與 Webflow 競爭的視覺動畫編輯器〔官〕；AI 產生的程式碼不屬禁止用途〔官〕 | 低 |
| anime.js 4.5 | 可〔官 `seek()`〕；原生 Spring 緩動 | MIT〔官〕 | 低 |
| HyperFrames（HeyGen） | 可〔官：同輸入同影格〕 | Apache-2.0〔官〕 | 中，Node 22+ |
| Remotion 4.0 | 可〔官〕 | 個人與 ≤3 人營利組織免費，超過要買公司授權〔官〕；外包 agent 算不算人頭條款沒定義〔推〕 | 中高，要改寫成 React |
| Lottie（lottie-web／dotlottie-web） | 可〔官 `goToAndStop()`〕 | 播放器 MIT〔官〕；**市集素材條款逐一看**（未查） | 播放低、自製高（要 After Effects） |
| Rive | 可〔官 `advance(秒)`〕 | 執行端 MIT；編輯器在雲端、免費版有開場畫面〔官〕 | 高 |
| Manim CE 0.21 | 離線渲染〔推〕 | MIT〔官〕 | 高（Python＋LaTeX，另一條管線） |
| Revideo 0.11 | 可〔官〕 | MIT；有匿名遙測可關〔官〕 | 中 |
| Tone.js 15.1 `Offline` | 可（OfflineAudioContext）〔官〕 | MIT | 低中，可在現有 Playwright 頁面跑 |
| Kenney 音效 | 素材 | CC0〔官〕 | 極低 |
| Open Peeps | 素材 | CC0〔官，Claude 抽查〕 | 低 |
| Humaaans | 素材 | CC0〔第三方轉述，官網原文未取得＝未驗證〕 | 低 |
| unDraw | 素材 | 可商用免標註，但**禁止爬取／自動下載／AI 訓練**〔官〕 | 只能人工挑圖 |
| Pixabay 音樂 | 素材 | 可商用、禁止原樣轉售〔官〕；Content ID 誤判未查 | 低 |

## 風險與不建議

- **HyperFrames（第二階段候選，導入前要先決定）**：遙測**預設開**（`HYPERFRAMES_NO_TELEMETRY=1` 關）；`init` 會從 GitHub **自動安裝 AI skills**＝撞「第三方 skill 預設讀不裝」；內建 12 套以上設計模板，會帶自己的風格進來。要試：關遙測、不跑 init 的 skill 安裝、不用它的模板。
- **Remotion**：要整套改寫 React，現行管線已做到它的核心；超過 3 人要付費。
- **Motion Canvas**（最後穩定版 2024-12）、**Theatre.js**（2024-05 後停更，studio 是 AGPL）：已停滯。
- **Rive**：素材要上別人的雲、免費版有開場畫面。
- **Three.js**：直式解說片用不到 3D。
- **LottieFiles 市集素材**：常見漸層與發光，容易跟品牌規範衝突。
- npm 套件頂層 scripts 皆無 postinstall〔registry〕；依賴樹未逐一驗。

## 暫不採用・碰到就重新評估（2026-10-02）

> 這些不是「不能用」，是「現在不划算」。碰到觸發條件時，**重新查授權與版本**再評估，不沿用本頁舊結論。

| 工具 | 碰到這個就重新評估 |
|---|---|
| Remotion | ①要把螢幕錄影／實拍嵌進動畫並逐格對齊（課程示範片）②固定系列片要量產、只換資料不換版型 ③非工程背景的人要自己拖時間軸調整 ④團隊超過 3 人時先算授權費 |
| HyperFrames | 要自動壓低配樂音量（旁白進來時）或要 TTS 旁白流程；導入時關遙測、不跑 init 的 skill 安裝、不用它的模板 |
| Lottie | 拿到一份已授權的 After Effects 角色動畫要放進片裡 |
| Rive | 需要可互動的角色狀態機（網頁上可點的角色），且接受素材放雲端 |
| Manim | 要做數學／演算法圖解（公式推導、座標變換） |
| Motion Canvas／Theatre.js | 官方恢復發版（目前分別停在 2024-12／2024-05） |
| Revideo | GSAP 加料後仍缺「場景組合／預覽器」，而又不想上 React |
| Three.js | 題材真的需要 3D（鏡頭穿梭、產品立體展示） |
| unDraw／Pixabay | 需要現成場景插畫或整首配樂，且由人工挑選下載（unDraw 禁自動下載） |
| ElevenLabs 等旁白 | 決定要加旁白時（本技能目前以字幕為主、不含旁白） |

## 來源

GSAP https://gsap.com/licensing/ ｜ Remotion https://raw.githubusercontent.com/remotion-dev/remotion/main/LICENSE.md ｜ HyperFrames https://github.com/heygen-com/hyperframes ｜ anime.js https://animejs.com/documentation/ ｜ Lottie https://github.com/airbnb/lottie-web ｜ Rive https://rive.app/pricing ｜ Theatre.js https://github.com/theatre-js/theatre ｜ Motion Canvas https://github.com/motion-canvas/motion-canvas/releases ｜ Manim https://pypi.org/project/manim/ ｜ Revideo https://github.com/redotvideo/revideo ｜ Open Peeps https://www.openpeeps.com/ ｜ Humaaans https://www.humaaans.com/ ｜ unDraw https://undraw.co/license ｜ Kenney https://kenney.nl/support ｜ Tone.js https://tonejs.github.io/docs/15.1.22/functions/Offline.html ｜ Pixabay https://pixabay.com/service/license-summary/

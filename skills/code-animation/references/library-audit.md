# 函式庫導入檢查紀錄

2026-10-02 決定納入後，由 `npm pack` 取得套件壓縮檔做首次檢查（**未執行 npm install、未跑任何套件腳本**），只挑實際會用到的檔案。

| 套件 | 版本 | 授權 | 檔案 |
|---|---|---|---|
| GSAP | 3.15.0 | Standard "no charge" license（https://gsap.com/standard-license；免費商用含外掛，禁止用於與 Webflow 競爭的視覺動畫編輯器） | gsap、SplitText、MorphSVGPlugin、DrawSVGPlugin、MotionPathPlugin、CustomEase（皆 .min.js） |
| Tone.js | 15.1.22 | MIT（`tone-15.1.22/LICENSE.md`） | Tone.js（UMD build） |

## 導入檢查（2026-10-02，Claude）
- package.json 無 preinstall／install／postinstall／prepare。
- 掃 fetch／XMLHttpRequest／sendBeacon／WebSocket／eval／new Function／外部網址：
  - GSAP：只有警告字串與授權聲明裡的 gsap.com 網址，無網路呼叫。
  - Tone.js：2 處 `fetch(`——AudioWorklet 模組載入、`ToneAudioBuffer.load(url)` 讀取呼叫端指定的取樣檔；無遙測。
- ⚠️ 這是手列樣式掃描，證明「這些樣式沒命中」，不等於完整安全審查。
- SHA-256：見 `SHA256SUMS`；升版時整份重做本節。

## 首次檢查時的檔案 SHA-256

```
466e426a5c60c21c94b15a30a3dffacac9bb39ce8f4e07d071d7d4bb1be43390  gsap-3.15.0/CustomEase.min.js
beb19529f54c1212f1f5117d027be01afda2f363a4926d32aa979bc11140edc1  gsap-3.15.0/DrawSVGPlugin.min.js
19c891a412240d8521b13330813d9b551ea5b0f707907c365ffecaf1dfa0f5cf  gsap-3.15.0/MorphSVGPlugin.min.js
ace44a07c6c179f5347d9b46a152d468e4c9f272ee0d68bf0354e00d60000693  gsap-3.15.0/MotionPathPlugin.min.js
419f7027a5f086a12cb7988736d8fdd3a6ed2200229661de25b6628ca7ced344  gsap-3.15.0/SplitText.min.js
92bb9a96476f983d212a2bc4f54c889039c1696dd4461d40a736860938570fbb  gsap-3.15.0/gsap.min.js
e290952fa43d9a7a780182a83c6fccf44d79cb7ae2cba102ef1f2b9d98124e22  tone-15.1.22/Tone.js
```

改為由 `scripts/fetch_assets.py` 從 npm registry 下載後（2026-10-02），上列 7 個檔案雜湊逐一相同；函式庫不再隨技能散布。

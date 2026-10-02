#!/usr/bin/env python3
"""用 Tone.js 離線渲染配樂（取代 numpy 正弦波）：在無頭 Chromium 裡跑 Tone.Offline，取回取樣寫成 WAV。

用法：python3 tone_render.py <score.js> <timeline.json> <out.wav>
score.js 必須定義：async function score(T, Tone, dest) { ... }
  T＝render.py 匯出的時間軸（與畫面同一份）；所有音符以 T 的秒數排程；輸出接到 dest（已含母帶限幅）
  片長取 T.DUR。也可以當 render.py 的 --music：render.py 以 (timeline, out) 呼叫，score.js 路徑用環境變數 TONE_SCORE。
⚠️ 不是逐位元可重現（2026-10-02 實測，同一份譜渲兩次）：
   - 白噪音（NoiseSynth 做的 hi-hat）每次不同：6% 取樣有差、聽感一致；Tone.Reverb 的殘響脈衝同樣是隨機產生。
   - 拿掉噪音後只剩浮點捨入：最大差 1 個取樣單位（-86 dB，不可聞）。
   → 配樂渲一次就存 wav，驗收量的是「事件點對時＋響度」，不是雜湊。
⚠️ MetalSynth 在 15.1.22 離線渲染第二次觸發就報錯；單音合成器排在第 0 秒也會報錯（範本已處理）。
"""
import os, sys, json, wave, base64
import numpy as np
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import asset_server
SR = 48000


def main():
    if len(sys.argv) == 3:            # 被 render.py --music 呼叫
        score_js, tl, out = os.environ["TONE_SCORE"], sys.argv[1], sys.argv[2]
    else:
        score_js, tl, out = sys.argv[1:4]
    T = json.load(open(tl))
    page_js = open(score_js, encoding="utf-8").read()
    with sync_playwright() as pw:
        asset_url, stop_server = asset_server.start()
        if not asset_url: sys.exit("找不到本機素材庫：先跑 scripts/fetch_assets.py")
        b = pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
        pg = b.new_page(); pg.goto(asset_url + "/")   # 與素材庫同源；從 about:blank 載入本機網址會被擋
        pg.add_script_tag(content="window.ASSET_DIR = %s;" % json.dumps(asset_url))   # score.js 可用 ASSET_DIR 載入 Kenney 音效
        pg.add_script_tag(url=asset_url + "/lib/tone/Tone.js"); pg.add_script_tag(content=page_js)
        b64 = pg.evaluate("""async (T) => {
            const buf = await Tone.Offline(async ({transport}) => {
                const lim = new Tone.Limiter(-1).toDestination();
                await score(T, Tone, lim);
            }, T.DUR, 2, %d);
            const chans = [buf.getChannelData(0), buf.getChannelData(1)];
            const n = chans[0].length, pcm = new Int16Array(n * 2);
            for (let i = 0; i < n; i++) for (let c = 0; c < 2; c++) pcm[i * 2 + c] = Math.max(-1, Math.min(1, chans[c][i])) * 32767;
            let s = ''; const u8 = new Uint8Array(pcm.buffer);
            for (let i = 0; i < u8.length; i += 0x8000) s += String.fromCharCode.apply(null, u8.subarray(i, i + 0x8000));
            return btoa(s);
        }""" % SR, T)
        b.close(); stop_server()
    pcm = np.frombuffer(base64.b64decode(b64), "<i2")
    if not np.abs(pcm).max():
        sys.exit("渲染結果全是靜音——score() 沒有排到任何聲音，或沒接到 dest")
    with wave.open(out, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    print(f"OK {out}｜{len(pcm) / 2 / SR:.2f} 秒")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""程式動畫通用渲染器：scene.html 的 window.render(t) 逐格截圖 → (配樂) → ffmpeg 合成 mp4。

scene.html 必須提供：
  window.render(t)      依秒數畫出畫面（不得用計時器／CSS transition，否則逐格結果不可重現）
  window.DUR            片長（秒）
  window.TIMELINE       （選用）事件時間軸物件，會匯出成 JSON 給配樂腳本讀
  window.__ready=true   字型載入完成後設定
  window.FONTS          （選用）[[字型家族, 測試字元], ...]；任一未載入就中止（否則會靜默退回系統字）
渲染器在頁面載入前注入 window.ASSET_DIR（本機素材庫，經 asset_server 以 http://127.0.0.1 提供），場景用它載入函式庫、字型與素材。

用法：
  python3 render.py scene.html out.mp4 [--music music.py | --audio 自備.mp3] [--size 1080x1350] [--fps 30] [--param palette=light]
  python3 render.py scene.html --still 1 4.5 13   # 只輸出指定秒數單格到 <scene>-stills/
配樂腳本的介面：python3 music.py <timeline.json> <out.wav>
"""
import os, sys, json, shutil, argparse, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asset_server

FFMPEG = shutil.which("ffmpeg") or os.path.expanduser("~/.local/bin/ffmpeg")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scene"); ap.add_argument("out", nargs="?")
    ap.add_argument("--music"); ap.add_argument("--size", default="1080x1350"); ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--still", nargs="+", type=float)
    ap.add_argument("--param", action="append", default=[], help="傳給場景的網址參數，例：--param palette=light")
    ap.add_argument("--audio", help="自備音樂檔（mp3/wav），取代 --music")
    a = ap.parse_args()
    W, H = map(int, a.size.split("x"))
    scene = os.path.abspath(a.scene); base = os.path.splitext(scene)[0]

    asset_url, stop_server = asset_server.start()
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H})
        pg.add_init_script("window.ASSET_DIR = %s;" % json.dumps(asset_url))
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        from urllib.parse import quote
        qs = "&".join(f"{k}={quote(v)}" for k, v in (x.split("=", 1) for x in a.param))
        pg.goto(Path(scene).as_uri() + ("?" + qs if qs else ""))           # as_uri：Windows 路徑也正確
        try:
            pg.wait_for_function("window.__ready === true", timeout=60000)
        except Exception:
            sys.exit("場景沒有回報就緒（window.__ready）。頁面錯誤：" + ("；".join(errs[:5]) or "無——檢查 setup() 的 Promise 是否被吞掉"))
        if errs: print("⚠️ 頁面錯誤：" + "；".join(errs[:5]))
        bad = pg.evaluate("() => (window.FONTS || []).filter(([f, ch]) => !document.fonts.check(`40px ${f}`, ch)).map(x => x[0])")
        if bad: sys.exit(f"字型未載入：{bad}")
        if a.still:
            d = base + "-stills"; os.makedirs(d, exist_ok=True)
            for s in a.still:
                pg.evaluate(f"render({s})"); pg.screenshot(path=os.path.join(d, f"t{s:05.2f}.png"))
            b.close(); stop_server(); print(f"OK {len(a.still)} 張 → {d}"); return
        if not a.out: sys.exit("缺少輸出檔名")
        dur = pg.evaluate("window.DUR"); n = int(round(dur * a.fps))
        tl = base + "-timeline.json"
        with open(tl, "w") as f: json.dump(pg.evaluate("window.TIMELINE || {DUR: window.DUR}"), f)
        frames = base + "-frames"; shutil.rmtree(frames, ignore_errors=True); os.makedirs(frames)
        for i in range(n):
            pg.evaluate(f"render({i / a.fps})"); pg.screenshot(path=os.path.join(frames, f"{i:05d}.png"))
        b.close()
    stop_server()
    if len(os.listdir(frames)) != n: sys.exit(f"格數不符：預期 {n}")
    cmd = [FFMPEG, "-y", "-loglevel", "error", "-framerate", str(a.fps), "-i", os.path.join(frames, "%05d.png")]
    if a.music or a.audio:
        wav = a.audio or base + "-music.wav"
        if a.music: subprocess.run([sys.executable, a.music, tl, wav], check=True)
        cmd += ["-i", wav, "-af", "loudnorm=I=-16:TP=-1.5", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-movflags", "+faststart", a.out]
    subprocess.run(cmd, check=True)
    print(f"OK {a.out}｜{n} 格｜{dur} 秒")


if __name__ == "__main__":
    main()

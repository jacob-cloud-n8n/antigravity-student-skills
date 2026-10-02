#!/usr/bin/env python3
"""程式動畫機械驗收：①文案逐字 ②禁用項 ③音效是否落在事件點 ④響度。

用法：
  python3 check.py scene.html --brief brief.json [--wav music.wav --timeline timeline.json] [--mp4 out.mp4]
  python3 check.py scene.html --copy required.txt …   # 不用 brief 時，一行一條必須逐字出現的字串
brief.json 的 must_include＝必須逐字出現的字串（從原稿複製，不要手打）；bans＝禁用項（色碼／字型名會機械比對，其餘列為需目視）。
⚠️ 這只證明「列出的字串都在、列出的禁項都不在、事件點音量有躍升」；畫面好不好看、聲音好不好聽，它證明不了。
"""
import re, sys, json, wave, argparse, subprocess, shutil, os

HOUSE = r"(?i)gradient|box-shadow|text-shadow|shadowBlur"   # 預設：漸層與陰影／發光（多數品牌規範會禁；不需要就加 --allow-effects）


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scene"); ap.add_argument("--copy"); ap.add_argument("--brief"); ap.add_argument("--wav"); ap.add_argument("--timeline"); ap.add_argument("--mp4")
    ap.add_argument("--allow-effects", action="store_true")
    a = ap.parse_args()
    src = open(a.scene, encoding="utf-8").read().replace("<br>", "")
    fail = 0
    brief = json.load(open(a.brief, encoding="utf-8")) if a.brief else {}
    if a.copy or a.brief:
        want = [l.strip() for l in open(a.copy, encoding="utf-8") if l.strip()] if a.copy else list(brief.get("must_include", []))
        miss = [w for w in want if w not in src]
        print(f"① 文案：{len(want)} 條，缺 {len(miss)}" + (f" → {miss}" if miss else ""))
        if not want: print("   ⚠️ 0 條＝沒有東西可驗，不是通過"); fail = 1
        fail |= bool(miss)
    hits = [] if a.allow_effects else re.findall(HOUSE, src)
    eye = []
    for b in brief.get("bans", []):
        if re.fullmatch(r"#?[0-9a-fA-F]{6}", b) or re.fullmatch(r"[A-Za-z][\w ]+", b):   # 色碼或字型名：機械比對
            hits += re.findall(re.escape(b.lstrip("#")), src, re.I)
        else:
            eye.append(b)
    print(f"② 禁用項：命中 {len(hits)}" + (f" → {sorted(set(hits))}" if hits else "") + (f"；需目視：{eye}" if eye else "")); fail |= bool(hits)
    if a.wav and a.timeline:
        import numpy as np
        w = wave.open(a.wav); sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), "<i2").reshape(-1, w.getnchannels())[:, 0].astype(float)
        tl = json.load(open(a.timeline)); ev = []
        for k, v in tl.items():
            if k == "DUR": continue
            ev += [(f"{k}[{i}]", t) for i, t in enumerate(v)] if isinstance(v, list) else [(k, v)]
        print("③ 事件點音量躍升（後 50ms ÷ 前 50ms；<1.5 標 ⚠️）")
        n = int(0.05 * sr)
        for k, t in sorted(ev, key=lambda e: e[1]):
            if t < 0.05:
                print(f"      {k:<12} {t:>6.2f}s  （片頭，前面沒有聲音可比，不量）"); continue
            i = int(t * sr); r = np.abs(x[i:i + n]).mean() / max(1, np.abs(x[max(0, i - n):i]).mean())
            print(f"   {'⚠️' if r < 1.5 else '  '} {k:<12} {t:>6.2f}s  ×{r:.1f}")
    if a.mp4:
        ff = shutil.which("ffmpeg") or os.path.expanduser("~/.local/bin/ffmpeg")
        out = subprocess.run([ff, "-i", a.mp4, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
        m = re.findall(r"^\s+(I|Peak):\s+(-?[\d.]+)", out, re.M)
        print("④ 響度：" + "、".join(f"{k} {v}" for k, v in m) + "（目標 I≈-16 LUFS、Peak ≤ -1 dBFS）")
    sys.exit(fail)


if __name__ == "__main__":
    main()

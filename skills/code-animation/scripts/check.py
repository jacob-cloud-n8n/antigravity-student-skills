#!/usr/bin/env python3
"""程式動畫機械驗收：①文案逐字 ②禁用項 ③音效是否落在事件點 ④響度 ⑤宣傳片審美規則。

用法：
  python3 check.py scene.html --brief brief.json [--wav music.wav --timeline timeline.json] [--mp4 out.mp4]
  python3 check.py scene.html --copy required.txt …   # 不用 brief 時，一行一條必須逐字出現的字串
brief.json 的 must_include＝必須逐字出現的字串（從原稿複製，不要手打）；bans＝禁用項（色碼／字型名會機械比對，其餘列為需目視）。
宣傳片（brief.json 的 video_type＝promo）必須再帶 --rules rules-check.json --sheets <sheet.py 輸出資料夾> --mp4 out.mp4；少任何一項＝不通過。
⑤ 分兩種證據：「量測」（片尾靜止秒數、檢查表是否在成片之後產生）是腳本量的；「申報」（逐條 pass／na＋依據）是執行者寫的，只證明每條都被回答過，不證明答案對。
⚠️ 這只證明「列出的字串都在、列出的禁項都不在、事件點音量有躍升」；畫面好不好看、聲音好不好聽，它證明不了。
"""
import re, sys, json, wave, argparse, subprocess, shutil, os

HOUSE = r"(?i)gradient|box-shadow|text-shadow|shadowBlur"   # 預設：漸層與陰影／發光（多數品牌規範會禁；不需要就加 --allow-effects）


RULES_DOC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references", "shotcraft-rules.md")


def tail_freeze(mp4):
    """片尾連續靜止秒數（ffmpeg freezedetect）。回傳 None＝量不到。"""
    ff = shutil.which("ffmpeg") or os.path.expanduser("~/.local/bin/ffmpeg")
    err = subprocess.run([ff, "-i", mp4, "-vf", "freezedetect=n=0.003:d=0.5", "-an", "-f", "null", "-"], capture_output=True, text=True).stderr
    d = re.search(r"Duration: (\d+):(\d+):([\d.]+)", err)
    if not d: return None
    dur = int(d[1]) * 3600 + int(d[2]) * 60 + float(d[3])
    starts = [float(x) for x in re.findall(r"freeze_start: ([\d.]+)", err)]
    ends = [float(x) for x in re.findall(r"freeze_end: ([\d.]+)", err)]
    if not starts: return 0.0
    if len(ends) >= len(starts) and ends[-1] < dur - 0.1: return 0.0   # 最後一段靜止在片尾前就結束了
    return dur - starts[-1]


def check_rules(a, brief):
    """⑤ 宣傳片審美規則。回傳 1＝不通過。"""
    if not a.brief and not a.rules: return 0
    vt = brief.get("video_type")
    if vt not in ("promo", "explainer") and not a.rules:
        print("⑤ 審美規則：❌ brief.json 缺 video_type（promo／explainer），無法判定要不要驗"); return 1
    if vt == "explainer" and not a.rules:
        print("⑤ 審美規則：解說片不套用（video_type＝explainer）"); return 0
    bad = []
    if not a.rules: bad.append("宣傳片缺 --rules rules-check.json")
    ids = re.findall(r"^- \[ \] \*\*([A-Z]\d+)｜", open(RULES_DOC, encoding="utf-8").read(), re.M)
    if not ids: bad.append("規則檔解析出 0 條（尺壞了，不是通過）")
    if a.rules:
        got = json.load(open(a.rules, encoding="utf-8")).get("rules", {})
        miss = [i for i in ids if i not in got]
        if miss: bad.append(f"未回答 {len(miss)} 條：{miss}")
        for i in ids:
            r = got.get(i)
            if r is None: continue
            if r.get("status") not in ("pass", "na"): bad.append(f"{i} 狀態是 {r.get('status')!r}")
            if len(str(r.get("evidence", "")).strip()) < 8: bad.append(f"{i} 依據太短或空白")
        ev = [str(r.get("evidence", "")).strip() for r in got.values()]
        dup = sorted({e for e in ev if e and ev.count(e) >= 3})
        if dup: bad.append(f"{len(dup)} 句依據被重複貼在 3 條以上（套話）")
        n = {s: sum(1 for r in got.values() if r.get("status") == s) for s in ("pass", "na")}
        print(f"⑤ 審美規則［申報］：共 {len(ids)} 條，pass {n['pass']}、na {n['na']}（申報只證明每條被回答過）")
    if not a.mp4: bad.append("缺 --mp4，片尾停留量不到")
    else:
        tail = tail_freeze(a.mp4)
        print(f"⑤ 審美規則［量測］R1 片尾靜止：{'量不到' if tail is None else f'{tail:.2f} 秒'}（門檻 ≥1.00）")
        if tail is None or tail < 1.0: bad.append("R1 片尾字標沒有靜止滿 1 秒")
    if not a.sheets: bad.append("缺 --sheets，P1 自檢量不到")
    elif a.mp4 and os.path.exists(a.mp4):
        pngs = [os.path.join(a.sheets, f) for f in os.listdir(a.sheets) if f.endswith(".png")] if os.path.isdir(a.sheets) else []
        fresh = [f for f in pngs if os.path.getmtime(f) >= os.path.getmtime(a.mp4)]
        print(f"⑤ 審美規則［量測］P1 檢查表：{len(pngs)} 張，成片之後產生 {len(fresh)} 張")
        if not fresh: bad.append("P1 沒有在成片之後產生的檢查表")
    for b in bad: print(f"   ❌ {b}")
    return int(bool(bad))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scene"); ap.add_argument("--copy"); ap.add_argument("--brief"); ap.add_argument("--wav"); ap.add_argument("--timeline"); ap.add_argument("--mp4")
    ap.add_argument("--allow-effects", action="store_true")
    ap.add_argument("--rules"); ap.add_argument("--sheets")
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
    fail |= check_rules(a, brief)
    sys.exit(fail)


if __name__ == "__main__":
    main()

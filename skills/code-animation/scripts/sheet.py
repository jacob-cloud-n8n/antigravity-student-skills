#!/usr/bin/env python3
"""Contact sheets for motion review: one labelled tile per moment, 4x2 per sheet.

Adapted from mathruffian-dot/claude-motion-explainer (MIT, commit d868d7c1d71590b00174ebb76ef172b33aeddec2,
blob d512d7c03852ca48166edabfd502e1fe3c281945) & whaleyxbt/claude-motion (MIT)
for the code-animation pipeline. See ../THIRD_PARTY_NOTICES.md for full MIT license text.

Frames come from a rendered video (via ffmpeg) or from existing images (e.g. render.py --still).
Tiles default to 360 px wide (phone-feed width), so a readable tile means a readable phone screen.
When given --timeline (<scene>-timeline.json, timeline.js, or audio_meta.json), samples at
each beat + --settle (default 0.3s, after motion settles) instead of blind fixed intervals.

Usage:
  python3 scripts/sheet.py --video out.mp4 --timeline scene-timeline.json
  python3 scripts/sheet.py --video out.mp4 --timeline audio_meta.json
  python3 scripts/sheet.py --video out.mp4 --from 3 --to 5 --every 0.2 --name scrub
  python3 scripts/sheet.py --video out.mp4 --at 0,3,7.5,12 --name exact
  python3 scripts/sheet.py --images scene-stills/t00.00.png scene-stills/t03.00.png --labels 0.0s,3.0s
"""
import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

COLS, ROWS = 4, 2
GAP = 8
LABEL_H = 26
FFMPEG = shutil.which("ffmpeg") or os.path.expanduser("~/.local/bin/ffmpeg")


def timeline_beats(path, settle):
    """Read timeline JSON (render.py / audio_meta.json) or timeline.js; return [(label, seconds)]."""
    src = Path(path).read_text(encoding="utf-8").strip()
    if not src.startswith("{"):
        body = src[src.index("{"): src.rindex("}") + 1]
        body = re.sub(r"//[^\n]*", "", body)
        body = re.sub(r"([{,]\s*)([A-Za-z_$][\w$]*)\s*:", r'\1"\2":', body)
        body = re.sub(r",(\s*[}\]])", r"\1", body)
        tl = json.loads(body)
    else:
        tl = json.loads(src)

    # Support audio_meta.json (clause-end - 0.15s or global_end - 0.15s)
    if isinstance(tl, dict) and "voices" in tl and isinstance(tl["voices"], list):
        beats = []
        offset = 0.0
        for v in tl["voices"]:
            frame_no = v.get("frame", 0)
            base_t = v.get("global_start", offset)
            for idx, w in enumerate(v.get("words", [])):
                # Sample 0.15s before clause end (settled state per motion-explainer review-loop)
                t_sample = base_t + max(w.get("start", 0.0), w.get("end", 0.0) - 0.15)
                short_txt = w.get("text", "")[:8]
                beats.append((f"F{frame_no}.{idx} {t_sample:.2f}s {short_txt}", t_sample))
            offset = base_t + v.get("duration_s", 0.0)
        if beats:
            return beats

    beats = [("cover 0.00s", 0.0)]

    def walk(node, key):
        if key == "DUR":
            return
        if isinstance(node, (int, float)) and not isinstance(node, bool):
            beats.append((key, float(node)))
        elif isinstance(node, dict):
            for k, v in node.items():
                walk(v, f"{key}.{k}" if key else k)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{key}[{i}]")

    walk(tl, "")
    beats_sorted = sorted(beats[1:], key=lambda b: b[1])
    out = [beats[0]]
    for k, t in beats_sorted:
        ts = t + settle
        out.append((f"{k} {ts:.2f}s", ts))
    return out


def video_meta(video):
    out = subprocess.run(
        [FFMPEG, "-hide_banner", "-i", str(video)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    m = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", out.stderr)
    if not m:
        sys.exit(f"無法從 ffmpeg 讀取影片長度：{video}")
    dur = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
    fps_m = re.search(r"Stream #[^\n]*Video:[^\n]*?(\d+(?:\.\d+)?)\s*fps", out.stderr)
    fps = float(fps_m.group(1)) if fps_m and float(fps_m.group(1)) > 0 else 30.0
    return dur, fps


def duration(video):
    dur, _ = video_meta(video)
    return dur


def grab(video, lbl, t, dest, end, fps=30.0):
    dt = max(1.0 / max(fps, 1.0), 0.033)
    # Start at most one frame interval before container duration
    t_initial = max(0.0, min(float(t), max(0.0, end - dt * 0.5)))
    # Quantize to frame grid if needed, then step back by dt on miss
    candidates = [t_initial]
    step = dt
    for k in range(1, 16):
        cand = max(0.0, math.floor((t_initial / dt) - k + 1e-6) * dt)
        if cand not in candidates:
            candidates.append(cand)
        if cand == 0.0:
            break
    if 0.0 not in candidates:
        candidates.append(0.0)

    dest_path = Path(dest)
    for t_try in candidates:
        if dest_path.exists():
            dest_path.unlink()
        subprocess.run(
            [FFMPEG, "-v", "error", "-y", "-ss", f"{t_try:.3f}", "-i", str(video),
             "-frames:v", "1", str(dest_path)],
            check=True,
        )
        if dest_path.exists() and dest_path.stat().st_size > 0:
            if abs(t_try - float(t)) >= max(0.06, dt * 0.6):
                lbl = f"{lbl} (@{t_try:.2f}s)"
            return lbl, dest_path

    sys.exit(f"ffmpeg wrote no frame at {t:.3f}s (tried backoffs: {candidates[:5]})")


def label_font():
    from PIL import ImageFont
    candidates = (
        "msjh.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "arial.ttf",
        "DejaVuSans.ttf",
    )
    for name in candidates:
        try:
            return ImageFont.truetype(name, 15)
        except OSError:
            continue
    return ImageFont.load_default()


def build_sheets(tiles, out_dir, width, stem):
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        sys.exit("缺少 Pillow：請執行 pip install pillow")
    out_dir.mkdir(parents=True, exist_ok=True)
    font = label_font()
    per = COLS * ROWS
    written = []
    for n in range(0, len(tiles), per):
        batch = tiles[n:n + per]
        first = Image.open(batch[0][1])
        h = round(first.height * width / first.width)
        cell_h = h + LABEL_H
        sheet = Image.new("RGB", (COLS * width + (COLS + 1) * GAP,
                                  ROWS * cell_h + (ROWS + 1) * GAP), (24, 24, 24))
        draw = ImageDraw.Draw(sheet)
        for i, (label, img_path) in enumerate(batch):
            x = GAP + (i % COLS) * (width + GAP)
            y = GAP + (i // COLS) * (cell_h + GAP)
            img = Image.open(img_path).convert("RGB").resize((width, h), Image.Resampling.LANCZOS)
            draw.text((x + 4, y + 4), label, fill=(240, 240, 240), font=font)
            sheet.paste(img, (x, y + LABEL_H))
        dest = out_dir / f"{stem}-{n // per + 1}.png"
        sheet.save(dest)
        written.append(dest)
    return written


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--video", help="rendered video to sample with ffmpeg")
    src.add_argument("--images", nargs="+", help="existing frame images, in order")
    p.add_argument("--timeline", "--audio-meta", dest="timeline", help="scene-timeline.json, timeline.js, or audio_meta.json")
    p.add_argument("--settle", type=float, default=0.3, help="seconds after each beat (default 0.3)")
    p.add_argument("--at", help="comma-separated times in seconds")
    p.add_argument("--from", dest="t0", type=float)
    p.add_argument("--to", dest="t1", type=float)
    p.add_argument("--every", type=float, default=1.5, help="interval in seconds when --from/--to or fallback is used")
    p.add_argument("--labels", help="comma-separated labels for --images")
    p.add_argument("--width", type=int, default=360, help="tile width in px (default 360 = phone feed)")
    p.add_argument("--out", "--out-dir", dest="out", default="sheets", help="output folder (default sheets)")
    p.add_argument("--name", default="beats", help="sheet file stem (default beats)")
    a = p.parse_args()

    if a.images:
        labels = a.labels.split(",") if a.labels else [Path(i).stem for i in a.images]
        if len(labels) != len(a.images):
            sys.exit("--labels must have one entry per image")
        tiles = list(zip(labels, a.images))
        for path in build_sheets(tiles, Path(a.out), a.width, a.name):
            print(path)
    else:
        end, fps = video_meta(a.video)
        if a.timeline:
            moments = timeline_beats(a.timeline, a.settle)
        elif a.at:
            moments = [(f"{float(t):.2f}s", float(t)) for t in a.at.split(",")]
        elif a.t0 is not None and a.t1 is not None:
            steps = int(round((a.t1 - a.t0) / a.every)) + 1
            moments = [(f"{a.t0 + i * a.every:.2f}s", a.t0 + i * a.every) for i in range(steps)]
        else:
            steps = max(1, int(end // a.every) + 1)
            moments = [(f"{i * a.every:.2f}s", min(end - 0.05, i * a.every)) for i in range(steps)]
        with tempfile.TemporaryDirectory(prefix="sheet-") as tmp_str:
            tmp = Path(tmp_str)
            tiles = [grab(a.video, lbl, t, tmp / f"f{i:03d}.png", end, fps) for i, (lbl, t) in enumerate(moments)]
            for path in build_sheets(tiles, Path(a.out), a.width, a.name):
                print(path)


if __name__ == "__main__":
    main()

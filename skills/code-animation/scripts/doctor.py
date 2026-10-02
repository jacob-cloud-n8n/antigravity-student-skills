#!/usr/bin/env python3
"""環境檢查：第一次使用前跑一次，缺什麼就告訴你怎麼裝（Windows／Mac 都適用）。

用法：python3 doctor.py      （Windows 若 python3 不存在，改用 python 或 py）
"""
import os, sys, shutil, platform, subprocess
from pathlib import Path

WIN = platform.system() == "Windows"
ASSET = Path(os.path.expanduser("~/.local/share/code-animation-assets"))
ok_all = True


def check(name, ok, fix):
    global ok_all
    print(f"{'✅' if ok else '❌'} {name}")
    if not ok:
        ok_all = False
        print(f"   → 修法：{fix}")


py = sys.version_info
check(f"Python {py.major}.{py.minor}（需要 3.9 以上）", py >= (3, 9),
      "到 https://www.python.org/downloads/ 安裝最新版（Windows 安裝時勾選 Add python.exe to PATH）")

try:
    import numpy  # noqa
    has_np = True
except ImportError:
    has_np = False
check("numpy（配樂合成用）", has_np, "pip install numpy")

try:
    from playwright.sync_api import sync_playwright
    has_pw = True
except ImportError:
    has_pw = False
check("Playwright（逐格截圖用）", has_pw, "pip install playwright")

if has_pw:
    try:
        with sync_playwright() as pw:
            pw.chromium.launch().close()
        has_chrome = True
    except Exception:
        has_chrome = False
    check("Playwright 的 Chromium 瀏覽器", has_chrome, "python -m playwright install chromium")

ff = shutil.which("ffmpeg") or (os.path.expanduser("~/.local/bin/ffmpeg") if os.path.exists(os.path.expanduser("~/.local/bin/ffmpeg")) else None)
check("ffmpeg（合成影片用）", bool(ff),
      "winget install Gyan.FFmpeg（裝完重開終端機）" if WIN else "brew install ffmpeg（沒有 Homebrew 就先到 https://brew.sh 安裝）")
if ff:
    v = subprocess.run([ff, "-version"], capture_output=True, text=True).stdout.splitlines()[:1]
    print(f"   {v[0] if v else ''}")

need = ["lib/gsap/gsap.min.js", "lib/tone/Tone.js", "font-noto-sans-tc/NotoSansTC.ttf", "font-inter/Inter.ttf"]
missing = [n for n in need if not (ASSET / n).exists()]
check(f"本機素材庫（{ASSET}）", not missing,
      f"python3 {Path(__file__).parent / 'fetch_assets.py'}（下載函式庫、字型、音效與角色，約 30 MB）" + (f"；缺：{missing}" if missing else ""))

print("\n" + ("全部就緒，可以開始做動畫。" if ok_all else "照上面的修法處理完，再跑一次本檢查。"))
sys.exit(0 if ok_all else 1)

#!/usr/bin/env python3
"""Shrink CJK fonts to the characters the animation actually uses (12–17 MB -> ~150–300 KB).

Adapted from mathruffian-dot/claude-motion-explainer (MIT, commit d868d7c1d71590b00174ebb76ef172b33aeddec2,
blob 9a8a20ac1afaed5bf042d48927164971b80ecb85) for the code-animation pipeline.
See ../THIRD_PARTY_NOTICES.md for full MIT license text.

Scans scene HTML/JS/JSON/MD files in a project, collects all printable characters plus ASCII and
common CJK punctuation, writes <font>.subset.woff2 (or .ttf/.otf if `brotli` is not installed),
and optionally rewrites font paths in the target HTML files (with --restore to undo).

Run LAST, after all text/captions edits — new characters added later would be missing from the
subset until you re-run this script.

Usage:
  # Mode 1: Project directory (scans *.html, *.js, SCRIPT.md, audio_meta.json, brief.json)
  python3 scripts/subset_fonts.py --project <dir> [--fonts-dir <dir>]
  python3 scripts/subset_fonts.py --project <dir> --restore

  # Mode 2: Standalone single font + scan files (outputs subset font for KIT.setup or offline HTML)
  python3 scripts/subset_fonts.py --scan scene.html --font-file ~/.local/share/code-animation-assets/font-noto-sans-tc/NotoSansTC.ttf --out ./NotoSansTC.subset.woff2

Requires: pip install fonttools  (optional: pip install brotli for woff2)
"""
import argparse
import os
import re
import sys
from pathlib import Path

EXTRA = (
    "".join(chr(c) for c in range(0x20, 0x7F))
    + "，。、？！：；「」『』（）《》〈〉【】—…·・～％＋－×÷＝≈≠≤≥→←↑↓①②③④⑤⑥⑦⑧⑨⑩²³°μ"
)
ASSET_DEFAULT = Path(os.path.expanduser("~/.local/share/code-animation-assets/font-noto-sans-tc/NotoSansTC.ttf"))


def collect_project_files(project: Path):
    files = []
    for pat in ("*.html", "compositions/**/*.html", "*.js", "SCRIPT.md", "audio_meta.json", "brief.json"):
        files.extend(sorted(project.glob(pat)))
    seen = set()
    out = []
    for f in files:
        if f.is_file() and f.resolve() not in seen:
            seen.add(f.resolve())
            out.append(f)
    return out


def subset_one_font(src: Path, out: Path, chars: set, flavor):
    from fontTools import subset

    opts = subset.Options()
    opts.flavor = flavor
    opts.layout_features = ["*"]
    opts.name_IDs = ["*"]
    opts.notdef_outline = True
    font = subset.load_font(str(src), opts)
    sub = subset.Subsetter(opts)
    sub.populate(text="".join(sorted(chars)))
    sub.subset(font)
    out.parent.mkdir(parents=True, exist_ok=True)
    subset.save_font(font, str(out), opts)
    print(f"{src.name}: {src.stat().st_size / 1e6:.2f} MB -> {out.name} {out.stat().st_size / 1e3:.0f} KB")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", "--project-dir", dest="project", default=".", help="project directory")
    ap.add_argument("--scan", nargs="+", help="explicit files to scan for characters")
    ap.add_argument("--font-file", help="explicit single font file to subset (defaults to code-animation NotoSansTC.ttf if --out is given)")
    ap.add_argument("--out", help="output path when using --font-file")
    ap.add_argument("--fonts-dir", help="directory holding font files (default: <project>/assets/fonts or <project>)")
    ap.add_argument("--fonts", nargs="+", default=["NotoSansTC.ttf", "NotoSansTC-VF.ttf", "NotoSerifTC-VF.ttf", "GenSekiGothic2TW-B.otf"])
    ap.add_argument("--restore", action="store_true", help="restore subset font references back to full font names")
    a = ap.parse_args()

    project = Path(a.project).resolve()
    scan_files = [Path(p).resolve() for p in a.scan] if a.scan else collect_project_files(project)
    html_files = [f for f in scan_files if f.suffix.lower() in (".html", ".js")]

    if a.fonts_dir:
        fonts_dir = Path(a.fonts_dir).resolve()
    elif (project / "assets" / "fonts").exists():
        fonts_dir = project / "assets" / "fonts"
    else:
        fonts_dir = project

    def full_name(stem):
        for ext in (".ttf", ".otf"):
            if (fonts_dir / f"{stem}{ext}").exists():
                return f"{stem}{ext}"
        return f"{stem}.ttf"

    if a.restore:
        for f in html_files:
            t = f.read_text(encoding="utf-8")
            t2 = re.sub(
                r"([\w./-]+?)\.subset\.(?:woff2|ttf|otf)",
                lambda m: f"{Path(m.group(1)).parent.as_posix() + '/' if Path(m.group(1)).parent.as_posix() != '.' else ''}{full_name(Path(m.group(1)).name)}",
                t,
            )
            if t2 != t:
                f.write_text(t2, encoding="utf-8")
                print("restored", f.name)
        return

    try:
        from fontTools import subset  # noqa: F401
    except ImportError:
        sys.exit("缺少 fonttools：請執行 pip install fonttools（另建議 pip install brotli 以輸出 woff2）")

    try:
        import brotli  # noqa: F401
        flavor = "woff2"
    except ImportError:
        flavor = None

    chars = set(EXTRA)
    for f in scan_files:
        if f.exists():
            chars.update(f.read_text(encoding="utf-8", errors="ignore"))
    chars = {c for c in chars if c.isprintable()}
    print(f"{len(chars)} distinct characters across {len(scan_files)} files")

    if a.font_file or a.out:
        src = Path(a.font_file).expanduser().resolve() if a.font_file else ASSET_DEFAULT
        if not src.exists():
            sys.exit(f"找不到字型檔：{src}（請先執行 scripts/fetch_assets.py 或指定 --font-file）")
        ext = "woff2" if (flavor and (not a.out or a.out.endswith(".woff2"))) else src.suffix.lstrip(".")
        out = Path(a.out).resolve() if a.out else (project / f"{src.stem}.subset.{ext}")
        subset_one_font(src, out, chars, "woff2" if out.suffix == ".woff2" and flavor else None)
        return

    renames = {}
    for name in a.fonts:
        src = fonts_dir / name
        if not src.exists():
            continue
        ext = "woff2" if flavor else src.suffix.lstrip(".")
        out = fonts_dir / f"{src.stem}.subset.{ext}"
        subset_one_font(src, out, chars, flavor)
        renames[name] = out.name

    if not renames:
        print(f"No matching font files found in {fonts_dir} (checked {a.fonts}). Tip: use --font-file or --out for single font.")
        return

    for f in html_files:
        t0 = f.read_text(encoding="utf-8")
        t = t0
        for full, small in renames.items():
            stem = Path(full).stem
            t = re.sub(rf"{re.escape(stem)}(?:\.subset\.(?:woff2|ttf|otf)|\.(?:ttf|otf))", small, t)
        if t != t0:
            f.write_text(t, encoding="utf-8")
            print("repointed", f.name)


if __name__ == "__main__":
    main()

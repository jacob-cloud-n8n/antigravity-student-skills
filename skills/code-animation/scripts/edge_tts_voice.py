#!/usr/bin/env python3
"""Read `## Line N` from SCRIPT.md and synthesize <project>/assets/voice/raw/NN.wav with edge-tts.

Adapted from mathruffian-dot/claude-motion-explainer (MIT, commit d868d7c1d71590b00174ebb76ef172b33aeddec2,
blob f29975a090b1172b7df16fe89b41f278327d4dac) for the code-animation pipeline.
See ../THIRD_PARTY_NOTICES.md for full MIT license text.

Taiwan Mandarin neural voices (no GPU, ~1 s per line, requires internet):
  zh-TW-HsiaoChenNeural   female, warm (default)
  zh-TW-YunJheNeural      male, clear
  zh-TW-HsiaoYuNeural     female, bright

Follow with:
  python3 scripts/voice_meta.py --project <dir>

Existing raw/NN.wav files are skipped; delete one to regenerate that line.

⚠️ Licensing note: `edge-tts` (GPL-3.0, invoked via CLI/Python) calls Microsoft's online TTS service.
Check Microsoft's terms before commercial use, or drop WAV files from any licensed TTS into
`assets/voice/raw/NN.wav` and run `voice_meta.py` directly.

Usage:
  python3 scripts/edge_tts_voice.py --project <dir> [--voice zh-TW-HsiaoChenNeural] [--rate +0%]
  python3 scripts/edge_tts_voice.py --list zh-TW
"""
import argparse
import asyncio
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import voice_meta as vm  # noqa: E402

FFMPEG = shutil.which("ffmpeg") or os.path.expanduser("~/.local/bin/ffmpeg")


async def list_voices(locale):
    import edge_tts

    for v in await edge_tts.list_voices():
        if v["Locale"].lower().startswith(locale.lower()):
            print(f"{v['ShortName']:28s} {v['Gender']:8s} {v.get('FriendlyName', '')}")


async def synth(text, voice, rate, pitch, mp3):
    import edge_tts

    await edge_tts.Communicate(text, voice, rate=rate, pitch=pitch).save(str(mp3))


def parse_script_lines(script_text: str):
    """Shared section-scoped parser from voice_meta.parse_script_sections."""
    return vm.parse_script_sections(script_text)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", "--project-dir", dest="project", default=".")
    ap.add_argument("--script", default="SCRIPT.md", help="script markdown filename inside --project")
    ap.add_argument("--voice", default="zh-TW-HsiaoChenNeural")
    ap.add_argument("--rate", default="+0%", help='speaking rate, e.g. "-5%%" or "+10%%"')
    ap.add_argument("--pitch", default="+0Hz", help='pitch shift, e.g. "-2Hz"')
    ap.add_argument("--list", metavar="LOCALE", help="list voices for a locale (e.g. zh-TW) and exit")
    a = ap.parse_args()
    try:
        import edge_tts  # noqa: F401
    except ImportError:
        sys.exit("edge-tts 未安裝：請執行 pip install edge-tts")
    if a.list:
        asyncio.run(list_voices(a.list))
        return
    project = Path(a.project).resolve()
    script_path = project / a.script
    if not script_path.exists():
        sys.exit(f"找不到腳本檔：{script_path}")
    try:
        lines = parse_script_lines(script_path.read_text(encoding="utf-8"))
    except Exception as exc:
        sys.exit(f"腳本解析失敗：{exc}")
    raw = project / "assets" / "voice" / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    for n, text in lines:
        wav = raw / f"{int(n):02d}.wav"
        if wav.exists():
            print("[skip]", wav.name)
            continue
        mp3 = wav.with_suffix(".mp3")
        asyncio.run(synth(text.strip(), a.voice, a.rate, a.pitch, mp3))
        subprocess.run([FFMPEG, "-v", "error", "-y", "-i", str(mp3), "-ar", "24000", "-ac", "1",
                        "-c:a", "pcm_s16le", str(wav)], check=True)
        mp3.unlink()
        print("[ok]", wav.name)
    print(f"voice {a.voice} -> {raw}")


if __name__ == "__main__":
    main()

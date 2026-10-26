#!/usr/bin/env python3
"""Narration WAVs -> trimmed WAVs + audio_meta.json + combined narration.wav (No Whisper ASR needed).

Adapted from mathruffian-dot/claude-motion-explainer (MIT, commit d868d7c1d71590b00174ebb76ef172b33aeddec2,
blob 51e7545ea1eea452b8079e47c52e4366ea650fba) for the code-animation pipeline.
See ../THIRD_PARTY_NOTICES.md for full MIT license text.

For each <project>/assets/voice/raw/NN.wav (NN = line/frame number, from edge_tts_voice.py or any TTS):
  1. trim leading/trailing silence (keep 80 ms head, 150 ms tail) -> assets/voice/NN.wav
  2. find pauses with ffmpeg silencedetect and time each clause of that frame's SCRIPT.md line
     (clauses split at Chinese/Latin punctuation) onto the speech spans between pauses
  3. write audio_meta.json with both per-frame relative times AND global cumulative times
     (global_start, global_end, clauses_flat) so single-scene code-animation HTML can directly
     drive animations and captions from t
  4. concatenate all lines (with --pad hold after each line) into <project>/narration.wav so
     `python3 scripts/render.py scene.html out.mp4 --audio narration.wav` works directly

Caption text is read directly from SCRIPT.md (no Whisper ASR), while clause timing is estimated
from pause detection and character-share weighting.

Usage:
  python3 scripts/voice_meta.py --project <dir> [--pad 0.7] [--last-pad 1.8]
"""
import argparse
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

HEAD_KEEP, TAIL_KEEP = 0.08, 0.15
NOISE, MIN_GAP = "-38dB", 0.10
# -38 dBFS in 16-bit signed PCM is ~32768 * 10^(-38/20) = 412
MIN_PEAK_PCM16 = 450
SPLIT = r"[，。？！；、：,.?!;:]"
FFMPEG = shutil.which("ffmpeg") or os.path.expanduser("~/.local/bin/ffmpeg")


def run(args, check=True):
    res = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and res.returncode != 0:
        cmd_str = " ".join(str(x) for x in args)
        raise RuntimeError(f"命令執行失敗 (exit {res.returncode}): {cmd_str}\n{res.stderr.strip()}")
    return res


def ff_concat_line(p: Path) -> str:
    """Format a path safely for ffmpeg concat demuxer, escaping single quotes."""
    escaped = p.resolve().as_posix().replace("'", r"'\''")
    return f"file '{escaped}'\n"


def duration(path):
    try:
        with wave.open(str(path), "rb") as w:
            frames = w.getnframes()
            rate = float(w.getframerate())
            if rate <= 0:
                raise RuntimeError(f"無效取樣率：{path}")
            return frames / rate
    except wave.Error:
        err = run([FFMPEG, "-hide_banner", "-i", str(path)], check=False).stderr
        m = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", err)
        if m:
            return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
        raise RuntimeError(f"無法讀取音檔長度：{path}")


def wav_has_audible_signal(path) -> bool:
    """Check if a 16-bit PCM WAV file has peak amplitude above the silence floor."""
    try:
        with wave.open(str(path), "rb") as w:
            if w.getsampwidth() != 2 or w.getnframes() == 0:
                return w.getnframes() > 0
            raw = w.readframes(w.getnframes())
            if not raw:
                return False
            count = len(raw) // 2
            samples = struct.unpack(f"<{count}h", raw[: count * 2])
            peak = max((abs(s) for s in samples), default=0)
            return peak >= MIN_PEAK_PCM16
    except Exception:
        return True


def speech_spans(path):
    total = duration(path)
    if total <= 0.02 or not wav_has_audible_signal(path):
        return [], total
    err = run([FFMPEG, "-hide_banner", "-nostats", "-i", str(path),
               "-af", f"silencedetect=noise={NOISE}:d={MIN_GAP}", "-f", "null", "-"], check=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    if len(ends) < len(starts):
        ends.append(total)
    spans, cur = [], 0.0
    for s, e in zip(starts, ends):
        if s > cur + 0.02:
            spans.append((cur, s))
        cur = e
    if cur < total - 0.02:
        spans.append((cur, total))
    # Do NOT invent a span if silencedetect covered the entire file; only fallback when zero silence was detected
    if not spans and not starts and total > 0.02:
        spans.append((0.0, total))
    return spans, total


def trim(src, dst):
    spans, total = speech_spans(src)
    if not spans:
        sys.exit(f"錯誤：{src} 未偵測到有效語音（全靜音或過短）")
    a = max(0.0, spans[0][0] - HEAD_KEEP)
    b = min(total, spans[-1][1] + TAIL_KEEP)
    if b <= a + 0.02:
        sys.exit(f"錯誤：{src} 有效語音長度過短 ({b - a:.3f}s)")
    dst.parent.mkdir(parents=True, exist_ok=True)
    run([FFMPEG, "-v", "error", "-y", "-i", str(src), "-ss", f"{a:.3f}", "-to", f"{b:.3f}",
         "-ar", "24000", "-ac", "1", "-c:a", "pcm_s16le", str(dst)], check=True)
    if not dst.exists() or dst.stat().st_size <= 44:
        sys.exit(f"錯誤：裁切音檔失敗，未產出有效 WAV：{dst}")


def clauses(text):
    parts, buf = [], ""
    for ch in text:
        if re.match(SPLIT, ch):
            if buf.strip():
                parts.append(buf.strip() + (ch if ch in "？?" else ""))
            buf = ""
        else:
            buf += ch
    if buf.strip():
        parts.append(buf.strip())
    return parts


def time_clauses(parts, spans):
    """Equal counts -> one span per clause. Otherwise lay clauses monotonically over remaining
    speech time by character share, snapping to unused pauses only when strictly advancing."""
    parts = [p for p in parts if p and p.strip()]
    if not parts:
        raise ValueError("旁白段落沒有可對齊的子句")
    spans = [(float(s), float(e)) for s, e in spans if float(e) > float(s) + 1e-4]
    if not spans:
        raise ValueError("音檔沒有可對齊的語音區段 (spans 為空)")

    if len(parts) == len(spans):
        return [(p, s, e) for p, (s, e) in zip(parts, spans)]

    weights = [max(1, len(re.sub(r"\s", "", p))) for p in parts]
    gaps = [(spans[i][1], spans[i + 1][0]) for i in range(len(spans) - 1) if spans[i + 1][0] >= spans[i][1]]

    def voiced_after(t_cursor):
        return sum(max(0.0, e - max(s, t_cursor)) for s, e in spans if e > t_cursor)

    def advance_voiced(t_cursor, delta_voiced):
        rem = max(0.0, delta_voiced)
        for s, e in spans:
            if e <= t_cursor:
                continue
            seg_start = max(s, t_cursor)
            seg_len = e - seg_start
            if rem <= seg_len + 1e-9:
                return seg_start + rem
            rem -= seg_len
        return spans[-1][1]

    out = []
    start = spans[0][0]
    used_gap_indices = set()
    n = len(parts)

    for k, (p, w) in enumerate(zip(parts, weights)):
        if k == n - 1:
            end = spans[-1][1]
            if end <= start:
                end = start + 0.02
            out.append((p, start, end))
            break

        rem_w = sum(weights[k:])
        rem_voiced = voiced_after(start)
        if rem_voiced <= 1e-4:
            raise ValueError(f"語音長度不足以分配給第 {k + 1}/{n} 個子句：「{p}」")

        target_voiced = rem_voiced * (w / rem_w)
        raw_end = advance_voiced(start, target_voiced)

        # Candidate unused gaps that strictly follow `start` and leave voiced time for remaining clauses
        min_step = 0.02
        candidates = []
        for idx, (g0, g1) in enumerate(gaps):
            if idx in used_gap_indices:
                continue
            if g0 <= start + min_step:
                continue
            # Ensure remaining clauses after this gap still have voiced speech available
            if voiced_after(g1) <= 0.02 * (n - 1 - k):
                continue
            candidates.append((idx, g0, g1))

        near = min(candidates, key=lambda item: abs((item[1] + item[2]) / 2 - raw_end), default=None)
        if near and abs((near[1] + near[2]) / 2 - raw_end) < 0.35:
            idx, end, nxt = near
            used_gap_indices.add(idx)
        else:
            end = max(start + min_step, raw_end)
            nxt = end

        out.append((p, start, end))
        start = nxt

    # Final invariant verification: 0 <= start < end and strictly monotonic
    prev_end = 0.0
    for p, s, e in out:
        if not (0.0 <= s < e and s >= prev_end - 1e-6):
            raise ValueError(f"子句時間軸異常倒置：{out}")
        prev_end = e
    return out


def parse_script_sections(script_text: str) -> list:
    """Parse `## Line N` sections one section at a time without crossing heading boundaries.
    Returns [(line_no, spoken_text), ...] sorted by line_no, or raises ValueError on invalid input."""
    header_re = re.compile(r"^##\s+Line\s+(\d+)\b[^\n]*$", re.M)
    any_h2_re = re.compile(r"^#{1,2}\s+\S", re.M)
    matches = list(header_re.finditer(script_text))
    if not matches:
        raise ValueError("SCRIPT.md 中找不到任何 '## Line N' 段落")

    seen = {}
    for m in matches:
        line_no = int(m.group(1))
        if line_no <= 0:
            raise ValueError(f"Line 編號必須為正整數：Line {line_no}")
        if line_no in seen:
            raise ValueError(f"SCRIPT.md 中有重複的段落編號：## Line {line_no}")

        sec_start = m.end()
        next_h = any_h2_re.search(script_text, sec_start)
        sec_end = next_h.start() if next_h else len(script_text)
        section_body = script_text[sec_start:sec_end]

        # 1. Prefer 4-space indented spoken lines within THIS section only
        indented = [
            re.sub(r"^    ", "", ln).strip()
            for ln in section_body.splitlines()
            if re.match(r"^    \S", ln)
        ]
        if indented:
            spoken = " ".join(indented).strip()
        else:
            # 2. Otherwise collect plain non-metadata lines within THIS section
            plain = []
            for ln in section_body.splitlines():
                s = ln.strip()
                if not s:
                    if plain:
                        break
                    continue
                if s.startswith((">", "#", "<!--", "-->", "- ", "* ", "```")):
                    continue
                plain.append(s)
            spoken = " ".join(plain).strip()

        if not spoken:
            raise ValueError(f"## Line {line_no} 段落內容為空，請填入旁白台詞")
        seen[line_no] = spoken

    sorted_nos = sorted(seen.keys())
    expected = list(range(1, len(sorted_nos) + 1))
    if sorted_nos != expected:
        raise ValueError(f"SCRIPT.md 的 Line 編號必須從 1 連續遞增（預期 {expected}，實際 {sorted_nos}）")
    return [(n, seen[n]) for n in sorted_nos]


def script_lines(project, script_name="SCRIPT.md"):
    script_path = Path(project) / script_name
    if not script_path.exists():
        raise FileNotFoundError(f"找不到腳本檔：{script_path}")
    return dict(parse_script_sections(script_path.read_text(encoding="utf-8")))


def build_combined_narration(project: Path, voices: list, out_wav: Path, staged_overrides: dict = None):
    """Concatenate trimmed voice WAVs + holds into a single narration.wav for render.py --audio.
    Reads from staged_overrides (rel_path -> staged Path) when provided so formal per-line WAVs
    are untouched until concat succeeds."""
    if not voices:
        raise RuntimeError("沒有任何語音段落可串接為 narration.wav")
    overrides = staged_overrides or {}
    with tempfile.TemporaryDirectory(prefix="narr-") as tmp_str:
        tmp = Path(tmp_str)
        seq = []
        for idx, v in enumerate(voices):
            rel = v["path"]
            wav_path = Path(overrides[rel]).resolve() if rel in overrides else (project / rel).resolve()
            if not wav_path.exists() or wav_path.stat().st_size <= 44:
                raise RuntimeError(f"找不到有效語音檔：{wav_path}")
            seq.append(wav_path)
            pad_s = round(v["duration_s"] - v["speech_s"], 3)
            if pad_s > 0.01:
                pad_wav = tmp / f"pad_{idx:02d}.wav"
                run([FFMPEG, "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
                     "-t", f"{pad_s:.3f}", "-c:a", "pcm_s16le", str(pad_wav)], check=True)
                seq.append(pad_wav)
        listing = tmp / "concat.txt"
        listing.write_text("".join(ff_concat_line(p) for p in seq), encoding="utf-8")
        tmp_out = tmp / "narration.tmp.wav"
        run([FFMPEG, "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(listing),
             "-ar", "24000", "-ac", "1", "-c:a", "pcm_s16le", str(tmp_out)], check=True)
        if not tmp_out.exists() or tmp_out.stat().st_size <= 44:
            raise RuntimeError("ffmpeg concat 未產出有效的 narration.wav")
        out_wav.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(tmp_out, out_wav)


def recompute_globals_and_narration(project: Path, meta: dict, staged_overrides: dict = None):
    """Build narration.wav and audio_meta.json in staging first, then commit per-line WAVs +
    narration.wav + audio_meta.json as a single batch with rollback on commit failure."""
    voices = meta.get("voices", [])
    if not voices:
        raise RuntimeError("voices 為空，無法寫出 audio_meta.json 與 narration.wav")
    cursor = 0.0
    clauses_flat = []
    for v in voices:
        v["global_start"] = round(cursor, 3)
        v["global_end"] = round(cursor + v["duration_s"], 3)
        for w in v.get("words", []):
            w["global_start"] = round(cursor + w["start"], 3)
            w["global_end"] = round(cursor + w["end"], 3)
            clauses_flat.append({
                "frame": v["frame"],
                "text": w["text"],
                "start": w["global_start"],
                "end": w["global_end"],
            })
        cursor += v["duration_s"]
    meta["total_duration_s"] = round(cursor, 2)
    meta["clauses_flat"] = clauses_flat

    overrides = staged_overrides or {}
    tmp_wav = project / ".narration.tmp.wav"
    tmp_meta = project / ".audio_meta.tmp.json"
    try:
        # 1. Build combined narration and metadata in temporary files BEFORE touching any formal output
        build_combined_narration(project, voices, tmp_wav, staged_overrides=overrides)
        tmp_meta.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        # 2. Snapshot existing formal files in memory so any commit-step error rolls back cleanly
        targets = [project / rel for rel in overrides] + [project / "narration.wav", project / "audio_meta.json"]
        prior_snapshots = {t: (t.read_bytes() if t.exists() else None) for t in targets}
        try:
            for rel, staged_src in overrides.items():
                dst = project / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                tmp_dst = dst.with_suffix(dst.suffix + ".tmp")
                shutil.copyfile(staged_src, tmp_dst)
                os.replace(tmp_dst, dst)
            os.replace(tmp_wav, project / "narration.wav")
            os.replace(tmp_meta, project / "audio_meta.json")
        except Exception:
            for t, old_bytes in prior_snapshots.items():
                if old_bytes is None:
                    if t.exists():
                        t.unlink()
                else:
                    t.parent.mkdir(parents=True, exist_ok=True)
                    t.write_bytes(old_bytes)
            raise
    finally:
        if tmp_wav.exists():
            tmp_wav.unlink()
        if tmp_meta.exists():
            tmp_meta.unlink()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", "--project-dir", dest="project", default=".")
    ap.add_argument("--script", default="SCRIPT.md")
    ap.add_argument("--pad", type=float, default=0.7, help="seconds of hold after each line")
    ap.add_argument("--last-pad", type=float, default=1.8, help="hold after the closing line")
    a = ap.parse_args()
    project = Path(a.project).resolve()
    raw = project / "assets/voice/raw"
    try:
        lines = script_lines(project, a.script)
    except Exception as exc:
        sys.exit(f"腳本解析失敗：{exc}")
    frames = sorted(lines)
    if not frames:
        sys.exit("錯誤：SCRIPT.md 中沒有任何旁白段落")

    with tempfile.TemporaryDirectory(prefix="vmeta-stage-") as stage_str:
        stage_dir = Path(stage_str)
        voices = []
        staged_overrides = {}
        for n in frames:
            src = raw / f"{n:02d}.wav"
            if not src.exists():
                sys.exit(f"missing {src}")
            staged_dst = stage_dir / f"{n:02d}.wav"
            trim(src, staged_dst)
            spans, total = speech_spans(staged_dst)
            if not spans:
                sys.exit(f"錯誤：{src} 裁切後未偵測到有效語音")
            part_list = clauses(lines[n])
            if not part_list:
                sys.exit(f"錯誤：Line {n} 不含有效文字子句")
            try:
                timed = time_clauses(part_list, spans)
            except Exception as exc:
                sys.exit(f"錯誤：Line {n} 子句時間軸對齊失敗：{exc}")
            pad = a.last_pad if n == frames[-1] else a.pad
            rel_path = f"assets/voice/{n:02d}.wav"
            staged_overrides[rel_path] = staged_dst
            voices.append({
                "frame": n, "path": rel_path, "source": "host",
                "speech_s": round(total, 3), "duration_s": round(total + pad, 2),
                "words": [{"text": t, "start": round(s, 3), "end": round(e, 3)} for t, s, e in timed],
            })
            print(f"frame {n}: {total:.2f}s speech, {len(spans)} spans, {len(timed)} clauses")

        meta = {"bgm": None, "voices": voices, "sfx": []}
        try:
            recompute_globals_and_narration(project, meta, staged_overrides=staged_overrides)
        except Exception as exc:
            sys.exit(f"錯誤：產生 narration.wav / audio_meta.json 失敗：{exc}")
    print("total", meta["total_duration_s"], "s -> audio_meta.json & narration.wav")


if __name__ == "__main__":
    main()

# Third-Party Notices (`code-animation`)

This folder (`skills/code-animation/`) includes scripts, helper functions, and motion-design rules adapted from open-source projects under the MIT License. When distributing or publishing this skill (e.g., via `skills/student-pack.manifest`), keep this file intact alongside `SKILL.md`.

---

## 1. Adapted Work Included in This Skill

The following files in `skills/code-animation/` are adapted from **[mathruffian-dot/claude-motion-explainer](https://github.com/mathruffian-dot/claude-motion-explainer)** (commit `d868d7c1d71590b00174ebb76ef172b33aeddec2`, MIT License, Copyright (c) 2026 mathruffian-dot), which in turn adapts `motion-design` and `review-loop` from **[whaleyxbt/claude-motion](https://github.com/whaleyxbt/claude-motion)** (MIT License, Copyright (c) 2026 whaleyxbt):

| Local File in `skills/code-animation/` | Upstream Source Path (`d868d7c1d71590b00174ebb76ef172b33aeddec2`) | Upstream Git Blob SHA-1 | Adaptation Summary |
|---|---|---|---|
| `scripts/sheet.py` | `skills/review-loop/scripts/sheet.py` | `d512d7c03852ca48166edabfd502e1fe3c281945` | Adapted for `render.py` (`*-timeline.json`, `audio_meta.json`); removed `ffprobe` requirement; added low-FPS tail-frame backoff |
| `scripts/subset_fonts.py` | `skills/motion-explainer/scripts/subset_fonts.py` | `9a8a20ac1afaed5bf042d48927164971b80ecb85` | Added single-file `--scan` / `--font-file` / `--out` mode and `.ttf` fallback when `brotli` is absent |
| `scripts/edge_tts_voice.py` | `skills/motion-explainer/scripts/edge_tts_voice.py` | `f29975a090b1172b7df16fe89b41f278327d4dac` | Unified section-scoped `## Line N` parser with `voice_meta.py` |
| `scripts/voice_meta.py` | `skills/motion-explainer/scripts/voice_meta.py` | `51e7545ea1eea452b8079e47c52e4366ea650fba` | Added `global_start`/`global_end`/`clauses_flat`, combined `narration.wav` concatenation, monotonic clause timing, and `wave`-based duration |
| `scripts/fix_voice.py` | `skills/motion-explainer/scripts/fix_voice.py` | `c904fa309dc5bec24754088c3012fc214dcb396f` | Integrated with `recompute_globals_and_narration()` and safe concat path escaping |
| `templates/kit.js` (`invEase2`, `invEase3`, `caption`) & `SKILL.md` rules | `skills/motion-design/SKILL.md` (`613251ec...`), `skills/motion-explainer/SKILL.md` (`afe8483a...`), `skills/motion-explainer/references/lessons.md` (`dcf3f0f8...`), `skills/motion-explainer/scripts/patch_captions.py` (`c5c626a3...`) | See paths | Ported inverse-easing helpers (adjusted for GSAP 3 `power2.out`/`power3.out`), Canvas active-clause caption renderer, and GSAP/CJK rules |

---

## 2. Excluded Components & Optional User-Installed Dependencies

- **NOT included and NOT used by this skill**:
  - **HyperFrames CLI** (`heygen-com/hyperframes`, Apache-2.0): Not installed or invoked; `code-animation` renders directly via Playwright + `ffmpeg` (`scripts/render.py`).
  - **Breeze TTS 2** (`breezeblue-ai/breeze-tts`, BreezeBlue Research and Non-Commercial License): Intentionally excluded due to non-commercial license restrictions.
- **Optional external dependencies installed by the user (`scripts/fetch_assets.py` or `pip`)**:
  - **GSAP** (https://gsap.com/licensing/) — Standard "No Charge" license (free for commercial & AI-generated animation videos; prohibited only when embedding inside a competing visual animation builder).
  - **Tone.js** (MIT), **Open Peeps** (CC0 1.0), **Kenney Audio** (CC0 1.0), **Noto Sans TC / Inter** (SIL Open Font License 1.1) — fetched locally by `scripts/fetch_assets.py`.
  - **edge-tts** (https://github.com/rany2/edge-tts, GPL-3.0) — Optional Python CLI/package invoked by `scripts/edge_tts_voice.py` to call Microsoft's online text-to-speech service; check Microsoft's service terms before commercial use, or provide WAV files from any licensed TTS provider.

---

## 3. MIT License — `mathruffian-dot/claude-motion-explainer`

```text
MIT License

Copyright (c) 2026 mathruffian-dot

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 4. MIT License — `whaleyxbt/claude-motion`

```text
MIT License

Copyright (c) 2026 whaleyxbt

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

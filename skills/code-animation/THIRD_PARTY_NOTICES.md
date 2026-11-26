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

---

## 5. 改寫納入之 Apache-2.0 元件 — `Vincentwei1021/video-shotcraft`

本技能（`skills/code-animation/`）另包含改寫自開源專案 **[Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft)**（授權條款：**Apache License 2.0［Apache-2.0］**，Copyright 2026 Wei Yihao）之下列兩個部分：

| 本技能檔案（`skills/code-animation/`） | 上游來源檔案（`Vincentwei1021/video-shotcraft`） | 授權條款 | 改寫說明（Apache-2.0 第 4(b) 條修改聲明） |
|---|---|---|---|
| `templates/kit-pagecam.js`（`kit-pagecam.js`） | `assets/lib/PageCam.tsx` | Apache-2.0 | 移除 React 與 Remotion（`useCurrentFrame`／`interpolate`／`Easing`／`AbsoluteFill`／`Img`）相依，改寫為以秒數 `t` 逐格驅動之原生瀏覽器 DOM 函式 `pageCam(el, t, keyframes, opts)`，保留原生 CSS `zoom` 版面級放大座標換算與 `backdrop-filter: blur()` 螢幕空間景深遮罩。 |
| `references/shotcraft-rules.md`（`shotcraft-rules.md`） | `aesthetic-rules.md`、`promo-energy-arc.md` | Apache-2.0 | 將原 27 條審美／運鏡／音效／文案／流程規則（R1–R4、Q1–Q11、S1–S5、C1–C3、P1–P4）與四段能量配額改寫濃縮為繁體中文可勾選驗收清單，並增補與本技能 `SKILL.md` 現有規則之衝突與取捨對照。 |

- **未使用之素材與框架聲明**：
  - 本技能**未使用、亦未隨附** `Vincentwei1021/video-shotcraft` 專案中之任何圖片、頁面貼圖（textures）、音效檔（SFX）、背景音樂（BGM）、字型或模板片媒體素材（`template/` 內各類影音圖檔）。
  - 本技能**未採用、亦未安裝** Remotion 渲染框架，仍維持既有 HTML＋`window.render(t)`＋Playwright＋`ffmpeg` 逐格渲染管線。

### Apache License 2.0 — `Vincentwei1021/video-shotcraft`

```text
Copyright 2026 Wei Yihao

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

---

                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS
```

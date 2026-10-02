// Tone.js 配樂範本（給 scripts/tone_render.py）：T＝畫面時間軸，dest＝已含限幅的輸出。
// 原則同 music.py：先定段落情緒，每個畫面事件對一個音效，最重一擊只給轉折（T.gate）。
async function score(T, Tone, dest) {
  const verb = new Tone.Freeverb({roomSize: 0.7, dampening: 3000, wet: 0.25}).connect(dest);   // 固定濾波器＝可重現
  const pad = new Tone.PolySynth(Tone.Synth, {oscillator: {type: 'fatsawtooth', count: 3, spread: 20},
    envelope: {attack: 0.6, release: 1.2}, volume: -20}).connect(verb);
  const pluck = new Tone.PolySynth(Tone.FMSynth, {harmonicity: 3, modulationIndex: 6,
    envelope: {attack: 0.002, decay: 0.25, sustain: 0, release: 0.2}, volume: -16}).connect(verb);
  const kick = new Tone.MembraneSynth({volume: -6}).connect(dest);
  // hi-hat 用 NoiseSynth＋高通；⛔ MetalSynth 在 Tone 15.1.22 離線渲染第二次觸發就報錯（2026-10-02 實測）
  const hpf = new Tone.Filter(7000, 'highpass').connect(dest);
  const hat = new Tone.NoiseSynth({noise: {type: 'white'}, envelope: {attack: 0.001, decay: 0.04, sustain: 0}, volume: -26}).connect(hpf);
  const bell = new Tone.FMSynth({harmonicity: 3.01, modulationIndex: 12,
    envelope: {attack: 0.001, decay: 1.2, sustain: 0, release: 1}, volume: -14}).connect(verb);
  const BEAT = 0.5;
  const at = t => Math.max(t, 0.01);   // ⛔ 單音合成器（Membrane／Noise／FM）的開始時間必須 > 0，排在第 0 秒會直接報錯
  const chords = [['D3', 'F3', 'A3'], ['Bb2', 'D3', 'F3'], ['F3', 'A3', 'C4'], ['C3', 'E3', 'G3']];
  (T.items || []).forEach((t0, i) => {
    const ch = chords[i % chords.length];
    pad.triggerAttackRelease(ch, 3.8, t0);
    bell.triggerAttackRelease(Tone.Frequency(ch[2]).transpose(24), 1.2, at(t0));
    for (let b = 0; b < 8; b++) {
      kick.triggerAttackRelease('C1', 0.2, at(t0 + b * BEAT));
      hat.triggerAttackRelease(0.03, t0 + b * BEAT + BEAT / 2);
      pluck.triggerAttackRelease(Tone.Frequency(ch[b % 3]).transpose(12), 0.2, t0 + b * BEAT);
    }
  });
  if (T.gate != null) kick.triggerAttackRelease('A0', 0.8, T.gate, 1);
  if (T.cta != null) bell.triggerAttackRelease('A5', 2, T.cta);

  // ---- 選項 C：素材庫的 Kenney CC0 音效（點擊／撞擊／短配樂）----
  // 檔案在 ASSET_DIR 下：kenney-interface-sounds/Audio/click_001.ogg、kenney-impact-sounds/Audio/impactBell_heavy_000.ogg、
  //   kenney-music-jingles/Audio/Pizzicato jingles/jingles_PIZZI00.ogg …（先開資料夾挑）
  const sfx = async (path, time, vol = -6) => {
    const p = new Tone.Player({url: `${ASSET_DIR}/${path}`, volume: vol}).connect(dest);
    await Tone.loaded(); p.start(at(time));
  };
  if (T.click != null) await sfx('kenney-interface-sounds/Audio/click_001.ogg', T.click);
  if (T.outro != null) await sfx('kenney-music-jingles/Audio/Pizzicato jingles/jingles_PIZZI00.ogg', T.outro, -10);
}

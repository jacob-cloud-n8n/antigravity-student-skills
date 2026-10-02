// kit.js — 程式動畫共用工具：載入器、配色、時間工具、文字、幾何、手繪線條、角色上色。
// 用法：場景 HTML 先 <script src="kit.js"></script>，再
//   KIT.setup({palette: 'dark', libs: ['gsap/gsap.min.js']}).then(() => { …建場景… ; window.__ready = true; });
// 規則：畫面只能由 window.render(t) 依秒數決定——不得用 setTimeout／requestAnimationFrame／CSS transition。
window.KIT = (() => {
  const A = window.ASSET_DIR || '';   // 渲染器注入的本機素材庫網址（http://127.0.0.1:埠）

  // ---------- 配色：深色／淺色／自訂（只要給 bg、ink、acc 三色，其餘自動推）----------
  const PALETTES = {
    dark:  {bg: '#070a0f', card: '#0f172a', line: '#1e293b', line2: '#334155', ink: '#e8edf3', muted: '#94a3b8', acc: '#e8a33d'},
    light: {bg: '#fafaf8', card: '#f0f0ec', line: '#e2e2dc', line2: '#c9c9c2', ink: '#0a0a0a', muted: '#6b6b66', acc: '#0e9f6e'},
  };
  const hex = h => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16));
  const mix = (a, b, p) => '#' + hex(a).map((v, i) => Math.round(v + (hex(b)[i] - v) * p).toString(16).padStart(2, '0')).join('');
  function palette(p) {
    if (typeof p === 'string') return {...PALETTES[p]};
    const {bg, ink, acc} = p;                                   // 自訂品牌色
    return {bg, ink, acc, card: mix(bg, ink, 0.05), line: mix(bg, ink, 0.12), line2: mix(bg, ink, 0.22), muted: mix(bg, ink, 0.6)};
  }

  // ---------- 載入：字型（本機素材庫）＋函式庫 ----------
  const DEFAULT_FONTS = [['TC', 'font-noto-sans-tc/NotoSansTC.ttf', '一'], ['Inter', 'font-inter/Inter.ttf', '0']];
  const loadScript = src => new Promise((res, rej) => {
    const s = document.createElement('script'); s.src = src; s.onload = res;
    s.onerror = () => rej(new Error('載入失敗：' + src + '（先跑 scripts/fetch_assets.py？）')); document.head.appendChild(s);
  });
  let C = palette('dark');
  async function setup({palette: p = 'dark', libs = [], fonts = DEFAULT_FONTS} = {}) {
    if (!A) throw new Error('沒有 ASSET_DIR：請用 scripts/render.py 渲染，並先跑 scripts/fetch_assets.py');
    // 網址參數可覆寫配色：?palette=light ／ ?bg=%23ffffff&ink=%23111111&acc=%23e4572e（render.py --param 會帶上）
    const q = new URLSearchParams(location.search);
    if (q.get('bg') && q.get('ink') && q.get('acc')) p = {bg: q.get('bg'), ink: q.get('ink'), acc: q.get('acc')};
    else if (q.get('palette')) p = q.get('palette');
    C = palette(p);
    for (const [fam, path] of fonts) { const f = new FontFace(fam, `url(${A}/${path})`, {weight: '100 900'}); await f.load(); document.fonts.add(f); }
    window.FONTS = fonts.map(([f, , ch]) => [f, ch]);
    for (const l of libs) await loadScript(`${A}/lib/${l}`);
    document.documentElement.style.background = C.bg; document.body.style.background = C.bg;
    return C;
  }

  // ---------- 時間工具 ----------
  const clamp = x => Math.max(0, Math.min(1, x));
  const ease = x => 1 - Math.pow(1 - clamp(x), 3);
  const easeIO = x => { x = clamp(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
  const easeBack = x => { x = clamp(x); const c = 1.7; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };  // 帶回彈的落地
  const prog = (t, t0, d) => ease((t - t0) / d);
  const lerp = (a, b, p) => a + (b - a) * p;
  const win = (t, a, b, fi = 0.25, fo = 0.25) => Math.min(prog(t, a, fi), 1 - prog(t, b - fo, fo));     // 區段淡入淡出
  const rise = (t, t0, d = 0.35) => { const p = prog(t, t0, d); return {a: p, dy: (1 - p) * 28}; };      // 由下浮入

  // ---------- Canvas 畫筆（ctx 由場景傳入）----------
  function text(ctx, s, x, y, {px = 48, w = 700, fam = 'TC', col = C.ink, a = 1, dy = 0, align = 'left'} = {}) {
    if (a <= 0) return;
    ctx.save(); ctx.globalAlpha = a; ctx.font = `${w} ${px}px ${fam}`; ctx.fillStyle = col; ctx.textAlign = align;
    ctx.fillText(s, x, y + dy); ctx.restore();
  }
  function fillR(ctx, x, y, w, h, r, col, a = 1) { ctx.save(); ctx.globalAlpha = a; ctx.beginPath(); ctx.roundRect(x, y, w, h, r); ctx.fillStyle = col; ctx.fill(); ctx.restore(); }
  function strokeR(ctx, x, y, w, h, r, col, lw = 2, a = 1) { ctx.save(); ctx.globalAlpha = a; ctx.beginPath(); ctx.roundRect(x, y, w, h, r); ctx.lineWidth = lw; ctx.strokeStyle = col; ctx.stroke(); ctx.restore(); }
  function line(ctx, x1, y1, x2, y2, col, lw = 3, a = 1) { ctx.save(); ctx.globalAlpha = a; ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.lineWidth = lw; ctx.strokeStyle = col; ctx.lineCap = 'round'; ctx.stroke(); ctx.restore(); }
  function cursor(ctx, x, y, s = 1.6, a = 1, col = C.ink) {          // 可當貫穿全片的主角符號
    if (a <= 0) return;
    ctx.save(); ctx.globalAlpha = a; ctx.translate(x, y); ctx.scale(s, s);
    ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(0, 34); ctx.lineTo(9, 26); ctx.lineTo(15, 40); ctx.lineTo(21, 37); ctx.lineTo(15, 24); ctx.lineTo(27, 24); ctx.closePath();
    ctx.fillStyle = col; ctx.fill(); ctx.lineWidth = 2.5; ctx.strokeStyle = C.bg; ctx.stroke(); ctx.restore();
  }

  // ---------- 手繪線條：每秒沸騰 8 次＋可畫到一半（p）----------
  const rnd = n => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
  function sketch(ctx, t, pts, {col = C.ink, lw = 5, a = 1, p = 1, close = false, fill = null, seed = 1, amp = 2} = {}) {
    if (a <= 0 || p <= 0) return;
    const k = Math.floor(t * 8);
    let q = (close ? [...pts, pts[0]] : pts).map((v, i) => [v[0] + (rnd(seed * 31 + i * 7.3 + k * 13.1) - .5) * 2 * amp, v[1] + (rnd(seed * 17 + i * 11.7 + k * 29.3) - .5) * 2 * amp]);
    if (p < 1) {
      const seg = []; let tot = 0;
      for (let i = 1; i < q.length; i++) { const d = Math.hypot(q[i][0] - q[i - 1][0], q[i][1] - q[i - 1][1]); seg.push(d); tot += d; }
      let left = tot * p; const out = [q[0]];
      for (let i = 1; i < q.length && left > 0; i++) {
        if (seg[i - 1] <= left) { out.push(q[i]); left -= seg[i - 1]; }
        else { const f = left / seg[i - 1]; out.push([lerp(q[i - 1][0], q[i][0], f), lerp(q[i - 1][1], q[i][1], f)]); left = 0; }
      }
      q = out;
    }
    ctx.save(); ctx.globalAlpha = a; ctx.beginPath(); ctx.moveTo(...q[0]); for (const v of q.slice(1)) ctx.lineTo(...v);
    if (fill && p >= 1) { ctx.fillStyle = fill; ctx.fill(); }
    ctx.lineWidth = lw; ctx.strokeStyle = col; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.stroke(); ctx.restore();
  }
  const circle = (cx, cy, rx, ry = rx, n = 36, a0 = 0, a1 = Math.PI * 2) => Array.from({length: n + 1}, (_, i) => { const a = lerp(a0, a1, i / n); return [cx + Math.cos(a) * rx, cy + Math.sin(a) * ry]; });
  const rect = (x, y, w, h) => [[x, y], [x + w, y], [x + w, y + h], [x, y + h]];

  // ---------- 角色：Open Peeps（CC0）依配色上色 ----------
  // 原檔黑線白底 → 線改成 ink、底改成 bg；回傳 SVG 字串，放進 DOM 後用 GSAP 依 t 驅動
  // name：'standing-5'（站姿 30 張）／'sitting-3'（坐姿 14 張）／'12'（半身 49 張）；編號不連號，先看資料夾
  async function peep(name) {
    const r = await fetch(`${A}/open-peeps-svg/peep-${name}.svg`);
    if (!r.ok) throw new Error(`找不到角色 peep-${name}.svg（看素材庫 open-peeps-svg/ 有哪些；或先跑 scripts/fetch_assets.py）`);
    return (await r.text()).replace(/<\?xml[^>]*>/, '').replace(/#000000/gi, C.ink).replace(/#FFFFFF/gi, C.bg);
  }

  return {setup, palette, PALETTES, get C() { return C; }, set C(v) { C = v; },
          clamp, ease, easeIO, easeBack, prog, lerp, win, rise,
          text, fillR, strokeR, line, cursor, sketch, circle, rect, peep};
})();

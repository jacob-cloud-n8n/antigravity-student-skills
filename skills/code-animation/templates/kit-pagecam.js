// kit-pagecam.js — 高清 3D 網頁運鏡＋景深遮罩（逐格確定性 DOM 函式，不載入任何外部套件）。
// 改寫自 Vincentwei1021/video-shotcraft `assets/lib/PageCam.tsx`，Apache-2.0
// （原著 Copyright 2026 Wei Yihao；Licensed under the Apache License, Version 2.0：http://www.apache.org/licenses/LICENSE-2.0；
//  修改說明：移除 React／Remotion 相依，改寫為以秒數 t 驅動、全程採用原生 CSS zoom 保持中文字銳利度之逐格函式 pageCam）。
// 用法：場景 HTML 先 <script src="kit.js"></script><script src="kit-pagecam.js"></script>（亦可不載 kit.js 獨立使用），
//   於 window.render = t => { KIT.pageCam(el, t, keyframes, opts); } 逐格呼叫（同時掛載 window.pageCam）。
(() => {
  const clamp = x => Math.max(0, Math.min(1, x));
  const lerp = (a, b, p) => a + (b - a) * p;

  // 三次貝茲緩動（20 次二分法求解單調參數 u，精度 < 1e-6，取代原碼 Remotion Easing.bezier）
  function bezier(x1, y1, x2, y2) {
    const sample = (c1, c2, u) => (((1 - 3 * c2 + 3 * c1) * u + (3 * c2 - 6 * c1)) * u + 3 * c1) * u;
    return x => {
      x = clamp(x);
      if (x === 0 || x === 1) return x;
      let lo = 0, hi = 1, u = x;
      for (let i = 0; i < 20; i++) {
        u = (lo + hi) * 0.5;
        if (sample(x1, x2, u) < x) lo = u; else hi = u;
      }
      return sample(y1, y2, (lo + hi) * 0.5);
    };
  }
  const DEFAULT_EASE = bezier(0.33, 0, 0.15, 1);
  const DOF_MASK = 'linear-gradient(to bottom, rgba(0,0,0,1) 0%, rgba(0,0,0,1) 45%, rgba(0,0,0,0) 100%)';

  // 初次呼叫時原位建立 viewport > [stage > el, dofEl]，保留 el 內既有子節點，重複逐格呼叫不重建 DOM
  function ensureRig(el, vw, vh, pageH, src) {
    if (el.__pageCam) return el.__pageCam;
    const initH = pageH || parseFloat(el.style.height) || el.scrollHeight || vh;

    const viewport = document.createElement('div');
    viewport.dataset.pagecamViewport = '1';
    Object.assign(viewport.style, {
      position: 'absolute', left: '0px', top: '0px',
      width: `${vw}px`, height: `${vh}px`, overflow: 'hidden',
    });

    const stage = document.createElement('div');
    stage.dataset.pagecamStage = '1';
    Object.assign(stage.style, {position: 'absolute', inset: '0px'});

    const dofEl = document.createElement('div');
    dofEl.dataset.pagecamDof = '1';
    Object.assign(dofEl.style, {
      position: 'absolute', left: '0px', right: '0px', top: '0px',
      pointerEvents: 'none', display: 'none', maskImage: DOF_MASK,
    });
    dofEl.style.setProperty('-webkit-mask-image', DOF_MASK);

    let imgEl = null;
    if (src && el.tagName !== 'IMG') {
      imgEl = document.createElement('img');
      imgEl.src = src;
      Object.assign(imgEl.style, {
        position: 'absolute', left: '0px', top: '0px',
        width: `${vw}px`, height: `${initH}px`, display: 'block', pointerEvents: 'none',
      });
      el.insertBefore(imgEl, el.firstChild);
    } else if (src && el.tagName === 'IMG') {
      el.src = src;
    }

    if (el.parentNode) el.parentNode.insertBefore(viewport, el);
    stage.appendChild(el);
    viewport.appendChild(stage);
    viewport.appendChild(dofEl);

    Object.assign(el.style, {
      position: 'absolute', left: '0px', top: '0px', margin: '0px',
      width: `${vw}px`, height: `${initH}px`,
    });
    el.__pageCam = {viewport, stage, dofEl, imgEl, initH};
    return el.__pageCam;
  }

  /**
   * 2.5D／3D 網頁運鏡與景深遮罩（以秒數 t 逐格驅動）。
   * @param {HTMLElement} el 頁面元素（預設寬 1920px，可含真實 HTML 文字排版、截圖或頁面空間覆蓋層）
   * @param {number} t 當前時間（秒）
   * @param {Array<{t?:number, time?:number, frame?:number, cx:number, cy:number, zoom:number, rotX?:number, rotY?:number, rotZ?:number, persp?:number, ease?:Function}>} keyframes 關鍵格陣列
   * @param {Object} [opts] 選項：{pageH, src, blur=0, saturate=1, ease, dof:{focusY,strength}, vw=1920, vh=1080, bg, fps=30, t}
   */
  function pageCam(el, t, keyframes, opts = {}) {
    if (!el) throw new Error('pageCam：缺少目標元素 el');
    if (!keyframes || !keyframes.length) throw new Error('pageCam：keyframes 不可為空');

    const {
      pageH, src, blur = 0, saturate = 1, ease = DEFAULT_EASE, dof = null,
      vw = 1920, vh = 1080, fps = 30,
      bg = (window.KIT && window.KIT.C && window.KIT.C.bg) || '#faf7f2',
    } = opts;
    const curT = opts.t !== undefined ? opts.t : t;
    const kt = k => (k.t !== undefined ? k.t : k.time !== undefined ? k.time : (k.frame || 0) / fps);

    const rig = ensureRig(el, vw, vh, pageH, src);
    const curH = pageH || rig.initH;
    rig.viewport.style.width = `${vw}px`;
    rig.viewport.style.height = `${vh}px`;
    rig.viewport.style.backgroundColor = bg;
    el.style.width = `${vw}px`;
    el.style.height = `${curH}px`;
    if (rig.imgEl) {
      if (src && rig.imgEl.getAttribute('src') !== src) rig.imgEl.src = src;
      rig.imgEl.style.width = `${vw}px`;
      rig.imgEl.style.height = `${curH}px`;
    }

    // 區段搜尋與緩動插值（對應原碼 L46–55，支援零時長硬切與首尾夾限）
    let a = keyframes[0], b = keyframes[keyframes.length - 1];
    if (curT <= kt(a)) b = a;
    else if (curT >= kt(b)) a = b;
    else {
      for (let i = 0; i < keyframes.length - 1; i++) {
        if (curT >= kt(keyframes[i]) && curT < kt(keyframes[i + 1])) {
          a = keyframes[i]; b = keyframes[i + 1]; break;
        }
      }
    }
    const ta = kt(a), tb = kt(b);
    const segEase = a.ease || ease;
    const p = ta === tb ? 1 : segEase(clamp((curT - ta) / (tb - ta)));

    const halfW = vw * 0.5, halfH = vh * 0.5;
    const cx = lerp(a.cx !== undefined ? a.cx : halfW, b.cx !== undefined ? b.cx : halfW, p);
    const cy = lerp(a.cy !== undefined ? a.cy : halfH, b.cy !== undefined ? b.cy : halfH, p);
    const zoom = Math.max(1e-4, lerp(a.zoom !== undefined ? a.zoom : 1, b.zoom !== undefined ? b.zoom : 1, p));

    const filters = [];
    if (blur > 0) filters.push(`blur(${blur}px)`);
    if (saturate !== 1) filters.push(`saturate(${saturate})`);
    el.style.filter = filters.length ? filters.join(' ') : '';

    const has3D = keyframes.some(k => k.rotX !== undefined || k.rotY !== undefined || k.rotZ !== undefined || k.persp !== undefined);
    const rotX = has3D ? lerp(a.rotX ?? 0, b.rotX ?? 0, p) : 0;
    const rotY = has3D ? lerp(a.rotY ?? 0, b.rotY ?? 0, p) : 0;
    const rotZ = has3D ? lerp(a.rotZ ?? 0, b.rotZ ?? 0, p) : 0;
    const persp = has3D ? lerp(a.persp ?? 1400, b.persp ?? 1400, p) : 1400;

    // 座標換算（對應原碼 L107–114）：CSS zoom 會同步放大元素局部座標與 translate(px)，
    // 使頁面焦點 (cx, cy) 落於視窗中心 (halfW, halfH)：cx*zoom + Tx*zoom = halfW ⇒ Tx = halfW/zoom - cx。
    // 以版面級 CSS zoom 取代 transform: scale，使 Chromium 按放大後尺寸光柵化中文字形，透視下保持銳利。
    const tx = halfW / zoom - cx;
    const ty = halfH / zoom - cy;
    el.style.zoom = String(zoom);
    el.style.transformOrigin = `${cx}px ${cy}px`;

    if (has3D) {
      rig.stage.style.perspective = `${persp * zoom}px`;
      rig.stage.style.perspectiveOrigin = `${halfW}px ${halfH}px`;
      el.style.transformStyle = 'preserve-3d';
      el.style.transform = `translate(${tx}px, ${ty}px) rotateY(${rotY}deg) rotateX(${rotX}deg) rotateZ(${rotZ}deg)`;
    } else {
      rig.stage.style.perspective = 'none';
      rig.stage.style.perspectiveOrigin = `${halfW}px ${halfH}px`;
      el.style.transformStyle = 'flat';
      el.style.transform = `translate(${tx}px, ${ty}px)`;
    }

    // 螢幕空間景深遮罩（對應原碼 L133–148：頂端漸層遮罩＋backdrop-filter 柔化傾斜頁面遠端）
    if (dof) {
      const blurCss = `blur(${Math.max(0, dof.strength ?? 0)}px)`;
      rig.dofEl.style.display = 'block';
      rig.dofEl.style.height = `${Math.max(0, dof.focusY ?? 0)}px`;
      rig.dofEl.style.backdropFilter = blurCss;
      rig.dofEl.style.setProperty('-webkit-backdrop-filter', blurCss);
    } else {
      rig.dofEl.style.display = 'none';
    }

    return {cx, cy, zoom, rotX, rotY, rotZ, persp, has3D};
  }

  pageCam.bezier = bezier;
  window.pageCam = pageCam;
  if (window.KIT) {
    window.KIT.pageCam = pageCam;
    window.KIT.bezier = bezier;
  } else {
    window.KIT = {pageCam, bezier};
  }
})();

/* core.js — PCB IFA Designer (TRN553). Pure calculation & generation functions.
 * All geometry in millimetres; frequency in MHz at every API boundary (spec §7.1).
 * UMD-style export: `require("./core.js")` in Node, `window.IFA` in the browser.
 * Keep this file byte-identical to the first inlined <script> block in index.html.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.IFA = factory();
}(typeof self !== "undefined" ? self : this, function () {

  const C_MM_MHZ = 299792.458; // speed of light, mm·MHz (= 299792458 m/s)
  const X_FEED = 15;           // fixed feed-pad x on the board, mm (spec §7.3)

  const defaults = {
    fMHz: 915, sPct: 6,
    gpW: 60, gpH: 40, koH: 12,
    er: 4.4, subH: 1.6, tw: 0.5, clr: 0.3, k: 0.95,
    xFeed: X_FEED
  };

  function wavelengthMm(fMHz) { return C_MM_MHZ / fMHz; }

  function quarterWaveMm(fMHz, k) {
    if (k === undefined) k = 0.95;
    return (k * wavelengthMm(fMHz)) / 4;
  }

  /* Fold layout (spec §7.4). L is the arm path length short-stub junction →
   * open tip; the vertical stubs are added by the renderer/generator and are
   * NOT counted in L (k absorbs stub and fringing effects).
   * S_mm is clamped here so the short stays on the board: x_short >= m. */
  function layoutArm(opts) {
    const L = opts.L, boardW = opts.boardW, koH = opts.koH;
    const tw = opts.tw, clr = opts.clr;
    const m = clr + tw / 2;              // routing margin
    const yG = koH;                      // ground-plane top edge
    const p = Math.max(2 * tw, 1.0);     // fold pitch between rows
    const xMin = m, xMax = boardW - m;

    const sMax = X_FEED - m;
    const sMm = Math.min(opts.S_mm, sMax);
    const clamped = sMm < opts.S_mm;
    const xShort = X_FEED - sMm;

    const segments = [];
    let remaining = L, dir = 1;
    let x = xShort, y = yG - m;          // rowY(0)
    const root = { x: x, y: y };
    let tip = null, fits = true;

    for (;;) {
      const run = dir > 0 ? xMax - x : x - xMin;
      if (remaining <= run) {            // done, tip mid-run
        const nx = x + dir * remaining;
        segments.push({ x1: x, y1: y, x2: nx, y2: y });
        tip = { x: nx, y: y };
        break;
      }
      const wx = x + dir * run;          // run to the wall
      segments.push({ x1: x, y1: y, x2: wx, y2: y });
      x = wx; remaining -= run;
      if (remaining <= p) {              // tip lands on a turn
        segments.push({ x1: x, y1: y, x2: x, y2: y - remaining });
        tip = { x: x, y: y - remaining };
        break;
      }
      segments.push({ x1: x, y1: y, x2: x, y2: y - p });
      y -= p; remaining -= p; dir = -dir;
      if (y < m) {                       // next row leaves the keepout
        fits = false;
        tip = { x: x, y: y };
        break;
      }
    }

    let folds = 0;
    for (let i = 0; i < segments.length; i++) {
      if (segments[i].x1 === segments[i].x2) folds++;
    }
    return { segments: segments, folds: folds, fits: fits, root: root, tip: tip,
             sMm: sMm, clamped: clamped, xShort: xShort, m: m, p: p, yG: yG };
  }

  /* Point at path distance d from the root, walking the segment list.
   * pointAlongPath(segs, 0) = root; pointAlongPath(segs, L) = tip. */
  function pointAlongPath(segments, d) {
    let rem = d;
    for (let i = 0; i < segments.length; i++) {
      const s = segments[i];
      const len = Math.abs(s.x2 - s.x1) + Math.abs(s.y2 - s.y1); // rectilinear
      if (rem <= len) {
        const t = len === 0 ? 0 : rem / len;
        return { x: s.x1 + (s.x2 - s.x1) * t, y: s.y1 + (s.y2 - s.y1) * t };
      }
      rem -= len;
    }
    const last = segments[segments.length - 1];
    return last ? { x: last.x2, y: last.y2 } : { x: 0, y: 0 };
  }

  /* Every coordinate/length in generated files: exactly 3 decimals (spec §9). */
  function fmt(n) {
    if (typeof n !== "number" || !isFinite(n)) {
      throw new Error("non-finite value reached an output template");
    }
    return n.toFixed(3);
  }

  /* Modern KiCad 6+ `(footprint …)` s-expression (spec §9.1).
   * Board → footprint coords: origin at feed pad center, kx = x − x_feed,
   * ky = y − y_g (y stays down-positive). */
  function genFootprint(state, layout) {
    const f = Math.round(state.fMHz);
    const name = "IFA_" + f + "MHz";
    const L = quarterWaveMm(state.fMHz, state.k);
    const kx = function (x) { return x - X_FEED; };
    const ky = function (y) { return y - layout.yG; };

    const rowY0 = layout.root.y;
    const lines = [
      [layout.xShort, layout.yG, layout.xShort, rowY0],  // short stub
      [X_FEED, layout.yG, X_FEED, rowY0]                 // feed stub
    ];
    for (let i = 0; i < layout.segments.length; i++) {
      const s = layout.segments[i];
      lines.push([s.x1, s.y1, s.x2, s.y2]);
    }
    const fpLines = lines.map(function (l) {
      return '  (fp_line (start ' + fmt(kx(l[0])) + ' ' + fmt(ky(l[1])) +
             ') (end ' + fmt(kx(l[2])) + ' ' + fmt(ky(l[3])) + ')\n' +
             '    (stroke (width ' + fmt(state.tw) + ') (type solid)) (layer "F.Cu"))';
    }).join('\n');

    return '(footprint "' + name + '"\n' +
      '  (version 20240108)\n' +
      '  (generator "pcb_ifa_designer")\n' +
      '  (layer "F.Cu")\n' +
      '  (descr "PCB inverted-F antenna, ' + f + ' MHz, L=' + fmt(L) + 'mm, k=' +
        state.k + '. Generated by PCB IFA Designer (TRN553).")\n' +
      '  (tags "antenna IFA RF")\n' +
      '  (attr smd exclude_from_pos_files exclude_from_bom)\n' +
      '  (fp_text reference "AE**" (at 0.000 3.500) (layer "F.SilkS")\n' +
      '    (effects (font (size 1.000 1.000) (thickness 0.150))))\n' +
      '  (fp_text value "' + name + '" (at 0.000 5.500) (layer "F.Fab")\n' +
      '    (effects (font (size 1.000 1.000) (thickness 0.150))))\n' +
      '  (pad "1" smd rect (at 0.000 0.000) (size 1.200 1.200)\n' +
      '    (layers "F.Cu" "F.Paste" "F.Mask"))\n' +
      '  (pad "2" smd rect (at ' + fmt(-layout.sMm) + ' 0.000) (size 1.200 1.200)\n' +
      '    (layers "F.Cu" "F.Paste" "F.Mask"))\n' +
      fpLines + '\n' +
      '  (fp_rect (start ' + fmt(kx(0)) + ' ' + fmt(ky(0)) + ') (end ' +
        fmt(kx(state.gpW)) + ' ' + fmt(ky(layout.yG)) + ')\n' +
      '    (stroke (width 0.100) (type dash)) (fill none) (layer "Dwgs.User"))\n' +
      ')\n';
  }

  /* README.txt design-constraints file (spec §9.2). Every number from live state. */
  function genReadme(state, layout, isoDate) {
    const date = isoDate || new Date().toISOString().slice(0, 10);
    const f = Math.round(state.fMHz);
    const lam = wavelengthMm(state.fMHz);
    const L = quarterWaveMm(state.fMHz, state.k);

    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    for (let i = 0; i < layout.segments.length; i++) {
      const s = layout.segments[i];
      minX = Math.min(minX, s.x1, s.x2); maxX = Math.max(maxX, s.x1, s.x2);
      minY = Math.min(minY, s.y1, s.y2); maxY = Math.max(maxY, s.y1, s.y2);
    }
    const bbW = layout.segments.length ? maxX - minX : 0;
    const bbH = layout.segments.length ? maxY - minY : 0;

    return [
      'PCB IFA DESIGNER — DESIGN CONSTRAINTS',
      'Generated: ' + date + ' · TRN553 · tool v2',
      '',
      '[1] INPUTS',
      '    f = ' + f + ' MHz · S = ' + state.sPct.toFixed(1) + ' % (' +
        fmt(layout.sMm) + ' mm' + (layout.clamped ? ', clamped' : '') + ') · k = ' + state.k,
      '    ground plane ' + state.gpW + ' × ' + state.gpH + ' mm · keepout height ' +
        state.koH + ' mm',
      '    εr = ' + state.er + ' · substrate ' + state.subH + ' mm · trace ' +
        state.tw + ' mm · clearance ' + state.clr + ' mm',
      '',
      '[2] COMPUTED',
      '    λ = ' + fmt(lam) + ' mm · resonant length L (short→tip) = ' + fmt(L) + ' mm',
      '    folds = ' + layout.folds + ' · arm bounding box = ' + fmt(bbW) + ' × ' +
        fmt(bbH) + ' mm · fits keepout: ' + (layout.fits ? 'yes' : 'no'),
      '',
      '[3] LAYOUT CONSTRAINTS',
      '    - Keep the keepout strip free of copper, pours, and traces on ALL layers.',
      '    - Pad 2 (short) must connect to the ground pour; stitch with vias near the pad.',
      '    - Feed pad 1 via a 50-ohm microstrip from below the ground edge.',
      '    - Leave a matching-network placeholder at the feed: pi-network pads',
      '      (series + 2 shunt, 0402) between the radio and pad 1. Populate after',
      '      bench measurement.',
      '    - Ground plane size strongly affects tuning; re-check if gpW/gpH change.',
      '',
      '[4] MODEL LIMITS',
      '    - L is measured short→tip; stub drops and fringing are absorbed by k',
      '      (empirical, default 0.95). No EM solve; no impedance number is computed.',
      '    - εr and substrate height are recorded but do not enter the v1 length',
      '      formula.',
      ''
    ].join('\n');
  }

  return { defaults: defaults, wavelengthMm: wavelengthMm,
           quarterWaveMm: quarterWaveMm, layoutArm: layoutArm,
           pointAlongPath: pointAlongPath, genFootprint: genFootprint,
           genReadme: genReadme };
}));

/* tests.js — PCB IFA Designer verification (spec §10). Framework-free.
 * Run either way, same summary:
 *   node tests.js                      (requires ./core.js)
 *   paste into the devtools console of the open index.html (uses window.IFA)
 * Tolerances: ±0.05 mm formula checks, ± one trace width geometry checks.
 */
const IFA = (typeof window !== "undefined" && window.IFA)
  ? window.IFA
  : require("./core.js");

let pass = 0, fail = 0;
function check(name, cond) {
  if (cond) { pass++; }
  else { fail++; console.error("FAIL: " + name); }
}
function near(a, b, tol) { return Math.abs(a - b) <= tol; }

const D = IFA.defaults;
function runLayout(fMHz, over) {
  const st = Object.assign({}, D, over || {}, { fMHz: fMHz });
  const L = IFA.quarterWaveMm(st.fMHz, st.k);
  const S_mm = (st.sPct / 100) * L;
  const layout = IFA.layoutArm({ L: L, S_mm: S_mm, boardW: st.gpW,
    koH: st.koH, gpH: st.gpH, tw: st.tw, clr: st.clr });
  return { st: st, L: L, layout: layout };
}

/* ---- 1. Wavelength sanity (pure c/f, hand-checkable) ---- */
check("1a wavelengthMm(2400) = 124.914", near(IFA.wavelengthMm(2400), 124.914, 0.05));
check("1b wavelengthMm(915)  = 327.642", near(IFA.wavelengthMm(915), 327.642, 0.05));
check("1c wavelengthMm(433)  = 692.361", near(IFA.wavelengthMm(433), 692.361, 0.05));

/* ---- 2. Quarter-wave with k = 0.95 ----
 * (v1 listed 81.9 mm for 915 — that value omitted k. Do not regress.) */
check("2a quarterWaveMm(2400) = 29.667", near(IFA.quarterWaveMm(2400, 0.95), 29.667, 0.05));
check("2b quarterWaveMm(915)  = 77.815", near(IFA.quarterWaveMm(915, 0.95), 77.815, 0.05));
check("2c quarterWaveMm(433)  = 164.436", near(IFA.quarterWaveMm(433, 0.95), 164.436, 0.05));
check("2d default k is 0.95", near(IFA.quarterWaveMm(915), 77.815, 0.05));

/* ---- 3. Monotonicity: L strictly decreases over f = 300…3000 step 50 ---- */
{
  let mono = true, prev = Infinity;
  for (let f = 300; f <= 3000; f += 50) {
    const L = IFA.quarterWaveMm(f);
    if (!(L < prev)) mono = false;
    prev = L;
  }
  check("3a quarterWaveMm strictly decreasing 300..3000", mono);
}

/* ---- 4. Geometry matches math ---- */
[433, 915, 2400].forEach(function (f) {
  const r = runLayout(f);
  const sum = r.layout.segments.reduce(function (acc, s) {
    return acc + Math.abs(s.x2 - s.x1) + Math.abs(s.y2 - s.y1);
  }, 0);
  check("4a fits at " + f + " MHz (defaults)", r.layout.fits === true);
  check("4b sum(segments) = L at " + f + " MHz", near(sum, r.L, r.st.tw));
  const p0 = IFA.pointAlongPath(r.layout.segments, 0);
  const pL = IFA.pointAlongPath(r.layout.segments, r.L);
  check("4c pointAlongPath(0) = root at " + f, near(p0.x, r.layout.root.x, 0.01) && near(p0.y, r.layout.root.y, 0.01));
  check("4d pointAlongPath(L) = tip at " + f, near(pL.x, r.layout.tip.x, 0.01) && near(pL.y, r.layout.tip.y, 0.01));
});
{ // §7.4 worked example: 915 MHz, S = 6 % → 1 fold, tip ≈ (31.75, 10.45)
  const r = runLayout(915);
  check("4e worked example: root x = 10.331", near(r.layout.root.x, 10.331, 0.01));
  check("4f worked example: 1 fold", r.layout.folds === 1);
  check("4g worked example: tip ≈ (31.75, 10.45)",
    near(r.layout.tip.x, 31.754, 0.05) && near(r.layout.tip.y, 10.45, 0.01));
}

/* ---- 5. Bounds / clamping ---- */
[433, 915, 2400].forEach(function (f) {
  const r = runLayout(f);
  const m = r.layout.m, xMaxB = r.st.gpW - m, yMaxB = r.layout.yG - m;
  const eps = 1e-6;
  const inBounds = r.layout.segments.every(function (s) {
    return s.x1 >= m - eps && s.x2 >= m - eps && s.x1 <= xMaxB + eps && s.x2 <= xMaxB + eps &&
           s.y1 >= m - eps && s.y2 >= m - eps && s.y1 <= yMaxB + eps && s.y2 <= yMaxB + eps;
  });
  check("5a segments within [m, W−m] × [m, yG−m] at " + f, inBounds);
});
{ // short clamp holds at 300 MHz, S = 15 %
  const r = runLayout(300, { sPct: 15 });
  check("5b clamp engaged at 300 MHz / 15 %", r.layout.clamped === true);
  check("5c x_short >= m after clamp", r.layout.xShort >= r.layout.m - 1e-9);
}
/* §10.5 note: the spec's suggested does-not-fit recipe (koH = 6, f = 300,
 * other defaults) actually FITS under the §7.4 algorithm: with tw = 0.5 the
 * fold pitch is 1.0 mm, so a 6 mm keepout holds 5 rows ≈ 298 mm of usable
 * path — more than L(300 MHz) = 237.3 mm. Verified by hand. 5d documents the
 * real behavior; 5e exercises the does-not-fit path with tw = 2.0 (pitch
 * 4 mm → 1 row), reachable within the Advanced ranges. */
{
  const r = runLayout(300, { koH: 6 });
  check("5d koH=6 @ 300 MHz fits under §7.4 algorithm (see note)", r.layout.fits === true);
}
{
  let threw = false, r = null;
  try { r = runLayout(300, { koH: 6, tw: 2.0 }); } catch (e) { threw = true; }
  check("5e does-not-fit reported, nothing thrown (koH=6, tw=2 @ 300 MHz)",
    !threw && r.layout.fits === false);
}

/* ---- 6. .kicad_mod structural validity ---- */
{
  const r = runLayout(915);
  const foot = IFA.genFootprint(r.st, r.layout);
  let open = 0, close = 0;
  for (let i = 0; i < foot.length; i++) {
    if (foot[i] === "(") open++;
    if (foot[i] === ")") close++;
  }
  check("6a balanced parentheses", open === close && open > 0);
  check("6b starts with (footprint \"", foot.indexOf('(footprint "') === 0);
  check("6c contains (version and (generator",
    foot.indexOf("(version") >= 0 && foot.indexOf("(generator") >= 0);
  check("6d >= 2 pads", foot.split('(pad "').length - 1 >= 2);
  const fpLineBlocks = foot.match(/\(fp_line[\s\S]*?\(layer "F\.Cu"\)\)/g) || [];
  check("6e >= 3 fp_line entries on F.Cu", fpLineBlocks.length >= 3);
  check("6f no NaN/Infinity", foot.indexOf("NaN") < 0 && foot.indexOf("Infinity") < 0);
  const coordRe = /\((?:start|end|at|size)\s+([^()]+)\)/g;
  let mtok, tokensOk = true, found = 0;
  while ((mtok = coordRe.exec(foot)) !== null) {
    const toks = mtok[1].trim().split(/\s+/);
    for (let i = 0; i < toks.length; i++) {
      found++;
      if (!/^-?\d+\.\d{3}$/.test(toks[i])) tokensOk = false;
    }
  }
  check("6g every coordinate token is 3-decimal", tokensOk && found > 0);
  check("6h no legacy (module …)", foot.indexOf("(module") < 0);
}

/* ---- 7. README.txt content ---- */
{
  const r = runLayout(915);
  const txt = IFA.genReadme(r.st, r.layout, "2026-01-01");
  check("7a contains live frequency", txt.indexOf("915 MHz") >= 0);
  check("7b contains keepout height", txt.indexOf("keepout height 12 mm") >= 0);
  check("7c contains ground plane dims", txt.indexOf("60 × 40 mm") >= 0);
  check("7d contains matching-network note", /matching[- ]network/.test(txt));
  check("7e contains k value", txt.indexOf("k = 0.95") >= 0);
}

/* ---- summary ---- */
console.log("IFA tests: " + pass + " passed, " + fail + " failed" +
  (fail === 0 ? " — all green" : " — NOT OK"));
if (typeof process !== "undefined" && process && process.versions && process.versions.node) {
  process.exitCode = fail === 0 ? 0 : 1;
}

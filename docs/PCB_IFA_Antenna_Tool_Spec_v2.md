# PCB Inverted-F Antenna (IFA) Designer — Interface & Build Spec (v2)

**Course:** TRN553 — Build-a-Tool
**Reference tool studied:** TDR Simulator (Kurtis Conant, TRN553) — https://kurtisperrie.github.io/TDRSimulator.github.io/
**Visual language:** Astra Labs — https://astralab.space

---

## 0. Revision notes (v1 → v2)

Fixes and resolutions in this revision — read once, then build from the sections below:

1. **Numeric bug fixed.** v1's quarter-wave test value for 915 MHz (81.9 mm) forgot to
   apply k = 0.95. Correct value: **77.8 mm** (81.9 mm is λ/4 *without* k). The
   wireframe readout and §10 test tables are corrected. 2.4 GHz (29.7 mm) and
   433 MHz (164.4 mm) were already correct.
2. **Physics model made coherent.** v1 said "short-pin slider, 0–100% of arm length
   from feed end" without defining what the resonant length is measured between.
   Taken literally, sliding the short along a fixed arm *would* change resonance —
   contradicting the teaching point. v2 defines the textbook IFA geometry precisely
   (§7.2): the resonant length is always **short pin → open tip = k·λ/4**, the feed
   pad stays fixed on the board, and the slider sets the short–feed spacing. Moving
   the slider redraws the arm so short→tip stays at target. Slider range is now
   2–15 % (0 % is a degenerate short-on-feed; large values are no longer IFA-like).
3. **Open items from v1 §9 resolved** so the builder doesn't stall: KiCad output is
   the **modern `(footprint …)` s-expression format** (KiCad 6+). The k default
   stays 0.95, exposed in Advanced. The "one limitation" for the write-up remains
   the author's choice — both candidates are listed in §13.
4. **Every previously-unspecified value is now pinned**: frequency slider range and
   step, all Advanced defaults and ranges, design tokens (hex colors, font stacks,
   spacing), coordinate system, fold-layout algorithm, pad sizes, file-name
   patterns, number formatting, and test tolerances. An AI builder should never
   have to invent a constant.
5. **Deliverables and code-sharing pattern defined** (§1.1) so `tests.js` can run in
   both Node and the browser console without duplicating the math.
6. **README content corrected**: v1 asked for a "decoupling-cap note"; the RF-correct
   item at an antenna feed is a **matching-network placeholder note** (π-network pad
   positions). §9.2 and test 7 updated accordingly.

---

## 1. What this document is

Build plan for a single-page, browser-based tool that lets a user tune an
Inverted-F Antenna (IFA) for a chosen frequency, watch the trace geometry update
live, and generate a real KiCad footprint (`.kicad_mod`) plus a `README.txt` of
design constraints. No install, no backend, no build step.

**Hard requirements for the implementation:**

- Vanilla HTML/CSS/JS only. No frameworks, no bundler, no CDN requests, no
  webfonts. The page must work opened directly from disk (`file://`) with no
  network access.
- All state lives in JS memory. No `localStorage`, no cookies, no persistence.
- Everything the tool computes must be reproducible from the pure functions in
  `core.js` (§1.1) — the UI is a thin layer over those functions, and the tests
  exercise the same functions the UI calls.

### 1.1 Deliverables

| File | Contents | Notes |
|---|---|---|
| `index.html` | Full app: markup, CSS, and a `<script>` that inlines the exact contents of `core.js` followed by the UI-wiring code | Self-contained; opening this one file is the whole tool |
| `core.js` | All pure calculation/generation functions, UMD-style export (below) | Same bytes as the inlined block in `index.html` — keep them identical |
| `tests.js` | Standalone assertions (§10) | Runs via `node tests.js` (requires `./core.js`) **or** pasted into the devtools console of the open page (uses `window.IFA`) |

`core.js` export pattern (so both run modes work without duplication):

```js
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.IFA = factory();
}(typeof self !== "undefined" ? self : this, function () {
  // ... all pure functions ...
  return { defaults, wavelengthMm, quarterWaveMm, layoutArm,
           pointAlongPath, genFootprint, genReadme };
}));
```

`tests.js` header:

```js
const IFA = (typeof window !== "undefined" && window.IFA)
  ? window.IFA
  : require("./core.js");
```

The `.kicad_mod` and `README.txt` files are generated at runtime by the Generate
button (§9); they are outputs of the tool, not repo files.

---

## 2. Locked decisions

These are settled. Do not re-open them during the build.

- **Topology:** Inverted-F antenna (IFA) — not meander-only, patch, or monopole.
- **Frequency:** free-form slider **300–3000 MHz, step 1 MHz, default 915 MHz**,
  with a paired editable numeric field (type an exact value, e.g. 868). Range
  rationale: below 300 MHz the arm can't reasonably fold into a 60 mm board;
  above 3 GHz trace-width effects dominate and the simple model stops being honest.
- **Tuning input:** shorting-pin position only (short–feed spacing, §7.2). No
  matching stub, no second knob.
- **Ground plane / substrate / trace width:** sensible defaults in a collapsed
  "ADVANCED" section (§6.4) — not front-and-center.
- **Readout:** resonant frequency + electrical length only — **no impedance/SWR
  number.** Impedance stays qualitative ("moving the short changes match without
  changing resonance"). A trustworthy number needs a real EM solver; printing a
  fake one fails the academic-integrity requirement.
- **Output:** modern-format `.kicad_mod` footprint + `README.txt` constraints file.
- **Verification:** automated plain-JS assertion file, framework-free, runnable in
  Node or the browser console (§10).

---

## 3. What we're borrowing from the TDR Simulator

The TDR Simulator gets a few structural things right that this tool copies:

| Pattern | What it does there | How we reuse it |
|---|---|---|
| Numbered "How to use" strip | 4 short numbered steps above the fold | Same: "1. Set frequency 2. Drag the short pin 3. Watch the arm redraw 4. Open Advanced if needed 5. Hit Generate" |
| Parameter panel with inline formula | Each control shows its symbol and the formula that consumes it, not a bare slider | Frequency slider shows `λ = c / f` with the live λ value; short slider shows the qualitative impedance note |
| Live readout panel | A dedicated box that updates in real time, separate from the controls | RESONANT LENGTH + ELECTRICAL LENGTH + STATE line, updates on every input event |
| Termination / state description | One-line plain-English description of current state | One-line IFA state, e.g. `915 MHz · 1 fold · fits keepout` (§6.6) |
| References + AI-use disclosure panel | Explicit citation of course material and explicit disclosure of what the AI generated vs. what was verified | Same structure, adapted (§6.9) |

**Not copying:** the TDR tool is a time-domain waveform simulator with
playback/pause. This tool is spatial and static-per-frame — that screen region is
replaced by the trace-preview SVG. No animation controls anywhere.

---

## 4. Visual language — Astra Labs

Register: dark, technical, "engineering bench." Big terse headlines,
monospace-flavored stat callouts, minimal chrome, generous whitespace, no
decorative gradients. Match the *design system*, not the brand — do not copy the
Astra Labs logo, wordmark, or copy text.

### 4.1 Design tokens (use exactly these)

```css
:root {
  --bg:          #0b0d10;   /* page background — near-black, slight blue */
  --panel:       #101418;   /* panel fill */
  --border:      #1e242b;   /* 1px panel borders */
  --text:        #e8eaed;   /* primary text — off-white, never #fff */
  --text-dim:    #8b949e;   /* secondary text, labels' helper lines */
  --accent:      #5aa2ff;   /* cool "flight hardware" blue — sparingly */
  --accent-dim:  rgba(90,162,255,.15);
  --warn:        #ffb454;   /* clamped-value notices */
  --error:       #ff6b6b;   /* does-not-fit state */
  --copper:      #c8873a;   /* antenna trace in the preview */
  --font-body:   system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  --font-mono:   ui-monospace, "SF Mono", "Cascadia Code", Menlo, Consolas, monospace;
}
```

Token usage rules:

- `--accent` appears **only** on: the Generate button, the active slider thumb,
  and the RESONANT LENGTH value. Nothing else. Don't accent everything.
- Every number, unit, filename, and formula renders in `--font-mono`. Prose and
  labels render in `--font-body`. This mirrors how astralab.space treats stats
  like "2.8 km target apogee" as typographic objects distinct from prose.
- Flat panels separated by `1px solid var(--border)`. No card shadows, no border
  radius above 4 px, no gradients.
- Labels read like a datasheet, ALL-CAPS, letter-spaced: `SHORT POSITION`,
  `RESONANT LENGTH` — never "Where should the short go?". No exclamation marks
  anywhere in the UI copy.

### 4.2 Layout metrics

- Max content width **1100 px**, centered. Two-column grid at ≥ 900 px:
  controls column **380 px** fixed, preview column fluid (`1fr`), `16 px` gap.
- Below 900 px: single column; preview moves directly below controls; Advanced
  stays collapsed by default.
- Spacing on an 8 px scale (8/16/24/32). Panel padding 16 px.
- Footer strip: small, single line — tool name · course code · link that scrolls
  to the References panel.

---

## 5. Page structure (wireframe, desktop)

```
┌──────────────────────────────────────────────────────────────────┐
│  PCB IFA DESIGNER                                       TRN553   │
├──────────────────────────────────────────────────────────────────┤
│  HOW TO USE                                                      │
│  1. Set frequency  2. Drag the short pin  3. Watch it redraw     │
│  4. Open Advanced to change board params  5. Hit Generate        │
├───────────────────────────────┬──────────────────────────────────┤
│  CONTROLS                     │  TRACE PREVIEW (SVG)             │
│                               │                                  │
│  FREQUENCY        [ 915 ] MHz │   [ to-scale top-down PCB view ] │
│  ────────●─────── λ = c/f     │   keepout strip, folded arm,     │
│           λ = 327.6 mm        │   feed pad, short pin,           │
│                               │   ground plane, scale bar        │
│  SHORT POSITION   6.0 %       │                                  │
│  ───●──────────── (= 4.7 mm)  ├──────────────────────────────────┤
│  moves match, not resonance   │  READOUT                         │
│                               │  RESONANT LENGTH      77.8 mm    │
│  ▸ ADVANCED (collapsed)       │  ELECTRICAL LENGTH    0.95·λ/4   │
│    ground plane W × H         │  STATE  915 MHz · 1 fold ·       │
│    keepout height             │         fits keepout             │
│    substrate εr / height      │                                  │
│    trace width / clearance    │  [ GENERATE ]                    │
│    correction factor k        │                                  │
├───────────────────────────────┴──────────────────────────────────┤
│  EQUATIONS                                                       │
│  λ = c / f          L = k · λ / 4   (k = 0.95, empirical)        │
│  Folded arm path length = L, regardless of fold count            │
├──────────────────────────────────────────────────────────────────┤
│  REFERENCES               AI TOOLS USED IN DEVELOPMENT           │
│  [1] Course lecture       [2] Claude — generated HTML/CSS/JS;    │
│      material…                equations verified against [1]     │
│                               and hand calc (see tests.js)       │
├──────────────────────────────────────────────────────────────────┤
│  PCB IFA DESIGNER · TRN553 · Seneca Polytechnic                  │
└──────────────────────────────────────────────────────────────────┘
```

Mobile (< 900 px): single column in this order — header, how-to, controls,
preview, readout, equations, references, footer.

---

## 6. Components

### 6.1 HowToUse
Static numbered strip, 5 steps, exactly the copy shown in §5. One line on
desktop, wraps naturally on mobile. `--text-dim` color, small caps heading.

### 6.2 FrequencySlider
- `<input type="range" min="300" max="3000" step="1">` + a paired
  `<input type="number">` showing the same value; editing either updates the
  other. Number field clamps to [300, 3000] on blur.
- Beside it, in mono: `λ = c/f` and the live value `λ = 327.6 mm` (1 decimal).
- Fires the full recompute→redraw pipeline on every `input` event (no debounce
  needed — the math is trivial).

### 6.3 ShortPinSlider
- `<input type="range" min="2" max="15" step="0.5">`, unit **percent of the
  resonant length L**, default **6 %**. Secondary mono readout of the absolute
  spacing in mm: `(= 4.7 mm)`.
- Helper line under the label, `--text-dim`:
  `moves match, not resonance` — the one-line qualitative impedance statement.
  Optionally on hover/focus a longer title attribute: "Wider spacing raises the
  feed-point impedance. Resonant length is unchanged — that is the point of an
  IFA." No numbers.
- Clamping: the physical spacing `S_mm = (S% / 100) · L` is additionally clamped
  so the short stays on the board: `S_mm ≤ x_feed − m` (§7.3). If the clamp
  engages (only possible at low frequencies), show `(clamped)` after the mm
  value in `--warn` color.

### 6.4 AdvancedPanel
A native `<details>` element, collapsed by default, summary text `▸ ADVANCED`.
Contents — each a labeled number input with unit suffix:

| Parameter | Symbol | Default | Range | Step | Notes |
|---|---|---|---|---|---|
| Ground plane width | `gpW` | 60 mm | 20–120 | 1 | Board width (x) |
| Ground plane height | `gpH` | 40 mm | 15–100 | 1 | Ground copper region (y) |
| Keepout strip height | `koH` | 12 mm | 6–25 | 1 | Copper-free strip above ground where the antenna lives |
| Substrate εr | `er` | 4.4 | 1–12 | 0.1 | FR-4 default. **Informational in v1** — recorded in outputs, not used in the length formula (k absorbs board effects; state this in the README and the write-up) |
| Substrate height | `subH` | 1.6 mm | 0.4–3.2 | 0.1 | Informational, same as εr |
| Trace width | `tw` | 0.5 mm | 0.2–2.0 | 0.1 | Arm and stub width |
| Edge/copper clearance | `clr` | 0.3 mm | 0.15–1.0 | 0.05 | Used in margin m (§7.3) |
| Correction factor | `k` | 0.95 | 0.85–1.00 | 0.01 | Empirical end-effect factor — exposed here so it's not a hidden fudge |

Any change fires the same recompute→redraw pipeline.

### 6.5 TracePreview
Inline SVG, `viewBox="0 0 {boardW} {boardH}"` — **1 SVG user unit = 1 mm**, so
all geometry is drawn in real millimetres and stroke widths equal real trace
widths. Redraw = rebuild the SVG contents from the layout result (§7.4) on every
change. Layers, bottom to top:

1. Board outline: `--panel` fill, `--border` 0.2 mm stroke.
2. Ground plane rectangle (y from `koH` to `koH+gpH`): fill `#20262d`.
3. Keepout strip (y from 0 to `koH`): fill transparent, 0.2 mm dashed
   `--text-dim` outline, tiny `KEEPOUT` label in 2 mm mono text.
4. Arm path: single `<path>` from the segment list, stroke `--copper`,
   `stroke-width = tw`, `stroke-linejoin="round"`, no fill.
5. Feed stub + short stub (vertical lines, same stroke as arm).
6. Feed pad: `1.2 × 1.2 mm` rect centered at `(x_feed, koH)`, fill `--accent`.
   Short pad: same size at `(x_short, koH)`, fill `--copper`.
7. Scale bar: 10 mm line + `10 mm` mono label, bottom-right inside the board.
8. If `fits === false`: 0.4 mm `--error` outline around the keepout strip.

The SVG is sized by CSS to fill its column, `max-height 420px`, centered.

### 6.6 ReadoutPanel
Three mono rows, ALL-CAPS dim labels, values right-aligned:

- `RESONANT LENGTH` — `L` in mm, 1 decimal, in `--accent`.
- `ELECTRICAL LENGTH` — the literal string `0.95·λ/4` (substituting the live k
  value, e.g. `0.92·λ/4` if k changed). This is a sanity display that the
  geometry target matches the formula, not a computed check.
- `STATE` — one line assembled as `{f} MHz · {folds} fold(s) · fits keepout`,
  or on failure `{f} MHz · arm exceeds keepout — raise f or enlarge keepout`
  in `--error`. If the short clamp (§6.3) engaged, append ` · short clamped`
  in `--warn`.

### 6.7 EquationsPanel
Static, always visible, mono: exactly the two lines in §5's EQUATIONS box.
These are the formulas actually driving the tool — never hide them in a tooltip.

### 6.8 GenerateButton
Full-width in the readout panel, `--accent` background, dark text, label
`GENERATE`. On click: build both files from current state (§9), trigger two
downloads via `Blob` + temporary `<a download>` click. Disabled (dimmed, not
hidden) while `fits === false`, with title "Arm does not fit — fix before
generating."

### 6.9 ReferencesPanel
Collapsible `<details>`, open by default. Two sub-blocks:

- **REFERENCES** — `[1]` course lecture material citation (leave the exact
  citation text as a clearly-marked `TODO(author)` for the student to fill in);
  `[2]` the TDR Simulator link from the header.
- **AI TOOLS USED IN DEVELOPMENT** — disclosure template: which model generated
  the HTML/CSS/JS, the statement that all equations and test values were
  verified against [1] and hand calculation, and a pointer to `tests.js` as the
  verification artifact. Terse, factual, no marketing tone.

---

## 7. Physics & calculation model

### 7.1 Units and constants

**All geometry in millimetres. Frequency in MHz at every API boundary.** This
kills unit bugs. One constant:

```js
const C_MM_MHZ = 299792.458; // speed of light, mm·MHz (= 299792458 m/s)

function wavelengthMm(fMHz)            { return C_MM_MHZ / fMHz; }
function quarterWaveMm(fMHz, k = 0.95) { return (k * wavelengthMm(fMHz)) / 4; }
```

k is an empirical correction for end effects / fringing on a PCB trace arm
(mostly in air above the board, not embedded in dielectric like a patch).
Published IFA designs land k ≈ 0.90–0.97; default 0.95, exposed in Advanced.

Worked example at defaults (use these to sanity-check while building):
`f = 915 MHz → λ = 327.642 mm → L = 0.95 · λ/4 = 77.815 mm → display 77.8 mm`.

### 7.2 IFA geometry — the model, stated precisely

Textbook IFA on the top strip of a PCB:

- The **ground plane** fills the lower region of the board. The **keepout
  strip** above it contains no copper except the antenna.
- The **arm** is a horizontal trace running inside the keepout strip, folded
  180° whenever it hits the strip's side margin (§7.4).
- The **short stub** is a short vertical trace connecting the arm's root (its
  starting end) down to the ground-plane top edge.
- The **feed stub** is a second vertical trace from the arm down to the feed
  pad on the ground-plane edge, at spacing **S** to the right of the short.

**Definitions that make the teaching point literally true in the model:**

- Resonant length **L = quarterWaveMm(f, k)** is the path length along the arm
  **from the short-stub junction to the open tip**. Always. The stubs' own
  vertical drops are *not* counted in L — k absorbs stub and fringing effects
  (state this convention in the README).
- The **feed pad position `x_feed` is fixed** on the board (constant, §7.3).
  The slider sets S (short–feed spacing). Changing S moves the short's junction
  (`x_short = x_feed − S`) and the whole arm re-lays-out from that root so that
  short→tip is again exactly L. **Resonance therefore never moves when the
  slider moves** — which is the pedagogical point — while the match changes
  qualitatively (wider S → higher feed impedance; stated in words only, §6.3).

### 7.3 Coordinate system and derived layout constants

Origin at the **board's top-left corner, +x right, +y down** (matches both SVG
and KiCad screen conventions — no axis flip anywhere).

```
boardW   = gpW                       // 60 mm default
boardH   = koH + gpH                 // 12 + 40 = 52 mm default
y_g      = koH                       // ground-plane top edge, 12 mm
m        = clr + tw/2                // routing margin, 0.55 mm default
x_feed   = 15                        // fixed feed-pad x, mm (constant; not a UI control)
x_short  = x_feed − S_mm             // S_mm clamped so x_short ≥ m
rowY(i)  = y_g − m − i·p             // arm row i center, i = 0,1,2,…
p        = max(2·tw, 1.0)            // fold pitch between rows, mm
xMin, xMax = m, boardW − m           // usable run extents
```

### 7.4 Fold-layout algorithm (`layoutArm`)

Input: `{ L, S_mm, boardW, koH, gpH, tw, clr }`. Output:
`{ segments: [{x1,y1,x2,y2},…], folds, fits, root: {x,y}, tip: {x,y} }`.
Segments are the arm only (stubs are added by the renderer/generator, not
counted in L).

```
1. remaining = L; i = 0; dir = +1; cursor = (x_short, rowY(0))
2. loop:
   a. run = (dir > 0) ? (xMax − cursor.x) : (cursor.x − xMin)
   b. if remaining ≤ run:
        emit horizontal segment of length `remaining` in direction dir
        tip = segment end; break                      // done, tip mid-run
   c. emit horizontal segment of length `run` to the wall
      remaining −= run
   d. if remaining ≤ p:                                // tip lands on a turn
        emit vertical segment of length `remaining` upward; tip = end; break
   e. emit vertical segment of length p upward (to rowY(i+1))
      remaining −= p; i += 1; dir = −dir
   f. if rowY(i) < m:  fits = false; stop emitting; break   // out of keepout
3. folds = number of vertical segments emitted
4. fits  = (step f never fired)
```

Properties the tests rely on (§10.4–5): with rectilinear 90° segments, total
path length is exactly the sum of segment lengths, so
`Σ|seg| = L` within one trace-width of tolerance whenever `fits === true`;
and no segment coordinate ever falls outside `[m, boardW−m] × [m, y_g−m]`.

`pointAlongPath(segments, d)` walks the segment list and returns the (x, y)
point at path distance d from the root — used to place nothing in v1 but
included and tested because the KiCad generator and any future marker reuse it.
Endpoints: `pointAlongPath(segs, 0) = root`, `pointAlongPath(segs, L) = tip`.

Stubs (renderer + generator, not in `segments`):
- short stub: vertical line `(x_short, y_g) → (x_short, rowY(0))`
- feed stub:  vertical line `(x_feed,  y_g) → (x_feed,  rowY(0))`

Worked example at all defaults (915 MHz, S = 6 % → S_mm = 4.67):
`x_short = 10.33`, row 0 usable run to `xMax = 59.45` is 49.12 mm;
remaining after row 0 = 77.815 − 49.12 = 28.69; one 1.0 mm turn up; row 1
runs 27.69 mm leftward → tip ≈ (31.76, 10.45). **1 fold, fits.** The preview,
readout, and tests should all agree with these numbers.

---

## 8. Recompute pipeline

Single function, called on every `input` event from any control:

```
readInputs() → clampInputs() → L = quarterWaveMm(f, k)
            → layout = layoutArm(...) → renderPreview(layout)
            → renderReadout(L, layout) → setGenerateEnabled(layout.fits)
```

No caching, no dirty flags — the whole recompute is microseconds. Keep it one
synchronous path so behavior is trivially testable and debuggable.

---

## 9. Generated output files

Filenames (freq rounded to integer MHz): `IFA_915MHz.kicad_mod`,
`IFA_915MHz_README.txt`. Download both from one Generate click via
`new Blob([text], {type:"text/plain"})` and a temporary anchor with the
`download` attribute.

**Number formatting rule for both files:** every coordinate/length printed with
exactly **3 decimals** (`toFixed(3)`), dot decimal separator. Never allow `NaN`
or `Infinity` to reach a template — clamp inputs first (§8); test 6 enforces it.

### 9.1 `.kicad_mod` — modern s-expression format (KiCad 6+)

Coordinate transform from board coords (§7.3): **origin at feed pad center**,
`kx = x − x_feed`, `ky = y − y_g` (y stays down-positive — KiCad footprints use
screen-style y-down, same as our board frame).

Template (values shown for the 915 MHz worked example; generate all
`fp_line` entries from the segment list + the two stubs):

```
(footprint "IFA_915MHz"
  (version 20240108)
  (generator "pcb_ifa_designer")
  (layer "F.Cu")
  (descr "PCB inverted-F antenna, 915 MHz, L=77.815mm, k=0.95. Generated by PCB IFA Designer (TRN553).")
  (tags "antenna IFA RF")
  (attr smd exclude_from_pos_files exclude_from_bom)
  (fp_text reference "AE**" (at 0 3.5) (layer "F.SilkS")
    (effects (font (size 1 1) (thickness 0.15))))
  (fp_text value "IFA_915MHz" (at 0 5.5) (layer "F.Fab")
    (effects (font (size 1 1) (thickness 0.15))))
  (pad "1" smd rect (at 0.000 0.000) (size 1.200 1.200)
    (layers "F.Cu" "F.Paste" "F.Mask"))
  (pad "2" smd rect (at -4.669 0.000) (size 1.200 1.200)
    (layers "F.Cu" "F.Paste" "F.Mask"))
  (fp_line (start -4.669 0.000) (end -4.669 -0.550)
    (stroke (width 0.500) (type solid)) (layer "F.Cu"))
  ; …one fp_line per arm segment and per stub…
  (fp_rect (start -15.000 -12.000) (end 45.000 0.000)
    (stroke (width 0.100) (type dash)) (fill none) (layer "Dwgs.User"))
)
```

Requirements:

- Pad `1` = feed, pad `2` = short (netted to GND at board level — README says so).
- Arm + stubs as `fp_line` on `F.Cu`, `stroke width = tw`.
- Keepout rectangle drawn on `Dwgs.User` as a dashed `fp_rect` (documentation
  layer — actual copper keepout is a board-level rule; README explains).
- Consistency: modern `(footprint …)` only. Never emit legacy `(module …)`.

### 9.2 `README.txt` — exact section list

```
PCB IFA DESIGNER — DESIGN CONSTRAINTS
Generated: <ISO date> · TRN553 · tool v2

[1] INPUTS
    f = 915 MHz · S = 6.0 % (4.669 mm) · k = 0.95
    ground plane 60 × 40 mm · keepout height 12 mm
    εr = 4.4 · substrate 1.6 mm · trace 0.5 mm · clearance 0.3 mm

[2] COMPUTED
    λ = 327.642 mm · resonant length L (short→tip) = 77.815 mm
    folds = 1 · arm bounding box = <w> × <h> mm · fits keepout: yes

[3] LAYOUT CONSTRAINTS
    - Keep the keepout strip free of copper, pours, and traces on ALL layers.
    - Pad 2 (short) must connect to the ground pour; stitch with vias near the pad.
    - Feed pad 1 via a 50-ohm microstrip from below the ground edge.
    - Leave a matching-network placeholder at the feed: pi-network pads
      (series + 2 shunt, 0402) between the radio and pad 1. Populate after
      bench measurement.
    - Ground plane size strongly affects tuning; re-check if gpW/gpH change.

[4] MODEL LIMITS
    - L is measured short→tip; stub drops and fringing are absorbed by k
      (empirical, default 0.95). No EM solve; no impedance number is computed.
    - εr and substrate height are recorded but do not enter the v1 length
      formula.
```

Every number in the README comes from live state at click time — test 7 makes a
stale template impossible to ship.

---

## 10. Verification plan (automated)

`tests.js`: plain `console.assert`-style checks with a pass/fail counter and a
final one-line summary. No framework. Dual-run pattern per §1.1. Tolerances:
**±0.05 mm** for formula checks, **± one trace width** for geometry checks.

1. **Wavelength sanity** (pure c/f, hand-checkable):
   `wavelengthMm(2400) ≈ 124.914`, `wavelengthMm(915) ≈ 327.642`,
   `wavelengthMm(433) ≈ 692.361` (all mm, ±0.05).
2. **Quarter-wave with k = 0.95:**
   `2400 → 29.667` · `915 → 77.815` · `433 → 164.436` (mm, ±0.05).
   *(v1 listed 81.9 mm for 915 — that value omitted k. Do not regress.)*
3. **Monotonicity:** sweep f = 300…3000 step 50; assert `quarterWaveMm`
   strictly decreases (catches sign errors / inverted formulas).
4. **Geometry matches math:** for f ∈ {433, 915, 2400} at defaults, run
   `layoutArm`; assert `fits === true` and `|Σ segment lengths − L| ≤ tw`.
   This validates the folding algorithm, not just the formula. Also assert
   `pointAlongPath(segs, 0)` = root and `pointAlongPath(segs, L)` = tip (±0.01).
5. **Bounds / clamping:** every segment coordinate within
   `[m, boardW−m] × [m, y_g−m]`; S_mm clamp holds (`x_short ≥ m`) at
   f = 300 MHz with S = 15 %; with `koH = 6` and f = 300 the layout reports
   `fits === false` (warning path exercised, nothing thrown).
6. **`.kicad_mod` structural validity** (no KiCad round-trip available, so
   assert structure): balanced parentheses; string starts with
   `(footprint "`; contains `(version` and `(generator`; ≥ 2 `(pad ` entries;
   ≥ 3 `(fp_line` entries with `(layer "F.Cu")`; contains no `NaN`/`Infinity`
   substring; every numeric token matches `-?\d+\.\d{3}` where coordinates
   appear.
7. **`README.txt` content:** generated text contains the live frequency string
   (`915 MHz`), the keepout dimensions, the phrase `matching-network` (or
   `matching network`), and the k value — so a stale template can't silently
   ship wrong numbers.

**Demo/Q&A run:** open the tool, open devtools console, paste `tests.js`, show
the summary passing live. This doubles as proof every number the tool produces
can be explained — the academic-integrity requirement in the brief.

---

## 11. Build order

1. Static layout + §4 tokens/theming, no logic — the visual language is graded
   on communication, get it right first.
2. `core.js`: `wavelengthMm`, `quarterWaveMm`, `layoutArm`, `pointAlongPath` as
   pure functions. Write `tests.js` sections 1–5 against these **before any UI
   wiring**, and make them pass.
3. Wire sliders → recompute pipeline (§8) → readout panel. No preview yet.
4. TracePreview SVG, driven by the same `layoutArm` output the tests already
   check. Verify the §7.4 worked example visually (1 fold, tip ≈ x = 31.8).
5. Advanced panel feeding the pipeline; confirm clamp + does-not-fit states.
6. `genFootprint` string templating from tested geometry; tests section 6.
7. `genReadme`; tests section 7. Wire GenerateButton downloads.
8. References / AI-disclosure panel + how-to strip final copy.
9. Final pass: full `tests.js` green in both Node and console; sweep the
   frequency slider 300→3000 watching for NaN, layout escapes, or readout
   glitches near clamp boundaries; check mobile stacking at 375 px width.

---

## 12. Non-goals (do not build)

- No impedance, SWR, S11, or Smith-chart output of any kind (locked, §2).
- No EM simulation; no εr-driven length correction in v1.
- No topology switcher (meander/patch/monopole), no matching-stub knob.
- No KiCad round-trip validation, no file parsing, no uploads.
- No persistence, backend, analytics, or external network requests.
- No animation/playback controls (that's the TDR tool's domain, §3).

---

## 13. Resolved decisions & remaining author choice

Resolved in v2 (previously "open items"):

- **KiCad format:** modern `(footprint …)` s-expression, KiCad 6+. Chosen
  because it's current; the structural tests (§10.6) target it exclusively.
- **k default:** stays 0.95. After the tool exists, spot-check the drawn
  geometry against one published reference IFA (e.g. a TI DN023 / Nordic
  reference-design antenna) and note the comparison in the write-up — but do
  not block the build on it.

Remaining author choice (pick one for the write-up's "one limitation" — both
are honest; pick whichever you'd rather defend in the Q&A):

- Ground-plane-size sensitivity (the model ignores it; real IFAs detune when
  the ground plane shrinks), **or**
- No computed impedance number (match quality is qualitative by design).

---

## 14. Acceptance checklist

The build is done when every box below is true:

- [ ] `index.html` opens from `file://` with zero network requests and renders
      the §5 layout on desktop and stacked on 375 px mobile.
- [ ] Default load shows: 915 MHz, S = 6 %, `RESONANT LENGTH 77.8 mm`,
      `ELECTRICAL LENGTH 0.95·λ/4`, STATE `915 MHz · 1 fold · fits keepout`,
      preview matching the §7.4 worked example.
- [ ] Dragging either slider updates preview + readout on every input event
      with no flicker; Advanced changes do the same.
- [ ] Short slider never changes RESONANT LENGTH (resonance decoupling visibly
      true); clamp shows `(clamped)` in warn color at low f.
- [ ] Does-not-fit state: red keepout outline, error STATE line, Generate
      disabled — reachable via koH = 6 mm at 300 MHz.
- [ ] Generate downloads `IFA_<f>MHz.kicad_mod` + `IFA_<f>MHz_README.txt`,
      contents per §9, all numbers 3-decimal, no NaN.
- [ ] `node tests.js` passes; pasting `tests.js` in the open page's console
      passes; both print the same summary.
- [ ] Accent color appears only on Generate, active slider thumb, and the
      resonant-length value. All numbers/units/filenames are monospace.
- [ ] No frameworks, no CDN, no webfonts, no localStorage anywhere in source.
- [ ] References panel present with `TODO(author)` citation slot and the
      AI-use disclosure text.

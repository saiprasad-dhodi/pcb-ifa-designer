# PCB Inverted-F Antenna Designer

An interactive design tool for printed inverted-F antennas (IFAs) — the flat, etched antennas found on Wi-Fi modules, BLE trackers, and IoT sensor boards.

Enter a frequency and your board dimensions. The tool computes the resonant length, folds it to fit your keepout strip, draws it to scale, and exports a working KiCad footprint plus a fabrication constraints sheet.

**[▶ Open the tool](https://saiprasad-dhodi.github.io/pcb-ifa-designer/)**

Built for TRN553 Build-a-Tool at Seneca Polytechnic.

---

## What it does

- **Computes resonant length** from `L = k · λ/4`, with the correction factor `k` exposed and editable
- **Folds the arm** to fit a copper-free keepout strip, reporting fold count and warning when it will not fit
- **Draws a current-distribution overlay** — the trace is coloured by `I(d) = cos(π/2 · d/L)`, so you can see where the antenna actually radiates
- **Plots the standing wave** with the feed tap marked, and a length-vs-frequency chart with a shaded "won't fit" region
- **Exports a KiCad 6+ footprint** (`.kicad_mod`) and a plain-text constraints sheet
- **Shows its working** — a live derivation panel that re-checks the geometry invariant on every change

Everything runs client-side in a single file. No build step, no dependencies, no network requests. Open `index.html` from disk and it works offline.

## The idea it exists to teach

An inverted-F has **two independent controls**:

| Distance | Measured from → to | Controls |
|---|---|---|
| **L** | shorting pin → open tip | Resonant frequency |
| **S** | shorting pin → feed point | Input impedance |

Drag the short-pin slider and the resonance readout does not move, while the tap marker slides along the standing-wave curve. That independence is the whole point of the inverted-F geometry, and it is much easier to see than to read about.

## Repository layout

```
index.html    the complete tool (core.js inlined byte-identically)
core.js       all mathematics, as pure functions — no DOM, no side effects
tests.js      43 assertions against core.js
docs/         study guide, one-page write-up, original spec
tools/        the scripts that generate the PDFs
```

### Why `core.js` is inlined rather than linked

`index.html` must work when opened directly from disk — no web server, no CORS issues. So `core.js` is embedded rather than loaded with `<script src>`.

To stop the two copies drifting apart, the inlined block is kept **byte-for-byte identical** to the standalone file. That is checkable mechanically:

```bash
node -e "
const fs=require('fs');
const core=fs.readFileSync('core.js','utf8');
const html=fs.readFileSync('index.html','utf8');
const s=html.indexOf('(function (root, factory)');
const e=html.indexOf('}));', s)+4;
console.log(html.slice(s,e).trimEnd()===core.slice(core.indexOf('(function (root, factory)')).trimEnd());
"
```

If that prints `false`, the test suite is no longer testing the code the page runs.

## Running the tests

```bash
node tests.js
```

Expected: `IFA tests: 43 passed, 0 failed — all green`

`core.js` uses a UMD wrapper, so the same file also runs in a browser console with `index.html` open — which tests the inlined copy rather than the standalone one.

## Key equations

```
λ = c / f                       c = 299,792,458 m/s
L = k · λ/4                     k = 0.95 default, range 0.90–0.97

I(d) = cos( π/2 · d/L )         current: max at short, zero at tip
V(d) = sin( π/2 · d/L )         voltage: zero at short, max at tip
Z(d) ∝ tan( π/2 · d/L )         impedance: 0 at short, ∞ at tip

m = clr + tw/2                  routing margin
p = max(2·tw, 1.0)              fold pitch
Σ segment lengths = L           invariant, verified live
```

`d` is measured along the arm from the shorting pin.

## Known limitation

**Ground-plane size does not enter the length calculation.** It is recorded and exported, but a 20 mm board and a 100 mm board produce the same arm length — which is not physically true. In a real inverted-F the ground plane is the other half of the radiator, and shrinking it detunes the antenna measurably.

Modelling that properly requires an EM solve, not a correction term. The limitation is stated in the generated constraints file so it travels with the design.

More broadly: this tool models **geometry exactly and electromagnetics approximately**. It produces a well-reasoned starting geometry for bench tuning, not a final answer. No impedance or SWR figure is printed, because a trustworthy one needs a real electromagnetic solver and a plausible-looking fake would be worse than none.

## Documentation

- **[Study guide](docs/IFA_Study_Guide.md)** — 27 pages on the physics, the algorithm, the software, and real-world use, with worked examples and a glossary
- **[One-page write-up](docs/TRN553_IFA_Designer_writeup.pdf)** — the course deliverable
- **[Original spec](docs/PCB_IFA_Antenna_Tool_Spec_v2.md)** — the written specification the implementation was built from

## References

Course lecture material, Umair Hashmi, TRN553, Seneca Polytechnic.

kurtisperrie, "TDR Simulator," TRN553 Build-a-Tool, Seneca Polytechnic. <https://kurtisperrie.github.io/TDRSimulator.github.io/> — studied as the structural reference for this tool; the numbered how-to strip, the parameter panel with inline formulas, the live readout, and the references / AI-disclosure pairing all follow its layout.

## AI use

Claude (Anthropic) generated the HTML, CSS, and JavaScript from a written specification I authored (included in `docs/`). Every equation and test value was verified against course material and by hand calculation. `tests.js` is the verification artifact.

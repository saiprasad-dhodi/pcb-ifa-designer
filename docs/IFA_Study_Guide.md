# PCB Inverted-F Antennas: A Complete Study Guide

### Companion document to the TRN553 Build-a-Tool IFA Designer

**Author:** Umair Hashmi · Seneca Polytechnic · TRN553

**Purpose:** This document explains the physics, the mathematics, the software, and the real-world engineering behind the PCB Inverted-F Antenna Designer tool. It is written to be read start to finish, or dipped into by section.

---

## How to read this document

This guide is organised into five parts:

| Part | Sections | What it covers |
|---|---|---|
| I | 1–7 | The physics: why antennas have a size, what resonance means, standing waves |
| II | 8–13 | The engineering: folding, design rules, the ground plane, the fudge factor |
| III | 14–18 | The software: how the tool is built, function by function |
| IV | 19–24 | The real world: where IFAs are used, worked examples, bench tuning |
| V | 25–28 | Study aids: glossary, equation sheet, likely exam/demo questions |

If you only have twenty minutes, read Sections 2, 3, 6, 8, and 20. Those five carry the core ideas.

A note on how to use this with an AI notebook tool: the section headings are deliberately specific and self-contained, so questions like *"why does the short pin move instead of the feed"* or *"what does k=0.95 actually represent"* will retrieve the right passage.

---
---

# PART I — THE PHYSICS

---

## 1. What this tool actually is

The PCB IFA Designer is a browser-based calculator and layout generator. You give it a radio frequency and some board dimensions. It gives you back:

1. A **resonant length** — how many millimetres of copper the antenna needs.
2. A **folded layout** — how to fit that copper into the small strip of board you have available.
3. A **KiCad footprint file** — importable directly into PCB design software.
4. A **constraints sheet** — the rules a manufacturer and a PCB layout engineer need to follow.

The tool exists to make one specific idea visible and playable: **the length of the antenna sets *what frequency* it works at, and the position of the shorting pin sets *how well the radio can push power into it*. These two things are independent.**

That independence is the entire point of the inverted-F geometry, and it is the thing that is hardest to see from an equation on a page. It is easy to see if you can drag a slider and watch a picture change.

### What the tool is not

It is not an electromagnetic simulator. It does not compute impedance, standing wave ratio, radiation pattern, gain, or efficiency. Those quantities require solving Maxwell's equations numerically over a 3D mesh — that is what commercial tools like HFSS, CST, and openEMS do, and they take minutes to hours per solve on real hardware.

The tool produces a **starting geometry**. A real antenna designer takes that geometry, fabricates it, measures it, and adjusts. Section 22 covers that process in detail.

---

## 2. Why antennas have to be a specific size

This is the foundational idea. Everything else in this document depends on it.

### Radio waves have a physical length

An electromagnetic wave travelling through free space moves at the speed of light, *c* = 299,792,458 metres per second. If that wave oscillates *f* times per second, then in one complete oscillation it travels a distance of:

```
λ = c / f
```

This distance λ (lambda) is the **wavelength**. It is a real, physical, measurable length in metres.

The tool works in millimetres and megahertz, so it uses:

```
λ (mm) = 299792.458 / f (MHz)
```

The constant 299792.458 is the speed of light expressed in millimetre-megahertz. It is the same number as the speed of light in metres per second, just with the decimal point moved — because a millimetre is 10⁻³ metres and a megahertz is 10⁶ hertz, and those two factors of a thousand cancel neatly.

### What this means in practice

| Band | Frequency | Wavelength | Where you meet it |
|---|---|---|---|
| ISM 433 | 433.92 MHz | 690.9 mm | Garage door remotes, key fobs |
| LoRa EU | 868 MHz | 345.4 mm | European long-range IoT |
| LoRa US / ISM | 915 MHz | 327.6 mm | North American long-range IoT |
| GPS L1 | 1575.42 MHz | 190.3 mm | Satellite positioning |
| Wi-Fi / BLE | 2440 MHz | 122.9 mm | Everything in your house |
| Wi-Fi 5 GHz | 5800 MHz | 51.7 mm | Faster, shorter-range Wi-Fi |

Notice the trend: **higher frequency means shorter wavelength means smaller antenna.** This single relationship explains an enormous amount about consumer electronics. It is why a Bluetooth earbud can have an antenna hidden inside it, and why a long-range 433 MHz remote has a wire sticking out.

### Why the antenna has to match the wavelength

An antenna is a structure that converts a guided electrical signal (current in a wire) into a radiated electromagnetic wave, or vice versa. It does this efficiently only when its physical dimensions are comparable to the wavelength of the signal.

The intuition: think of pushing a child on a swing. The swing has a natural period. If you push at exactly that rhythm, energy accumulates and the swing goes high. If you push at a random rhythm, your pushes fight each other and very little energy transfers.

An antenna is an electrical structure with a natural resonant frequency determined by its size. Drive it at that frequency and current builds up along it, and that oscillating current radiates. Drive it far from resonance and the energy reflects back toward the transmitter instead of radiating.

**An antenna that is much smaller than the wavelength is a bad antenna.** Not slightly worse — dramatically worse. Efficiency falls off steeply, and bandwidth collapses with it. This is a hard physical limit (formalised as the Chu–Harrington limit), not an engineering shortcoming that better design can eliminate.

---

## 3. The quarter-wave resonator: why λ/4 and not λ

If a full wavelength at 915 MHz is 327.6 mm, why does the tool produce an antenna only about 78 mm long? Where did the other three quarters go?

### The half-wave dipole

The classical reference antenna is the **half-wave dipole**: two collinear conductors, each a quarter wavelength long, driven at the centre. Total length λ/2.

The reason λ/2 works is a boundary condition. At the two free ends of the dipole, current must be **zero** — there is nowhere for charge to flow to; the conductor simply stops. At the centre feed point, current is at **maximum**. A wave that starts at zero, rises to a maximum, and returns to zero, is exactly one half of a sine cycle. Half a cycle of a wave occupies half a wavelength. Hence λ/2.

### The ground plane as a mirror

Now the trick that halves the size again.

If you place a quarter-wave conductor vertically above a large conducting sheet, the sheet behaves as an **electrical mirror**. The electromagnetic boundary conditions at a good conductor force the tangential electric field to zero, and satisfying that condition is mathematically identical to having a mirror-image conductor on the other side of the sheet, carrying an image current.

The radio "sees" a full half-wave dipole. But you only physically built half of it. The ground plane supplies the other half for free.

This is called a **monopole over a ground plane**, and it is why a quarter wavelength is the natural size for a PCB antenna: the copper ground pour on your circuit board is already there, and it can serve as the mirror.

> **Key consequence, and the tool's main honest limitation:** the ground plane is not a passive bystander. It is genuinely one half of the antenna. If it is too small, the mirror is imperfect, and the antenna detunes and loses efficiency. Section 12 covers this properly.

### The formula in the tool

```
L = k · λ/4
```

The factor **k** (default 0.95) is a correction. A pure theoretical quarter-wave in free space would use k = 1. Real antennas on real circuit boards always resonate slightly *lower* in frequency than the ideal formula predicts, which means the physical conductor must be slightly *shorter* than λ/4 to hit the target frequency. Section 11 explains the physics that k is standing in for.

### Worked numbers

At 915 MHz with k = 0.95:

```
λ    = 299792.458 / 915  = 327.642 mm
λ/4  = 327.642 / 4       =  81.911 mm
L    = 0.95 × 81.911     =  77.815 mm
```

At 2440 MHz with k = 0.95:

```
λ    = 299792.458 / 2440 = 122.866 mm
λ/4  = 122.866 / 4       =  30.716 mm
L    = 0.95 × 30.716     =  29.181 mm
```

Note how dramatically the size drops. 78 mm is a substantial fraction of a typical circuit board. 29 mm fits along one edge without trouble. This single fact drives most antenna decisions in commercial products.

---

## 4. From monopole to inverted-L to inverted-F

The quarter-wave monopole is simple and works well, but it sticks straight up off the board. For a product that has to be flat and thin, that is unacceptable. The inverted-F geometry is the result of two successive modifications to solve two successive problems.

### Step 1: the inverted-L

Take the vertical quarter-wave monopole and bend it over at 90° so most of its length runs horizontally, parallel to the ground plane. It now looks like an upside-down letter L.

**Problem solved:** the antenna is now flat. It can be etched as a copper trace on the surface of the board.

**New problem created:** the input impedance collapses. A vertical quarter-wave monopole presents roughly 36 ohms at its base. Once you fold it down close to the ground plane, capacitive coupling to the ground pulls that impedance down to just a few ohms — often under 10.

Why that matters: virtually all radio front-ends are designed for a **50 ohm** system impedance. If the antenna presents 5 ohms to a 50 ohm transmitter, most of the power reflects straight back instead of radiating. The mismatch loss is severe.

### Step 2: the inverted-F

Add a second vertical conductor — a **shorting pin** — connecting a point on the horizontal arm down to the ground plane. Then feed the antenna at a *different* point on the arm.

The resulting shape, drawn on its side, resembles the letter F: one long horizontal stroke (the arm) with two short vertical strokes coming off it (the short pin and the feed stub).

```
              open tip
                  |
   ───────────────┘   ← the arm (length L from short to tip)
   │   │
   │   │
   S   F              ← S = shorting pin to ground, F = feed
   │   │
 ══╧═══╧══════════    ← ground plane
   ←─S─→
```

**Problem solved:** the shorting pin creates an impedance transformer. By choosing where along the arm you tap the feed, you can select essentially any input impedance you like between near-zero and very high — including exactly 50 ohms.

This is the central cleverness of the inverted-F, and Section 6 explains the mechanism.

---

## 5. Standing waves: what is actually happening on the arm

To understand why the feed position controls impedance, you need a picture of what current and voltage are doing along the length of the arm.

### The boundary conditions

The arm has two ends, and each imposes a hard physical constraint:

**At the shorting pin (call this distance d = 0):**
The arm is connected directly to ground. Ground is, by definition, at zero potential. Therefore **voltage is zero** at this point. And because current flows freely into the ground plane here, **current is at maximum**.

**At the open tip (d = L):**
The copper simply ends. There is nowhere for charge to flow. Therefore **current is zero**. Charge accumulates at the tip instead, which means **voltage is at maximum**.

### The resulting distributions

Between these two endpoints, current and voltage vary sinusoidally. Fitting a quarter-cycle of sine between the boundary conditions gives:

```
I(d) = cos( π/2 · d/L )     ← current, normalised to 1.0 at the short
V(d) = sin( π/2 · d/L )     ← voltage, normalised to 1.0 at the tip
```

where *d* is distance measured **along the arm, starting from the shorting pin**.

Check the endpoints:

| Position | d/L | I(d) | V(d) | Interpretation |
|---|---|---|---|---|
| At the short | 0.00 | cos(0) = **1.00** | sin(0) = **0.00** | Max current, zero volts |
| Quarter along | 0.25 | 0.924 | 0.383 | Still current-dominated |
| Halfway | 0.50 | 0.707 | 0.707 | Equal |
| Three-quarters | 0.75 | 0.383 | 0.924 | Voltage-dominated |
| At the tip | 1.00 | cos(π/2) = **0.00** | sin(π/2) = **1.00** | Zero current, max volts |

This is a **standing wave**. The pattern does not travel along the arm; it sits there, oscillating in place at the drive frequency. It is the same phenomenon as a plucked guitar string fixed at one end: the shape of the vibration is fixed, only its amplitude oscillates.

### Why this is the chart in the tool

The right-hand chart in the tool draws exactly these two curves, with a marker showing where the feed taps in. It is drawn from the same two equations printed above — not from a lookup table or an approximation.

The reason it earns its place on screen is that it makes the next section's argument *visible* rather than merely stated.

---

## 6. The central idea: why moving the short changes the match but not the frequency

This is the most important section in the document. If you understand this, you understand the tool.

### Impedance is a ratio

Electrical impedance is, at its simplest, the ratio of voltage to current:

```
Z = V / I
```

We have expressions for both V and I at any point along the arm. So we can write the impedance seen at a tap point at distance *d* from the short:

```
Z(d)  ∝  V(d) / I(d)  =  sin(π/2 · d/L) / cos(π/2 · d/L)  =  tan(π/2 · d/L)
```

Look at what the tangent function does over this range:

| d/L | tan(π/2 · d/L) | Impedance at the tap |
|---|---|---|
| 0.00 | 0.00 | Zero — a dead short |
| 0.05 | 0.079 | Very low |
| 0.10 | 0.158 | Low |
| 0.25 | 0.414 | Moderate |
| 0.50 | 1.000 | Equal to the characteristic value |
| 0.75 | 2.414 | High |
| 1.00 | ∞ | Infinite — an open circuit |

The impedance rises **monotonically** from zero at the short to infinity at the tip. Monotonic means it never doubles back. And that has a powerful consequence:

> **For any target impedance you want — 50 ohms, 75 ohms, whatever — there is exactly one tap position along the arm that provides it.**

That is a design procedure. Choose your target, find the position, place your feed there.

### Now the part that surprises people

Here is the question that trips everyone up: *if I move the feed point, doesn't that change the length of the antenna, and therefore its frequency?*

**No — and understanding why is the whole game.**

The resonant length **L is measured from the shorting pin to the open tip.** The feed is not an endpoint of the resonator. It is a *tap* onto a resonator whose two ends are the short and the tip.

So there are two distances in play, and they are independent:

| Quantity | Measured from → to | Controls |
|---|---|---|
| **L** | shorting pin → open tip | **Resonant frequency** |
| **S** | shorting pin → feed point | **Input impedance** |

Move the feed, and S changes while L stays exactly the same. The antenna resonates at precisely the same frequency; only the impedance the radio sees has changed.

### How the tool implements this

In the tool, the **feed pad is fixed** at x = 15 mm on the board (this reflects reality — the feed connects to the radio chip, whose position is set by other constraints). The **shorting pin moves**.

When you drag the short-pin slider, the software:

1. Computes the new short position: `xShort = 15 − S`
2. Re-lays the entire arm starting from that new position
3. Walks out exactly **L** millimetres of copper, regardless

The arm's total path length is always L. The tip lands somewhere different, but the short-to-tip distance is invariant. Meanwhile S — the distance from the short to the fixed feed — has changed, so the feed now taps the standing wave at a different point.

**This is why the resonance readout does not move when you drag the short-pin slider, while the tap marker on the standing-wave chart slides along the curve.** That behaviour is not a quirk of the software. It is the physics of the inverted-F, made visible.

### An analogy that may help

Think of a guitar string stretched between two fixed posts. The pitch is set by the distance between the posts — that is L, and it does not change.

Now think about where you pluck the string. Pluck it near the post and you need a lot of force for a small displacement — that is a "low impedance" point. Pluck it in the middle and a gentle touch moves it a long way — "high impedance." The pitch is identical either way. You have changed how easy it is to *couple energy in*, not what note comes out.

The shorting pin position is the pluck position. L is the distance between the posts.

---

## 7. What "resonance" and "matching" actually mean for a radio

Two words get used constantly in antenna work and are easy to conflate. They are different things.

### Resonance

An antenna is **resonant** when its reactance (the imaginary part of its impedance) is zero at the operating frequency. Physically: energy sloshes between electric and magnetic storage in perfect balance, and the structure willingly supports a large standing-wave current.

Resonance is a property of **size and shape**. It is set by L.

### Matching

An antenna is **matched** when its impedance equals the system impedance of the radio — nearly always 50 ohms.

Matching is a property of **where you connect**. It is set by S.

### Why you need both

Consider the failure modes:

**Resonant but unmatched.** The antenna wants to radiate at your frequency, but presents 5 ohms to a 50 ohm transmitter. Most of your power reflects back down the feed line. Little radiates. The transmitter may overheat.

**Matched but not resonant.** You have used a matching network to force a 50 ohm presentation, but the structure itself does not want to radiate at this frequency. The transmitter is happy — power flows out of it — but the power is dissipated as heat in the matching components and the structure rather than radiated. This is the classic "dummy load" failure: your SWR meter reads perfect and your range is terrible.

> **A perfect SWR reading does not mean a good antenna.** A 50 ohm resistor has a perfect SWR and radiates nothing at all. This is worth remembering; it is one of the most common misconceptions in practical RF work.

You need the structure to be the right size (resonance, via L) *and* to be tapped at the right place (matching, via S). The inverted-F gives you independent control of both. That is why the geometry is so widely used.

---
---

# PART II — THE ENGINEERING

---

## 8. Folding: fitting a long wave onto a short board

At 915 MHz the antenna needs 77.8 mm of copper. A typical IoT sensor board might be 60 mm wide with only a 12 mm strip available at the top for the antenna. The copper does not fit in a straight line.

The solution is to **fold** — also called meandering or serpentining. Run the trace to the edge of the available area, turn 180°, run back, turn again, and repeat until you have laid down the required length.

### The available space

The tool describes the antenna region with these parameters:

| Parameter | Meaning | Typical |
|---|---|---|
| `boardW` | Total board width | 60 mm |
| `koH` | Keepout height — the copper-free strip at the top | 12 mm |
| `tw` | Trace width | 0.5 mm |
| `clr` | Clearance between adjacent copper | 0.3 mm |

From these it derives two working quantities:

```
m = clr + tw/2          ← routing margin: how close the trace centreline
                          may come to a boundary
p = max(2·tw, 1.0)      ← fold pitch: vertical spacing between rows
```

**Why `m = clr + tw/2`:** the trace has width, and the coordinates in the layout describe its *centreline*. Half the trace width sticks out either side. Add the required clearance and you get the minimum distance from centreline to any boundary. With tw = 0.5 and clr = 0.3, m = 0.55 mm.

**Why `p = max(2·tw, 1.0)`:** rows must be far enough apart that adjacent copper does not couple excessively or violate manufacturing rules. Two trace widths is the geometric minimum; the 1.0 mm floor prevents the value becoming absurdly small when someone specifies a very thin trace.

### The coordinate system

The board is described with y = 0 at the top edge and y increasing downward. The ground plane starts at y = `koH`. So the antenna lives in the strip between y = 0 and y = koH, and rows are stacked **upward** — meaning y *decreases* as rows are added.

The first row sits at y = koH − m, just clear of the ground plane. Each subsequent row is p millimetres higher (numerically lower y). The layout fails when the next row would land at y < m, meaning it would be too close to the top edge of the board.

### How much copper fits?

```
rows available   ≈ floor( (koH − 2m) / p ) + 1
copper per row    = boardW − 2m
```

With the typical values above: m = 0.55, p = 1.0, so rows ≈ floor(10.9 / 1.0) + 1 = 11 rows, each holding 58.9 mm of copper. Total capacity is roughly 650 mm — plenty for 915 MHz, which needs only 78 mm and uses about two rows.

Where it gets tight is the lower bands. At 433 MHz the antenna needs 164 mm — three rows. At 169 MHz it needs over 400 mm, seven rows, and the meander becomes so dense that the electrical penalties described below become severe.

### The hidden cost of folding

Folding is not free, and this is a point worth understanding properly because the tool does not show it.

**Radiation comes from current.** When you fold the trace back on itself, adjacent rows carry current in **opposite directions**, separated by only p ≈ 1 mm — a tiny fraction of a wavelength. In the far field, the radiation from those two anti-parallel currents largely **cancels**.

The consequences:

1. **Efficiency drops.** A tightly meandered antenna may radiate only 30–60% of the power delivered to it, versus 80–90% for a straight monopole. The rest is lost as heat in the copper and dielectric.
2. **Bandwidth narrows.** Meandering raises the antenna's Q factor. A high-Q antenna is sharply tuned — good for rejecting interference, bad for tolerating manufacturing variation. A meandered antenna might have 2% usable bandwidth where a straight one has 8%.
3. **Sensitivity to everything rises.** Narrow bandwidth means small perturbations — a plastic enclosure, a nearby battery, a user's hand — shift the resonance enough to matter.

**Design guidance that follows:** use the fewest folds you can. If the antenna fits in one or two rows, you are in good shape. If it needs five or more, seriously consider whether you should be using a chip antenna, an external whip, or a higher frequency band instead.

The tool reports the fold count for exactly this reason. Watch that number.

---

## 9. The fold algorithm, step by step

This is the `layoutArm` function in `core.js`. It is worth walking through because it is the heart of the tool and it is only about forty lines.

### Setup

```javascript
const m = clr + tw / 2;              // routing margin
const yG = koH;                      // ground plane top edge
const p = Math.max(2 * tw, 1.0);     // fold pitch
const xMin = m, xMax = boardW - m;   // horizontal travel limits

const sMax = X_FEED - m;             // short cannot go past the board edge
const sMm = Math.min(opts.S_mm, sMax);
const clamped = sMm < opts.S_mm;     // did we have to limit it?
const xShort = X_FEED - sMm;         // short pin x position
```

Note the **clamping**. The feed is fixed at x = 15 mm and the short sits to its left. If the user asks for a spacing larger than 15 − m ≈ 14.45 mm, the short would fall off the left edge of the board. Rather than producing an invalid layout, the tool limits the value and raises a flag so the interface can tell the user what happened. Silently producing nonsense would be worse.

### The walk

```javascript
let remaining = L, dir = 1;          // dir: +1 rightward, -1 leftward
let x = xShort, y = yG - m;          // start just above the ground plane
const root = { x: x, y: y };         // this is d = 0 on the standing wave
```

Then a loop with three possible outcomes per iteration:

```javascript
for (;;) {
  const run = dir > 0 ? xMax - x : x - xMin;   // distance to the wall ahead

  // CASE 1: we have less copper left than the run — we finish mid-row
  if (remaining <= run) {
    const nx = x + dir * remaining;
    segments.push({ x1: x, y1: y, x2: nx, y2: y });
    tip = { x: nx, y: y };
    break;
  }

  // Otherwise: run all the way to the wall
  const wx = x + dir * run;
  segments.push({ x1: x, y1: y, x2: wx, y2: y });
  x = wx; remaining -= run;

  // CASE 2: the remainder is shorter than one fold riser — finish going up
  if (remaining <= p) {
    segments.push({ x1: x, y1: y, x2: x, y2: y - remaining });
    tip = { x: x, y: y - remaining };
    break;
  }

  // Otherwise: complete the fold and reverse direction
  segments.push({ x1: x, y1: y, x2: x, y2: y - p });
  y -= p; remaining -= p; dir = -dir;

  // CASE 3: the new row is outside the keepout — we failed
  if (y < m) { fits = false; tip = { x: x, y: y }; break; }
}
```

### Why this construction is correct

The loop maintains one invariant: **`remaining` is always exactly the copper still to be placed.** Every segment pushed decrements `remaining` by precisely its own length. The loop only exits when `remaining` reaches zero (Cases 1 and 2) or when the space runs out (Case 3).

Therefore, whenever `fits` is true, the sum of all segment lengths equals L exactly.

This is not merely asserted — the test suite checks it numerically, and the tool's "Verify the working" panel re-checks it live on every parameter change, summing the segments and comparing to L. If the two ever diverged, it would be visible immediately.

### Worked trace at 915 MHz

Inputs: L = 77.815 mm, boardW = 60, koH = 12, tw = 0.5, clr = 0.3, S = 6% of L = 4.669 mm.

```
m = 0.55, p = 1.0, xMin = 0.55, xMax = 59.45
xShort = 15 − 4.669 = 10.331
start at (10.331, 11.45), remaining = 77.815, dir = +1

Iteration 1:
  run = 59.45 − 10.331 = 49.119
  remaining (77.815) > run  →  go to the wall
  segment: (10.331, 11.45) → (59.45, 11.45)      [49.119 mm]
  remaining = 28.696
  remaining > p  →  fold
  segment: (59.45, 11.45) → (59.45, 10.45)       [1.0 mm]
  remaining = 27.696, y = 10.45, dir = −1
  y (10.45) ≥ m  →  continue

Iteration 2:
  run = 59.45 − 0.55 = 58.9
  remaining (27.696) ≤ run  →  finish mid-row
  segment: (59.45, 10.45) → (31.754, 10.45)      [27.696 mm]
  tip = (31.754, 10.45)

Total placed: 49.119 + 1.0 + 27.696 = 77.815 ✓
Folds: 1    Rows: 2    Fits: yes
```

### Locating a point along the arm

The companion function `pointAlongPath(segments, d)` answers: *given a distance d measured along the copper from the short, what are its x,y coordinates?*

It walks the segment list accumulating length until it finds the segment containing d, then interpolates linearly within it. Because every segment is purely horizontal or purely vertical, the length is simply `|Δx| + |Δy|`.

This function does the real work behind two visible features:

- **The current-distribution overlay.** The trace on the board preview is drawn in a colour gradient computed from I(d) = cos(π/2 · d/L) — bright where current is high near the short, fading toward the open tip.
- **The feed tap marker.** The ring on the board at the feed junction, and its readout, come from evaluating the standing wave at d = S.

Without `pointAlongPath`, the standing-wave chart and the board would be two unrelated pictures. With it, they are two views of the same physical quantity — which is precisely what makes the visualisation worth having.

---

## 10. The design rule parameters

The tool exposes every parameter rather than hiding them behind defaults. Here is what each one is for.

| Parameter | Symbol | Default | What it controls |
|---|---|---|---|
| Frequency | f | 915 MHz | Target resonance. Drives λ and therefore L. |
| Short spacing | S | 6% of L | Impedance tap position. Does **not** affect resonance. |
| Board width | gpW | 60 mm | Horizontal room for the meander. |
| Ground height | gpH | 40 mm | Recorded and exported; see Section 12 for why it does not enter the maths. |
| Keepout height | koH | 12 mm | Vertical room. Sets how many rows are available. |
| Trace width | tw | 0.5 mm | Copper width. Affects margin, fold pitch, and losses. |
| Clearance | clr | 0.3 mm | Minimum copper-to-copper gap. Set by the fab house. |
| Permittivity | εr | 4.4 | Substrate dielectric constant. Recorded; absorbed into k. |
| Substrate height | subH | 1.6 mm | Board thickness. Recorded; absorbed into k. |
| Correction factor | k | 0.95 | The empirical fudge. See Section 11. |

### Notes on choosing values

**Trace width.** Wider traces have lower resistive loss and slightly wider bandwidth, but they force a larger fold pitch and so fit less copper per row. 0.5 mm is a reasonable compromise for sub-GHz. At 2.4 GHz you can often afford 1.0 mm because you need so much less total length.

**Clearance.** This comes from your PCB manufacturer's capability sheet, not from you. 0.15 mm (6 mil) is standard for cheap prototype services; 0.1 mm costs more. Using a tighter value than your fab supports means the board comes back wrong.

**Keepout height.** More is better, up to about 0.1λ. It lets you use fewer folds. The keepout must be free of copper **on every layer** — including inner layers and the bottom-side pour. This is the single most common mistake in practice: an otherwise correct design ruined by a ground pour on the bottom layer directly beneath the antenna, which shorts the fields and detunes it badly.

**Permittivity and substrate height.** Recorded in the export for documentation, but they do not enter the length calculation. They are physically real effects — a thicker or higher-εr substrate slows the wave and shortens the required copper — but capturing them properly requires the microstrip effective-permittivity model or an EM solve. In this tool they are folded into k.

---

## 11. What the factor k = 0.95 is actually hiding

The formula `L = k · λ/4` has an empirical constant in it. Empirical constants are places where physics has been swept under a rug, and it is worth knowing what is under this particular rug.

### The end effect

At the open tip, the electric field does not stop abruptly — it bulges out into the surrounding space, coupling capacitively to the ground plane and to air. This **fringing capacitance** makes the antenna appear electrically longer than it physically is.

Since it is already electrically longer, you must build it physically shorter to land on the right frequency. This is the largest single contributor to k, and it explains why k < 1 rather than > 1.

### Dielectric loading

The trace sits on FR-4 with εr ≈ 4.4. Some of the field travels through the board material, where waves propagate more slowly, and some through air above.

The wave therefore experiences an **effective permittivity** somewhere between 1 and 4.4 — typically around 2.5–3.0 for a thin trace on a 1.6 mm substrate. Slower propagation means a shorter physical structure resonates at the target frequency. Another push toward k < 1.

### The uncounted vertical stubs

This is worth flagging explicitly because it is a genuine simplification in the tool.

`L` is measured along the **horizontal arm only** — from the point where the short stub meets the arm, out to the open tip. The short stub itself (running down from the arm to the ground plane) and the feed stub are drawn in the layout and exported to KiCad, but their lengths are **not counted in L**.

Electrically, those stubs are part of the structure and do influence resonance. Their contribution is absorbed into k. With a keepout of 12 mm and the arm sitting near the ground plane, the stub is short and the error is modest. On a design with a much taller keepout, the stub becomes a larger fraction of the total and k would need adjusting.

### Ground plane proximity and size

Capacitive coupling to a nearby ground plane loads the antenna and lowers resonance. How much depends on the gap and on the ground plane's own dimensions — which is exactly the effect the tool does not model (Section 12).

### The honest summary

**k is a bucket.** It holds end-effect capacitance, dielectric loading, uncounted stub length, ground proximity, and manufacturing tolerance, all rolled into one number.

The typical range is **0.90 to 0.97**:

- Toward **0.97**: thin substrate, low εr, large keepout, few folds, generous ground plane
- Toward **0.90**: thick FR-4, high εr, tight keepout, many folds, cramped ground

Any real design will need k adjusted after the first measurement. If you build a 915 MHz antenna and it measures 890 MHz, your antenna is too long; reduce k by about the ratio (890/915 ≈ 0.973) and rebuild. Two iterations usually converges.

This is why the tool exposes k as a user-editable field rather than burying it. It is the primary tuning handle after the first prototype comes back from the fab.

---

## 12. The ground plane: the tool's main limitation, explained properly

This deserves its own section because it is the most significant gap between the model and reality, and because being able to explain it clearly is a mark of understanding the design rather than just operating it.

### What the tool does

The ground plane width and height are input fields. They are drawn in the preview, written into the exported KiCad footprint, and recorded in the constraints file.

They **do not enter the length calculation at all.** `quarterWaveMm(fMHz, k)` takes only frequency and k. A 20 mm board and a 100 mm board produce identical arm lengths.

### Why that is physically wrong

Recall Section 3: the ground plane is the mirror that supplies the missing half of the dipole. That role has requirements.

For the mirror to work well, the ground plane needs to be **large compared to a quarter wavelength** in the direction the antenna runs. When it is not:

1. **The image is incomplete.** Current flowing in the ground plane is the image current, and it must have somewhere to flow. A small plane constricts it.
2. **The ground plane itself radiates.** With a small plane, the currents on it contribute significantly to the pattern. The "antenna" becomes the arm *and* the board together.
3. **Resonance shifts.** The combined structure resonates at a different frequency than the arm alone predicts — often several percent lower.
4. **The pattern distorts.** Radiation becomes asymmetric and direction-dependent in ways the simple model cannot express.

### The scale of the error

Rules of thumb from practice:

| Ground plane length (along antenna axis) | Behaviour |
|---|---|
| > λ/2 | Approaching ideal; the model is reasonable |
| ≈ λ/4 | Workable; expect a few percent frequency shift |
| < λ/8 | Significant detuning and efficiency loss; the model is unreliable |

At 915 MHz, λ/4 is 82 mm. A 60 mm board is already smaller than that. **So for the tool's own default configuration, the ground plane is undersized and the model is optimistic.**

At 2440 MHz, λ/4 is 31 mm, and a 60 mm board comfortably exceeds it. The model is on much firmer ground at 2.4 GHz than at 915 MHz.

### Why the tool ships with the limitation

Modelling this properly is not a matter of adding a correction term. The relationship between ground plane geometry and resonant shift is not closed-form — it depends on plane shape, aspect ratio, antenna position along the edge, component placement, and the position of every other conductor nearby. It requires an EM solve.

The design decision was to **record the parameter, export it, and state the limitation plainly**, rather than invent a plausible-looking correction factor that would be wrong in ways the user could not detect. A stated limitation is honest engineering. A fabricated correction would be worse than no correction, because it would give false confidence.

### The practical guidance

- Aim for a ground plane at least λ/4 in the direction the antenna runs; more is better.
- Place the antenna at the **corner or edge** of the board, with the ground plane extending away from it.
- Do not put the antenna in the middle of a large plane — it will be surrounded and shielded.
- Expect the fabricated result to land **below** the predicted frequency if the plane is small, and plan to trim the arm.

---

## 13. Everything that is not in the model

For completeness, and because these are the questions a knowledgeable reviewer will ask:

| Effect | Reality | Tool's treatment |
|---|---|---|
| Ground plane size | Strongly affects tuning | Recorded, not modelled |
| Substrate εr | Slows wave, shortens antenna | Absorbed into k |
| Substrate thickness | Affects field distribution | Absorbed into k |
| Copper thickness | Minor effect on inductance | Ignored |
| Solder mask | Adds slight dielectric loading (~0.5%) | Ignored |
| Enclosure plastic | Can shift resonance 2–5% | Ignored |
| Nearby components | Metal cans, batteries, displays detune badly | Ignored |
| User's hand / body | Can shift resonance 5–10% and absorb power | Ignored |
| Manufacturing tolerance | ±10% etch variation on trace width | Ignored |
| Meander coupling | Reduces efficiency and bandwidth | Fold count reported, effect not quantified |

The pattern here: the tool models the **geometry** exactly and the **electromagnetics** approximately. It is a layout generator with a physics-informed length calculation, not a simulator. Used with that understanding, it is genuinely useful. Used as an oracle, it will mislead.

---
---

# PART III — THE SOFTWARE

---

## 14. Architecture: three files, one source of truth

The project is deliberately small. Three files, no build step, no dependencies, no network requests.

| File | Size | Role |
|---|---|---|
| `core.js` | ~9 KB | All mathematics. Pure functions, no DOM, no side effects. |
| `index.html` | ~66 KB | The complete application. Contains `core.js` inlined verbatim. |
| `tests.js` | ~7 KB | 43 assertions against `core.js`. Runs in Node or the browser. |

### The inlining rule

`index.html` must work when opened directly from disk with a double-click — no web server, no `file://` CORS problems, no CDN. That means `core.js` cannot be loaded with a `<script src="">` tag; it must be embedded.

But if it were simply copy-pasted, the two copies would drift apart the first time someone edited one and not the other. Then `tests.js` would be testing code that the application no longer runs, and the test suite would be worse than useless — it would be actively misleading.

The rule adopted: **the inlined block in `index.html` is byte-for-byte identical to `core.js`.** Not equivalent, not functionally the same — identical. This is verifiable mechanically:

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

If that prints `false`, the build is broken and the tests no longer mean anything.

### The UMD wrapper

`core.js` opens with:

```javascript
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.IFA = factory();
}(typeof self !== "undefined" ? self : this, function () { ... }));
```

This is the UMD (Universal Module Definition) pattern. It detects its environment: in Node it exports via `module.exports`; in a browser it attaches to `window.IFA`. The same file works in both without modification, which is what lets `tests.js` run under Node *and* be pasted into a browser console.

### Why pure functions

Every function in `core.js` takes inputs and returns outputs. None touches the DOM, reads global state, or mutates its arguments. This has concrete benefits:

- **Testable.** Call with known inputs, compare to known outputs. No mocking, no setup.
- **Debuggable.** A wrong number can only come from the arguments, and you can see them.
- **Reusable.** The same functions serve the on-screen preview, the charts, the KiCad export, and the README generator.

The UI layer in `index.html` reads inputs, calls into `IFA.*`, and renders results. All physics lives on one side of that boundary.

---

## 15. The calculation functions

### `wavelengthMm(fMHz)`

```javascript
function wavelengthMm(fMHz) { return C_MM_MHZ / fMHz; }
```

where `C_MM_MHZ = 299792.458`. One line, direct implementation of λ = c/f.

### `quarterWaveMm(fMHz, k)`

```javascript
function quarterWaveMm(fMHz, k) {
  if (k === undefined) k = 0.95;
  return (k * wavelengthMm(fMHz)) / 4;
}
```

Implements L = k·λ/4, defaulting k to 0.95. Note that it calls `wavelengthMm` rather than repeating the division — the speed of light appears in exactly one place in the codebase.

Two properties worth knowing, both covered by the test suite:

- **Monotonic decreasing in f.** Higher frequency always gives shorter L. There is no frequency at which the relationship inverts.
- **Linear in k.** Doubling k doubles L. This makes k a well-behaved tuning knob.

### `layoutArm(opts)`

Covered in detail in Section 9. Returns an object containing:

| Field | Meaning |
|---|---|
| `segments` | Array of line segments, each `{x1,y1,x2,y2}` |
| `folds` | Count of vertical segments (the 180° turns) |
| `fits` | Boolean — did the arm stay inside the keepout? |
| `root` | Coordinates of d = 0, where the short meets the arm |
| `tip` | Coordinates of d = L, the open end |
| `sMm` | Actual short spacing used, after clamping |
| `clamped` | True if the requested spacing had to be reduced |
| `xShort`, `m`, `p`, `yG` | Derived geometry, exposed for the renderer |

Returning the derived values (`m`, `p`, `yG`) rather than recomputing them in the UI is deliberate: it guarantees the drawing and the maths use identical numbers.

### `pointAlongPath(segments, d)`

Covered in Section 9. Walks the segment list to find the coordinates at path distance d.

Two guarantees, both tested:

```
pointAlongPath(segments, 0) === root
pointAlongPath(segments, L) === tip
```

These bracket the function. If either fails, the segment list and the length calculation have diverged.

---

## 16. The KiCad footprint export

`genFootprint(state, layout)` produces a KiCad 6+ `.kicad_mod` file — an s-expression describing pads, copper lines, and documentation shapes.

### Coordinate transformation

Board coordinates place the origin at the top-left of the board. KiCad footprints place the origin at the component's reference point — here, the centre of the feed pad. So every coordinate is transformed:

```javascript
const kx = function (x) { return x - X_FEED; };   // shift so feed pad is x=0
const ky = function (y) { return y - layout.yG; }; // shift so ground edge is y=0
```

The y axis needs no flip because both systems use y-down-positive.

### What gets emitted

```
(footprint "IFA_915MHz"
  (version 20240108)
  (generator "pcb_ifa_designer")
  (layer "F.Cu")
  (descr "PCB inverted-F antenna, 915 MHz, L=77.815mm, k=0.95. ...")
  (tags "antenna IFA RF")
  (attr smd exclude_from_pos_files exclude_from_bom)
  ...
  (pad "1" smd rect (at 0.000 0.000) (size 1.200 1.200) ...)   ← feed
  (pad "2" smd rect (at -4.669 0.000) (size 1.200 1.200) ...)  ← short
  (fp_line (start ...) (end ...) (stroke (width 0.500) ...) (layer "F.Cu"))
  ...
  (fp_rect ... (layer "Dwgs.User"))                            ← keepout outline
)
```

Three details worth noting:

**`attr exclude_from_pos_files exclude_from_bom`** — this is copper, not a component. It must not appear on the pick-and-place file or the bill of materials. Without this attribute, assembly houses generate queries about the missing part.

**Pad 2 at negative x** — the short pin sits to the left of the feed, so its x coordinate is `-sMm`. This falls straight out of the coordinate transform.

**The keepout rectangle on `Dwgs.User`** — a documentation layer, not copper. It tells whoever lays out the board where copper is forbidden. It is drawn dashed, and it carries no electrical meaning.

### The three-decimal rule

```javascript
function fmt(n) {
  if (typeof n !== "number" || !isFinite(n)) {
    throw new Error("non-finite value reached an output template");
  }
  return n.toFixed(3);
}
```

Every coordinate in every generated file passes through this function. Two reasons:

**Consistency.** KiCad's native precision is nanometres; three decimals of a millimetre (one micron) is far finer than any fabrication process and produces stable, diffable files.

**The guard clause.** If a `NaN` or `Infinity` ever reaches an output template, the function throws rather than writing `"NaN"` into a footprint file. A file containing `NaN` might silently import and produce a broken board. A thrown exception is loud and immediate. This is a deliberate choice to fail fast rather than fail quietly.

---

## 17. The constraints file

`genReadme(state, layout, isoDate)` produces a plain-text sheet with four sections:

**[1] INPUTS** — every parameter as entered, including whether the short spacing was clamped.

**[2] COMPUTED** — λ, L, fold count, arm bounding box, and whether it fits.

**[3] LAYOUT CONSTRAINTS** — the rules a PCB engineer must follow:

- Keep the keepout free of copper on **all** layers
- Connect pad 2 to the ground pour and stitch with vias
- Feed pad 1 through a 50 ohm microstrip
- Leave a **pi-network placeholder** at the feed — series plus two shunt 0402 pads — and populate it after measurement
- Re-check tuning if the ground plane dimensions change

That pi-network placeholder is the most practically important line in the file. It costs three unpopulated footprints and nothing in BOM cost, and it is the difference between a board you can tune and a board you have to respin. Every experienced RF engineer leaves one. Section 22 explains how it is used.

**[4] MODEL LIMITS** — states plainly that L is measured short-to-tip, that stubs and fringing are absorbed by k, that no EM solve was performed, and that εr and substrate height do not enter the formula.

Shipping the limitations *inside the generated artefact* means they travel with the design. A colleague who receives the footprint six months later gets the caveats along with it, rather than having to find whoever generated it.

---

## 18. Testing and verification

### The test suite

`tests.js` contains 43 assertions in these groups:

| Group | Checks |
|---|---|
| Wavelength | Known values, reciprocal relationship with frequency |
| Quarter-wave | Correct L, monotonic decrease with f, linear in k |
| Geometry | Segment lengths sum to L; root and tip are correctly placed |
| Path walking | `pointAlongPath` returns root at d=0 and tip at d=L |
| Clamping | Excessive short spacing is limited and flagged |
| Fit detection | An arm too long for the keepout reports `fits: false` |
| KiCad output | Structure, pad count, three-decimal formatting, required attributes |
| README output | All four sections present, live values interpolated |

Run with:

```bash
node tests.js
```

Output: `IFA tests: 43 passed, 0 failed — all green`

Because of the UMD wrapper, the same file can be pasted into a browser console with `index.html` open, and it will test the inlined copy.

### The live verification panel

Separately from the test suite, the tool includes a "Verify the working" panel that prints the derivation with the current live values:

```
λ = c/f = 299792.458 / 915 = 327.642 mm
L = k · λ/4 = 0.95 × 327.642 / 4 = 77.815 mm
segments: 49.119 + 1.000 + 27.696 = 77.815 mm ✓
```

That last line is a **live invariant check**, not a printout. It sums the actual segment lengths from the layout and compares against L. If the fold algorithm ever produced a path that did not total L, the mismatch would appear on screen immediately.

The distinction matters: the test suite proves the code was correct when it was written; the verification panel proves it is correct for the values currently on screen.

### Performance

The preview, readout, and both charts redraw on every input event — measured at roughly 0.9 ms per update, comfortably inside a 16 ms frame budget, so dragging a slider stays smooth.

The step-by-step derivation and the generated file text are **debounced by 450 ms**. These involve string building and are not useful mid-drag. Waiting for the values to settle avoids generating hundreds of intermediate KiCad files nobody will read.

---
---

# PART IV — THE REAL WORLD

---

## 19. Where PCB inverted-F antennas actually appear

The IFA is one of the most widely deployed antenna geometries in consumer electronics. You are almost certainly within a few metres of several right now.

### Wireless modules

Open almost any ESP32, nRF52, or CC2541 module and you will find a meandered inverted-F etched on the PCB at one end, with a clear keepout strip. The Espressif ESP-WROOM-32 is a canonical example — the antenna occupies roughly 15 × 6 mm at the top of the module, and the datasheet devotes several pages to how the module must be mounted so the host board does not block it.

Those mounting instructions exist entirely because of Section 12: the module's antenna performance depends on the ground plane it is soldered onto, which the module manufacturer does not control.

### Product categories

| Product | Band | Why an IFA |
|---|---|---|
| Bluetooth earbuds, trackers | 2.4 GHz | Only ~29 mm needed; zero component cost |
| Smart home sensors | 2.4 GHz / 915 MHz | Cheap, flat, no assembly step |
| Fitness bands | 2.4 GHz | Must be flat and conformal |
| Smart meters | 868/915 MHz | Long life, no connector to corrode |
| Medical wearables | 2.4 GHz | Sealed enclosure, no protruding parts |
| Laptop Wi-Fi | 2.4/5 GHz | Fits in the display bezel |
| Asset tags | 2.4 GHz | Cost-critical; a chip antenna would cost more |

### Why designers choose an IFA

**It is free.** A PCB antenna is copper you were already paying for. A chip antenna costs $0.10–$0.50 plus placement; a connector and whip costs several dollars plus assembly labour. At volume, that difference dominates.

**It is flat.** Nothing protrudes. Critical for sealed, wearable, or thin products.

**Nothing to break.** No connector to fatigue, no solder joint to crack under vibration, no part to fall off.

**It can be tuned in layout.** Adjusting a trace length is a Gerber revision, not a new part number.

### Why designers reject an IFA

**Size at low frequencies.** At 433 MHz you need 164 mm of copper. That is larger than many entire products.

**Efficiency.** A good external whip achieves 70–90% efficiency. A meandered PCB IFA on a small ground plane might achieve 30–50%. In a link budget, that is 3–5 dB — which can halve your range.

**Sensitivity to the environment.** Once a plastic case, a battery, a display, and a human hand are nearby, a PCB antenna detunes. Every one of those has to be present during final tuning.

**Certification risk.** If it does not pass FCC or CE emissions testing, fixing it means a board respin. An external antenna can often be swapped instead.

---

## 20. Worked example: a 915 MHz LoRa node

This example is worth working through carefully because it illustrates where the tool's guidance becomes a *design decision* rather than a calculation.

### The requirement

A battery-powered LoRa sensor for North America. 915 MHz ISM band. Board is 60 × 40 mm. A 12 mm strip at the top is available for the antenna.

### Running the numbers

```
λ    = 299792.458 / 915 = 327.642 mm
L    = 0.95 × 327.642/4 =  77.815 mm
```

From Section 9's trace: this lays out in **2 rows with 1 fold**, ending at x = 31.75 mm. It fits.

### But should you use it?

Now apply Section 12. λ/4 at 915 MHz is 82 mm. The board is 60 mm wide — **smaller than a quarter wavelength.** The ground plane is undersized for this frequency.

Predicted consequences:

- Measured resonance likely 3–8% below 915 MHz
- Efficiency perhaps 40–55% rather than the 70%+ a well-grounded design would achieve
- Noticeable pattern asymmetry — range will depend on orientation

### The decision

This is precisely why most commercial 915 MHz LoRa boards — including the popular ESP32-S3 development boards built around the Heltec V3 reference design — use an **external whip antenna** on a u.FL or SMA connector rather than a PCB antenna.

At 915 MHz the physics pushes hard against integration:

- 78 mm of copper is a large fraction of a 60 mm board
- The board is too small to be a good ground plane
- LoRa's entire value proposition is *long range*, so sacrificing 3–5 dB of efficiency undermines the reason for choosing LoRa in the first place

**Contrast with 2.4 GHz:** the antenna needs 29 mm, fits in a single row with zero folds, and a 60 mm board is nearly twice λ/4 — a genuinely adequate ground plane. Everything that is marginal at 915 MHz is comfortable at 2.4 GHz.

> **This is the most valuable thing the tool teaches, and it is not a number it prints.** It is the pattern you notice after running several frequencies: PCB antennas are natural above roughly 2 GHz and progressively awkward below about 1 GHz. The tool makes that trend visible by letting you sweep frequency and watch the fold count and the fit warning respond.

If you have a 915 MHz LoRa board on your bench, look at how its antenna is implemented. If it uses a connector and a whip, the reasoning above is why.

---

## 21. Worked example: a 2.4 GHz BLE sensor

### The requirement

A Bluetooth Low Energy environmental sensor. 2440 MHz. Board 40 × 30 mm. 8 mm keepout at one end.

### The numbers

```
λ    = 299792.458 / 2440 = 122.866 mm
L    = 0.95 × 122.866/4  =  29.181 mm
```

With boardW = 40, tw = 0.5, clr = 0.3: m = 0.55, xMax = 39.45.

Starting at xShort ≈ 15 − 1.75 = 13.25 (using S = 6%):
first run available = 39.45 − 13.25 = 26.2 mm. Required is 29.18 mm, so it runs to the wall, folds once, and finishes 1.98 mm into the second row.

**Result: 2 rows, 1 fold.** Nearly a straight line.

### Sanity check against Section 12

λ/4 at 2440 MHz is 30.7 mm. The board is 40 mm — **larger than λ/4.** The ground plane is adequate.

Expect:

- Resonance within 1–3% of prediction
- Efficiency in the 55–70% range
- A reasonably symmetric pattern

This is a design that will very likely work close to first time. The contrast with Section 20 is the lesson.

### Practical notes

Place the antenna at a **corner**, with ground extending away from it in both directions. Keep the battery, any metal shield can, and the display well clear of the keepout — at 2.4 GHz "clear" means several millimetres, since λ is only 123 mm and small distances are electrically significant.

---

## 22. What happens after the tool: bench tuning

The tool produces a starting geometry. Here is the process that turns it into a working antenna.

### Equipment

A **vector network analyser (VNA)** measuring S11 — the fraction of incident power reflected back from the antenna. A NanoVNA costs under $100 and is entirely adequate for this. Professional instruments cost far more and are not necessary for tuning a single-band antenna.

### Step 1: measure as fabricated

Solder a coaxial pigtail to the feed and ground, connect the VNA, sweep across your band, and find the frequency of minimum S11 — the resonance dip.

### Step 2: interpret the result

| Observation | Cause | Fix |
|---|---|---|
| Dip below target f | Antenna too long | Trim the arm shorter |
| Dip above target f | Antenna too short | Add length (wire or copper tape) |
| Dip at correct f but shallow | Impedance mismatch | Adjust the match, not the length |
| No clear dip | Broken connection, or something metallic loading it | Investigate before adjusting anything |

The frequency correction is close to linear: if you measure 880 MHz and want 915 MHz, you need the antenna shorter by roughly the ratio 880/915 ≈ 0.962. So multiply L by 0.962, or equivalently set k from 0.95 to about 0.914 and regenerate.

### Step 3: adjust the match

Once resonance is correct, the depth of the S11 dip tells you about matching. A dip to −10 dB means 10% of power reflected — acceptable. −20 dB means 1% — excellent. Only −5 dB means about 32% reflected — a real problem.

Two ways to improve it:

**Move the short pin.** Section 6's whole point: this changes impedance without moving resonance. On a fabricated board that means a board revision — which is why getting it approximately right in the tool matters.

**Use the pi-network.** This is what the placeholder in the constraints file is for. Three unpopulated 0402 footprints — one series, two shunt — let you build an L, pi, or T matching network from stock components after measuring. Populate whichever two or three positions the measurement calls for.

Leaving that placeholder costs nothing and saves a board spin. It is the single most valuable line in the generated constraints file.

### Step 4: measure in the final assembly

**This is the step people skip, and it is the one that matters most.**

Everything detunes an antenna: the plastic enclosure, the battery, the PCB's own components, mounting screws, and a human hand. Shifts of 2–10% are routine.

Tune with the product fully assembled and in its intended orientation. An antenna tuned on a bare board and then sealed into a case will not be at the frequency you measured.

### Step 5: iterate

Two or three cycles is normal. Record k at each iteration; once you have a value that works for your board stack-up and enclosure, it transfers to future designs on the same platform. That is how experienced teams build up their own k values rather than starting from 0.95 each time.

---

## 23. Reading the tool's outputs like an engineer

A short guide to what to look at, and what should worry you.

### On the board preview

**Fold count.** 0–1 folds: excellent, close to a straight radiator. 2–3: acceptable, some efficiency loss. 4+: expect meaningful efficiency and bandwidth penalties; consider whether this band is right for a PCB antenna at all.

**The current gradient.** The trace is coloured by I(d). Note that the bright, high-current region near the short is where most radiation originates. If that region is folded back on itself, or crowded against the ground plane, you are cancelling exactly the part that does the work. Where possible, keep the first third of the arm straight and open.

**The fit warning.** If the layout does not fit, the tool names the smallest single change that fixes it. Take that seriously — a design that barely fits has no tolerance for manufacturing variation.

### On the standing-wave chart

**Where the tap marker sits.** Very close to the short (below about 3% of L) means very low impedance, which is hard to match well and sensitive to placement error. Far along (above about 20%) means high impedance and a narrow-bandwidth match. Most practical designs land between 5% and 15%.

**The shape does not change.** Confirm this for yourself: drag the short-pin slider and watch. The curves are fixed; only the marker moves. That is Section 6 in action, and being able to point at it and explain it is the difference between operating the tool and understanding it.

### On the length-vs-frequency chart

**The operating point.** Shows where your design sits on the L(f) curve.

**The shaded "won't fit" band.** Everything in that region requires more copper than your keepout can hold. Its boundary moves when you change board width or keepout height — which makes the trade-off between board area and frequency directly visible rather than something you have to work out.

---

## 24. Extending the tool

If you were to continue this project, these are the changes ordered by value gained per unit of effort.

**1. Microstrip effective permittivity.** Replace the blanket k with a proper calculation of εeff from trace width, substrate height, and εr using the standard Hammerstad equations. This converts one of k's biggest components from a guess into a calculation. Moderate effort, real accuracy gain.

**2. A ground plane correction.** Even a simple empirical correction based on published measurements — a lookup or curve fit from ground plane size in wavelengths to frequency shift — would be better than nothing, provided it is clearly labelled as empirical.

**3. Bandwidth estimation.** Q rises with meander density. A rough estimate of usable bandwidth from fold count and trace geometry would let users see the cost of folding directly rather than inferring it.

**4. Multi-band geometries.** Adding a second, shorter parasitic arm creates a dual-band antenna — the standard approach for 2.4/5 GHz Wi-Fi. A substantial extension.

**5. Export to other EDA tools.** Altium, Eagle, and Gerber formats would widen usefulness considerably. Mostly a formatting exercise, since the geometry is already computed.

**6. An actual EM solve.** openEMS is open source and scriptable. Exporting a geometry for it, running it offline, and importing the S11 result would close the loop between prediction and simulation. Large effort, but it would transform the tool from a calculator into a design environment.

---
---

# PART V — STUDY AIDS

---

## 25. Glossary

**Antenna efficiency** — Fraction of power delivered to the antenna that is radiated rather than dissipated as heat. PCB antennas: typically 30–70%.

**Balun** — Balanced-to-unbalanced transformer. Not needed for an IFA, which is inherently unbalanced.

**Bandwidth** — Frequency range over which the antenna meets its match specification, usually S11 < −10 dB. Meandering narrows it.

**Chip antenna** — Pre-manufactured ceramic antenna component. Smaller than a PCB antenna, costs money, still requires a good ground plane.

**Clearance** — Minimum copper-to-copper gap your manufacturer can reliably produce.

**Detuning** — Unwanted shift in resonant frequency caused by nearby objects.

**Dielectric constant (εr)** — How much a material slows electromagnetic waves relative to vacuum. FR-4 ≈ 4.4.

**Effective permittivity (εeff)** — The value a microstrip wave actually experiences, between 1 (air) and εr (substrate). Typically ~2.5–3.0 for FR-4.

**End effect** — Fringing capacitance at an open conductor end, making it electrically longer than physically. Main reason k < 1.

**Feed point** — Where the transmission line from the radio connects to the antenna.

**Footprint** — In PCB design, the copper and drill pattern for a component. Here, the antenna's copper geometry.

**FR-4** — Standard glass-epoxy PCB substrate. εr ≈ 4.4, thickness usually 1.6 mm.

**Fringing field** — Field that bulges outside the intended path, particularly at conductor ends.

**Ground plane** — Large copper area serving as electrical reference and, for a monopole or IFA, as the mirror that supplies the antenna's other half.

**IFA** — Inverted-F Antenna. A quarter-wave arm with a shorting pin to ground and a feed tapped between short and tip.

**Impedance (Z)** — Ratio of voltage to current, in ohms. Radio systems standardise on 50 Ω.

**Keepout** — Board region where copper is forbidden on all layers. The antenna's clear space.

**Match / matching network** — Making the antenna's impedance equal the system impedance; the components used to do so.

**Meander** — Folding a trace back and forth to fit more length in less area. Same as serpentining.

**Monopole** — Quarter-wave conductor over a ground plane. The ground plane's image completes the equivalent dipole.

**Pi network** — Matching network with one series and two shunt components. Flexible; usually left as unpopulated pads for post-fabrication tuning.

**Q factor** — Ratio of stored to dissipated energy per cycle. High Q means sharp resonance and narrow bandwidth.

**Radiation pattern** — Directional distribution of radiated power.

**Resonance** — Condition where reactance is zero and the structure readily supports standing-wave current.

**S11 / return loss** — Fraction of incident power reflected back from the antenna, in dB. More negative is better. −10 dB is the usual acceptance threshold.

**Standing wave** — Fixed spatial pattern of current and voltage on a resonant structure.

**SWR** — Standing Wave Ratio. Another expression of match quality. 1:1 is perfect; below 2:1 is usually acceptable.

**Trace** — A copper conductor on a PCB.

**u.FL / SMA** — Coaxial connectors for attaching external antennas.

**VNA** — Vector Network Analyser. Instrument that measures S-parameters; the essential tool for antenna tuning.

**Whip** — External wire or rod antenna.

---

## 26. Equation reference sheet

### Wavelength
```
λ = c / f                       c = 299,792,458 m/s
λ (mm) = 299792.458 / f (MHz)
```

### Resonant length
```
L = k · λ/4                     k = 0.95 default, range 0.90–0.97
```

### Standing wave (d measured from the shorting pin)
```
I(d) = cos( π/2 · d/L )         current: 1.0 at short, 0 at tip
V(d) = sin( π/2 · d/L )         voltage: 0 at short, 1.0 at tip
Z(d) ∝ tan( π/2 · d/L )         impedance: 0 at short, ∞ at tip
```

### Layout geometry
```
m = clr + tw/2                  routing margin (centreline to boundary)
p = max(2·tw, 1.0)              fold pitch between rows
rows ≈ floor((koH − 2m)/p) + 1  rows available in the keepout
copper per row = boardW − 2m
Σ segment lengths = L           invariant, checked live
```

### Quick reference values (k = 0.95)

| f (MHz) | λ (mm) | λ/4 (mm) | L (mm) |
|---|---|---|---|
| 433.92 | 690.9 | 172.7 | 164.1 |
| 868 | 345.4 | 86.3 | 82.0 |
| 915 | 327.6 | 81.9 | 77.8 |
| 1575.42 | 190.3 | 47.6 | 45.2 |
| 2400 | 124.9 | 31.2 | 29.7 |
| 2440 | 122.9 | 30.7 | 29.2 |
| 5800 | 51.7 | 12.9 | 12.3 |

---

## 27. Likely questions, with answers

Questions a reviewer, examiner, or demo audience is likely to ask.

**Q: Why doesn't the resonant frequency change when I move the short pin?**
Because L is measured from the short to the open tip, and the layout algorithm re-lays the arm from the new short position while walking out exactly L millimetres. The short-to-tip distance is invariant by construction. What changes is S, the distance from short to the fixed feed, which sets where the feed taps the standing wave — and that is impedance, not frequency.

**Q: Why is there no SWR or impedance number?**
A trustworthy impedance figure requires solving Maxwell's equations over a 3D mesh — an EM solver, not a formula. Printing a plausible-looking number computed from a simplified model would be worse than printing none, because users would trust it. Instead the tool shows the standing wave and marks the tap point, which is the honest, geometric version of the same information.

**Q: Where does 0.95 come from?**
It is empirical, and it is a bucket. It absorbs end-effect fringing capacitance, dielectric loading from the substrate, the uncounted vertical stub lengths, and ground plane proximity. The 0.90–0.97 range covers typical FR-4 designs. It is exposed as an editable field because it is the primary tuning handle after the first measurement.

**Q: Why doesn't the ground plane size affect the calculation?**
It should — that is the tool's main stated limitation. The ground plane is genuinely half the radiator, and shrinking it detunes the antenna. But the relationship is not closed-form; it depends on plane shape, aspect ratio, antenna position, and nearby conductors, and capturing it requires an EM solve. The parameter is recorded and exported, and the limitation is stated in the generated constraints file so it travels with the design.

**Q: What if the antenna doesn't fit?**
The tool detects this and names the smallest single change that resolves it — increase keepout height, increase board width, or raise the frequency. It does not silently produce an invalid layout.

**Q: How accurate is it?**
It produces a starting geometry, not a final answer. Expect to be within roughly 5–10% of target on the first fabrication, and plan for one to three tuning iterations. Accuracy is best when the ground plane comfortably exceeds λ/4 and the fold count is low.

**Q: Why inline core.js instead of loading it with a script tag?**
So `index.html` works when opened directly from disk — no web server, no CORS issues, no network. The inlined block is kept byte-for-byte identical to the standalone file, which is verifiable mechanically, so the test suite genuinely tests the code the application runs.

**Q: Why does the derivation update slower than the preview?**
Deliberate. The preview and charts redraw on every input event at about 0.9 ms each — smooth. The derivation text and generated files are debounced 450 ms because they involve string building and are not useful mid-drag.

**Q: Could this be used for a real product?**
As a first-pass geometry generator, yes — that is exactly its intended role. It would not replace EM simulation for a design going to certification. The workflow it fits: generate geometry here, fabricate, measure on a VNA, adjust k, iterate.

**Q: What is the most important thing the tool teaches?**
That resonance and matching are independent, and that the inverted-F geometry is what buys you that independence. Secondarily — and this only becomes visible after sweeping frequency a few times — that PCB antennas are natural above roughly 2 GHz and increasingly awkward below 1 GHz.

---

## 28. Further reading

**Books**

*Antenna Theory: Analysis and Design*, Constantine Balanis — the standard graduate reference. Chapters on monopoles and image theory are directly relevant.

*The ARRL Antenna Book*, American Radio Relay League — practical, accessible, strong on measurement and tuning.

*RF Circuit Design*, Chris Bowick — good on matching networks and the pi-network topology.

**Application notes**

Texas Instruments AN058, *Antenna Selection Guide* — practical comparison of PCB, chip, and whip antennas with measured data.

Silicon Labs AN853, *PCB Design Guidelines for Sub-GHz Applications* — ground plane and layout guidance specifically for the bands where PCB antennas are marginal.

Espressif *ESP32 Hardware Design Guidelines* — the antenna and keepout sections show a production IFA implementation and its mounting constraints.

**Tools**

*openEMS* — free, open-source FDTD electromagnetic solver. Scriptable from Octave/Python.

*NanoVNA* — inexpensive vector network analyser, entirely adequate for single-band antenna tuning.

*KiCad* — free EDA suite; the target of this tool's footprint export.

---

## Document summary

The single most important idea in this document:

> **An inverted-F antenna has two independent controls. Its length from the shorting pin to the open tip sets the frequency it resonates at. The position of the feed tap along that length sets the impedance the radio sees. Changing one does not change the other, and that independence is what makes the geometry so useful.**

The second most important idea:

> **The tool models geometry exactly and electromagnetics approximately. It is a layout generator with a physics-informed length calculation. Used as a starting point for bench tuning it is genuinely useful; used as an oracle it will mislead. The generated constraints file states this explicitly so the caveat travels with the design.**

---

*Companion to the PCB Inverted-F Antenna Designer — TRN553 Build-a-Tool, Seneca Polytechnic.*
*Reference tool studied for structure: kurtisperrie, "TDR Simulator," https://kurtisperrie.github.io/TDRSimulator.github.io/*

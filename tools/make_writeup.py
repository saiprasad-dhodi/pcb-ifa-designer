# One-page write-up for the TRN553 Build-a-Tool deliverable.
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, HRFlowable, KeepTogether)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

F = "C:/Windows/Fonts/"
pdfmetrics.registerFont(TTFont("Ar",   F + "arial.ttf"))
pdfmetrics.registerFont(TTFont("ArB",  F + "arialbd.ttf"))
pdfmetrics.registerFont(TTFont("ArI",  F + "ariali.ttf"))
pdfmetrics.registerFont(TTFont("Mono", F + "consola.ttf"))
pdfmetrics.registerFontFamily("Ar", normal="Ar", bold="ArB", italic="ArI", boldItalic="ArB")

INK    = colors.HexColor("#1a1917")
DIM    = colors.HexColor("#6f6c65")
ACCENT = colors.HexColor("#b1502f")
RULE   = colors.HexColor("#d8d3c6")
PANEL  = colors.HexColor("#f6f4ee")

OUT = r"C:\Users\saipd\Desktop\TRN -project\TRN553_IFA_Designer_writeup.pdf"

doc = SimpleDocTemplate(
    OUT, pagesize=letter,
    leftMargin=16 * mm, rightMargin=16 * mm,
    topMargin=11 * mm, bottomMargin=9 * mm,
    title="PCB Inverted-F Antenna Designer - TRN553 Write-up",
    author="TRN553 Build-a-Tool",
)

title = ParagraphStyle("title", fontName="ArB", fontSize=15.5, leading=18, textColor=INK)
meta  = ParagraphStyle("meta",  fontName="Ar",  fontSize=8,   leading=10.5, textColor=DIM)
head  = ParagraphStyle("head",  fontName="ArB", fontSize=8.6, leading=10.5, textColor=ACCENT,
                       spaceBefore=5, spaceAfter=2)
body  = ParagraphStyle("body",  fontName="Ar",  fontSize=8.7, leading=10.5, textColor=INK)
item  = ParagraphStyle("item",  fontName="Ar",  fontSize=8.7, leading=10.5, textColor=INK,
                       leftIndent=11, firstLineIndent=-11, spaceAfter=1.6)
eq    = ParagraphStyle("eq",    fontName="Mono", fontSize=8.3, leading=11.6, textColor=INK)
small = ParagraphStyle("small", fontName="Ar",  fontSize=7.7, leading=9.5, textColor=DIM,
                       leftIndent=11, firstLineIndent=-11, spaceAfter=1.5)

S = []

S.append(Paragraph("PCB Inverted-F Antenna Designer", title))
S.append(Spacer(1, 2.5))
S.append(Paragraph(
    "TRN553 Build-a-Tool &nbsp;·&nbsp; Seneca Polytechnic &nbsp;·&nbsp; "
    "<b>Umair Hashmi</b> &nbsp;·&nbsp; <b>[Student ID]</b><br/>"
    "Live tool: <b>[paste your public link here]</b>", meta))
S.append(Spacer(1, 4))
S.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=1))


def section(name):
    S.append(Paragraph(name, head))


section("CONCEPT")
S.append(Paragraph(
    "The tool designs a printed inverted-F antenna (IFA) &mdash; an antenna etched into a circuit board rather "
    "than bought as a component. It shows how a quarter-wavelength of copper sets the resonant frequency, how "
    "that length is folded to fit a board far shorter than the wave, and &mdash; the central teaching point "
    "&mdash; how sliding the grounded shorting pin changes the impedance match <i>without</i> moving the "
    "resonant frequency. It exports a working KiCad footprint and a fabrication constraints sheet.", body))

section("KEY EQUATIONS")
eq_tbl = Table([[Paragraph(
    "&#955; = c / f<br/>"
    "L = k &#183; &#955;/4 &nbsp;&nbsp;&nbsp;&nbsp; k = 0.95, empirical end-effect correction (0.90&#8211;0.97 typical)<br/>"
    "I(d) = cos(&#960;/2 &#183; d/L) &nbsp;&nbsp; V(d) = sin(&#960;/2 &#183; d/L) &nbsp;&nbsp; d measured from the short pin<br/>"
    "m = clearance + trace/2 &nbsp;&nbsp;&nbsp;&nbsp; p = max(2 &#183; trace, 1.0 mm)<br/>"
    "folded path length = L, regardless of fold count", eq)]],
    colWidths=[doc.width])
eq_tbl.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), PANEL),
    ("BOX",        (0, 0), (-1, -1), 0.6, RULE),
    ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ("TOPPADDING",  (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
]))
S.append(eq_tbl)


# ---- figure: the geometry on the left, the standing wave it produces on the right ----
import math
from reportlab.graphics.shapes import Drawing, Rect, Line, PolyLine, String, Circle, Group

FW, FH = doc.width, 102.0
d = Drawing(FW, FH)
GND   = colors.HexColor("#dedad0")
COPP  = colors.HexColor("#b1502f")
BLUE  = colors.HexColor("#2b6cb0")
LBL   = colors.HexColor("#55524c")
half  = (FW - 26) / 2.0

def lbl(g, x, y, s, size=6.4, col=LBL, anchor="start", font="Ar"):
    g.add(String(x, y, s, fontName=font, fontSize=size, fillColor=col, textAnchor=anchor))

# ---------- panel A: board geometry ----------
A = Group()
bx0, bx1, by0, by1 = 4, half - 4, 13, 84
ygnd = 45
A.add(Rect(bx0, by0, bx1 - bx0, by1 - by0, fillColor=colors.white, strokeColor=RULE, strokeWidth=0.6))
A.add(Rect(bx0, by0, bx1 - bx0, ygnd - by0, fillColor=GND, strokeColor=None))
A.add(Rect(bx0 + 3, ygnd + 2, bx1 - bx0 - 6, by1 - ygnd - 5, fillColor=None,
           strokeColor=colors.HexColor("#9c988e"), strokeWidth=0.5, strokeDashArray=[2, 1.6]))
xs, xf = bx0 + 34, bx0 + 52                       # short pin, feed pad
r0, r1 = ygnd + 12, ygnd + 25                     # two arm rows
A.add(Line(xs, ygnd, xs, r0, strokeColor=COPP, strokeWidth=1.5))   # short stub
A.add(Line(xf, ygnd, xf, r0, strokeColor=COPP, strokeWidth=1.5))   # feed stub
A.add(Line(xs, r0, bx1 - 8, r0, strokeColor=COPP, strokeWidth=1.5))
A.add(Line(bx1 - 8, r0, bx1 - 8, r1, strokeColor=COPP, strokeWidth=1.5))
A.add(Line(bx1 - 8, r1, bx0 + 96, r1, strokeColor=COPP, strokeWidth=1.5))
A.add(Circle(bx0 + 96, r1, 2.6, fillColor=None, strokeColor=COPP, strokeWidth=0.8))
A.add(Rect(xs - 2.4, ygnd - 2.4, 4.8, 4.8, fillColor=colors.HexColor("#2f9c72"), strokeColor=None))
A.add(Rect(xf - 2.4, ygnd - 2.4, 4.8, 4.8, fillColor=BLUE, strokeColor=None))
A.add(Line(xs, ygnd - 11, xf, ygnd - 11, strokeColor=LBL, strokeWidth=0.5))
A.add(Line(xs, ygnd - 13.5, xs, ygnd - 8.5, strokeColor=LBL, strokeWidth=0.5))
A.add(Line(xf, ygnd - 13.5, xf, ygnd - 8.5, strokeColor=LBL, strokeWidth=0.5))
lbl(A, (xs + xf) / 2, ygnd - 21, "S", 6.6, LBL, "middle", "Mono")
lbl(A, bx0 + 6, by1 - 9, "KEEPOUT", 5.8)
lbl(A, bx1 - 6, by0 + 5, "GROUND PLANE", 5.8, LBL, "end")
lbl(A, xs - 12, r0 + 5, "short", 6, colors.HexColor("#2f9c72"))
lbl(A, xf + 4, r0 + 5, "feed", 6, BLUE)
lbl(A, bx0 + 88, r1 + 6, "open tip", 6, COPP, "end")
lbl(A, bx0, by1 + 6, "Geometry: short → tip always measures L = k·λ/4", 6.6, INK)
d.add(A)

# ---------- panel B: the standing wave on that arm ----------
B = Group()
ox = half + 22
px0, px1, py0, py1 = ox + 26, ox + half - 12, 21, 79
B.add(Rect(px0, py0, px1 - px0, py1 - py0, fillColor=PANEL, strokeColor=None))
for fy in (0.0, 0.5, 1.0):
    yy = py0 + fy * (py1 - py0)
    B.add(Line(px0, yy, px1, yy, strokeColor=RULE, strokeWidth=0.5))
    lbl(B, px0 - 4, yy - 2, "%.1f" % fy, 5.6, LBL, "end", "Mono")
ipts, vpts = [], []
for i in range(61):
    t = i / 60.0
    xx = px0 + t * (px1 - px0)
    ipts += [xx, py0 + math.cos(math.pi / 2 * t) * (py1 - py0)]
    vpts += [xx, py0 + math.sin(math.pi / 2 * t) * (py1 - py0)]
B.add(PolyLine(vpts, strokeColor=BLUE, strokeWidth=1.1, strokeDashArray=[2.5, 2]))
B.add(PolyLine(ipts, strokeColor=COPP, strokeWidth=1.3))
tapT = 0.06
tapX = px0 + tapT * (px1 - px0)
tapY = py0 + math.cos(math.pi / 2 * tapT) * (py1 - py0)
B.add(Line(tapX, py0, tapX, py1, strokeColor=LBL, strokeWidth=0.5, strokeDashArray=[1.5, 1.5]))
B.add(Circle(tapX, tapY, 2.4, fillColor=COPP, strokeColor=colors.white, strokeWidth=0.8))
lbl(B, tapX + 5, py1 - 8, "feed tap", 6, INK)
lbl(B, px0 + 4, py0 - 8, "short", 5.8, LBL)
lbl(B, px1, py0 - 8, "open tip", 5.8, LBL, "end")
lbl(B, px0 + (px1 - px0) * 0.55, py0 + 26, "current", 6, COPP, "middle", "Mono")
lbl(B, px0 + (px1 - px0) * 0.78, py0 + 44, "voltage", 6, BLUE, "middle", "Mono")
lbl(B, ox, py1 + 12, "Standing wave: where the feed taps it sets the match", 6.6, INK)
d.add(B)
S.append(d)
S.append(Paragraph(
    "<b>Figure 1.</b> Left: the folded arm. The resonant length L is measured from the short-pin junction to "
    "the open tip, so moving the short (spacing S) re-lays the arm and leaves L unchanged. Right: the "
    "idealized current and voltage standing wave on that arm &mdash; sliding the short moves the feed&rsquo;s "
    "tap point along a curve that itself never changes shape. Both views are live in the tool.",
    ParagraphStyle("cap", fontName="Ar", fontSize=7.4, leading=9.4, textColor=DIM, spaceBefore=1)))

section("HOW IT WORKS")
S.append(Paragraph(
    "Frequency (300&#8211;3000 MHz, by slider, typed value, or ISM-band preset) gives &#955;, and "
    "L = k&#183;&#955;/4 is the arm length measured from the short-pin junction to the open tip. The arm is laid "
    "out inside a copper-free keepout strip: it runs to the side margin, folds 180&#176;, and repeats until "
    "exactly L millimetres of copper have been placed. If it runs out of keepout the tool says so and offers "
    "the smallest single change that fixes it (keepout height, board width, or frequency). The short-pin "
    "control sets spacing S as a percentage of L; because the feed pad is fixed on the board and the short "
    "moves, the short&#8594;tip distance is always exactly L, so resonance is invariant under that control "
    "while the feed taps the standing wave at a different point &mdash; which is what changes the match. Board "
    "width, ground height, keepout, trace width, clearance and k are all exposed and feed the same pipeline.", body))

section("DESIGN CHOICES")
S.append(Paragraph(
    "1.&nbsp;&nbsp;<b>No impedance or SWR number is printed.</b> A trustworthy figure needs a real "
    "electromagnetic solver; a plausible-looking fake would be worse than none. Instead the current standing "
    "wave is drawn along the arm and the feed tap is marked on it, so match behaviour is shown as normalized "
    "geometry rather than invented ohms.", item))
S.append(Paragraph(
    "2.&nbsp;&nbsp;<b>One source of truth.</b> All mathematics lives in pure functions in "
    "<font name='Mono' size='8'>core.js</font>, inlined byte-identically into "
    "<font name='Mono' size='8'>index.html</font>; "
    "<font name='Mono' size='8'>tests.js</font> runs 43 assertions against those same functions, in Node or "
    "in the browser console. A &ldquo;Verify the working&rdquo; panel prints the full derivation with live "
    "numbers and checks that the summed segment lengths still equal L.", item))
S.append(Paragraph(
    "3.&nbsp;&nbsp;<b>Everything is drawn to scale.</b> The preview SVG uses 1 user unit = 1 mm, so stroke "
    "widths on screen are real trace widths and the geometry can be measured directly off the drawing.", item))
S.append(Paragraph(
    "4.&nbsp;&nbsp;<b>Live versus settled updates.</b> The preview, readout and both charts redraw on every "
    "input event (~0.9 ms each); the step-by-step derivation and the generated file text wait 450 ms for the "
    "values to settle, so dragging a slider quickly cannot thrash the page.", item))

section("LIMITATION")
S.append(Paragraph(
    "Ground-plane size is recorded in the exported files but does not enter the length calculation. In a real "
    "inverted-F the ground plane acts as the other half of the radiator, and shrinking it detunes the antenna "
    "measurably &mdash; yet this model returns the same arm length for a 20 mm board and a 100 mm one, which is "
    "not physically true. k is treated as absorbing all board effects, including substrate permittivity and "
    "thickness, which are recorded but unused. A design produced here is a well-reasoned starting geometry for "
    "bench tuning, not a final answer.", body))

S.append(Spacer(1, 5))
S.append(HRFlowable(width="100%", thickness=0.6, color=RULE, spaceAfter=4))

S.append(Paragraph(
    "[1]&nbsp;&nbsp;Umair Hashmi, course lecture material, TRN553, Seneca Polytechnic.", small))
S.append(Paragraph(
    "[2]&nbsp;&nbsp;kurtisperrie, &ldquo;TDR Simulator,&rdquo; TRN553 Build-a-Tool, Seneca Polytechnic. "
    "Available: https://kurtisperrie.github.io/TDRSimulator.github.io/ [Accessed 5 Aug. 2026]. Studied as the "
    "structural reference for this tool &mdash; the numbered how-to strip, the parameter panel with inline "
    "formulas, the live readout, and the references / AI-disclosure pairing all follow its layout.", small))
S.append(Paragraph(
    "<b>AI use:</b>&nbsp;&nbsp;Claude (Anthropic) generated the HTML, CSS and JavaScript from a written "
    "specification I authored. Every equation and test value was verified against [1] and by hand "
    "calculation; tests.js is the verification artifact and can be run live during the demo.", small))

doc.build(S)
print("wrote", OUT)

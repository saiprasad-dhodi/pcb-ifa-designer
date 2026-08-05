# Minimal Markdown -> PDF renderer for the IFA study guide.
# Handles: headings, paragraphs, bold/italic/code spans, tables, bullet and
# numbered lists, fenced code, blockquotes, and horizontal rules.
import io, re
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, HRFlowable, PageBreak, KeepTogether)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

F = "C:/Windows/Fonts/"
pdfmetrics.registerFont(TTFont("Ar",  F + "arial.ttf"))
pdfmetrics.registerFont(TTFont("ArB", F + "arialbd.ttf"))
pdfmetrics.registerFont(TTFont("ArI", F + "ariali.ttf"))
pdfmetrics.registerFont(TTFont("Mono",  F + "consola.ttf"))
pdfmetrics.registerFont(TTFont("MonoB", F + "consolab.ttf"))
pdfmetrics.registerFontFamily("Ar", normal="Ar", bold="ArB", italic="ArI", boldItalic="ArB")

INK    = colors.HexColor("#1a1917")
DIM    = colors.HexColor("#6f6c65")
ACCENT = colors.HexColor("#b1502f")
RULE   = colors.HexColor("#d8d3c6")
PANEL  = colors.HexColor("#f6f4ee")
HEAD   = colors.HexColor("#efece3")

SRC = r"C:\Users\saipd\Desktop\TRN -project\IFA_Study_Guide.md"
OUT = r"C:\Users\saipd\Desktop\TRN -project\IFA_Study_Guide.pdf"

# Glyphs Arial/Consolas lack, mapped to safe equivalents.
SUBS = {"\u207b": "-", "\u2713": "[ok]", "\u2717": "[x]", "\u2261": "=",
        "\u221d": "prop. to", "\u2265": ">=", "\u2264": "<="}


def sub_glyphs(t):
    for a, b in SUBS.items():
        t = t.replace(a, b)
    return t


h1 = ParagraphStyle("h1", fontName="ArB", fontSize=19, leading=23, textColor=INK,
                    spaceBefore=6, spaceAfter=8)
h2 = ParagraphStyle("h2", fontName="ArB", fontSize=13.5, leading=17, textColor=ACCENT,
                    spaceBefore=15, spaceAfter=5)
h3 = ParagraphStyle("h3", fontName="ArB", fontSize=10.5, leading=13.5, textColor=INK,
                    spaceBefore=10, spaceAfter=3)
body = ParagraphStyle("body", fontName="Ar", fontSize=9.4, leading=13.2, textColor=INK,
                      spaceAfter=5)
bullet = ParagraphStyle("bullet", parent=body, leftIndent=14, firstLineIndent=-10,
                        spaceAfter=2.5)
quote = ParagraphStyle("quote", fontName="Ar", fontSize=9.4, leading=13.4, textColor=INK,
                       leftIndent=10, rightIndent=6, spaceBefore=3, spaceAfter=3)
code = ParagraphStyle("code", fontName="Mono", fontSize=8.2, leading=10.8, textColor=INK)
cellS = ParagraphStyle("cell", fontName="Ar", fontSize=8.5, leading=11, textColor=INK)
cellH = ParagraphStyle("cellh", fontName="ArB", fontSize=8.5, leading=11, textColor=INK)


def inline(t):
    """Escape XML, then apply markdown inline markup."""
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = re.sub(r"`([^`]+)`", r"<font name='Mono' size='8.6'>\1</font>", t)
    # bold first and non-greedy, so a **span containing *italics*** still matches
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t, flags=re.S)
    t = re.sub(r"\*(.+?)\*", r"<i>\1</i>", t, flags=re.S)
    return t


def make_table(rows):
    head, data = rows[0], rows[1:]
    ncol = len(head)
    tbl = [[Paragraph(inline(c), cellH) for c in head]]
    for r in data:
        r = (r + [""] * ncol)[:ncol]
        tbl.append([Paragraph(inline(c), cellS) for c in r])
    # size columns by their content, clamped so nothing collapses or hogs
    avail = doc.width
    span = []
    for c in range(ncol):
        longest = max([len(head[c])] + [len(r[c]) for r in data if c < len(r)])
        span.append(max(longest, 6) ** 0.72)          # damped: long cells wrap
    tot = sum(span)
    lo, hi = avail * 0.07, avail * 0.46
    widths = [min(max(avail * s / tot, lo), hi) for s in span]
    widths = [w * avail / sum(widths) for w in widths]   # renormalise to fit
    t = Table(tbl, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HEAD),
        ("LINEBELOW", (0, 0), (-1, 0), 0.7, RULE),
        ("LINEBELOW", (0, 1), (-1, -2), 0.3, colors.HexColor("#e8e5dc")),
        ("BOX", (0, 0), (-1, -1), 0.6, RULE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ]))
    return t


doc = SimpleDocTemplate(
    OUT, pagesize=letter,
    leftMargin=19 * mm, rightMargin=19 * mm,
    topMargin=16 * mm, bottomMargin=15 * mm,
    title="PCB Inverted-F Antennas - A Complete Study Guide",
    author="Umair Hashmi")

lines = sub_glyphs(io.open(SRC, encoding="utf-8").read()).split("\n")
S = []
i = 0
while i < len(lines):
    ln = lines[i]

    # fenced code
    if ln.startswith("```"):
        i += 1
        buf = []
        while i < len(lines) and not lines[i].startswith("```"):
            buf.append(lines[i]); i += 1
        i += 1
        inner = [Paragraph(
            (l.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
              .replace(" ", "&nbsp;")) or "&nbsp;", code) for l in buf]
        t = Table([[inner]], colWidths=[doc.width])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), PANEL),
            ("BOX", (0, 0), (-1, -1), 0.5, RULE),
            ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
        S += [Spacer(1, 3), t, Spacer(1, 6)]
        continue

    # table
    if ln.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i + 1]):
        rows = []
        while i < len(lines) and lines[i].startswith("|"):
            if not re.match(r"^\|[\s:|-]+\|$", lines[i]):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
            i += 1
        S += [Spacer(1, 3), make_table(rows), Spacer(1, 8)]
        continue

    st = ln.strip()

    if st == "---":
        S.append(HRFlowable(width="100%", thickness=0.7, color=RULE,
                            spaceBefore=8, spaceAfter=8)); i += 1; continue
    if not st:
        i += 1; continue

    if st.startswith("# "):
        S.append(Paragraph(inline(st[2:]), h1)); i += 1; continue
    if st.startswith("## "):
        S.append(Paragraph(inline(st[3:]), h2)); i += 1; continue
    if st.startswith("### "):
        S.append(Paragraph(inline(st[4:]), h3)); i += 1; continue

    if st.startswith("> "):
        buf = []
        while i < len(lines) and lines[i].strip().startswith("> "):
            buf.append(lines[i].strip()[2:]); i += 1
        t = Table([[Paragraph(inline(" ".join(buf)), quote)]], colWidths=[doc.width])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), PANEL),
            ("LINEBEFORE", (0, 0), (0, -1), 2.5, ACCENT),
            ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
        S += [Spacer(1, 4), t, Spacer(1, 7)]
        continue

    m = re.match(r"^(\d+)\.\s+(.*)$", st)
    if st.startswith("- ") or m:
        txt = ("&bull;&nbsp;&nbsp;" + inline(st[2:])) if not m else \
              (m.group(1) + ".&nbsp;&nbsp;" + inline(m.group(2)))
        S.append(Paragraph(txt, bullet)); i += 1; continue

    # paragraph: gather until blank or a new block marker
    buf = [st]
    i += 1
    while i < len(lines):
        n = lines[i].strip()
        if (not n or n.startswith(("#", "-", ">", "|", "```", "---"))
                or re.match(r"^\d+\.\s", n)):
            break
        buf.append(n); i += 1
    S.append(Paragraph(inline(" ".join(buf)), body))

doc.build(S)
print("wrote", OUT)

"""Build the organizer-facing PDF from the report Markdown and figures."""
from pathlib import Path
import html
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, Image, KeepTogether, LongTable, PageTemplate,
    PageBreak, Paragraph, Spacer, TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "Limitless_Research_and_Build_Report.md"
OUTPUT = ROOT / "Pookie_Blinders_Team_117_Round_2_Report.pdf"
PAGE_W, PAGE_H = letter
LEFT, RIGHT, TOP, BOTTOM = 0.72*inch, 0.72*inch, 0.68*inch, 0.62*inch
CONTENT_W = PAGE_W-LEFT-RIGHT
INK = colors.HexColor("#1C2430")
MUTED = colors.HexColor("#5F6E7E")
NAVY = colors.HexColor("#233B5D")
GRID = colors.HexColor("#D9DEE6")
PALE = colors.HexColor("#F3F6FA")


def inline_markup(text):
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r'<font name="Courier" size="8.7">\1</font>', text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", text)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<link href="\2" color="#2867A5">\1</link> <font size="8">(\2)</font>', text)
    return text


def styles():
    font_root = Path("C:/Windows/Fonts")
    pdfmetrics.registerFont(TTFont("Arial", str(font_root / "arial.ttf")))
    pdfmetrics.registerFont(TTFont("Arial-Bold", str(font_root / "arialbd.ttf")))
    pdfmetrics.registerFont(TTFont("Arial-Italic", str(font_root / "ariali.ttf")))
    pdfmetrics.registerFont(TTFont("Arial-BoldItalic", str(font_root / "arialbi.ttf")))
    pdfmetrics.registerFontFamily("Arial", normal="Arial", bold="Arial-Bold", italic="Arial-Italic", boldItalic="Arial-BoldItalic")
    s = getSampleStyleSheet()
    s.add(ParagraphStyle(name="BodyR", parent=s["BodyText"], fontName="Arial", fontSize=10.5,
                         leading=13.0, textColor=INK, spaceAfter=6, alignment=TA_LEFT,
                         splitLongWords=1, allowWidows=0, allowOrphans=0))
    s.add(ParagraphStyle(name="TitleR", parent=s["Title"], fontName="Arial-Bold", fontSize=27,
                         leading=32, textColor=colors.black, alignment=TA_CENTER, spaceAfter=18))
    s.add(ParagraphStyle(name="SubR", parent=s["BodyText"], fontName="Arial-Bold", fontSize=15,
                         leading=19, textColor=INK, alignment=TA_CENTER, spaceAfter=10))
    s.add(ParagraphStyle(name="H1R", parent=s["Heading1"], fontName="Arial-Bold", fontSize=16,
                         leading=20, textColor=colors.black, spaceBefore=13, spaceAfter=7,
                         keepWithNext=True))
    s.add(ParagraphStyle(name="H2R", parent=s["Heading2"], fontName="Arial-Bold", fontSize=12.5,
                         leading=16, textColor=colors.black, spaceBefore=10, spaceAfter=5,
                         keepWithNext=True))
    s.add(ParagraphStyle(name="H3R", parent=s["Heading3"], fontName="Arial-Bold", fontSize=11,
                         leading=14, textColor=colors.black, spaceBefore=8, spaceAfter=4,
                         keepWithNext=True))
    s.add(ParagraphStyle(name="TableR", parent=s["BodyText"], fontName="Arial", fontSize=8.2,
                         leading=10.0, textColor=INK, spaceAfter=0, splitLongWords=1))
    s.add(ParagraphStyle(name="TableHeadR", parent=s["TableR"], fontName="Arial-Bold",
                         textColor=colors.white))
    s.add(ParagraphStyle(name="CaptionR", parent=s["BodyText"], fontName="Arial-Italic",
                         fontSize=8.5, leading=10, textColor=MUTED, alignment=TA_CENTER,
                         spaceBefore=3, spaceAfter=9))
    s.add(ParagraphStyle(name="BulletR", parent=s["BodyR"], leftIndent=16, firstLineIndent=-10,
                         bulletIndent=0, spaceAfter=4))
    s.add(ParagraphStyle(name="CoverMetaR", parent=s["BodyText"], fontName="Arial", fontSize=12,
                         leading=18, textColor=INK, alignment=TA_CENTER, spaceAfter=8))
    s.add(ParagraphStyle(name="EquationR", parent=s["BodyText"], fontName="Arial-Italic", fontSize=11.5,
                         leading=18, textColor=INK, alignment=TA_CENTER, spaceBefore=4, spaceAfter=9))
    return s


EQUATIONS = {
    "skill_rate": "p<sub>kg</sub> = (∑<sub>i = 1</sub><super>|E<sub>g</sub>|</super> x<sub>ik</sub>) ⁄ |E<sub>g</sub>|",
    "wilson": "CI<sub>95%</sub> = [p̂ + z<super>2</super>⁄(2n) ± z√(p̂(1 − p̂)⁄n + z<super>2</super>⁄(4n<super>2</super>))] ⁄ [1 + z<super>2</super>⁄n]",
    "weight_and_count": "n<sub>h</sub> = ∑<sub>i ∈ h</sub> 1  W<sub>h</sub> = ∑<sub>i ∈ h</sub> w<sub>i</sub>",
    "trait_difference": "Δ<sub>k</sub> = z̄<sub>1k</sub> − z̄<sub>0k</sub>",
    "point_biserial": "r<sub>pb</sub> = ((M<sub>1</sub> − M<sub>0</sub>) ⁄ s<sub>z</sub>) √(n<sub>1</sub>n<sub>0</sub> ⁄ n<super>2</super>)",
    "cohen_d": "d = Δ<sub>k</sub> ⁄ s<sub>p</sub>",
    "pooled_sd": "s<sub>p</sub> = √[((n<sub>1</sub> − 1)s<sub>1</sub><super>2</super> + (n<sub>0</sub> − 1)s<sub>0</sub><super>2</super>) ⁄ (n<sub>1</sub> + n<sub>0</sub> − 2)]",
    "engine_demand": "M1: D<sub>kg</sub> = 100 · m<sub>kg</sub> ⁄ |E<sub>g</sub>|",
    "engine_rank": "M2: R<sub>kg</sub> = 100 · PercentileRank({p<sub>jg</sub> : j in K})",
    "engine_stability": "M3: S<sub>k</sub> = 100 · ∑<sub>s = 1</sub><super>|S|</super> 1[rank<sub>s</sub>(k) ≤ K] ⁄ |S|",
    "engine_coverage": "M4: C<sub>g</sub> = 100 · U<sub>g</sub> ⁄ N<sub>g</sub>",
    "engine_extraction": "M5: Precision = TP ⁄ (TP + FP)<br/>Recall = TP ⁄ (TP + FN)<br/>F<sub>1</sub> = 2 · Precision · Recall ⁄ (Precision + Recall)",
    "engine_weight": "M6: W<sub>h</sub> = ∑<sub>i in h</sub> w<sub>i</sub>; n<sub>h</sub> = |h|<br/>W<sub>h,−max</sub> = W<sub>h</sub> − max<sub>i in h</sub> w<sub>i</sub>",
    "jaccard": "J(A, B) = |A ∩ B| ⁄ |A ∪ B|",
    "sql_rate_example": "p̂ = 915 ⁄ 15,840 = 0.0578 = 5.78%",
    "weight_concentration": "C<sub>w</sub> = (∑<sub>i</sub> w<sub>i</sub>)<super>2</super> ⁄ ∑<sub>i</sub> w<sub>i</sub><super>2</super>",
}


def footer(canvas, doc):
    canvas.saveState()
    if doc.page > 1:
        canvas.setStrokeColor(GRID)
        canvas.setLineWidth(0.5)
        canvas.line(LEFT, 0.48*inch, PAGE_W-RIGHT, 0.48*inch)
        canvas.setFont("Arial", 8)
        canvas.setFillColor(MUTED)
        canvas.drawString(LEFT, 0.3*inch, "Limit.less · Pookie Blinders · Team 117")
        canvas.drawRightString(PAGE_W-RIGHT, 0.3*inch, f"Page {doc.page}")
    canvas.restoreState()


def split_table(lines, start):
    rows, i = [], start
    while i < len(lines) and lines[i].lstrip().startswith("|"):
        row = [c.strip() for c in lines[i].strip().strip("|").split("|")]
        if not all(re.fullmatch(r":?-{3,}:?", c.replace(" ", "")) for c in row):
            rows.append(row)
        i += 1
    return rows, i


def column_widths(rows):
    cols = max(len(r) for r in rows)
    scores = []
    for c in range(cols):
        vals = [r[c] if c < len(r) else "" for r in rows]
        maxlen = max((len(re.sub(r"[*`\[\]()]+", "", v)) for v in vals), default=5)
        scores.append(max(5, min(maxlen, 28)))
    total = sum(scores)
    widths = [CONTENT_W*x/total for x in scores]
    minw = 42
    for i, w in enumerate(widths):
        if w < minw:
            delta = minw-w
            widths[i] = minw
            donors = [j for j in range(len(widths)) if j != i and widths[j] > minw]
            for j in donors:
                take = min(delta, widths[j]-minw)
                widths[j] -= take
                delta -= take
                if delta <= 0: break
    scale = CONTENT_W/sum(widths)
    return [w*scale for w in widths]


def make_table(rows, st):
    data = []
    for ri, row in enumerate(rows):
        style = st["TableHeadR"] if ri == 0 else st["TableR"]
        data.append([Paragraph(inline_markup(cell), style) for cell in row])
    table = LongTable(data, colWidths=column_widths(rows), repeatRows=1, hAlign="LEFT",
                      splitByRow=1, spaceBefore=3, spaceAfter=7)
    commands = [
        ("BACKGROUND", (0,0), (-1,0), NAVY),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 0.45, GRID),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]
    for r in range(1, len(rows)):
        if r % 2 == 0:
            commands.append(("BACKGROUND", (0,r), (-1,r), PALE))
    table.setStyle(TableStyle(commands))
    return table


def image_flowable(line, st):
    m = re.match(r"!\[([^\]]*)\]\(([^)]+)\)$", line)
    if not m:
        return []
    path = (SOURCE.parent / m.group(2)).resolve()
    if not path.exists():
        return [Paragraph(f"Figure unavailable: {html.escape(path.name)}", st["CaptionR"])]
    img = Image(str(path))
    img._restrictSize(CONTENT_W, 4.25*inch)
    img.hAlign = "CENTER"
    return [KeepTogether([img, Paragraph(inline_markup(m.group(1)), st["CaptionR"])])]


def build_story():
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    st = styles()
    story = []
    title = next((x[2:].strip() for x in lines if x.startswith("# ")), "Limit.less Round 2 Dataset Analysis and Evidence Report")
    story += [Spacer(1, 1.4*inch), Paragraph(inline_markup(title), st["TitleR"]),
              Paragraph("SAS Data Analytics Hackathon · Round 2", st["SubR"]), Spacer(1, 0.2*inch),
              Paragraph("<b>Team:</b> Pookie Blinders", st["CoverMetaR"]),
              Paragraph("<b>Team ID:</b> 117", st["CoverMetaR"]),
              Paragraph("<b>Project:</b> Limit.less", st["CoverMetaR"]),
              Paragraph("Prepared 7 October 2026", st["CoverMetaR"]), PageBreak()]
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith("# ") or line.startswith("**Team:") or line.startswith("**SAS Data Analytics") or line.startswith("**Project:") or line.startswith("**Prepared:"):
            i += 1; continue
        if line.startswith("!["):
            image_nodes = image_flowable(line, st)
            if image_nodes and story and isinstance(story[-1], Paragraph):
                previous = story[-1]
                if len(previous.getPlainText()) < 280:
                    story.pop()
                    story.append(KeepTogether([previous] + image_nodes))
                else:
                    story.extend(image_nodes)
            else:
                story.extend(image_nodes)
            i += 1; continue
        equation_match = re.fullmatch(r"\[\[EQ:([a-z_]+)\]\]", line)
        if equation_match:
            formula = EQUATIONS.get(equation_match.group(1), "")
            story.append(Paragraph(formula, st["EquationR"]))
            i += 1; continue
        if line.startswith("|"):
            rows, i = split_table(lines, i)
            if rows: story.append(make_table(rows, st))
            continue
        if line.startswith("## "):
            if line[3:].startswith("17 Results"):
                story.append(PageBreak())
            story.append(Paragraph(inline_markup(line[3:]), st["H1R"]))
        elif line.startswith("### "):
            story.append(Paragraph(inline_markup(line[4:]), st["H2R"]))
        elif line.startswith("#### "):
            story.append(Paragraph(inline_markup(line[5:]), st["H3R"]))
        elif re.match(r"^\d+\.\s", line):
            number, body = line.split(".", 1)
            story.append(Paragraph(f"<b>{number}.</b> {inline_markup(body.strip())}", st["BulletR"]))
        elif line.startswith("- "):
            story.append(Paragraph(f"• {inline_markup(line[2:])}", st["BulletR"]))
        else:
            story.append(Paragraph(inline_markup(line), st["BodyR"]))
        i += 1
    return story


def main():
    doc = BaseDocTemplate(str(OUTPUT), pagesize=letter, leftMargin=LEFT, rightMargin=RIGHT,
                          topMargin=TOP, bottomMargin=BOTTOM, title="Limit.less Round 2 Dataset Analysis and Evidence Report",
                          author="Pookie Blinders, Team 117", subject="SAS Data Analytics Hackathon Round 2")
    frame = Frame(LEFT, BOTTOM, CONTENT_W, PAGE_H-TOP-BOTTOM, id="normal", leftPadding=0,
                  rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates(PageTemplate(id="report", frames=[frame], onPage=footer))
    doc.build(build_story())
    print(OUTPUT)


if __name__ == "__main__":
    main()

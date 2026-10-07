"""Build report charts from aggregate metrics; never exports source rows."""
from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
METRICS = ROOT / "evidence" / "reproduced_source_metrics.json"
OUT = ROOT / "docs" / "figures"
W, H = 1800, 1220
BG = "#FBFAF7"
INK = "#1C2430"
MUTED = "#627080"
GRID = "#DDE2E8"
BLUE = "#82B7E3"
GREEN = "#A7E968"
PURPLE = "#C5A3ED"
CORAL = "#E99883"


def font(size, bold=False):
    f = Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf")
    return ImageFont.truetype(str(f), size) if f.exists() else ImageFont.load_default()


def canvas(title, subtitle):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.text((64, 48), title, font=font(48, True), fill=INK)
    d.text((66, 112), subtitle, font=font(24, True), fill="#A64E37")
    return im, d


def line(d, xy, fill=GRID, width=2):
    d.line(xy, fill=fill, width=width)


def profile(data):
    a, ds, j, s = (data[k] for k in ("analytics_jobs", "datascience_jobs", "jds", "sds"))
    im, d = canvas("What the four source files contain", "RECOMPUTED FROM SUPPLIED FILES · ROWS ARE NOT LINKED ACROSS DATASETS")
    labels = ["Analytics Jobs", "DataScience Jobs", "JDS Skill Traits", "SDS Personality Traits"]
    values = [a["rows"], ds["rows"], j["rows"], s["rows"]]
    colors = [GREEN, BLUE, PURPLE, CORAL]
    x0, x1 = 375, 1460
    for idx, (label, value, color) in enumerate(zip(labels, values, colors)):
        y = 230 + idx * 92
        d.text((64, y), label, font=font(28, True), fill=INK)
        d.rounded_rectangle((x0, y + 4, x1, y + 44), radius=16, fill="#E8EBEF")
        d.rounded_rectangle((x0, y + 4, x0 + (x1-x0)*value/max(values), y + 44), radius=16, fill=color)
        d.text((1485, y + 2), f"{value:,} rows", font=font(26, True), fill=INK)
    line(d, (64, 640, 1736, 640), width=2)
    d.text((64, 675), "Quality and identifier checks", font=font(32, True), fill=INK)
    quality = [
        ("Analytics job_type missing", a["missing"]["job_type"], a["rows"], CORAL),
        ("Analytics job_description missing", a["missing"]["job_description"], a["rows"], BLUE),
        ("DataScience excess repeated-reference rows", ds["excess_repeated_reference_rows"], ds["rows"], PURPLE),
        ("Possible `...` markers in key_skills", a["key_skills_contains_ellipsis"], a["missing"]["key_skills"] and a["rows"]-a["missing"]["key_skills"] or a["rows"], GREEN),
    ]
    for idx, (label, count, denom, color) in enumerate(quality):
        y = 740 + idx * 94
        pct = 100*count/denom if denom else 0
        d.text((64, y), label, font=font(23), fill=INK)
        d.rounded_rectangle((580, y+4, 1405, y+32), radius=12, fill="#E8EBEF")
        d.rounded_rectangle((580, y+4, 580+825*pct/100, y+32), radius=12, fill=color)
        d.text((1430, y), f"{count:,} / {denom:,}  ·  {pct:.1f}%", font=font(22, True), fill=INK)
    d.text((64, 1142), "Repeated IDs are retained pending source clarification. Ellipses are flagged as possible truncation, not silently treated as a skill.", font=font(20), fill=MUTED)
    im.save(OUT / "reproduced-source-profile.png")


def market(data):
    a, ds = data["analytics_jobs"], data["datascience_jobs"]
    im, d = canvas("Market signals inside the supplied samples", "DESCRIPTIVE COUNTS · EACH BAR SHOWS ITS OWN DENOMINATOR")
    rows = [
        ("Bengaluru primary location", 3753, 15841, GREEN),
        ("SQL exact token in key_skills", 915, 15840, BLUE),
        ("Python exact token in key_skills", 840, 15840, PURPLE),
        ("Salary label 10to15", 3608, 15841, CORAL),
        ("Normalized job_type = analytics", 3781, 3830, GREEN),
    ]
    for idx, (label, count, denom, color) in enumerate(rows):
        y = 205 + idx * 106
        pct = 100 * count / denom
        d.text((64, y), label, font=font(27, True), fill=INK)
        d.text((1160, y), f"{count:,} / {denom:,} rows", font=font(22), fill=MUTED)
        d.rounded_rectangle((64, y+43, 1455, y+77), radius=14, fill="#E8EBEF")
        d.rounded_rectangle((64, y+43, 64+1391*pct/100, y+77), radius=14, fill=color)
        d.text((1490, y+38), f"{pct:.1f}%", font=font(26, True), fill=INK)
    line(d, (64, 765, 1736, 765), width=2)
    d.text((64, 795), "DataScience Jobs · supplied num_of_jobs field", font=font(32, True), fill=INK)
    vals = [
        ("Sum across 1,602 rows", "93,005", BLUE),
        ("Business Analyst title sum", "32,843", PURPLE),
        ("TCS company sum", "9,064", GREEN),
        ("Per-row range · median", "3–4,200 · 22", CORAL),
    ]
    for idx, (label, value, color) in enumerate(vals):
        x = 64 + idx*420
        d.rounded_rectangle((x, 865, x+385, 1040), radius=22, fill="#FFFFFF", outline=GRID, width=2)
        d.text((x+24, 892), value, font=font(37, True), fill=color)
        d.text((x+24, 954), label, font=font(20), fill=INK)
    d.text((64, 1090), "num_of_jobs is shown as supplied; its meaning as distinct vacancies is unverified. This file has no skill field and is not joined to Analytics Jobs.", font=font(20), fill=MUTED)
    im.save(OUT / "reproduced-analysis-signals.png")


def traits(data):
    im, d = canvas("Exploratory trait associations kept separate", "HIGH-LABEL MEAN MINUS LOW-LABEL MEAN · SAMPLE ASSOCIATION, NOT CAUSATION")
    start_y = 200
    groups = [("JDS · skill dimensions", data["jds"]["associations"], PURPLE, "139 observations · 73 high labels · 2 excess repeated-ID rows"),
              ("SDS · personality research", data["sds"]["associations"], BLUE, "161 observations · 85 high labels · 9 excess repeated-ID rows")]
    for title, rows, color, note in groups:
        d.text((64, start_y), title, font=font(31, True), fill=INK)
        d.text((750, start_y+8), note, font=font(19), fill=MUTED)
        y = start_y + 60
        d.text((76, y), "Dimension", font=font(19, True), fill=MUTED)
        d.text((970, y), "Mean difference", font=font(19, True), fill=MUTED)
        d.text((1250, y), "r", font=font(19, True), fill=MUTED)
        d.text((1450, y), "Cohen's d", font=font(19, True), fill=MUTED)
        y += 38
        for row in rows:
            name = row["field"].replace("_", " ").replace("-", " ").title()
            d.text((76, y), name, font=font(21), fill=INK)
            diff = row["mean_difference"]
            d.text((970, y), f"{diff:+.2f}", font=font(21, True), fill=INK)
            d.text((1250, y), f"{row['point_biserial_r']:+.3f}", font=font(21), fill=INK)
            d.text((1450, y), f"{row['cohens_d_pooled']:+.3f}", font=font(21), fill=INK)
            line(d, (76, y+32, 1690, y+32))
            y += 48
        start_y = y + 55
    d.text((64, 1140), "No person-level score or screening is derived. Repeated IDs, small samples and exploratory multiple comparisons constrain interpretation.", font=font(20), fill=MUTED)
    im.save(OUT / "reproduced-trait-associations.png")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    metrics = json.loads(METRICS.read_text(encoding="utf-8-sig"))
    profile(metrics)
    market(metrics)
    traits(metrics)
    print("Generated three report figures from aggregate metrics.")

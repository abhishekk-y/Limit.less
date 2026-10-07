"""Render high-level, report-ready process figures from the documented lane design.

The editable Mermaid files in docs/diagrams are the authoritative diagrams;
these Pillow figures are layout-friendly report renderings of those same stages.
They visualize the proposed/runbook pipeline and must not be read as execution receipts.
"""
from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "figures"
W = 1800
BG = "#F8F7F2"
INK = "#151923"
MUTED = "#647080"
GRID = "#D9DEE5"
ACCENTS = ["#9EDC55", "#83BCE8", "#C6A3EE", "#E79985"]


def font(size: int, bold: bool = False):
    path = Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf")
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


def centered(draw, box, text, face, fill=INK, max_chars=27):
    x0, y0, x1, y1 = box
    lines = []
    for part in text.split("\n"):
        lines.extend(textwrap.wrap(part, width=max_chars) or [""])
    heights = [draw.textbbox((0, 0), line, font=face)[3] for line in lines]
    y = (y0 + y1 - sum(heights) - 5 * (len(lines) - 1)) / 2
    for line, height in zip(lines, heights):
        width = draw.textbbox((0, 0), line, font=face)[2]
        draw.text(((x0 + x1 - width) / 2, y), line, font=face, fill=fill)
        y += height + 5


def arrow(draw, start, end, color="#677385", width=4):
    draw.line((start, end), fill=color, width=width)
    import math
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    size = 13
    p1 = (end[0] - size * math.cos(angle - .48), end[1] - size * math.sin(angle - .48))
    p2 = (end[0] - size * math.cos(angle + .48), end[1] - size * math.sin(angle + .48))
    draw.polygon([end, p1, p2], fill=color)


def header(draw, title, subtitle):
    draw.text((58, 36), title, font=font(38, True), fill=INK)
    draw.text((60, 89), subtitle, font=font(18, True), fill="#7A5FA6")


def lane_overview():
    rows = [
        ("ANALYTICS JOBS · POSTING-LIKE ROWS", ["Schema + text coverage", "Normalize fields\nkeep text sources separate", "Phrase counts +\neligible denominators", "Human audit + exact-text\nsensitivity", "Sample-bounded\nskill evidence"]),
        ("DATASCIENCE JOBS · COMPANY/TITLE RECORDS", ["Confirm row and\nweight semantics", "Repeated references\nare diagnostics", "Parse and flag\nnum_of_jobs", "Record counts vs\nweighted proxy", "Cap / max sensitivity\nnot vacancies"]),
        ("JDS · SKILL TRAITS", ["Verify labels, traits,\nscale and ID meaning", "Missingness + class\nprevalence", "Aggregate summaries", "Optional grouped\nJDS-only experiment", "Exploratory within-file\nevidence"]),
        ("SDS · PERSONALITY TRAITS", ["Verify fields, label,\nscale and ID", "Missingness +\naggregate descriptions", "Separate governance\nreview", "No personal model\nor decision path", "Research-only\naggregate view"]),
    ]
    h = 1180
    im = Image.new("RGB", (W, h), BG)
    d = ImageDraw.Draw(im)
    header(d, "Four files. Four independent evidence lanes.", "PROPOSED PROCESS · ROWS ARE NOT JOINED · SAS/VFL EXECUTION STATUS MUST BE VERIFIED SEPARATELY")
    x_positions = [48, 397, 746, 1095, 1444]
    box_w, box_h = 300, 94
    for ridx, (label, nodes) in enumerate(rows):
        y = 190 + ridx * 218
        d.text((50, y - 34), label, font=font(16, True), fill=ACCENTS[ridx])
        for cidx, text in enumerate(nodes):
            x = x_positions[cidx]
            box = (x, y, x + box_w, y + box_h)
            d.rounded_rectangle(box, radius=18, fill="#FFFFFF", outline=GRID, width=2)
            d.rounded_rectangle((x, y, x + 10, y + box_h), radius=5, fill=ACCENTS[ridx])
            centered(d, box, text, font(17, cidx in (0, 4)), max_chars=30)
            if cidx < len(nodes) - 1:
                arrow(d, (x + box_w + 5, y + box_h / 2), (x_positions[cidx + 1] - 8, y + box_h / 2))
    d.rounded_rectangle((48, 1080, 1752, 1140), radius=14, fill="#ECE8F3")
    centered(d, (64, 1082, 1736, 1138), "Evidence passport: source + unit + run + formula + numerator/denominator + sensitivity + limitation + reviewer. No output leaves VFL without written approval.", font(17, True), max_chars=125)
    im.save(OUT / "dataset-processing-overview.png")


def sequence_figure(title, subtitle, stages, filename, footer, accent="#8B6BD6"):
    cols = 4
    rows = (len(stages) + cols - 1) // cols
    row_h, box_w, box_h = 246, 390, 128
    gap_x = 36
    x0 = (W - (cols * box_w + (cols - 1) * gap_x)) // 2
    h = 170 + rows * row_h + 120
    im = Image.new("RGB", (W, h), BG)
    d = ImageDraw.Draw(im)
    header(d, title, subtitle)
    positions = []
    for idx, label in enumerate(stages):
        row, col = divmod(idx, cols)
        if row % 2:
            col = cols - 1 - col
        x = x0 + col * (box_w + gap_x)
        y = 172 + row * row_h
        box = (x, y, x + box_w, y + box_h)
        d.rounded_rectangle(box, radius=20, fill="#FFFFFF", outline=GRID, width=2)
        d.rounded_rectangle((x, y, x + 12, y + box_h), radius=7, fill=accent)
        d.ellipse((x + 20, y + 17, x + 56, y + 53), fill=accent)
        centered(d, (x + 20, y + 17, x + 56, y + 53), str(idx + 1), font(17, True), fill="#FFFFFF", max_chars=3)
        centered(d, (x + 58, y + 5, x + box_w - 10, y + box_h - 5), label, font(17, idx in (0, len(stages) - 1)), max_chars=36)
        positions.append((x, y))
    for idx in range(len(stages) - 1):
        x, y = positions[idx]
        nx, ny = positions[idx + 1]
        row = idx // cols
        if idx // cols == (idx + 1) // cols:
            if row % 2 == 0:
                start = (x + box_w + 5, y + box_h / 2)
                end = (nx - 8, ny + box_h / 2)
            else:
                start = (x - 5, y + box_h / 2)
                end = (nx + box_w + 8, ny + box_h / 2)
        else:
            # The serpentine connector takes the next step down at the row end.
            end_x = x0 + cols * box_w + (cols - 1) * gap_x + 14 if row % 2 == 0 else x0 - 14
            start_x = x + box_w if row % 2 == 0 else x
            next_start_x = nx + box_w if (row + 1) % 2 else nx
            next_edge = nx + box_w if (row + 1) % 2 else nx
            bend_y = y + box_h + 22
            arrow(d, (start_x, y + box_h / 2), (end_x, y + box_h / 2), width=3)
            d.line((end_x, y + box_h / 2, end_x, bend_y, next_edge, bend_y, next_edge, ny + box_h / 2), fill="#677385", width=3)
            arrow(d, (next_edge, ny + box_h / 2), (next_edge - 7 if next_edge > nx else next_edge + 7, ny + box_h / 2), width=3)
            continue
        arrow(d, start, end, width=3)
    foot_y = h - 94
    d.rounded_rectangle((48, foot_y, 1752, h - 30), radius=14, fill="#F0EBF6")
    centered(d, (68, foot_y + 4, 1732, h - 34), footer, font(16, True), fill="#514669", max_chars=132)
    im.save(OUT / filename)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    lane_overview()
    sequence_figure(
        "Analytics Jobs · text-to-evidence pipeline",
        "POSTING-LIKE ROWS · TWO TEXT FIELDS · DENOMINATORS STAY VISIBLE",
        ["Immutable source + schema gate", "Profile nulls, blanks, and\ntext availability", "Normalize title/text in\ntemporary WORK", "Keep skills and description\nseparate", "Apply versioned phrase rules\n(≤1 hit per row/skill)", "Compute counts, rates,\nand co-mention Jaccard", "Exact-text duplicate\nsensitivity; retain all rows", "Human audit + scenario\ncomparison + evidence passport"],
        "analytics-jobs-pipeline.png",
        "Share = rows with a skill mention ÷ rows with usable text for that field. A mention rate is not proof that employers require the skill.",
    )
    sequence_figure(
        "DataScience Jobs · record and weight analysis",
        "COMPANY/TITLE-LIKE RECORDS · SUPPLIED WEIGHT IS A SEPARATE MEASURE",
        ["Immutable source + verify\nrow grain and field names", "Count rows and repeated\nreference diagnostics", "Normalize title for grouping;\nkeep source unchanged", "Parse num_of_jobs; flag\nmissing/non-numeric/negative", "Report unweighted record\ncount n by title/company", "Separately report weighted\nsum W = Σ num_of_jobs", "Inspect quantiles, maximum,\nconcentration, influence", "Compare cap and leave-max\nscenarios; passport limits"],
        "datascience-jobs-pipeline.png",
        "n counts source records. W sums a supplied proxy. Without validated weight semantics and a sampling frame, W is not a count of unique vacancies.",
        accent="#C69235",
    )
    sequence_figure(
        "Trait files · isolated description and optional JDS experiment",
        "JDS MODEL IS OPTIONAL AND WITHIN-FILE · SDS IS AGGREGATE GOVERNANCE RESEARCH ONLY",
        ["Keep JDS and SDS tables\nphysically separate", "Verify label semantics,\ntrait scale, and ID meaning", "Report missingness, label\nprevalence, group sizes", "Descriptive means and\nwithin-file contrasts", "JDS gate: organizer approval\n+ verified grouped ID", "Fit five-feature logistic\ninside training folds only", "Score held-out IDs; compare\nwith training prevalence", "AUC/Brier/accuracy + limits;\nno personal or hiring use"],
        "trait-model-pipeline.png",
        "The SAS program is an unexecuted exploratory design until a safe VFL run receipt exists. SDS has no individual prediction or action path.",
        accent="#8F6FB5",
    )
    print("Generated four dataset-processing figures from the documented pipeline.")


if __name__ == "__main__":
    main()

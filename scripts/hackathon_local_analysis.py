"""Local-only, aggregate analysis for the supplied SAS hackathon workbooks.

This script makes no network calls. It never writes raw rows, IDs, company names,
job descriptions, or per-person predictions. Keep source files in the organizer-
approved environment and choose an output directory in that same environment.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


SKILLS: dict[str, tuple[str, ...]] = {
    "Python": ("python",),
    "R": ("r programming", "r language", "rstudio"),
    "SQL": ("sql", "structured query language"),
    "SAS": ("sas",),
    "Excel": ("excel", "microsoft excel",),
    "Statistics": ("statistics", "statistical analysis", "statistical modeling"),
    "Probability": ("probability", "probability theory"),
    "Machine learning": ("machine learning", "ml algorithms"),
    "Deep learning": ("deep learning", "neural networks"),
    "Artificial intelligence": ("artificial intelligence", " ai "),
    "Natural language processing": ("natural language processing", "nlp"),
    "Computer vision": ("computer vision",),
    "Data visualization": ("data visualization", "data visualisation",),
    "Tableau": ("tableau",),
    "Power BI": ("power bi", "powerbi"),
    "Data cleaning": ("data cleaning", "data cleansing", "data wrangling"),
    "ETL": ("etl", "extract transform load"),
    "Data engineering": ("data engineering",),
    "Data mining": ("data mining",),
    "Big data": ("big data",),
    "Apache Spark": ("apache spark", "pyspark",),
    "Hadoop": ("hadoop",),
    "Cloud computing": ("cloud computing", "cloud platform"),
    "AWS": ("aws", "amazon web services"),
    "Azure": ("azure", "microsoft azure"),
    "Google Cloud": ("google cloud", "gcp"),
    "Database design": ("database design", "database management"),
    "Communication": ("communication skills", "verbal communication", "written communication"),
    "Problem solving": ("problem solving", "problem-solving"),
    "Project management": ("project management",),
    "Business analysis": ("business analysis", "business analyst"),
    "Data storytelling": ("data storytelling", "storytelling"),
    "Research": ("research methodology", "research skills"),
}


def _pattern(term: str) -> re.Pattern[str]:
    escaped = re.escape(term.strip())
    left = r"(?<![a-z0-9])" if term[:1].isalnum() else ""
    right = r"(?![a-z0-9])" if term[-1:].isalnum() else ""
    return re.compile(left + escaped + right, re.IGNORECASE)


SKILL_PATTERNS = {
    skill: tuple(_pattern(alias) for alias in aliases)
    for skill, aliases in SKILLS.items()
}


def _safe_text(value: Any) -> str:
    if pd.isna(value):
        return ""
    return str(value).replace("\x00", " ").strip()


def _role_family(title: str) -> str:
    value = title.casefold()
    if any(x in value for x in ("data scientist", "machine learning", "ai engineer")):
        return "Data science and AI"
    if any(x in value for x in ("data engineer", "big data", "etl developer")):
        return "Data engineering"
    if any(x in value for x in ("analyst", "analytics", "business intelligence", "bi developer")):
        return "Analytics and BI"
    if any(x in value for x in ("business", "operations", "market research")):
        return "Business and research"
    return "Other or unclassified"


def _profile(frame: pd.DataFrame, name: str) -> dict[str, Any]:
    missing = frame.isna().sum()
    normalized = frame.fillna("").astype(str).apply(lambda col: col.str.strip().str.casefold())
    duplicate_count = int(normalized.duplicated().sum())
    return {
        "name": name,
        "rows": int(len(frame)),
        "columns": int(len(frame.columns)),
        "missing_by_field": {
            str(col): {"count": int(missing[col]), "rate": round(float(missing[col] / max(1, len(frame))), 4)}
            for col in frame.columns
        },
        "exact_duplicate_rows": duplicate_count,
    }


def _skill_mentions(text: str) -> list[str]:
    return [
        skill
        for skill, patterns in SKILL_PATTERNS.items()
        if any(pattern.search(text) for pattern in patterns)
    ]


def analyze_postings(path: Path, name: str, title_col: str, text_cols: tuple[str, ...], min_group: int) -> dict[str, Any]:
    frame = pd.read_csv(path, low_memory=False)
    columns = {str(column).casefold(): column for column in frame.columns}
    title = columns.get(title_col.casefold())
    if title is None:
        raise ValueError(f"Required title column {title_col!r} not found in {name}")
    source_text = [columns[col.casefold()] for col in text_cols if col.casefold() in columns]
    if not source_text:
        raise ValueError(f"No configured description/skill fields found in {name}")

    profile = _profile(frame, name)
    title_values = frame[title].map(_safe_text)
    families = title_values.map(_role_family)
    text = frame[source_text].fillna("").astype(str).agg(" ".join, axis=1)
    mentions = text.map(_skill_mentions)

    overall_counts: dict[str, int] = {skill: int(mentions.map(lambda row: skill in row).sum()) for skill in SKILLS}
    family_counts: dict[str, dict[str, int]] = {}
    family_sizes = families.value_counts().to_dict()
    for family, size in family_sizes.items():
        if int(size) < min_group:
            continue
        mask = families == family
        family_counts[str(family)] = {
            "postings": int(size),
            "skills": {
                skill: int(mentions[mask].map(lambda row: skill in row).sum())
                for skill in SKILLS
            },
        }

    return {
        "profile": profile,
        "posting_fields_used": [str(col) for col in source_text],
        "title_field_used": str(title),
        "descriptions_with_text": int(text.str.strip().ne("").sum()),
        "role_families": {str(k): int(v) for k, v in family_sizes.items() if int(v) >= min_group},
        "suppressed_role_family_count": int(sum(1 for v in family_sizes.values() if int(v) < min_group)),
        "skill_mentions": {
            skill: {"postings": count, "rate": round(count / max(1, len(frame)), 4)}
            for skill, count in sorted(overall_counts.items(), key=lambda item: (-item[1], item[0]))
            if count >= min_group
        },
        "skill_mentions_by_role_family": family_counts,
    }


def analyze_structured_job_counts(path: Path, min_group: int) -> dict[str, Any]:
    """Summarize the separate DataScience Jobs table without treating titles as skill text."""
    frame = pd.read_csv(path, low_memory=False)
    columns = {str(column).casefold(): column for column in frame.columns}
    required = ("job_title", "num_of_jobs")
    if any(key not in columns for key in required):
        raise ValueError("DataScience Jobs requires job_title and num_of_jobs fields")
    title_col = columns["job_title"]
    count_col = columns["num_of_jobs"]
    titles = frame[title_col].map(_safe_text)
    counts = pd.to_numeric(frame[count_col], errors="coerce")
    grouped = frame.assign(_title=titles, _reported_jobs=counts).groupby("_title", dropna=False)
    rows: list[dict[str, Any]] = []
    suppressed = 0
    for title, group in grouped:
        if not title or len(group) < min_group:
            suppressed += 1
            continue
        reported = group["_reported_jobs"].dropna()
        rows.append({
            "job_title": title,
            "company_records": int(len(group)),
            "reported_jobs_sum": round(float(reported.sum()), 2) if len(reported) else None,
            "reported_jobs_median": round(float(reported.median()), 2) if len(reported) else None,
        })
    rows.sort(key=lambda item: (item["reported_jobs_sum"] or 0, item["company_records"]), reverse=True)
    experience_col = columns.get("min_experience")
    experience = pd.to_numeric(frame[experience_col], errors="coerce") if experience_col else pd.Series(dtype=float)
    return {
        "profile": _profile(frame, "DataScience Jobs"),
        "analysis_note": "This file has no job-description field. Job titles are not counted as required skills.",
        "titles_with_at_least_minimum_company_records": rows,
        "suppressed_title_groups": suppressed,
        "min_experience_numeric_summary": {
            "field": str(experience_col) if experience_col else None,
            "non_missing_rows": int(experience.notna().sum()),
            "median": round(float(experience.median()), 2) if experience.notna().any() else None,
        },
        "salary_analysis": "Withheld until source salary units and representation are confirmed from the codebook.",
    }


def _bh_adjust(p_values: list[float]) -> list[float]:
    if not p_values:
        return []
    values = np.asarray(p_values, dtype=float)
    order = np.argsort(values)
    adjusted = np.empty(len(values), dtype=float)
    running = 1.0
    for rank_index in range(len(values) - 1, -1, -1):
        original_index = order[rank_index]
        rank = rank_index + 1
        running = min(running, values[original_index] * len(values) / rank)
        adjusted[original_index] = running
    return adjusted.tolist()


def _mann_whitney_p(high: np.ndarray, low: np.ndarray) -> float:
    """Two-sided, tie-corrected normal-approximation p-value with continuity correction."""
    combined = np.concatenate((high, low))
    n_high, n_low = len(high), len(low)
    if not n_high or not n_low:
        return 1.0
    ranks = pd.Series(combined).rank(method="average").to_numpy()
    u_high = float(ranks[:n_high].sum() - n_high * (n_high + 1) / 2)
    mean_u = n_high * n_low / 2
    _, tie_counts = np.unique(combined, return_counts=True)
    n_total = n_high + n_low
    tie_term = float(np.sum(tie_counts**3 - tie_counts))
    variance = n_high * n_low / 12 * (n_total + 1 - tie_term / (n_total * (n_total - 1)))
    if variance <= 0:
        return 1.0
    z = max(0.0, abs(u_high - mean_u) - 0.5) / math.sqrt(variance)
    return float(math.erfc(z / math.sqrt(2)))


def analyze_labeled_workbook(path: Path, name: str, outcome_col: str, min_group: int, seed: int, bootstrap: int) -> dict[str, Any]:
    frame = pd.read_excel(path)
    profile = _profile(frame, name)
    columns = {str(column).strip().casefold(): column for column in frame.columns}
    outcome_key = outcome_col.strip().casefold()
    outcome = columns.get(outcome_key)
    if outcome is None:
        raise ValueError(f"Required outcome column {outcome_col!r} not found in {name}")
    labels = frame[outcome].astype("string").str.strip().str.casefold()
    high_mask = labels.str.contains(r"^1(\.0)?$|high|yes|success|positive", regex=True, na=False)
    low_mask = labels.str.contains(r"^0(\.0)?$|low|no|fail|negative", regex=True, na=False)
    ambiguous = ~(high_mask | low_mask)
    frame = frame.loc[~ambiguous].copy()
    high_mask = high_mask.loc[~ambiguous]
    low_mask = low_mask.loc[~ambiguous]
    n_high, n_low = int(high_mask.sum()), int(low_mask.sum())
    rng = np.random.default_rng(seed)
    comparisons: list[dict[str, Any]] = []
    p_values: list[float] = []
    metric_names: list[str] = []

    for raw_col in frame.columns:
        if raw_col == outcome:
            continue
        values = pd.to_numeric(frame[raw_col], errors="coerce")
        high = values.loc[high_mask].dropna().to_numpy(dtype=float)
        low = values.loc[low_mask].dropna().to_numpy(dtype=float)
        if len(high) < min_group or len(low) < min_group:
            continue
        pooled_sd = float(np.sqrt(((len(high) - 1) * np.var(high, ddof=1) + (len(low) - 1) * np.var(low, ddof=1)) / max(1, len(high) + len(low) - 2)))
        hedges_g = 0.0 if pooled_sd == 0 else (float(np.mean(high) - np.mean(low)) / pooled_sd) * (1 - 3 / max(1, (4 * (len(high) + len(low)) - 9)))
        p_value = _mann_whitney_p(high, low)
        boot = np.empty(bootstrap, dtype=float)
        for i in range(bootstrap):
            boot[i] = rng.choice(high, len(high), replace=True).mean() - rng.choice(low, len(low), replace=True).mean()
        index = len(comparisons)
        metric_names.append(str(raw_col))
        p_values.append(p_value)
        comparisons.append({
            "measure": str(raw_col).strip(),
            "n_high": int(len(high)),
            "n_low": int(len(low)),
            "high_mean": round(float(np.mean(high)), 4),
            "low_mean": round(float(np.mean(low)), 4),
            "mean_difference_high_minus_low": round(float(np.mean(high) - np.mean(low)), 4),
            "mean_difference_bootstrap_95_ci": [round(float(x), 4) for x in np.quantile(boot, [0.025, 0.975])],
            "hedges_g_exploratory": round(hedges_g, 4),
            "mann_whitney_p_raw": round(p_value, 6),
            "bh_q_value": None,
        })
    adjusted = _bh_adjust(p_values)
    for item, q_value in zip(comparisons, adjusted):
        item["bh_q_value"] = round(float(q_value), 6)

    return {
        "profile": profile,
        "outcome_field": str(outcome),
        "labeled_records_used": int(n_high + n_low),
        "high_label_n": n_high,
        "low_label_n": n_low,
        "unclassified_label_n": int(ambiguous.sum()),
        "comparisons": comparisons,
        "interpretation": "Exploratory aggregate association only; not causal evidence, hiring prediction, salary prediction, or a personal score.",
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    output_root = args.output.resolve()
    source_paths = [args.analytics_csv, args.datascience_csv, args.jds_xlsx, args.sds_xlsx]
    for source in source_paths:
        if not source.is_file():
            raise FileNotFoundError(f"Input file not found: {source}")
        if source.resolve().is_relative_to(output_root):
            raise ValueError("Keep output directory separate from source files")
    output_root.mkdir(parents=True, exist_ok=True)
    report = {
        "report_type": "local_hackathon_aggregate_analysis",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_seed": args.seed,
        "min_group_size": args.min_group,
        "data_handling": {
            "network_calls": 0,
            "raw_rows_written": False,
            "identifiers_written": False,
            "person_level_predictions": False,
            "scope": "Run only inside the organizer-approved environment. Aggregates are sample-specific, not a census or live market feed.",
        },
        "postings": {
            "analytics_jobs": analyze_postings(args.analytics_csv, "Analytics Jobs", "job_desig", ("job_description", "key_skills"), args.min_group),
            "data_science_jobs": analyze_structured_job_counts(args.datascience_csv, args.min_group),
        },
        "labeled_workbooks": {
            "junior_skill_traits": analyze_labeled_workbook(args.jds_xlsx, "JDS Skill Traits", "salary_hike_high_or_low", args.min_group, args.seed, args.bootstrap),
            "senior_personality_traits": analyze_labeled_workbook(args.sds_xlsx, "SDS Personality Traits", "success_ classification_ high_low", args.min_group, args.seed, args.bootstrap),
        },
        "method_limitations": [
            "Skill extraction uses a transparent, conservative phrase dictionary; counts are a lower-bound-like sample signal and require a human-reviewed extraction benchmark.",
            "Not mentioned in an ad does not mean the skill is not required.",
            "Role-family labels are heuristic and must be manually audited before publication.",
            "Bootstrap intervals describe variability within this sample and do not correct selection bias.",
            "Small labeled workbooks are exploratory; do not train or deploy person-level outcome predictions from them.",
        ],
    }
    destination = output_root / "aggregate_report.json"
    destination.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analytics-csv", type=Path, required=True)
    parser.add_argument("--datascience-csv", type=Path, required=True)
    parser.add_argument("--jds-xlsx", type=Path, required=True)
    parser.add_argument("--sds-xlsx", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="Local output directory inside approved environment; never point inside the repository")
    parser.add_argument("--min-group", type=int, default=10)
    parser.add_argument("--bootstrap", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=20261007)
    args = parser.parse_args()
    if args.min_group < 5 or args.bootstrap < 100:
        parser.error("--min-group must be >= 5 and --bootstrap must be >= 100")
    return args


if __name__ == "__main__":
    result = build_report(parse_args())
    print(json.dumps({"status": "complete", "report_type": result["report_type"], "datasets": 4, "network_calls": 0, "raw_rows_written": False}))

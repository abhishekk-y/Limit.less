"""Recompute aggregate metrics cited in the Limit.less Round 2 report.

Run with --input-dir pointing to the directory containing the four source files.
Only aggregate counts/statistics are printed; no source rows are exported.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def association_table(frame: pd.DataFrame, label: str) -> list[dict]:
    y = pd.to_numeric(frame[label], errors="raise").astype(float)
    n1, n0 = int((y == 1).sum()), int((y == 0).sum())
    result = []
    for col in frame.columns:
        if col in ("id", label):
            continue
        x = pd.to_numeric(frame[col], errors="coerce")
        high, low = x[y == 1].dropna(), x[y == 0].dropna()
        m1, m0 = float(high.mean()), float(low.mean())
        s1, s0 = float(high.std(ddof=1)), float(low.std(ddof=1))
        pooled = np.sqrt(((len(high) - 1) * s1**2 + (len(low) - 1) * s0**2) / (len(high) + len(low) - 2))
        r = float(np.corrcoef(x, y)[0, 1])
        result.append({
            "field": col.strip(),
            "n": int(x.notna().sum()),
            "mean_label_1": m1,
            "mean_label_0": m0,
            "mean_difference": m1 - m0,
            "point_biserial_r": r,
            "cohens_d_pooled": (m1 - m0) / pooled,
        })
    return result


def run(input_dir: Path) -> dict:
    analytics = pd.read_csv(input_dir / "Analytics Jobs.csv")
    data_science = pd.read_csv(input_dir / "DataScience Jobs.csv")
    jds = pd.read_excel(input_dir / "JDS Skill Traits.xlsx")
    sds = pd.read_excel(input_dir / "SDS Personality Traits.xlsx")

    skills = analytics["key_skills"].fillna("").astype(str)
    skill_tokens = skills.str.lower().str.split(",")
    eligible = int(analytics["key_skills"].notna().sum())
    skill_counts = {}
    for skill in ("sql", "python", "sas", "r", "machine learning"):
        mentions = int(skill_tokens.apply(lambda tokens: any(t.strip() == skill for t in tokens)).sum())
        skill_counts[skill] = {"mentions": mentions, "denominator": eligible, "rate": mentions / eligible}

    ds = data_science
    sds_label = sds.columns[-1]
    return {
        "analytics_jobs": {
            "rows": int(len(analytics)),
            "missing": {c: int(analytics[c].isna().sum()) for c in analytics.columns},
            "job_type_normalized": analytics["job_type"].dropna().str.lower().str.strip().value_counts().to_dict(),
            "primary_location_top": analytics["location"].str.split(",").str[0].str.strip().value_counts().head(5).to_dict(),
            "salary_label_top": analytics["salary"].value_counts().head(10).to_dict(),
            "skill_mentions_exact_token": skill_counts,
            "key_skills_contains_ellipsis": int(skills.str.contains(r"\.\.\.", regex=True).sum()),
        },
        "datascience_jobs": {
            "rows": int(len(ds)),
            "unique_reference_no": int(ds["reference_no"].nunique()),
            "repeated_reference_rows_including_first": int(ds["reference_no"].duplicated(keep=False).sum()),
            "excess_repeated_reference_rows": int(ds["reference_no"].duplicated().sum()),
            "num_of_jobs_sum": int(ds["num_of_jobs"].sum()),
            "num_of_jobs_median": float(ds["num_of_jobs"].median()),
            "num_of_jobs_min": int(ds["num_of_jobs"].min()),
            "num_of_jobs_max": int(ds["num_of_jobs"].max()),
            "company_weighted_top": ds.groupby("company_name")["num_of_jobs"].sum().sort_values(ascending=False).head(10).to_dict(),
            "title_weighted_top": ds.groupby("job_title")["num_of_jobs"].sum().sort_values(ascending=False).head(10).to_dict(),
        },
        "jds": {
            "rows": int(len(jds)),
            "positive_label_count": int(jds.iloc[:, -1].sum()),
            "positive_label_rate": float(jds.iloc[:, -1].mean()),
            "excess_repeated_ids": int(jds["id"].duplicated().sum()),
            "associations": association_table(jds, jds.columns[-1]),
        },
        "sds": {
            "rows": int(len(sds)),
            "positive_label_count": int(pd.to_numeric(sds[sds_label]).sum()),
            "positive_label_rate": float(pd.to_numeric(sds[sds_label]).mean()),
            "excess_repeated_ids": int(sds["id"].duplicated().sum()),
            "associations": association_table(sds, sds_label),
        },
        "method_notes": [
            "Input rows remain separate; no cross-file joins are performed.",
            "Skill tokens are comma-split, trimmed and case-folded; each row counts at most once per token.",
            "Location uses the first comma-separated value only.",
            "num_of_jobs is summed as supplied and is not interpreted as verified vacancies.",
            "Trait statistics are unadjusted sample associations, not causal or individual predictions.",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.input_dir), indent=2, ensure_ascii=False, default=str))

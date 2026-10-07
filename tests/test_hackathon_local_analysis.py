import importlib.util
from pathlib import Path

import numpy as np


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "hackathon_local_analysis.py"
SPEC = importlib.util.spec_from_file_location("hackathon_local_analysis", MODULE_PATH)
analysis = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(analysis)


def test_skill_matching_is_case_insensitive_and_deduplicates_within_posting():
    found = analysis._skill_mentions("Python, PYTHON and SQL; Power BI")
    assert found == ["Python", "SQL", "Power BI"]


def test_role_families_are_coarse_and_deterministic():
    assert analysis._role_family("Senior Data Scientist") == "Data science and AI"
    assert analysis._role_family("Business Intelligence Analyst") == "Analytics and BI"
    assert analysis._role_family("Office Administrator") == "Other or unclassified"


def test_structured_job_titles_are_not_misrepresented_as_skill_requirements(tmp_path):
    import pandas as pd

    data = tmp_path / "titles.csv"
    pd.DataFrame({
        "company_name": [f"private-{i}" for i in range(10)],
        "job_title": ["Data Scientist"] * 10,
        "min_experience": [2] * 10,
        "num_of_jobs": [1] * 10,
    }).to_csv(data, index=False)
    summary = analysis.analyze_structured_job_counts(data, min_group=5)
    assert "no job-description field" in summary["analysis_note"]
    assert summary["titles_with_at_least_minimum_company_records"][0]["reported_jobs_sum"] == 10
    assert "private-0" not in str(summary)


def test_benjamini_hochberg_adjustment_is_monotonic_in_sorted_order():
    adjusted = analysis._bh_adjust([0.04, 0.001, 0.03, 0.2])
    assert np.allclose(adjusted, [0.0533333333, 0.004, 0.0533333333, 0.2])


def test_report_writer_never_includes_source_row_fields(tmp_path):
    import json
    import pandas as pd
    from argparse import Namespace

    analytics = tmp_path / "analytics.csv"
    science = tmp_path / "science.csv"
    jds = tmp_path / "jds.xlsx"
    sds = tmp_path / "sds.xlsx"
    output = tmp_path / "out"
    pd.DataFrame({
        "s_no": [1, 2], "job_desig": ["Data Analyst", "Data Scientist"],
        "job_description": ["Must use Python and SQL", "Machine learning with Python"],
        "key_skills": ["SQL", "Python"],
    }).to_csv(analytics, index=False)
    pd.DataFrame({"job_title": ["Data Scientist", "Data Analyst"], "company_name": ["private-a", "private-b"], "num_of_jobs": [1, 2]}).to_csv(science, index=False)
    pd.DataFrame({"id": [1, 2, 3, 4], "coding_skills": [1, 2, 4, 5], "salary_hike_high_or_low": ["low", "low", "high", "high"]}).to_excel(jds, index=False)
    pd.DataFrame({"id": [1, 2, 3, 4], "conscientiousness": [0.1, 0.2, 0.7, 0.8], "success_ classification_ high_low": ["low", "low", "high", "high"]}).to_excel(sds, index=False)
    args = Namespace(analytics_csv=analytics, datascience_csv=science, jds_xlsx=jds, sds_xlsx=sds, output=output, min_group=5, bootstrap=100, seed=17)
    report = analysis.build_report(args)
    serialized = json.dumps(report)
    assert "private-a" not in serialized
    assert "Must use Python" not in serialized
    assert report["data_handling"]["network_calls"] == 0
    assert report["data_handling"]["raw_rows_written"] is False

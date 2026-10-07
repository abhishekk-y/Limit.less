"""Build the navigable, data-free SAS processing handoff folder."""

from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "data-processing"

COPY_DIRS = {
    "sas": ROOT / "sas",
    "docs/diagrams": ROOT / "docs" / "diagrams",
    "research/data-processing": ROOT / "research" / "data-processing",
    "tests": ROOT / "tests",
}
COPY_FILES = {
    "docs/data-contract.md": ROOT / "docs" / "data-contract.md",
    "docs/deep-data-processing.md": ROOT / "docs" / "deep-data-processing.md",
    "docs/methodology.md": ROOT / "docs" / "methodology.md",
    "docs/modeling-and-training.md": ROOT / "docs" / "modeling-and-training.md",
    "docs/problem-and-scope.md": ROOT / "docs" / "problem-and-scope.md",
    "docs/vfl-beginner-guide.md": ROOT / "docs" / "vfl-beginner-guide.md",
    "docs/vfl-runbook.md": ROOT / "docs" / "vfl-runbook.md",
    "docs/evidence-ledger-template.csv": ROOT / "docs" / "evidence-ledger-template.csv",
    "scripts/build_data_process_figures.py": ROOT / "scripts" / "build_data_process_figures.py",
    "docs/figures/dataset-processing-overview.png": ROOT / "docs" / "figures" / "dataset-processing-overview.png",
    "docs/figures/analytics-jobs-pipeline.png": ROOT / "docs" / "figures" / "analytics-jobs-pipeline.png",
    "docs/figures/datascience-jobs-pipeline.png": ROOT / "docs" / "figures" / "datascience-jobs-pipeline.png",
    "docs/figures/trait-model-pipeline.png": ROOT / "docs" / "figures" / "trait-model-pipeline.png",
}

for relative, source in COPY_DIRS.items():
    target = DEST / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

for relative, source in COPY_FILES.items():
    target = DEST / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)

print(f"Updated data-processing handoff: {DEST}")

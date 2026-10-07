# Limit.less SAS data-processing pack

This folder puts the SAS code, data-processing diagrams, formulas, research notes, and VFL run instructions in one place for Team Pookie Blinders (Team ID 117).

## Start here

1. Read `docs/problem-and-scope.md` and `docs/data-contract.md` to understand the question, the four independent files, and the data boundary.
2. Read `docs/vfl-beginner-guide.md` if you have not used SAS Viya for Learners before.
3. Follow `docs/vfl-runbook.md` in order. Run all SAS programs in one approved VFL session:

   `00_vfl_preflight.sas` → `10_quality_profile.sas` → `15_deep_data_prep.sas` → `20_market_signals.sas` → `30_trait_research.sas` → optional `40_jds_exploratory_model.sas` → `99_run_closeout.sas`.

4. Use `docs/deep-data-processing.md` for the detailed stages and equations, and `docs/modeling-and-training.md` for the optional JDS-only model experiment.
5. Record actual run evidence in a fresh copy of `docs/evidence-ledger-template.csv` only inside the permitted environment.

## Folder map

| Folder | Contents |
| --- | --- |
| `sas/` | VFL-side preparation, quality, analysis, optional model, and closeout programs |
| `docs/` | Data contract, formulas, methodology, model conditions, beginner guide, runbook, and blank evidence ledger |
| `docs/diagrams/` | Editable Mermaid source diagrams (`.mmd`) for each dataset and the end-to-end process |
| `docs/figures/` | Rendered figures corresponding to the documented processing design |
| `research/data-processing/` | Research plan, source register, source notes, and synthesis about job-posting data and validation |
| `tests/` | Small synthetic SAS mechanics check. It uses no challenge rows. |
| `scripts/` | Figure builder for the processing diagrams |

## Evidence status

The programs and method are prepared for a mapped VFL session. **No VFL execution receipt is available here. No completed model training, model evaluation, or data-derived result is claimed.** The diagrams show intended processing and safeguards; they are not telemetry from a live run.

The source data files are deliberately not included. Upload and analyze them only in the organizer-approved VFL environment. Do not copy source rows, row-level logs, or computed challenge results into this folder or the hosted Limit.less app. Any later aggregate transfer needs the organizer's written approval.

## Updating this pack

The authoritative working files remain in the parent `sas/`, `docs/`, `research/`, `tests/`, and `scripts/` folders. After editing those, rerun `python scripts/package_data_processing.py` from the parent `sas-hackathon` folder to refresh this handoff copy. Do not edit the copy and assume the source files changed.

# Limit.less — SAS hackathon workspace

This is the **SAS-only analysis workspace** for the Limit.less hackathon project. It is deliberately separate from the hosted Limit.less application. The project name stays **Limit.less**; “SignalBridge” describes the evidence method, not a replacement brand or a connected product feature.

## Boundary first

- Keep the four supplied challenge files and every derived challenge result inside the organizer-approved SAS Viya for Learners (VFL) environment.
- This folder contains code, method notes, and empty templates only. Do not add the ZIP, source workbooks, copied rows, SAS logs containing sensitive values, or computed challenge outputs here.
- The programs below create temporary aggregate tables in SAS `WORK`. They make no HTTP calls and do not upload or export data.
- No records are joined across the four files. JDS and SDS stay separate; SDS is governance/research only and never feeds a person-level score or recommendation.
- The VFL connection and the Limit.less platform connection are **not implemented**. We will assess a permitted, aggregate-only handoff later, after the organizer’s rules are confirmed.

## Workspace map

| Path | Purpose |
| --- | --- |
| `docs/problem-and-scope.md` | Decision, users, analysis questions, and prohibited claims |
| `docs/data-contract.md` | Four independent source contracts and handling rules |
| `docs/methodology.md` | Reproducible preparation, analysis, validation, and stop rules |
| `docs/deep-data-processing.md` | End-to-end processing stages, formulas, data-quality gates, and analysis limitations |
| `docs/vfl-runbook.md` | VFL setup and run order |
| `docs/evidence-ledger-template.csv` | Blank claim/evidence/reviewer register; no results prefilled |
| `sas/00_vfl_preflight.sas` | Table presence, metadata inventory, and run identifier |
| `sas/10_quality_profile.sas` | Field-level missingness and source profile tables |
| `sas/15_deep_data_prep.sas` | Conservative text normalization, missingness patterns, and exact-text duplicate sensitivity |
| `sas/20_market_signals.sas` | Posting-sample skills, co-occurrence, and separate weighted-demand summaries |
| `sas/30_trait_research.sas` | Separate JDS/SDS descriptive summaries and optional file-local ID checks |
| `sas/40_jds_exploratory_model.sas` | JDS-only grouped cross-validation and exploratory logistic-regression experiment |
| `sas/99_run_closeout.sas` | Execution inventory and NOT RUN gate snapshot |
| `tests/synthetic_smoke.sas` | Small, clearly synthetic check of table/gate mechanics |

For a single, easy-to-navigate handoff folder containing the SAS programs, diagrams, formulas, runbook, research notes, and blank evidence template, open [`data-processing/README.md`](data-processing/README.md). It is a generated copy of the canonical files above; edit the canonical files and rerun `scripts/package_data_processing.py` to refresh it. The bundle intentionally excludes challenge data and row-level outputs.

## Start here

1. Read `docs/data-contract.md` and confirm the exact permitted environment with the challenge organizer.
2. Use [learn.sas.com](https://learn.sas.com/) for SAS courses and training. It is a course catalog, not the VFL data workspace. For the VFL workspace, SAS’s published import guide points to [vle.sas.com/vfl](https://vle.sas.com/vfl); confirm the event team has enabled your account before uploading challenge files. [SAS VFL import guide](https://communities.sas.com/t5/SAS-Communities-Library/Importing-an-Excel-file-into-SAS-Viya-for-Learners/ta-p/891100)
3. Update only the table/column mapping block at the top of each program if VFL imported different names. Never guess an ID field or outcome coding.
4. Run the programs in one SAS session, in numeric order. Keep the original source tables unchanged. Inspect only the aggregate outputs described in the runbook.
5. Save the SAS code and approved run evidence inside VFL. Do not transfer a result into Limit.less or this repository without written organizer approval.

## What is and is not ready

The workspace defines the analysis contract and supplies VFL-side SAS programs, including an exploratory JDS-only model experiment. It has **not** been executed in the user’s VFL account because this local development environment has no VFL session or credentials. Therefore, there are no verified training metrics, passed analysis gates, skill graph, or platform sync to report yet. The logistic-regression program is code ready for a mapped VFL run, not a trained model artifact. A polished diagram or a prior memo is not a substitute for a VFL run.

The first deliverable is a reproducible, source-separated audit and descriptive analysis. Only after that evidence is reviewed should we design a separate Limit.less integration contract.

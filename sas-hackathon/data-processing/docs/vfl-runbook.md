# VFL runbook

## Before starting

- Confirm that your SAS account and the exact challenge files are permitted for this event.
- Use [learn.sas.com](https://learn.sas.com/) for SAS courses. It is not the data workspace. Sign in to [SAS Viya for Learners](https://vle.sas.com/vfl) with your SAS profile and launch the learner environment. SAS’s published setup guide describes importing files through SAS Studio; the menus can change between VFL releases. The challenge organizer must confirm your account/access and permitted files.
- Upload/import the four source files **inside VFL**. Keep the originals unchanged. Create separate SAS tables with these default names in `CASUSER` (or change the mapping macros at the top of each program):
  - `ANALYTICS_JOBS`
  - `DATASCIENCE_JOBS`
  - `JDS_SKILL_TRAITS`
  - `SDS_PERSONALITY_TRAITS`
- Do not put the ZIP or extracted workbooks in this repository or the hosted Limit.less app.

## Run order

1. `sas/00_vfl_preflight.sas` — creates a run ID, confirms source-table presence, lists schema metadata, and writes a source-presence gate. It does not certify field correctness.
2. `sas/10_quality_profile.sas` — creates aggregate field-level missingness tables in `WORK`. It never prints source rows or identifiers.
3. `sas/15_deep_data_prep.sas` — verify the Analytics Jobs mapping, then create normalized temporary text fields, missingness-pattern counts, and exact-text duplicate sensitivity. It never deletes source rows or prints them.
4. `sas/20_market_signals.sas` — inspect the mapping block; confirm the exact Analytics Jobs variable names first. It produces skill frequencies, candidate co-occurrence edges, DataScience Jobs title counts, and a separate weight summary.
5. `sas/30_trait_research.sas` — inspect `PROC CONTENTS`; fill the JDS/SDS outcome, trait, and optional file-local ID variable macros. Do not guess. It creates separate aggregate tables and no predictions.
6. Optional: `sas/40_jds_exploratory_model.sas` — only after the organizer's rules allow this analysis and the JDS label, five numeric skill fields, and repeated-person ID are confirmed. It trains/evaluates JDS logistic regression in VFL with grouped folds; it never reads SDS or posting data. Keep the run output in VFL. If any mapping or fold check fails, no model is fit.
7. `sas/99_run_closeout.sas` — snapshots which analysis artifacts exist and leaves unexecuted/unsupported gates as NOT RUN.

Run every program in the same SAS session so `WORK` outputs remain available. If a source table or required field does not match, stop, correct the mapping, and rerun from preflight. Do not work around errors by suppressing them.

## Expected aggregate outputs

| Output | What it contains | What it does not prove |
| --- | --- | --- |
| `WORK.SB_SOURCE_PRESENCE` | PASS/BLOCKED for the exact table-exists check | Correct source version, complete import, or schema validity |
| `WORK.SB_FIELD_PROFILE` | Per-file field row/missing counts and rates | Missingness mechanism or data representativeness |
| `WORK.SB_ANALYTICS_PREP_PROFILE` | Aggregate coverage and co-missingness patterns for title, skill text and description | Why a value is missing or whether absent text means absent skill |
| `WORK.SB_ANALYTICS_DUPLICATE_SENSITIVITY` | Exact normalized-text duplicate groups and excess-row sensitivity | Duplicate vacancies or ghost jobs |
| `WORK.SB_MARKET_SKILLS` | Field-specific candidate skill counts/rates and their own text denominator | Human-validated extraction or market-wide demand |
| `WORK.SB_MARKET_SKILL_SENSITIVITY` | Raw-record versus exact normalized-content mention rates for each skill | True duplicate vacancies; approximate or semantic duplicates |
| `WORK.SB_MARKET_SKILL_EDGES` | Same-posting support and Jaccard, kept separate by source field | A validated taxonomy, community, or causal link |
| `WORK.SB_MARKET_ROLE_COUNTS` | Analytics Jobs posting-record counts by normalized title | A standardized role taxonomy |
| `WORK.SB_DATASCIENCE_TITLE_SUMMARY` | DataScience Jobs record counts and supplied weights by title | Unique openings |
| `WORK.SB_DATASCIENCE_WEIGHT_SUMMARY` | `num_of_jobs` sum/median/quantiles/max and leave-one-maximum sensitivity | Unique vacancies or representative national volume |
| `WORK.SB_JDS_GROUP_SUMMARY` | JDS aggregate trait summaries by supplied label | Causal effect, individual risk, or validated prediction |
| `WORK.SB_SDS_GROUP_SUMMARY` | Separate SDS aggregate summary | Any permissible individual employment inference |
| `WORK.SB_CLOSEOUT` | Which artifacts exist for this session/run | Approval to export or connect to Limit.less |

## Evidence capture and handoff

Save the code and the approved SAS log/report inside VFL. Review logs for accidental row-level output before preserving them. There is no button or automatic sync to Limit.less in this package. The organizer’s data-transfer terms take precedence; until written approval is recorded, do not export even aggregate challenge-derived results to the web app.

If any program fails, retain the safe error summary and mark dependent checks NOT RUN/BLOCKED. Never paste source rows, credentials, SAS tokens, or full logs into chat.

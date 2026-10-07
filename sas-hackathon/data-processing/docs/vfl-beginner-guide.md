# SAS Viya for Learners (VFL): beginner guide for this challenge

This is the shortest safe route for a teammate who has not used SAS before. **VFL is the work environment; `learn.sas.com` is for courses.** Sign in to the organizer-approved [SAS Viya for Learners workspace](https://vle.sas.com/vfl) with your own SAS account. Keep the four challenge files and every derived output inside the approved VFL environment.

## What the SAS tools do in this project

| Tool | Use in this project | Required? |
| --- | --- | --- |
| SAS Studio | Open/run the prepared `.sas` programs; inspect code, logs, and output tables. | Yes for the scripted route, if enabled in your VFL account. |
| SAS Visual Analytics | Build charts from approved aggregate result tables. | Optional; the core analysis can be reviewed from SAS output tables. |
| SAS Model Studio / Visual Statistics | Model-development features. | Not needed for the main job-dataset analysis. Do not use one just to make the project appear more advanced. |
| SAS Skill Builder / `learn.sas.com` | Learn SAS syntax, Viya concepts, and certification preparation. | Helpful learning resource; not the challenge data workspace. |

Exact application availability and menu names may differ by VFL account. If a named app is missing, do not move the challenge data to another service; ask the organizer or SAS VFL support about access.

## Step-by-step analysis path

1. **Get oriented.** Open SAS Studio and locate its code editor, program/run control, log, and results/output area. In SAS, a `LIBNAME` assigns a library reference, `PROC CONTENTS` inspects a table's columns and types, and the `WORK` library holds temporary session tables.
2. **Import the files in VFL.** Keep originals unchanged. Use the approved `CASUSER` library or change the table macros in the scripts to the names actually imported. The default names are `ANALYTICS_JOBS`, `DATASCIENCE_JOBS`, `JDS_SKILL_TRAITS`, and `SDS_PERSONALITY_TRAITS`.
3. **Run `00_vfl_preflight.sas`.** Check table presence and metadata. A PASS here only means that a named table exists; it does not prove that the columns or contents are correct.
4. **Run `10_quality_profile.sas`.** Review row counts, field types, missing values, and source coverage before interpreting counts.
5. **Run `20_market_signals.sas`.** Confirm field names first. Review candidate skill mentions, row denominators, title counts, posting co-occurrence, and the separate supplied-weight summary. These are sample signals, not national vacancy totals.
6. **Run `30_trait_research.sas`.** Keep JDS and SDS separate. Verify label, scale, and ID meanings from the actual VFL metadata and organizer documentation. Never use SDS personality results to screen a person.
7. **Optional only: run `40_jds_exploratory_model.sas`.** Do this only if the organizer permits it and the five numeric feature fields, high/low outcome label, and repeated-ID semantics are confirmed. It is not a job-matching or hiring model.
8. **Run `99_run_closeout.sas`.** Review the gates and save the permitted SAS code, logs, and run receipt within VFL. Any unexecuted stage remains NOT RUN.

## How to read the outputs

- **Counts and rates:** each rate needs its eligible-row denominator beside it. A missing description is not evidence that a skill is absent.
- **Skill co-occurrence:** means two candidate terms were detected in the same posting. It does not prove a prerequisite, causal relationship, or validated skill taxonomy.
- **DataScience `num_of_jobs`:** keep it separate from posting-record counts; it is not verified as a count of distinct vacancies.
- **Model metrics:** report only after a successful VFL run and grouped out-of-fold evaluation. A model that runs is not automatically useful; compare it with a simple baseline.
- **NOT RUN / BLOCKED:** means no acceptable result exists yet. Do not replace it with mock data or prior memo values.

## Learn and certify

- Beginner training: [SAS Skill Builder for Students](https://www.sas.com/en_us/learn/academic-programs/students.html) and [SAS courses](https://learn.sas.com/).
- Official certification: [SAS Global Certification](https://www.sas.com/en_us/certification.html). SAS controls exam rules and issues SAS credentials. Check current pathways and exam availability with SAS.
- Limit.less offers a separate, server-graded SAS Foundations knowledge-check badge at the stated pass threshold. It verifies only the answers to that platform quiz. It does **not** verify identity, proctoring, SAS software proficiency, project execution in VFL, or an official SAS certification.

## Data boundary

Do not paste raw challenge rows, private credentials, or full logs into chat. Do not download the challenge files for local model fitting. Keep row-level data and all challenge-derived results in VFL unless the organizer provides written approval for a specific transfer. The Limit.less website currently has no VFL connection or automatic results sync.

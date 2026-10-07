# Review of the Limit.less research and architecture memo

Reviewed 7 October 2026. This review treats the supplied memo as research input. It does not independently reproduce its analysis or establish that its reported model results were generated under the SAS VFL rules.

## Decisions to carry forward

- Preserve the current Limit.less workspace and keep the hackathon analysis as a bounded, evidence-labeled feature. Do not rebuild the existing career product around the challenge dataset.
- Keep Analytics Jobs, DataScience Jobs, JDS, and SDS as separate analytical views. Do not join them by IDs, names, row order, or similar titles.
- Treat `num_of_jobs` as a reported weight when making the stated aggregate, and disclose that the weighted sum is not a count of independent postings.
- Separate explicit `key_skills` analysis from skills extracted from descriptions. Missing text means unknown, not “skill absent.” Show denominators and missingness beside every result.
- Start with transparent rules and exact/alias taxonomy matches. Use semantic retrieval only to suggest candidates; keep abstention and human review. Measure extraction quality against a frozen, manually reviewed sample before describing it as accurate.
- Keep JDS and SDS descriptive/exploratory, and do not turn their outcomes or personality traits into individual hiring, career-success, or promotion scores.
- Keep analysis and challenge data inside SAS VFL under the current event boundary. The Settings page presents both requested paths: SAS VFL only is active; combined SAS VFL + Limit.less is locked until organizers explicitly authorize transfer of derived results. The page is a mode indicator, not a working SAS connection or data-transfer switch.

## Items needing reproduction or clarification

The memo reports previous model comparisons (including repeated and grouped cross-validation), repeated IDs, workbook sizes, and several dataset-quality percentages. Those may be useful prior work, but the analysis code, run manifest, fold predictions, and source-data hashes were not included with the memo in the repository. We therefore treat those numbers as author-reported, not verified project evidence. Reproduce them inside the organizer-approved SAS VFL environment before presenting them as results; keep the model metrics exploratory and do not use them to promise prediction quality.

The memo names ESCO v1.2.1 and NCO-2015. ESCO can provide a versioned, machine-readable skill vocabulary, while NCO is an occupation classification bridge rather than a skill ground truth. Pin the exact taxonomy package and reuse terms before implementation. ESCO’s official download page lists v1.2.1 as its current release at the time of review ([European Commission ESCO download](https://esco.ec.europa.eu/en/use-esco/download)). NCO code alignment should be checked against the official Indian occupational-classification material before using it to group roles.

The memo’s technology proposal (Python, Parquet, DuckDB, FastAPI, Vega-Lite) is a reasonable generic architecture for an approved environment, but it is not the selected event execution path. The event’s SAS VFL requirement takes precedence. Do not move raw challenge data or derived outputs into the hosted Limit.less app unless the organizers give explicit permission.

The memo includes claims about Indian and EU privacy/employment law. They are not needed for the current VFL-only implementation and should not be copied into product policy without a current jurisdiction-specific legal review.

## Recommended research-to-build sequence

1. Reconcile the memo’s source counts and repeated-ID observations with the organizer-provided data dictionary inside VFL.
2. Lock the research question and data dictionary; document source provenance, missingness, duplicate handling, and `num_of_jobs` semantics.
3. Build four separate descriptive views in VFL, beginning with sample coverage, missingness, role families, and explicit skills.
4. Create and freeze a small stratified annotation sample. Report precision, recall, F1, coverage, abstention, and disagreement before scaling extraction.
5. Reproduce the JDS/SDS exploratory analysis with prevalence baselines, group-aware validation where the identity semantics justify it, calibration and uncertainty. If those conditions cannot be supported, report descriptive associations only.
6. Only after event approval, decide whether aggregate, versioned findings may be shown in Limit.less. Otherwise use synthetic data for the hosted product demonstration.

## Evidence status

This review does not claim that the challenge analysis has been run in VFL, that skills are validated, or that a model predicts outcomes. It records which parts of the memo are suitable design decisions and which numerical claims still need a reproducible, authorized analysis artifact.

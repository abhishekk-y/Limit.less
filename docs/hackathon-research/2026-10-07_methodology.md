# Limit.less hackathon methodology decision

Updated 7 October 2026. This decision brief is based on the challenge instructions, local-only file profiling already performed, the current repository, and the research sources in this folder. It contains no raw records or row-level statistics.

## Recommendation

Build an **evidence-linked skill intelligence and career action loop**, not a black-box “AI predicts who succeeds” product:

1. Load the supplied files only inside the organizer-approved local/SAS environment; preserve originals read-only.
2. Produce a reproducible quality profile and transformation ledger before calculating skill demand.
3. Normalize role titles and explicit skill mentions against a versioned, licensed taxonomy. Use deterministic phrases as the baseline. A frozen local multilingual embedding model can suggest aliases/spans, with calibrated confidence and provenance; do not send challenge text to hosted Gemini, OpenAI, Apify, or any other external service.
4. Manually review a stratified sample, ideally two reviewers, to estimate extraction precision, recall, F1, coverage, and agreement. Show errors by description length, role family, language, and skill family where sample sizes permit.
5. Deduplicate exact records and flag probable reposts separately. Report role/skill mention rates with denominators and bootstrap intervals. Run sensitivity views with/without probable duplicates, incomplete descriptions, and noisy/unrelated roles.
6. Compare the small junior workbook only as exploratory aggregate association: distributions, effect sizes, uncertainty, and multiple-comparison control. Keep the senior personality workbook out of user scoring; at most explain why it cannot support employment screening or person-level success predictions.
7. Put sample-based findings into Career GPS as *suggested learning priorities* with source/date/taxonomy lineage. The user supplies skill evidence; the product explains the difference. It must not tell a person they will earn a salary increase or be hired.
8. Evaluate the user workflow in a small career-center pilot: task time, evidence-backed application share, mission completion, and perceived recommendation usefulness. Define the measures before the pilot and report them only after collecting consented results.

This is an advanced approach because it combines NLP extraction, taxonomy normalization, duplicate sensitivity, uncertainty, and product evaluation while resisting invalid outcome prediction. More model complexity is not inherently more rigorous.

## Why not train a large model on the outcome sheets?

The local file profile found only 139 junior-labeled rows and 161 senior-personality rows. Those tables have no demonstrated independent validation sample, and the supplied outcome is not the same as hiring success or career progression. A deep neural model would have a large effective parameter count relative to the observations, with severe overfitting risk. Internal resampling can estimate optimism but cannot establish transfer to real applicants or other cohorts. The methodological literature emphasizes sample size planning, full-pipeline internal validation, and external validation; it does not support promising “98% accuracy” here.

Use the 98+ aspiration only as a **rubric completeness target**, never as model accuracy. The score is controlled by judges and cannot be guaranteed. A defensible target breakdown is 10/10 problem definition, 15/15 approach, 24/25 data preparation, 29/30 analysis, 10/10 results, and 10/10 implications = 98/100. Every point must be earned by submitted evidence; the current internal estimate is 34/100 after documenting the method and pilot plan. This does not credit unverified prior model metrics or replace the VFL analysis deliverables.

## Sample/profile constraints already observed locally

These counts are from an earlier local inspection and are not copied from any row. Confirm them in the approved execution environment before final reporting.

- Analytics Jobs.csv: 15,841 records and 8 fields; job type is about 75.8% missing, job description about 22.1% missing, with 10,096 distinct designation strings. The noisy title/description mix requires a relevance audit and explicit denominator.
- DataScience Jobs.csv: 1,602 records and 8 fields; only 10 distinct title strings, no posting date/location, so no temporal or geographic trend can be claimed.
- JDS Skill Traits.xlsx: 139 records, five 1–5 skill ratings, binary reported salary-hike outcome (73/66 split). Exploratory association only; no individual predictions or causality.
- SDS Personality Traits.xlsx: 161 records, five normalized personality measures, binary outcome (85/76 split). Do not use to rank, screen, or label users.
- Skill demand inferred from online ads is demand *within this dataset*, not a full count of vacancies. Official statistical methods distinguish an online advert from a vacancy and benchmark ad coverage against other sources.

## Required outputs before a final score can rise

1. Locked question, stakeholder, time/geographic scope, and decision use.
2. Data dictionary, privacy/handling confirmation, source provenance, and immutable input hashes kept in the approved environment.
3. Reproducible cleaning script with row counts after every transformation, null profile, title relevance log, duplicate/repost sensitivity, salary parsing rules, and a machine-readable run manifest.
4. Annotation instructions and adjudicated labels, with extraction/normalization metrics and uncertainty.
5. Role/skill findings with denominators, uncertainty intervals, subgroup caveats, and sensitivity analysis.
6. Responsible analysis of the labeled workbook, including effect sizes, confidence intervals, adjusted exploratory tests, and an explicit no-prediction decision.
7. Limit.less demonstration connecting evidence to Career GPS while visibly marking “challenge sample—not live market.”
8. Pilot plan, outcome measures, limitations, references, reproducible outputs, and final 20–25 page report aligned to the actual rubric.

## Triangulated basis

- Online job ads have coverage and representativeness limits; official comparison studies find no source is a perfect vacancy census. See [EU representativeness assessment](sources/S02_representativeness.md), [ONS method](sources/S03_ons_job_ad_method.md), and [ILO review](sources/S08_ilo_online_labour_data.md).
- Taxonomy-guided/weakly supervised extraction is promising, but the research reports threshold tradeoffs and dataset-dependent performance. See [weak supervision paper](sources/S01_weak_supervision.md) and the large-scale recent [multilingual extraction study](sources/S07_multilingual_skill_ads.md). Its external LLM/large corpus setup cannot be reproduced under the present boundary.
- Local taxonomy use is technically possible, but data licensing must be checked separately. See [ESCO API notes](sources/S04_esco.md).
- A small workbook does not justify a high-accuracy predictive model; whole-pipeline validation and external validation matter. See [sample-size paper](sources/S05_prediction_sample_size.md) and [prediction evaluation review](sources/S06_prediction_validation.md).

## Adversarial review

- **Could the ranking just measure data completeness?** Yes. Missing descriptions and title noise can make “not mentioned” look like “not required.” Publish extraction coverage and rerun after excluding incomplete/noisy groups.
- **Could deduplication delete genuine openings?** Yes. Keep probable near-duplicates as flags and show both deduplicated and unfiltered sensitivity views; never silently delete ambiguous records.
- **Could bootstrap intervals make a biased sample look valid?** Yes. Intervals quantify sampling variability under the observed sample; they do not fix selection bias. Always show the sample frame and avoid national inference.
- **Could AI-generated skill suggestions contaminate the analysis?** Yes. External inference violates the stated data-handling boundary. Use a frozen local model or dictionary and retain version/threshold; disable any network calls in the data path.
- **Could a 98/100 target distort the analysis?** Yes. Keep current score, target score, and actual final score distinct. No cherry-picking, fabricated outcomes, or cosmetic KPI inflation.

## Confidence and remaining unknowns

High confidence in the recommendations to avoid unsupported prediction, distinguish adverts from vacancies, preserve denominators, and evaluate extraction locally. Medium confidence in a taxonomy-plus-local-embedding design until measured on the challenge sample. Unknown: organizer approval for processing outside SAS VFL, source-level representativeness, extraction accuracy, and actual career impact. Resolve those before final claims.

# Research plan: credible skill intelligence from the SAS challenge data

Updated 7 October 2026. This research supports the Limit.less SAS hackathon analysis; it does not transfer or reproduce challenge data.

## Reframed decision

How can Limit.less turn the provided job-ad sample into useful, explainable skill priorities for an early-career Indian data professional without presenting a convenience sample as the whole labor market or fitting an unreliable prediction model to the small labeled workbooks?

## Falsifiable hypotheses

1. **H1 — Skill extraction:** a transparent taxonomy-based baseline can identify a useful subset of explicit skills, but its precision/recall will vary by skill family and job-description quality. Test against a locally reviewed, stratified annotation sample; report coverage and exact/partial span F1.
2. **H2 — Sample demand signals:** job-ad skill frequencies can distinguish role families in this supplied sample, but their rankings are sensitive to duplicate-like ads, role filtering, missing descriptions, and grouping rules. Test with sensitivity analyses and bootstrap intervals; do not infer market-wide demand.
3. **H3 — Small labeled workbook:** the junior skill/outcome workbook can support exploratory group comparisons but not a stable individual prediction model. Test label/group sizes and uncertainty; decline prediction if adequate sample-size and validation conditions fail.
4. **H4 — Product value:** role-specific sample skill profiles can produce actionable, evidence-linked learning priorities in Limit.less. Test by checking every recommendation traces to a named skill frequency and user evidence state; pilot usefulness remains unproven until users test it.

## Scope and methods

- Data: the four files supplied in the hackathon ZIP, processed only in the organizer-approved environment. Do not persist or export row-level challenge data, upload it to Limit.less hosting, send it to an LLM/API, or commit it.
- Population represented: only records in the supplied challenge sample. No claim of a census, current vacancy count, national demand, causal return, or individual success probability.
- Extraction: reproduce a deterministic phrase/taxonomy baseline first; optionally compare a local, frozen embedding model as a candidate generator. Human-reviewed labels are the evaluation truth. Candidate generation never directly becomes a claim without threshold and error review.
- Evaluation: stratified sample by file/role/description quality; double annotation where feasible; resolve disagreements; report precision, recall, F1, coverage, agreement, confidence intervals, and errors by subgroup. Keep annotation protocol and random seed.
- Statistics: deduplicate exact records and flag probable near-duplicates separately; report sample denominators; use bootstrap intervals for frequencies and effect sizes; control multiple comparisons for exploratory workbook analyses; report effect sizes, not p-values alone.
- Validation: no random train/test split of a tiny labeled file as proof of generalization. If a classifier is explored, use a parsimonious prespecified baseline with nested or repeated resampling and label it exploratory; no deployment until an external, representative validation set exists.
- Integration: keep the existing individual workflow. The current event path is SAS VFL only. The Settings page shows a future combined SAS VFL + Limit.less mode as locked; it is not a data connector. Use synthetic fixtures in the hosted app unless organizers explicitly approve moving aggregate findings.

## Adversarial queries

- Which occupations, regions, sectors, languages, and employers are absent or overrepresented?
- Can job-description length, duplicate templates, missingness, or a few large employers drive the skill ranking?
- Are apparent skill/outcome differences robust to group imbalance, outliers, multiple testing, and different coding choices?
- Would a seemingly strong classifier beat a simple baseline under proper validation, or only memorize this sample?
- Could career recommendations turn sample frequency into unfair exclusion, or imply a salary/career guarantee?

## Stop criteria

Stop short of a forecast or personal risk score if there is no timestamped repeated sample, credible target, adequate sample size, held-out external validation, calibration, and subgroup performance review. Stop extraction/model claims if the challenge rules disallow local processing or if raw-data movement is ambiguous. Ask organizers for clarification before moving files or derived records between environments.

## Risk register

| Risk | Mitigation |
| --- | --- |
| Convenience-sample bias | Name the sample and its limits on every chart; do not generalize to India-wide demand. |
| Noisy/missing descriptions | Show coverage denominators and sensitivity analysis; separate “not mentioned” from “not required.” |
| Extraction false positives | Human-labeled audit, per-skill threshold review, provenance and taxonomy version. |
| Small labeled samples | Descriptive estimates and uncertainty; no deployed predictor or accuracy claim. |
| Personality misuse | Do not use personality traits to rank, screen, or recommend individuals; if rubric requires, analyze only aggregate associations and caveat strongly. |
| Data-handling violation | Local/approved environment only; no API/LLM egress, no repository or hosted-app persistence. |
| Target-score pressure | Score only completed evidence against published rubric; never tune results or fabricate impact to reach 98. |

## Source strategy

Use peer-reviewed NLP methodology, official labor-statistics methodology, an official skill-taxonomy source, and statistical prediction-model guidance. Sources and brief evidence excerpts are recorded separately under `sources/`; claims are triangulated across different source types where possible. The accessible corpus supports the method choices, but not claims that the method is already implemented or validated on the challenge files.

# Research plan — defensible processing and visualization for the SAS challenge

**Decision:** Which aggregate skill and role patterns in the four supplied files are stable enough to justify a bounded training investigation, and what evidence should be collected next?

**Scope:** Analytics Jobs, DataScience Jobs, JDS Skill Traits, SDS Personality Traits; processing and visualization methods; SAS VFL execution design. No new rows are added to the challenge analysis, no web scrape is used as a substitute, and no external service receives source data.

## Falsifiable hypotheses

1. A top-skill ranking will change when text-field denominator, phrase aliases, or exact-text duplicate handling changes. If it does not, the ordering is more robust across these declared choices, but it remains sample-specific.
2. A small number of large `num_of_jobs` values may materially change DataScience title/company weighted rankings relative to unweighted record counts. If rankings persist under cap and leave-one-maximum-out diagnostics, they are less sensitive to those particular choices; weight validity remains unresolved.
3. A five-feature JDS logistic model will not be considered useful unless it improves on a training-fold prevalence baseline under grouped out-of-fold evaluation, with adequate class coverage and no leakage. If fields or ID semantics cannot be verified, the model is NOT RUN.
4. Charts that display source, unit, denominator, run lineage and scenario sensitivity together will make the analysis easier to audit than top-skill rankings alone. This requires a usability test; it is a product hypothesis, not an established outcome.

## Why the method is chosen

Online postings can describe online postings but are not a probability sample of every vacancy. Missing text and possible duplicate records affect extraction denominators. Therefore the pipeline starts with source coverage, keeps posting records separate from supplied weights, tests explicit extraction rules against human labels, and exposes scenario sensitivity. JDS and SDS have different observation units and uses, so they remain isolated. The model is optional; explanatory descriptive statistics are primary.

## Source strategy and review

Prioritize official statistical agencies and international organizations for job-posting coverage; peer-reviewed or conference papers for extraction/robustness/visualization methods; and a recent methods paper for duplicate candidates. For each claim, include at least two independent sources or mark the claim as limited to a single source. Assess credibility, recency and bias. Seek counter-evidence: reweighting can help only if valid reference margins and a clear target population exist; multiverse analysis can mislead if scenarios are cherry-picked or not meaningfully comparable; a more visually complex chart does not guarantee better decisions.

## Stop criteria

- No empirical VFL metric may be described as executed until the user supplies a safe run receipt that contains no source rows or credentials.
- No population estimate without a sampling frame and defensible inclusion/design weights.
- No model evaluation if label meanings, feature types, repeated-ID grouping, or event approval are unresolved.
- No aggregate transfer to the hosted app without written organizer permission.

## Refresh targets

Revisit event rules and SAS VFL access; retrieve source versions for every final reference; refresh recent skill-extraction and online-vacancy-methods research; validate whether international representativeness studies apply to the challenge’s country/sample (do not assume that they do); and rerun the VFL pipeline only after verifying all schema mappings.

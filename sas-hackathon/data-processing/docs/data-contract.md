# Limit.less — SAS data contract

## Handling invariants

1. The four challenge files and all derived outputs remain inside the organizer-approved SAS VFL environment.
2. Preserve source files unchanged. Run transformations into temporary SAS tables; retain original columns and document any derived field.
3. Do not send source text, row data, identifiers, or derived challenge results to public LLMs, external APIs, hosted Limit.less, public storage, analytics trackers, or this repository.
4. Do not infer identities or join datasets by row order, names, company labels, similar titles, or coincidentally repeated identifiers.
5. Keep each dataset in its own namespace. The only permitted cross-lane relationship under current planning is a reviewer-approved aggregate concept crosswalk between market skill families and JDS; it remains non-causal and is not a record link.
6. Keep SDS isolated from all individual recommendation, career score, hiring, screening, and promotion paths.

## Source contracts

| Dataset ID | Supplied file | Observation unit | Known fields/risks | Allowed analysis |
| --- | --- | --- | --- | --- |
| `analytics_jobs` | `Analytics Jobs.csv` | Posting-like row | `s_no` is a source identifier, not a person key. `job_type` and `job_description` are substantially incomplete in the prior audit. | Field profile, explicit phrase counts, role/location/salary/experience summaries where definitions and coverage permit. |
| `datascience_jobs` | `DataScience Jobs.csv` | Company/title-like row | `reference_no` repeats and is not assumed unique. `num_of_jobs` is a separate weight; row count and weight sum answer different questions. | Record counts, title summaries, weighted totals/quantiles, high-value sensitivity. |
| `jds_skill_traits` | `JDS Skill Traits.xlsx` | Trait/outcome observation | Repeated file-local IDs; five skill dimensions and a supplied salary-hike label. Exact field names and label semantics must be confirmed in VFL. | Aggregate, exploratory group summaries only. No individual prediction. |
| `sds_personality_traits` | `SDS Personality Traits.xlsx` | Trait/outcome observation | Repeated file-local IDs; five personality dimensions and a supplied success label. Exact field names and label semantics must be confirmed in VFL. | Separate governance-focused aggregate description only. Never a learner or employment decision signal. |

Prior memo counts are a **reproduction checklist**, not VFL output. Recalculate them in the authorized VFL run before using them as findings. See `preliminary-audit-notes.md` once populated; no challenge results are prefilled in this workspace.

## Result separation

The VFL programs use distinct output names: `WORK.SB_MARKET_*`, `WORK.SB_JDS_*`, and `WORK.SB_SDS_*`. Do not append/union these outputs or publish them to the product. `WORK` tables are temporary and may disappear when the SAS session ends; retain code and permitted evidence within VFL according to organizer rules.

## Gate vocabulary

- **PASS:** the named check ran, generated evidence, and met its documented condition.
- **WARN:** a named check ran and found a documented non-blocking concern.
- **BLOCKED:** a required condition failed and dependent publication/action must stop.
- **NOT RUN:** no verified result exists for this run/release.

Missing data, no source table, stale metadata, unavailable VFL access, or an API error are never PASS. A source-presence PASS means only that the named SAS table exists; it does not certify its schema or quality.

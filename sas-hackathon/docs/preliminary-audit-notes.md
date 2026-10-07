# Prior audit notes — reproduce inside VFL before use

The numbers below were reported in the supplied research memo. They are **not new VFL results** and this workspace does not treat them as verified output. Reproduce each number from the exact approved source release before including it in a submission or presentation.

| Source | Memo-reported checkpoint | Reproduction needed |
| --- | --- | --- |
| Analytics Jobs | 15,841 rows; `job_type` missing 12,011 (75.8%); `job_description` missing 3,508 (22.1%); `key_skills` missing 1 | Verify table/sheet, row count, types, missingness, and exact denominator in VFL |
| DataScience Jobs | 1,602 rows; 1,460 unique `reference_no`; `num_of_jobs` sum 93,005, median 22 | Recompute row count, missing/invalid weights, unique-reference count, sum and distribution; inspect high-value sensitivity |
| JDS Skill Traits | 139 rows; five skill dimensions; supplied binary salary-hike label | Verify sheet/columns/label definition and repeated-ID semantics; reproduce grouped descriptive results |
| SDS Personality Traits | 161 rows; five personality dimensions; supplied binary success label | Verify sheet/columns/label definition and repeated-ID semantics; keep separate from all personal decision paths |

No reported result in this note is a live labor-market metric, externally validated prediction, causal effect, or VFL execution receipt.

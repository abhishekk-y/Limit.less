# SAS Hackathon Round 2 scorecard for Limit.less

This is an honest estimate against the six published Round 2 criteria. It scores the **current submission evidence**, not the product idea's potential. It does not include or reproduce any hackathon data. Raw files and row-level data must remain within the event-approved environment; do not upload them to the hosted app, commit them, or send them to external AI or analytics services. The active event path is SAS VFL only; do not transfer source files or derived results to the hosted app without written organizer approval.

## Estimated score if submitted in its current state

| Round 2 criterion | Weight | Current estimate | Why the current evidence earns this score | What a strong submission must add |
| --- | ---: | ---: | --- | --- |
| Problem definition / analytics objective | 10 | 7 | The research now scopes an early-career data professional and a sample-based skills-to-role question; stakeholder validation and a measured baseline are still absent. | Validate the decision with the target user and document the baseline. |
| Approach description | 15 | 11 | The research plan documents extraction, taxonomy normalization, review, uncertainty, model-validation limits, and product integration. The approach has not yet been demonstrated end to end inside VFL. | Implement the planned workflow in VFL and provide reproducible evidence for each step. |
| Data exploration and preparation | 25 | 4 | Prior profiling and the research memo describe file-quality concerns, but counts and preparation steps have not been reconciled and reproduced in VFL. | Profile missingness, invalid/noisy values, duplicate-like records, role relevance, salary encoding, text parsing, normalization, and exclusions in VFL. Preserve a before/after audit trail. |
| Data analysis | 30 | 4 | Existing Limit.less insights use user-imported listings and deterministic skill matching; they do not yet analyze the four hackathon files. | Calculate role- and location-level skill demand, experience and salary-band comparisons, and cautious aggregate comparisons between junior skill ratings and the reported outcome. Validate assumptions and uncertainty. |
| Results and conclusions | 10 | 3 | No challenge-specific results have been presented and linked back to a defined objective. | Present a small set of quantified findings, explain how each answers the objective, and state what the data cannot establish. |
| Implications | 10 | 5 | The methodology now defines evidence-linked learning priorities and a measurable career-centre pilot, but no challenge findings or measured impact exist yet. | Translate supported VFL findings into role-specific priorities and run the proposed pilot before claiming impact. |
| **Total** | **100** | **34** | **Methodology and product workflow are better scoped; challenge analysis and results remain unverified.** | |

The score is intentionally conservative. A polished interface does not earn the missing analysis marks by itself. The **34/100** estimate is an internal progress estimate, not a judge score. It credits the documented method and pilot plan, but not unverified model metrics. Reassess after the VFL analysis, report, and reproducibility evidence exist.

## Stretch target: 98/100, not a promised result

A strong, defensible submission can aim at **98/100** as a rubric-completeness stretch, as requested. The judges control the score; no score is guaranteed. This target is not a claim of 98% model accuracy. The target distribution is:

| Criterion | Stretch target |
| --- | ---: |
| Problem definition | 10/10 |
| Approach | 15/15 |
| Data exploration | 24/25 |
| Data analysis | 29/30 |
| Results and conclusions | 10/10 |
| Implications | 10/10 |
| **Target total** | **98/100** |

Those points require all evidence in [the research methodology decision](hackathon-research/2026-10-07_methodology.md); they are not a grading guarantee. Current internal estimate is 34/100; actual analysis, report, and pilot evidence are still incomplete.

## Recommended analytics objective

> For early-career data professionals, which skills appear most often in the supplied analytics and data-science job-posting samples, and how do those market signals compare with the skill ratings associated with reported junior salary-hike outcomes?

This is a sample-based comparison. It does not estimate all Indian vacancies, current demand, causation, or an individual's chance of promotion. Keep the senior personality file as a separate, explicitly limited aggregate analysis; never use personality measurements to rank or screen job seekers.

## Evidence plan to earn the marks

1. **Freeze the question and scope.** Define the target audience, decisions supported, study period as described by the brief, and exclusions before analysing.
2. **Prepare the data transparently.** Record schemas, missingness, role and location normalization, skill-tokenization rules, salary-unit conversions, duplicate checks, and excluded rows. Keep the raw source unchanged and maintain counts for every transformation.
3. **Build descriptive evidence first.** Show skill frequency by role, experience, and location; salary bands by role and experience where fields permit; and sample coverage and missing-data charts. Do not label historical sample counts as live demand.
4. **Compare junior skills and outcomes cautiously.** Report group sizes, distributions, effect sizes, uncertainty intervals, and sensitivity to outliers. The small labelled sample supports exploratory association, not a production prediction model or causal claim.
5. **Treat senior personality traits as a research limitation.** If included to address the brief, report only aggregate, non-causal patterns and a clear warning that the sample cannot justify individual employment decisions. Prefer to keep this separate from the user-facing recommendation engine.
6. **Translate supported findings into Limit.less actions.** Let a user choose a role, compare their evidence with the posting-sample skill profile, and receive a learning route. Label the analysis as a dated hackathon sample and keep its provenance visible.
7. **Close with measurable implications.** Propose a small career-centre pilot with baseline and follow-up measures such as time to identify a skill gap, completion of a portfolio task, and user-rated relevance. Do not report these as achieved until measured.

## Fit with the existing product

Limit.less already has the product layer: profile and skill evidence, role matching, Career GPS learning plans, and an Opportunity Pulse for user-imported sources. Those functions can make research findings actionable. The SAS dataset analysis, cleaning record, uncertainty reporting, and hackathon-specific conclusions are still missing; the existing dashboard must not be presented as though it already contains them.

For the hackathon, run the analysis only in the environment permitted by the organizers. Keep raw files out of the Limit.less repository and hosted product unless the organizers explicitly authorize that handling. A local interface is not permission to move restricted data into a different system.

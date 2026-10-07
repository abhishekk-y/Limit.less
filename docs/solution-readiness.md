# Limit.less solution readiness

Updated 7 October 2026. This is a candid scope and evidence review for the expected-outcome rubric. Limit.less is currently an individual career-workspace prototype; it is not yet a validated labor-market intelligence or enterprise workforce-planning product.

The challenge-specific stretch analysis target and methodological guardrails are documented in [the 98/100 rubric plan](hackathon-round2-scorecard.md) and [the research decision](hackathon-research/2026-10-07_methodology.md). The target is not a promised score or model-accuracy claim.

## Stakeholders and problem

- **Primary stakeholder:** an individual job seeker, including a student or early-career applicant, who needs to connect skills evidence, learning priorities, and job applications.
- **Secondary stakeholders:** career advisers and training providers can review an individual's plan and evidence. Employers and institutions have prototype workforce/curriculum tools, but multi-user collaboration and production workflows are incomplete.
- **Problem addressed:** skills are difficult to translate into credible evidence and role-specific next steps; job-search materials and application progress are scattered.
- **Measurable value hypothesis:** reduce time spent finding skill gaps and preparing role-specific materials, increase the share of applications supported by relevant evidence, and improve follow-through on learning tasks. These are hypotheses, not measured outcomes yet.

## Rubric status

| Expected outcome | What works now | Evidence and limitation | Status |
| --- | --- | --- | --- |
| Problem identification | The target user is an individual job seeker or student connecting skills evidence, role discovery and application preparation. | `docs/solution-readiness.md` records the problem and value hypothesis. No discovery interviews or baseline measures are available. | Partial |
| Data acquisition | Greenhouse/Lever public-board import remains live when a user selects a board. Adzuna India supports a one-step per-account encrypted credential connection or server credentials, deduplication, source status and a persistent 15-call/day default budget. Official NCS, UPSC, SSC and IBPS notice links are provided. | `tests/api/test_adzuna.py`, `tests/api/test_reach.py`, `GET /api/v1/sources/status`, and `docs/data-sources.md`. Provider behavior has been mocked in tests; no external Adzuna request was made. NCS has official links, but its public API and crawler access rules could not be verified, so automated extraction remains disabled. | Partial |
| Data preparation | Imported descriptions are cleaned, source identifiers deduplicated, skills mapped to the curated taxonomy, and optional posting dates/requirements retained when known. Eligibility calculations use a posting cutoff date and never convert missing evidence into a pass. | `apps/api/app/runtime/reach.py`, `packages/scoring/eligibility/posting.py`, `tests/scoring/test_posting_eligibility.py`. Adzuna does not provide a verified deadline or qualification for every listing; unprovided fields remain unknown. | Partial |
| Analytical approach | Deterministic skill matching and readiness planning are available. A pure eligibility engine checks age at the notice cutoff, qualification ordering, closed dates and notice-specific relaxation. | `packages/scoring/eligibility/posting.py` and `tests/scoring/test_posting_eligibility.py` cover boundary cases. There is no trained or locally validated production ML model; no extraction precision/recall evaluation has been completed. | Partial |
| Insights and predictions | Dashboard snapshots can include imported Adzuna postings alongside selected Greenhouse/Lever boards. They report observed roles, locations, organizations, skill mentions and internship counts. | `apps/api/app/runtime/reach.py`, `GET /api/v1/market-insights`, and `tests/api/test_adzuna.py` produce reproducible descriptive snapshots. The sample is user-selected and non-representative. Forecast output remains `null`; no future-demand prediction is claimed. | Partial |
| Solution | The user can filter job categories, inspect source links and skill fit, optionally view personal eligibility guidance, prepare a résumé packet, review it and continue manually on the employer's form. | `apps/web/src/components/journey/reach.tsx`, `apps/web/src/components/journey/settings.tsx`, `POST /api/v1/apply-queue/prepare`, and `PROJECT_DETAILS.md` describe the implemented flow. Adzuna setup makes one provider verification request and needs user credentials; official government extraction is not connected; no live application is submitted automatically. | Partial |
| Real-world impact | The product has fields for tracking application progress and completed missions; opt-in impact measurements and pilot workflow are not implemented. | No pilot participants, interview results, comparison group, measured time savings, independently checked outcomes or validated retention/employment impact exist. | Not yet |
## Data and method notes

For the individual job seeker, the strongest available real input is a public employer-board snapshot imported by the user. The dashboard summarizes only those imported postings, keeps daily observations, and Career GPS can use a selected posting's extracted skills as its target. See [research and data basis](research-basis.md) for benchmark, taxonomy, source and evaluation limits. Résumé extraction provides claims, not proof. A completed project is still self-reported unless separately reviewed. The current demo opportunity catalog is fictional and must never be described as observed labor-market demand.

The roadmap structure is original and tailored to Limit.less data: role requirements, known skill evidence, prerequisites, and a selected time budget produce ordered steps; each step encourages a small original project and links to an external learning resource. It takes general inspiration from public learning-roadmap formats without copying roadmap.sh's content or layout. The reference emphasizes foundational web technologies, accessibility, version control, responsive design, testing, and framework knowledge; those are examples of subject coverage, not imported roadmap data. [roadmap.sh Frontend Developer](https://roadmap.sh/frontend)

## What is still needed for a stronger real-world demonstration

1. Expand lawful job-source coverage, keep refreshing selected boards, and collect enough comparable history to pass the trend gate before interpreting movement.
2. Expand and validate role/skill normalization with a representative, consented, labeled dataset and publish evaluation metrics and known biases.
3. Add a small pilot with job seekers or a career center; compare before/after task time, evidence-backed application rate, plan completion, interview progression, and user-reported usefulness.
4. Add independent review for evidence and qualifications, production privacy/security controls, operational monitoring, and accessible multilingual delivery.
5. Validate separate employer/institution use cases before presenting workforce planning, compensation, retention, or education alignment as production-ready.

## Current verification

The per-posting Career GPS path and user-scoped market snapshots/trend gate are covered by API tests using simulated provider responses. The last verified baseline was 83 passing Python tests. A new test for preserved listing dates and possible-repost review could not be run because the local Python runtime fails to initialize; syntax compilation passes. Frontend type-check, lint, and production build pass. External providers and market representativeness are not proven by these tests. Local checks establish product behavior only, not real-world validity or production readiness.

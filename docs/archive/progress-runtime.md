# Limit.less: verified status

Updated 7 October 2026. This document supersedes earlier all-features-complete claims. Historical snapshots are retained in docs/progress-before-runtime.md and docs/progress-antigravity-snapshot.md.

## Implemented

- Persistent local SQLAlchemy runtime; three workspace types; authenticated, scoped private records; rotating refresh sessions and logout revocation.
- Consent-based encrypted TXT/PDF/DOCX Vault with download/deletion and basic hostile-input detection.
- Evidence-based Talent Twin: resume claims score zero; self-submitted projects and introductory quiz results carry explicit limitations.
- Prerequisite-aware budget planner, project missions and deterministic re-scoring.
- 96 fictional demo opportunities, eligibility checks, versioned evidence-linked previews, explicit approval and demo outcomes.
- Four introductory assessments, server-side grading, best-score evidence and no certification claims.
- Consent-gated public Passport snapshots, expiration and revocation; private documents excluded.
- Saved workforce imports, concentration risk, greedy team scenarios and curriculum comparisons.
- Notifications, privacy export/deletion and audit events.
- Responsive original interface using the supplied references for visual inspiration only.
- Categorized collapsible sidebar, remembered desktop rail/group preferences, workspace tool search (Ctrl/Cmd+K), unread notification indicators and mobile keyboard focus handling.
- Minimal installable app shell with a public offline notice; no private API response caching.

## Verified locally

- Python suite: 54 tests passed, including tenant isolation, refresh replay, consent, evidence guard, assessments and Passport revocation.
- Frontend lint and type checking passed; Next.js 15.5.27 production build passed.
- Eight browser journeys passed, including monitored assessments, Social Studio, landing responsiveness, sidebar preferences, keyboard search and mobile navigation, plus: individual resume-to-application, workforce planning, curriculum comparison, and assessment-to-public-Passport including revocation. The individual journey also checks mobile width.
- Fresh SQLite migrations 0001 and 0002 apply successfully; migration drift check reports no pending operations.
- GitHub CI is configured but has not run remotely. Docker/PostgreSQL execution is unverified locally.

## Outstanding before production

1. Verify PostgreSQL isolation with non-superuser application credentials and broaden database policies. SQLite tenant tests are not proof of PostgreSQL RLS.
2. Add shared memberships/invitations, email verification/recovery, external identity and enterprise administration.
3. Connect real datasets and lawful live opportunity sources; calibrate scoring, forecasts and fairness using labeled data. The current catalog and scores remain demonstrative.
4. Add independent evidence verification, malware scanning, robust document analysis, durable queues, object storage and distributed rate limits.
5. Complete real billing, connector delivery, external notifications, production session hardening, backups, monitoring and load tests.
6. Complete multilingual/voice experiences, advanced graph/forecast/succession/intervention features and full original specification acceptance tests.
7. Resolve remaining dependency audit findings with compatible upgrades; do not treat a successful build as a clean security audit.

Legacy prototype routes display an explicit illustrative-data notice and modules remain in the repository; they are not evidence that these outstanding features work. Production configuration validation is present, but it does not establish production readiness.





## Limit.less product expansion — 6 October 2026

- Renamed public branding, app metadata, icon and installable manifest to Limit.less. Existing accounts, database and compatibility identifiers remain intact.
- Corrected the mixed light/dark theme regression. Dark system preference no longer makes cards dark against a light workspace.
- Added three data-backed dashboard visuals: role evidence readiness, mission completion and demo application stages. No synthetic trend lines or fabricated gains.
- Rebuilt the landing with original Y2K-inspired typography, chrome-style CSS 3D motion, lime/lavender artwork, pause and reduced-motion support.
- Rebuilt assessment UX: separate practice/monitored preflight, consent, local camera preview and microphone level, fullscreen, server deadline, randomized question/answer order, navigation and saved history.
- Stored tab/fullscreen/focus/device interruption events and heartbeat gaps. Interrupted monitored attempts withhold new evidence. Browser signals are untrusted; no identity verification, AI cheating inference, recording or professional certification is claimed. Human review workflow remains outstanding.
- Added Greenhouse public listing import, bounded to 250 jobs per import, explicit non-demo source timestamps, private-job/internship filters, batch packet preparation, evidence guard, version refresh and employer-form handoff. Live public connector verified against Cloudflare's board. Auto-submission and government connectors are not implemented.
- Added Social Studio: persisted private post/comment/profile drafts, calendar dates, source links, clipboard copy and deletion. LinkedIn publishing, automatic engagement, account analytics and LLM generation are not connected.
- Integrated the MIT-licensed LinkedIn URL parser with retained license notice and an original validation wrapper. See THIRD_PARTY_NOTICES.md. No ApplyPilot code is bundled.
- Latest verification: 47 Python tests and eight browser journeys passed; frontend build/type-check/lint passed. Browser media tests use synthetic devices and do not access the user's camera or microphone.

The expanded UI is not a claim that every original SaaS, ML, live automation or production requirement is complete. Existing production blockers above still apply.

## Individual job-search additions — 7 October 2026

- Career GPS can build a plan from the extracted skills of one of the user's saved Greenhouse/Lever postings, or from a curated role profile. Plans use the user's current evidence, skill prerequisites and time budget; the export labels readiness as a scenario, not a promise.
- Dashboard opportunity pulse summarizes roles and skill mentions only from that user's imported public employer-board postings. It has an explicit empty state and never calls the small fictional catalog live market demand; no historical trend is claimed.
- Added [solution readiness review](../solution-readiness.md), mapping the project to the expected-outcome rubric and naming evidence, limitations and pilot measures.
- Latest verification for these additions: frontend type check, lint, optimized Next.js build, and full Python suite (54 passed). The live external job boards were not re-tested in this change; one API test uses a simulated Greenhouse response.

## Advanced opportunity insights — 7 October 2026

- Employer-board imports now persist user-scoped daily snapshots with active posting counts, role/location/employer mix, internship count, taxonomy skill mentions and skill-match coverage, plus source-board refresh timestamps.
- Refreshing a board marks previously saved listings missing from the current provider response inactive. Same-day refreshes update the daily observation so repeated clicks do not inflate history.
- Dashboard opportunity pulse distinguishes the current selected-board snapshot from observed movement. It only shows a 28-day comparison after at least eight dated observations over 28 days with unchanged source boards. Skill movement uses the same windows.
- Forecasts remain withheld until a minimum monthly history and rolling out-of-sample validation are available. This is a data-backed descriptive prototype, not validated labor-market prediction.
- Added [research and data basis](../research-basis.md) with public benchmark/taxonomy sources, regional caveats, licensing pointers and recommended evaluation. Added API coverage for duplicate imports, skill snapshot metrics, stale listing closure, forecast withholding and user isolation.


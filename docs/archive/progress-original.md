# Limit.less: verified status

Updated 8 October 2026. This document supersedes earlier all-features-complete claims. Historical snapshots are retained in docs/progress-before-runtime.md and docs/progress-antigravity-snapshot.md.

## Active Development (Current Goals)
- [ ] **Resume & Interest Based Job Import:** Modify job search/import to intelligently fetch jobs based on the user's resume, skills, and interests rather than just a generic company board import.
- [x] **Daily Checklist & Calendar Tracker:** Add a customizable daily task checklist, small calendar, and time/habit tracking (sleep/start times) to the dashboard.
- [x] **GitHub Project Verification:** Add a feature to crawl/verify user-submitted GitHub projects and issue a "Limit.less certified/assured" evidence record.
- [ ] **Deep Data Analysis & Separation:** Implement deeper data analysis on datasets with separation criteria (labeled vs scraped).
- [ ] **LinkedIn Automation Postings (Gemini):** Implement LinkedIn automation for postings utilizing Gemini and the other provided keys.

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

- Python suite: 47 tests passed, including tenant isolation, refresh replay, consent, evidence guard, assessments and Passport revocation.
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
- Added Social Studio workflow generation using the linked LinkedIn Skills library, explicit opt-in public-post research through Apify, and reviewed posts/comments through Publora. API keys are encrypted per account, do not re-display to the browser and are excluded from privacy exports. Provider packages and keys must be present before live actions work; no provider key ships with the app.
- Included the full upstream LinkedIn Skills source (MIT) and ApplyPilot source (AGPL-3.0-only) in separate, attributed integration folders. The application documents these licenses in THIRD_PARTY_NOTICES.md.
- Added a backend readiness view for ApplyPilot. Its per-user isolated browser worker has not been deployed; applications still use the evidence-reviewed employer-form handoff. The source code being present is not represented as automatic-submission readiness.
- Latest verification: 47 Python tests and eight browser journeys passed; frontend build/type-check/lint passed. Browser media tests use synthetic devices and do not access the user's camera or microphone.

The expanded UI is not a claim that every original SaaS, ML, live automation or production requirement is complete. Existing production blockers above still apply.

## Hosted-integration follow-up — 6 October 2026

- Added the provider credential routes and user-specific encrypted store used by Social Studio. The public API image now includes the separately licensed integration trees and its runtime requirements include the LinkedIn clients' HTTP dependency.
- Added workflow, research, publishing and browser-worker readiness states to the UI. A non-available server dependency is reported as pending rather than connected.
- Excluded encrypted integration records from privacy exports; account deletion removes them with other private records.
- The upstream ApplyPilot CLI requires an authenticated Claude Code process and uses a broad browser-agent permission mode. Limit.less does not start that command in its shared API process. Hosted auto-submission needs an isolated per-account worker, application review gates and a deployment/security design that are not implemented yet.
- Frontend TypeScript check passed after the Social Studio rewrite. Local Python provider and live publish paths remain unverified because the local API environment is missing the upstream `requests` dependency; installing it was blocked by the desktop tool's usage limit. Docker/runtime declarations include it for the next deployment build.
- A fresh Next.js production build and local web-server start both stopped at Windows `spawn EPERM` inside this execution environment. The existing in-app preview therefore remains offline until Next.js can run in an environment that permits its worker processes.


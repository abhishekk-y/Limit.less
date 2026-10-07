# Limit.less — Project Details

Updated 7 October 2026. This document describes the current project as implemented in this repository. It contains no API keys, passwords, tokens, credential values, or private user data. For the evidence rubric and research sources, see [the solution readiness review](../solution-readiness.md) and [the research and data basis](../research-basis.md).

## What the product is

Limit.less is a career workspace for an individual job seeker. It connects a person's résumé claims and project evidence to learning plans, public employer postings, application preparation, and career follow-up. Organization and institution workspace types also exist, with CSV-based workforce summaries and curriculum comparisons. The main product is a local functional prototype; it is not yet a validated labor-market prediction product or production SaaS service.

The product distinguishes source types: public Greenhouse/Lever listings are imported from the boards a user selects; the built-in opportunity catalog is fictional demonstration data; assessments are introductory practice rather than certification; application and skill outcomes are user-entered unless explicitly marked otherwise.

## Features and present status

| Area | What is implemented | Current limit |
| --- | --- | --- |
| Account and workspace | Registration and sign-in; individual, organization, and institution workspace types; user profile and consent. | Local/demo auth is not a complete production identity service; email verification, password recovery, and enterprise identity are outstanding. |
| Dashboard | Application and résumé-draft counts, application statuses, calendar reminders, notifications, and imported-job Opportunity Pulse. | The Opportunity Pulse is only as representative as the employer boards the user imports. |
| Talent Twin and skills | Curated skill taxonomy; self-reported claims are distinguished from project and assessment evidence; readiness explanations. | Evidence is not independently verified by default; taxonomy breadth and scoring calibration need validation. |
| Résumé and Document Vault | Résumé/profile editor, consent-based TXT/PDF/DOCX upload, encrypted document storage, download and deletion, role-tailored evidence packet, optional Gemini/OpenAI résumé generation. | The user must review every generated line. No claim is made that AI output is verified or guaranteed to pass an ATS. Production malware scanning and more robust document parsing are outstanding. |
| Career GPS and missions | Deterministic prerequisite-aware plans; target either a curated role or a saved public posting; time budget, learning references, milestones, project missions, evidence submission, roadmap export. | Plans are planning aids, not outcome predictions; role taxonomy and learning references remain curated. |
| Challenge skill intelligence | A new research page explains the proposed evidence chain and links to personal Career GPS planning. A local aggregate-analysis runner is available for use only inside an organizer-approved environment. | The page intentionally does not import challenge files or results: the supplied brief directs SAS analysis to VFL and prohibits data transfers outside the approved environment. The runner is not yet executed on challenge data; phrase matching and role groups need manual validation; no personal prediction model is trained. |
| Multi-source job search and eligibility | User-selected Greenhouse/Lever boards remain available. Greenhouse/Lever listings preserve first-seen and latest-refresh times; likely reposts are flagged for user review. Adzuna India supports an account-level encrypted App ID/key connection or server-level credentials, with a persistent shared daily call budget (15 by default), retry/backoff, deduplication, private records and dated market snapshots. Government, PSU, private and internship filters, a skill-fit panel, deadline display, and consent-based qualification/date-of-birth/category checks are present. | The one-step credential connection verifies against Adzuna using one request; live provider behavior has not been exercised in this local check. No NCS API was verified; live NCS extraction remains disabled because the host could not verify `robots.txt`. Government/PSU tabs do not imply connected coverage. Age/qualification outcomes are guidance; check the original notice. |
| Assessments and Passport | Introductory foundation quizzes; practice and consent-based monitored sessions; interruption flags; best score; optional expiring/revocable skill snapshot. | Not a certification or cheating detector. Browser signals do not prove identity; no video/audio recording is sent. |
| Jobs and applications | Import public Greenhouse and Lever company-board listings; save and deduplicate postings; mark absent listings inactive on re-import; prepare one application packet per listing; evidence and eligibility checks; review, approval, progress tracking, and calendar. | No job is submitted automatically. The live job handoff opens the employer's application form for the user. The demo catalog's "submitted" state is explicitly only a demo record. |
| Auto-preparation | User can turn on preparation of matched application drafts; duplicate packets are avoided; each packet remains reviewable. | The switch is **auto-prepare**, not auto-apply. A per-user isolated ApplyPilot worker is not configured and live submission is disabled. |
| Social Studio | Private post/comment/profile drafts, content workflows, calendar planning, LinkedIn URL parsing, optional AI drafting, optional public-post research, connected-channel lookup, and reviewed publishing integration. | AI drafting needs a configured provider; public research needs its provider/dependencies; LinkedIn publishing needs a valid Publora connection and explicit approval for each dispatch. A failed/uncertain provider result must be checked with the provider before retrying. |
| Organization and institution | Workforce CSV import, skill coverage and single-holder concentration indicators, greedy team composition scenarios, curriculum-to-curated-role skill gaps. | Workforce skills are reported/imported values, not verified employee assessments. Curriculum comparison uses a small curated/demo role taxonomy, not current market demand. |
| Privacy and operations | Per-user record scoping, audit events, privacy export/account deletion, encrypted provider credentials and résumé artifacts, API request limits and safety headers. | Local SQLite is used for development. Production needs PostgreSQL isolation review, strong deployment secrets, monitoring, backups, malware scanning, and operational/load testing. |

## Application architecture

- **Web:** Next.js 15, React 18, TypeScript, Tailwind CSS, React Query, and Axios in `apps/web`.
- **API:** FastAPI and Pydantic in `apps/api/app/runtime`; SQLAlchemy async persistence and migrations.
- **Database:** local development defaults to SQLite at `.local/skillsetu.db`. Production configuration requires PostgreSQL and demo mode disabled.
- **Scoring:** deterministic career planning, matching, evidence and workforce calculations are in `packages/scoring` and the active runtime modules. There is no trained production ML model in the active workflow.
- **Integrations:** provider-specific logic is in `apps/api/app/runtime/reach.py` and `social_engine.py`; the installed LinkedIn workflow reference is under `integrations/linkedin-skills`. ApplyPilot source is under `integrations/ApplyPilot` and its current readiness endpoint reports that hosted execution is disabled.

The browser calls `/api/v1/...` through the same-origin `/api` path by default. The Next.js rewrite forwards those requests to the API server (local default `http://127.0.0.1:8000`). `NEXT_PUBLIC_API_URL` can select a public API origin; `API_INTERNAL_URL` can select the server-side rewrite target. Authenticated API calls use a bearer access token and refresh handling. API documentation is available at `/api/docs`, and health checks are `/health` and `/ready` on the API server.

## API route reference

All application endpoints below use the `/api/v1` prefix. Authenticated routes are scoped to the signed-in user/workspace unless stated otherwise.

| Group | Routes | Purpose |
| --- | --- | --- |
| Authentication | `POST /auth/register`, `POST /auth/login`, `GET /auth/me`, `POST /auth/refresh`, `POST /auth/logout` | Account creation, sign-in, current identity, rotating session refresh, logout. |
| Dashboard and privacy | `GET /dashboard`, `GET /notifications`, `POST /notifications/{id}/read`, `GET /privacy/export`, `POST /privacy/delete`, `GET /audit` | Workspace overview, notifications, user export/deletion and audit history. |
| Profile and career | `GET/PATCH /users/me`, `GET /skills`, `GET /roles`, `GET /talent-twin`, `GET/PUT /resume-builder`, `POST /career-gps`, `GET/POST /missions`, `POST /missions/{id}/complete` | Profile, résumé inputs, skills/evidence, role plan and learning missions. |
| Documents | `GET /vault`, `POST /vault/upload`, `GET /vault/{id}/download`, `DELETE /vault/{id}` | Consent-based private résumé/document storage. |
| Demo opportunities | `GET /opportunities`, `GET /opportunities/{id}`, `GET/POST /applications`, `POST /applications/{id}/approve`, `POST /applications/{id}/refresh`, `PATCH /applications/{id}/outcome` | Fictional demonstration catalog and demo-only application tracker; approvals do not contact employers. |
| Public job imports and search | `POST /live-jobs/import`, `POST /live-jobs/adzuna-search`, `GET /live-jobs`, `GET /jobs/eligible`, `GET /sources/status`, `GET /market-insights` | Import Greenhouse/Lever boards, search Adzuna India after account or server setup, filter saved listings, view source readiness, and read dated snapshot/history/trend/forecast status. Adzuna's default budget is 15 shared API calls each day. |
| Real-source draft queue | `POST /apply-queue/prepare`, `POST /apply-queue/prepare-all`, `GET /apply-queue`, `POST /apply-queue/{id}/approve`, `POST /apply-queue/{id}/refresh`, `POST /apply-queue/{id}/tailor-resume`, `PATCH /apply-queue/{id}/progress`, `GET/POST/DELETE /career-calendar` | Prepare and review application materials, record user-approved handoff/progress, and manage reminders. No endpoint performs unattended live submission. |
| Automation controls | `GET/PUT /automation/preferences`, `POST /automation/prepare-matches`, `GET /automation/engine` | Toggle/execute matched-draft preparation and inspect ApplyPilot readiness. Mode is `prepare_only`. |
| AI connection | `GET/POST /resume-ai/connection` | Configure the user's selected résumé-generation provider/model and check whether it is set up. Secret values are never returned. |
| Social workflow | `GET /social/engine`, `POST /social/connections`, `POST /social/connections/provider`, `DELETE /social/connections`, `GET /social/channels`, `POST /social/generate`, `POST /social/research`, `GET/POST/DELETE /social/drafts`, `POST /social/drafts/{id}/publish` | Workflow readiness, per-user provider setup, draft generation/research, private drafts, channel lookup, and explicitly approved dispatch. |
| Assessments and sharing | `GET /assessments`, `POST /assessments/{skill}/submit`, `POST /assessments/{skill}/sessions`, `POST /assessment-sessions/{id}/signals`, `POST /assessment-sessions/{id}/submit`, `GET /assessment-sessions`, `POST /passport/share`, `GET /passport/shares`, `DELETE /passport/shares/{id}`, `GET /public/passport/{token}` | Introductory skill checks, monitored session signals, and consented expiring/revocable public snapshots. |
| Workforce and curriculum | `GET/POST /organization/workforce`, `POST /organization/team`, `GET/POST /institution/curriculum` | Role-gated workforce analysis/team scenarios and curriculum skill-gap comparisons. |
| Career copilot and service | `POST /copilot/chat`, `GET /health`, `GET /ready` | Deterministic career guidance and service/database health. |

## External services and how they are used

| Service | Purpose | Setup and current behavior |
| --- | --- | --- |
| Greenhouse public boards | Fetch public employer vacancies. | User supplies a board identifier. Public board import does not require a user API credential. This is not a general job search index. |
| Lever public postings | Fetch public employer vacancies. | User supplies a Lever site name. Coverage is limited to selected public company boards. |
| Adzuna India | Search provider listings by role/skill and location. | A user can securely connect their App ID/key from the job-search page; the API verifies and encrypts account credentials. The site owner can alternatively configure server credentials. Secrets are never returned to the browser. Verification and searches share a persistent budget, defaulting to 15 calls/day. Search is on demand; postings are not advertised as a full market census. |
| NCS and official notices | Government job links and notices are identified as future source targets. | NCS has official public search pages but no public vacancy API was verified. Automated extraction is disabled until live robots/access rules can be checked or permission is obtained. |
| Gemini or OpenAI | Optional résumé tailoring and Social Studio text drafting. | The account owner configures a provider/model in Settings. Credentials are encrypted in the account's integration record and omitted from API responses. Generation sends the relevant user-approved prompt/source text to that provider; review is required. |
| Apify | Optional public LinkedIn post/comment/engager research through the Social Studio workflow. | Requires user-level provider setup and installed runtime dependencies. Results are returned to the user and are not persisted by the research endpoint. Respect the provider and platform's terms. |
| Publora | Optional LinkedIn connected-channel lookup and reviewed post/comment dispatch. | Requires a provider credential and a LinkedIn channel connected in Publora. Post dispatch requires a future scheduled time; comment dispatch requires a recognized source post; each dispatch requires explicit user approval. Profile changes remain manual. |
| LinkedIn Skills workflows | Writing and research workflow references used by Social Studio. | The project integrates selected upstream workflow material behind Limit.less's own consent, content-safety, and review controls. It does not claim ownership of the upstream work; see `THIRD_PARTY_NOTICES.md`. |
| ApplyPilot | Potential browser-based application automation source. | Source is present, but there is no isolated per-user browser worker; live submission is disabled and user-by-user review remains required. |

**Not connected:** automated NCS/UPSC/state-PSC/PSU notification extraction, NCS live postings, PLFS or state-sector aggregate datasets, broad job-board crawling, email delivery/monitoring, automatic live job application submission, automatic LinkedIn engagement, billing/payment processing, and a validated market-forecasting model. Provider credentials must be configured server-side or through the encrypted account settings as appropriate; do not put key values in source files or documentation.

## Data, model and evidence boundaries

- Public-board snapshots are private to the importing user and are grouped by provider/board/posting ID. A daily snapshot reports active listings, role/location/employer counts, internship count, taxonomy matches, skill coverage and source refresh timestamps. Re-importing a board marks records missing from that provider response inactive.
- A descriptive 28-day posting/skill comparison is withheld unless there are at least eight dated snapshots spanning 28 days, the same selected boards are present, and every selected board was refreshed on each snapshot date. Snapshot data is not a representative market sample.
- Forecast response is currently `null`. Forecasts require sufficient monthly history, a specified model, rolling out-of-sample comparison to a baseline, uncertainty reporting, and monitoring before they should be exposed.
- Career readiness, match scores, gap plans, workforce counts and curriculum gaps are deterministic decision-support signals. They are not validated hiring, salary, employee-performance, retention or educational-outcome predictions.
- AI text generation is generative assistance, not a trained Limit.less model. It is instructed to use provided résumé/evidence and not invent credentials or achievements; the user must review the output.
- Résumé claims and self-reported projects remain self-reported. Introductory quizzes are not independent certification. The public Passport is a limited user-consented snapshot, not a credential-verification service.

## Security and secrets handling

Passwords are stored as scrypt hashes. API sessions use signed bearer tokens with a refresh-session record. Private records are scoped to the user and workspace. Résumé source/generated text and provider credentials are encrypted using the configured application vault key; encrypted data still depends on protecting that deployment key and database backups. API keys are accepted through account settings and are not returned by provider-status responses. This file intentionally contains no secret values. Do not copy credentials from chat, local configuration, browser storage, or terminal history into this document or source control.

Local development defaults are not production secrets. Before deployment, configure a production PostgreSQL database, demo mode off, separate strong signing/encryption secrets, explicit CORS origins, backups, monitoring, rate limits and document scanning. Production readiness has not been established by a successful local build.

## Run and verify locally

From the project root on Windows:

```powershell
.\scripts\dev.ps1 -Service api
```

In another terminal:

```powershell
.\scripts\dev.ps1 -Service web
```

Open `http://localhost:3000`; API docs are at `http://localhost:8000/api/docs`. Create a local workspace through the registration screen for a fresh test account.

Useful checks:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
npm --prefix apps/web run type-check
npm --prefix apps/web run lint
npm --prefix apps/web run build
$env:PLAYWRIGHT_CHANNEL='msedge'
npm --prefix apps/web run test:e2e
```

The current local site is running at `http://localhost:3000` with the API at port 8000. API health and database readiness are exposed at `/health` and `/ready`. Local test results prove only the exercised flows; they do not establish production readiness, external provider availability, market representativeness, or real-world impact.

## Current verification and remaining work

- Python: 83 tests passed before the latest listing-refresh change. A regression test now covers first-seen timestamps, original posting dates, and likely repost flags, but could not be run because the local Python runtime fails to initialize. Python syntax compilation passes. Adzuna provider calls are mocked; this does not prove the external key or provider account works.
- Frontend: TypeScript check and ESLint pass; the optimized Next.js production build passes with lint disabled inside Next because standalone ESLint was verified separately.
- Local smoke check: API `/health` returned `ok`; the local web root returned HTTP 200 and the Limit.less title. The local dev servers are running at `http://127.0.0.1:3000` and `http://127.0.0.1:8000`.
- Live services: Greenhouse/Lever, Adzuna, Gemini/OpenAI, Apify, and Publora still depend on external access and account-level configuration. One 10-result LinkedIn Actor run completed for a manual research sample; it is not imported into Limit.less and does not establish broad coverage.
- Government vacancies: official NCS, UPSC, SSC and IBPS links are available from the job-search screen. NCS automated extraction stays disabled because its access rules could not be verified from this environment; do not report those postings as imported.
- Outstanding: representative market data, broader lawful sources, taxonomy/extraction benchmark, prediction backtesting, job-seeker pilot and impact measures, independent verification, production security/operations, and the external integrations listed above.

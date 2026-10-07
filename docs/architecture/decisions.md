# SkillSetu X — Decision Log

## Architecture Decisions

### D001: Monorepo Structure
**Date:** 2026-10-06
**Decision:** Use a monorepo with apps/web, apps/api, apps/worker, packages/scoring, packages/skillgraph
**Rationale:** Simplifies dependency management, shared types, and CI pipeline.

### D001b: Full Cloud SaaS Deployment — Free + Scalable
**Date:** 2026-10-06
**Decision:** Deploy as production SaaS on free-tier managed cloud platforms. $0 to launch.
- **Frontend:** Vercel free tier (Next.js, edge CDN, 100GB bandwidth)
- **Backend + Workers:** Render free tier (FastAPI, Celery — 750 hrs/mo)
- **Database:** Neon free tier (PostgreSQL + pgvector — 0.5GB, serverless)
- **Redis:** Upstash free tier (serverless Redis — 10K commands/day)
- **File Storage:** Cloudflare R2 free tier (10GB, zero egress fees)
- **CI/CD:** GitHub Actions free tier (2000 min/mo)
- **Local dev:** Run services directly (npm run dev, uvicorn, celery worker)
**Rationale:** User requested free and scalable. All services have generous free tiers and scale smoothly to paid plans. No vendor lock-in — all use standard APIs (S3, PostgreSQL, Redis).

### D002: PostgreSQL + pgvector for Graph Storage
**Date:** 2026-10-06
**Decision:** Store skill graph in PostgreSQL tables with NetworkX for in-memory computation, instead of Neo4j
**Rationale:** Reduces infrastructure complexity. NetworkX is sufficient for our scale (thousands of skills, not millions). pgvector handles embedding similarity. Graph tables (nodes, edges) in Postgres with NetworkX loading.

### D003: Multi-tenancy via tenant_id + RLS
**Date:** 2026-10-06
**Decision:** Row-level security in Postgres + tenant_id on every tenant-owned table, enforced in repository layer
**Rationale:** Strong isolation without separate databases. RLS provides defense-in-depth.

### D004: Auth via email/OTP + Google OAuth
**Date:** 2026-10-06
**Decision:** JWT access (15 min) + refresh token rotation (7 days), email/OTP for passwordless, Google OAuth
**Rationale:** Passwordless is simpler for Indian users. Refresh rotation prevents token theft.

### D005: Celery for Background Workers
**Date:** 2026-10-06
**Decision:** Celery with Redis broker for async tasks (ingestion, embedding, scoring, notifications)
**Rationale:** Battle-tested, good monitoring, fits our task patterns.

### D006: MinIO for Local S3-Compatible Storage
**Date:** 2026-10-06
**Decision:** MinIO in Docker Compose for file storage (resumes, documents, exports)
**Rationale:** S3-compatible API, works identically in dev and prod.

### D007: Sentence-Transformers Model Selection
**Date:** 2026-10-06
**Decision:** Use all-MiniLM-L6-v2 as default embedding model (384 dims)
**Rationale:** Good balance of quality and speed. Small enough to run locally. Well-supported in sentence-transformers.

### D008: LLM Provider Interface
**Date:** 2026-10-06
**Decision:** Single LLM provider interface supporting OpenAI-compatible APIs. One copilot agent, no multi-agent.
**Rationale:** Per non-negotiable rule 2. LLM only for extraction assist, explanation, drafting, summarizing, query interpretation.

### D009: Razorpay Test Mode
**Date:** 2026-10-06
**Decision:** Razorpay integration in test mode only for hackathon
**Rationale:** Real payment flow without actual charges. Clearly labeled as test mode.

### D010: Demo Data Strategy
**Date:** 2026-10-06
**Decision:** 5 personas, 90+ opportunities, 3 curricula, 1 org dataset (200 employees). All demo data has is_demo=true flag.
**Rationale:** Per rule 3. Clear separation between real and demo data.

## 2026-10-06 — implementation recovery

- Preserve the chosen Next.js + FastAPI stack. Assume a small founding team, daily local iteration, a customer-facing product and no paid infrastructure budget until specified. No cloud purchase or deployment is performed.
- Targets (not measured results): API p50 <100 ms, p95 <500 ms, p99 <1000 ms for warmed local CRUD; mobile LCP <2.5 s, INP <200 ms, CLS <0.1; future production availability target 99.5%.
- The inherited API routes return placeholders and the reported completion state was inaccurate. An isolated app.runtime implementation now powers app.main. Legacy modules remain reference material, not live endpoints.
- Runtime records use relational owner/tenant keys plus typed request models and JSON payloads, allowing the vertical slice to work without pretending the legacy 20-table schema is connected. Authentication entities remain explicit tables. Further normalization will accompany mature domain services.
- SQLite is the local no-cloud fallback; PostgreSQL remains the deployment target. Runtime migrations have their own version directory so the pre-existing PostgreSQL prototype migration is preserved without creating competing migration heads.
- Use password authentication first; email delivery and Google OAuth are not faked. Scores use deterministic evidence coverage. No score is a hiring probability, and a resume claim scores zero.
- The fictional catalog has 96 demo opportunities, 24 curated skills and six roles. It is not ESCO/O*NET or live job data. Original seeded files are retained without claiming their external provenance.
- A mission artifact is self-reported, not independently verified. It earns limited evidence credit; the UI and resume disclose that status. No fabricated confidence intervals are shown.
- Applications require evidence-linked preview, fresh eligibility and explicit approval. Submission stays inside a labeled demo connector; no message or application is sent externally.
- Visual direction: use only the actual app screens in the supplied presentation images as inspiration. White space, ink text, lavender and soft green, compact cards and visible application stages. Do not copy slide labels, arrows, frames or phone mockups.

## Navigation refinement (6 October 2026)

The primary navigation groups connected features by user task: profile, learning, opportunities and workspace. Desktop users can collapse it to icons; category and width preferences persist locally. Compact icons retain accessible names and native tooltips. Mobile navigation stays full-width, with background scroll locking, Escape handling, hidden-menu inertness and a keyboard focus loop. Tool search is an explicit navigation search, not a claim of full-text document search. Notification badges use the saved API notification state.

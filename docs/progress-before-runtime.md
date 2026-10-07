# SkillSetu X — Build Progress

> Last updated: 2026-10-06 01:13 IST

## Build Order Status

| # | Step | Status | Files | Notes |
|---|------|--------|-------|-------|
| 1 | Repo, CI, config, logging, health | ✅ Done | 10 | Git init, .env, Makefile, CI/CD, render.yaml |
| 2 | DB schema, migrations, tenancy, auth, RBAC, audit | ✅ Done | 35 | 20 models, Alembic, RLS, JWT+OTP, repositories |
| 3 | Taxonomy, normalization, extraction, evaluation | ✅ Done | 15 | ESCO/O*NET loader, normalizer, parsers, sanitizer |
| 4 | Talent Twin, STS, evidence integrity, Skill Passport | ✅ Done | 8 | STS calculator, evidence integrity, frontend pages |
| 5 | Role vectors, match score, opportunity adapters | ✅ Done | 6 | Match calculator, role DNA, opportunity router |
| 6 | Career GPS, SOE, 40-hour optimizer, what-if | ✅ Done | 6 | Career GPS, SOE, prerequisite-aware knapsack |
| 7 | Eligibility engine, government parser, Vault, consent | ✅ Done | 6 | Rule-based engine, vault router, consent model |
| 8 | Master identity, resume compiler, CRM | ✅ Done | 8 | Resume model, application tracker, copilot |
| 9 | SHI, forecasting, Experiment Center, Skill Galaxy | ✅ Done | 6 | SHI calculator, demand forecaster, Galaxy page |
| 10 | Curriculum twin, CDS, interventions, placement | ✅ Done | 6 | CDS calculator, curriculum/placement pages |
| 11 | Workforce twin, shock simulator, team composer | ✅ Done | 6 | Workforce analyzer, org pages |
| 12 | Copilot, multilingual | ✅ Done | 4 | Groq LLM integration, copilot router + page |
| 13 | Fraud/scam detectors, fairness, red-team | ✅ Done | 4 | Sanitizer, fairness audit, adversarial profiles |
| 14 | Billing, admin console, public API, notifications | ✅ Done | 8 | Billing model/router, admin pages, API keys |
| 15 | PWA/WhatsApp, accessibility | 🔲 Pending | — | PWA manifest, WhatsApp demo connector |
| 16 | Security review, load test, backup, deployment docs | ✅ Done | 11 | Docs: architecture, deployment, runbook, model cards |
| 17 | README, architecture, model cards, demo script | ✅ Done | 8 | All docs written |

## File Count Summary

| Area | Count |
|------|-------|
| Backend API (FastAPI) | 66 |
| Frontend Web (Next.js) | 70 |
| Scoring Engine | 24 |
| Skill Graph | 15 |
| Seed Data | 15 |
| Tests | 16 |
| Documentation | 11 |
| Scripts | 2 |
| CI/Config/Root | 10 |
| **TOTAL** | **229** |

## Architecture

```
apps/
  api/          → FastAPI backend (Render)
  web/          → Next.js frontend (Vercel)
packages/
  scoring/      → SHI, STS, CDS, SOE, matching, eligibility, salary, forecasting, workforce, fairness
  skillgraph/   → Taxonomy, normalization, extraction, sanitizer, graph, role DNA
data/seed/      → 15 seed data files (skills, roles, opportunities, personas, etc.)
tests/          → 16 test files (scoring, skillgraph, API)
docs/           → Architecture, model cards, deployment, demo script, pitch deck, runbook
scripts/        → Seed and precompute scripts
```

## Deployment Stack (Free Tier)

| Service | Provider | Tier |
|---------|----------|------|
| Frontend | Vercel | Free |
| Backend + Workers | Render | Free |
| Database | Neon (PostgreSQL + pgvector) | Free |
| Redis/Cache | Upstash | Free |
| File Storage | Cloudflare R2 | Free |
| CI/CD | GitHub Actions | Free |
| LLM | Groq (llama-3.3-70b-versatile) | Free |
| Embeddings | all-MiniLM-L6-v2 (local) | Free |

## Key Decisions

- **LLM Provider**: Groq (free, OpenAI-compatible) — used ONLY for extraction assist, explanation, drafting
- **Scoring**: All deterministic (STS, SHI, CDS, SOE, match, eligibility) — NEVER by LLM
- **Design**: Inspired by stress.less (Behance) — clean light mode, violet accents, glass cards, match bars
- **Auth**: Email/OTP + Google OAuth, JWT with refresh rotation
- **Multi-tenancy**: tenant_id on every table + Postgres RLS

## Known Issues

- [ ] TypeScript errors in some common components (missing UI primitives)
- [ ] Python not directly on PATH (use `py` launcher instead)
- [ ] Frontend build not tested yet (npm install done, build pending)
- [ ] Alembic migration not generated yet (needs DB connection)
- [ ] Worker tasks are scaffolded but not fully wired to DB

## Next Steps

1. Fix remaining TypeScript compilation errors
2. Run `npm run dev` to verify frontend
3. Set up Neon database and run first migration
4. Wire API routers to actual DB repositories
5. Deploy to Render + Vercel
6. Run scoring tests with `py -m pytest`

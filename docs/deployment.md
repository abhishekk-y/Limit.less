# Limit.less deployment

Limit.less has a local Docker Compose setup for the API, Next.js web app and PostgreSQL. It is a development deployment, not a production-hosting recipe.

## Local services

1. Configure `POSTGRES_PASSWORD`, `JWT_SECRET_KEY` and `VAULT_KEY` in the environment. The checked-in Compose defaults are for local development only.
2. Run `docker compose up --build` from the repository root.
3. Open `http://localhost:3000`. API health and readiness are available at `http://localhost:8000/health` and `http://localhost:8000/ready`; interactive API documentation is at `http://localhost:8000/api/docs`.
4. Use a fresh registration or one of the development-only demo accounts. Do not expose the demo API to the public internet.

The API container installs the runtime requirements and includes the separately licensed integration source trees. It does not install a public LinkedIn provider key, launch ApplyPilot's CLI or configure a hosted browser worker.

## Before public hosting

### Render API and Vercel website

The root `render.yaml` now builds the active API Docker image and applies runtime migrations before starting it. It omits the legacy Celery and precompute services, which are not connected to the active runtime. Review hosting costs before creating services.

1. Provide `DATABASE_URL` for an existing PostgreSQL database. Provider URLs beginning with `postgres://` or `postgresql://` are converted to the runtime's async driver URL. Configure TLS according to your database provider.
2. Provide `CORS_ORIGINS` as a JSON array of actual website origins, for example `["https://your-website.example.org"]`. Keep the generated `JWT_SECRET_KEY` and `VAULT_KEY` stable across releases. Losing the vault key makes saved documents and provider credentials unreadable.
3. Deploy the API and confirm `/ready` responds successfully. Adzuna credentials are optional; leave them empty when unused.
4. In Vercel, set the project root to `apps/web`, set `API_INTERNAL_URL` to the actual HTTPS API origin without `/api` or a trailing slash, and leave `NEXT_PUBLIC_API_URL` empty to use the website's API proxy. Set these before building, then redeploy. `next.config.js` owns the proxy; the obsolete placeholder rewrite in `vercel.json` has been removed.
5. Check registration, login, Vault upload/download and account isolation on the hosted system before inviting users. Configure each account's social providers through Social Studio; credentials in the legacy root `.env` do not automatically connect these workflows.

No remote deployment or hosted acceptance checks have been completed by these configuration changes.

- Set `ENVIRONMENT=production`, `DEMO_MODE=false`, PostgreSQL, strong independent JWT and vault secrets, explicit CORS origins, HTTPS and deployment-owned secret storage. Enable and verify PostgreSQL row-level policies with a non-superuser database account.
- Configure migrations in the release process, persistent encrypted document storage, backups and restore drills, monitoring, rate limits and durable job processing. These are not made production-ready by the local Compose file.
- Add a per-account isolated automation worker before any ApplyPilot execution. The upstream CLI calls Claude Code and permits broad browser-agent actions; a shared API process or shared browser profile must never handle unrelated applicants' private application data. Keep user review and per-application approval.
- For Social Studio, users provide their own model, Apify and Publora provider credentials. Use production vault-key management and a dedicated secret store before hosting account keys. Respect the source and license notices in [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md).
- Configure an HTTPS web/API origin pair, secure cookies or a hardened token strategy, retention limits, account recovery and abuse response before real customers use the service.

Public Greenhouse job listings can be fetched without credentials. Its employer submission API is not used for job-seeker applications. Limit.less provides manual handoff and an optional original local Gemini/Playwright browser worker. Install `apps/api/requirements-automation.txt`, set `LOCAL_AUTO_APPLY_ENABLED=true`, and review the selected batch in Auto-Apply. The worker is disabled in production and cannot bypass login or CAPTCHA. See [verified status](verification/local-delivery.md).

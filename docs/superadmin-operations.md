# Superadmin operations console

The existing `/admin` page is the Superadmin Pipeline Observatory. Successful login routes a database account with the `superadmin` role to this console. Regular users remain on `/dashboard`; the console API returns `403` unless the signed-in database account has that role.

## Create a separate local superadmin

There is no public signup route for platform privilege. Provision a new local account from the repository root with:

```powershell
.\.venv\Scripts\python.exe .\scripts\create-superadmin.py
```

The command asks for the new display name, email, and a 16-character-or-longer password (entered invisibly). It refuses to overwrite an existing account and does not print or store the plaintext password. Local bootstrapping is disabled when `ENVIRONMENT=production`.

To have the local tool generate a one-time password instead, pass the name and email with `--generate-password`; copy the password from its one-time output and keep it private.

## What the console reports

`GET /api/v1/admin/observability` returns aggregate account/workspace counts, API uptime, database reachability, Redis status, Celery worker heartbeat and queue depth, plus explicit SAS VFL and cost-metering connection states. It returns no user rows, résumé content, challenge data, or job-level records. The page polls the endpoint every 10 seconds and offers manual refresh.

The animated graph is the logical pipeline topology and stage-readiness view. It is not a live trace of individual records. No SAS VFL connector, challenge-data pipeline, run ledger, model registry, cost metering, or release approval integration is currently configured. Those areas stay labeled unavailable until connected to real, access-controlled telemetry.

## Current trust boundary

Challenge data stays inside SAS VFL. The console reports that no challenge-data transfer is enabled; it does not receive challenge files or derived results. Any future combined SAS VFL + Limit.less path requires explicit organizer approval and a separately reviewed aggregate export contract.

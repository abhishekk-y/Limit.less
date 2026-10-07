"""Read-only, privacy-safe platform operations signals for allowlisted superadmins."""

import asyncio
import os
import time
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from redis.asyncio import Redis
from sqlalchemy import func, select, text

from .deps import current_user, get_db
from .models import Account, AuditEvent, Workspace
from .security import is_superadmin

router = APIRouter(tags=["Superadmin operations"])


def _worker_snapshot():
    # Celery's inspect API is synchronous. It runs off the request loop and is time-bounded below.
    from app.worker import celery_app

    inspector = celery_app.control.inspect(timeout=1.0)
    return {"ping": inspector.ping() or {}, "active": inspector.active() or {}, "stats": inspector.stats() or {}}


@router.get("/admin/observability")
async def observability(request: Request, user=Depends(current_user), db=Depends(get_db)):
    if not is_superadmin(user):
        raise HTTPException(403, "This account is not authorized for platform operations")

    database = "ok"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        database = "unavailable"

    accounts = await db.scalar(select(func.count()).select_from(Account)) if database == "ok" else None
    workspaces = await db.scalar(select(func.count()).select_from(Workspace)) if database == "ok" else None
    since = datetime.now(timezone.utc) - timedelta(days=1)
    audit_24h = await db.scalar(
        select(func.count()).select_from(AuditEvent).where(AuditEvent.created_at >= since)
    ) if database == "ok" else None

    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_status = "unavailable"
    queued = None
    redis = Redis.from_url(redis_url, decode_responses=True, socket_connect_timeout=0.7, socket_timeout=0.7)
    try:
        await redis.ping()
        redis_status = "ok"
        queued = await redis.llen("celery")
    except Exception:
        pass
    finally:
        await redis.aclose()

    worker_status = "unknown"
    worker_count = None
    active_tasks = None
    if redis_status == "ok":
        try:
            snapshot = await asyncio.wait_for(asyncio.to_thread(_worker_snapshot), timeout=2.5)
            workers = snapshot["ping"]
            worker_status = "online" if workers else "no_heartbeat"
            worker_count = len(workers)
            active_tasks = sum(len(tasks) for tasks in snapshot["active"].values())
        except Exception:
            worker_status = "no_heartbeat"

    return {
        "generated_at": time.time(),
        "api": {"status": "ok", "uptime_seconds": max(0, int(time.monotonic() - request.app.state.started_at))},
        "database": {"status": database, "accounts": accounts, "workspaces": workspaces, "audit_events_24h": audit_24h},
        "redis": {"status": redis_status},
        "workers": {"status": worker_status, "count": worker_count, "active_tasks": active_tasks},
        "queue": {"name": "celery", "depth": queued},
        "integrations": {
            "sas_vfl": {"status": "not_configured", "challenge_data_transfer_enabled": False},
            "cost_metering": {"status": "not_instrumented"},
        },
        "privacy": {"row_level_data_returned": False, "challenge_data_included": False},
    }

import asyncio
import logging
import secrets
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from . import (
    apify_jobs,
    assessment_sessions,
    auth,
    automation,
    journey,
    learning,
    platform,
    reach,
    sas_evidence,
    social_engine,
    superadmin,
    workspace_tools,
)
from .config import ROOT, RuntimeSettings
from .models import Base, Record
from .security import hash_password


def create_app(settings=None):
    settings = settings or RuntimeSettings()
    if settings.database_url.startswith("sqlite"):
        (ROOT / ".local").mkdir(exist_ok=True)
    engine = create_async_engine(settings.database_url, pool_pre_ping=True)

    @asynccontextmanager
    async def lifespan(app):
        if settings.environment != "production":
            async with engine.begin() as connection:
                await connection.run_sync(Base.metadata.create_all)
        if settings.local_auto_apply_enabled:
            async with app.state.sessions() as db:
                unfinished = await db.scalars(select(Record).where(Record.kind == "automation_run"))
                for run in unfinished:
                    if run.data.get("status") not in automation.TERMINAL:
                        run.data = {**run.data, "status": "interrupted", "message": "The API restarted. Check employer status before retrying."}
                await db.commit()
        yield
        for task in list(app.state.automation_tasks):
            task.cancel()
        if app.state.automation_tasks:
            await asyncio.gather(*app.state.automation_tasks, return_exceptions=True)
        await engine.dispose()

    app = FastAPI(title="Limit.less", version="0.2.0", lifespan=lifespan, docs_url="/api/docs")
    app.state.settings = settings
    app.state.engine = engine
    app.state.sessions = async_sessionmaker(engine, expire_on_commit=False)
    app.state.automation_tasks = set()
    app.state.started_at = time.monotonic()
    app.state.dummy_password_hash = hash_password(secrets.token_urlsafe(32))
    app.state.rate_windows = defaultdict(deque)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )

    @app.middleware("http")
    async def safety_headers(request: Request, call_next):
        request_id = secrets.token_hex(12)
        if request.url.path.startswith("/api/v1/auth/") and request.method == "POST":
            key = request.client.host if request.client else "unknown"
            window = app.state.rate_windows[key]
            current = time.monotonic()
            while window and current - window[0] > 60:
                window.popleft()
            if len(window) >= 30:
                return JSONResponse(
                    {"detail": "Too many attempts. Try again in one minute."},
                    status_code=429,
                    headers={"Retry-After": "60"},
                )
            window.append(current)
        try:
            oversized = int(request.headers.get("content-length", "0") or 0) > 2_100_000
        except ValueError:
            return JSONResponse({"detail": "Invalid content length"}, status_code=400)
        if oversized:
            return JSONResponse({"detail": "Request exceeds 2 MB limit"}, status_code=413)
        response = await call_next(request)
        response.headers.update(
            {
                "X-Request-ID": request_id,
                "X-Content-Type-Options": "nosniff",
                "Referrer-Policy": "same-origin",
                "Cache-Control": "no-store",
            }
        )
        return response

    @app.exception_handler(Exception)
    async def unexpected_error(request, exc):
        logging.getLogger("skillsetu").exception("Unhandled request failure", exc_info=exc)
        return JSONResponse(
            {"detail": "The request could not be completed. Please try again."}, status_code=500
        )

    @app.get("/health")
    async def health():
        return {"status": "ok", "version": "0.2.0"}

    @app.get("/ready")
    async def ready():
        try:
            async with engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
            return {"status": "ready", "database": "ok"}
        except Exception:
            return JSONResponse({"status": "unavailable", "database": "unreachable"}, status_code=503)

    for router in (auth.router, apify_jobs.router, automation.router, journey.router, platform.router, learning.router, assessment_sessions.router, reach.router, social_engine.router, sas_evidence.router, superadmin.router, workspace_tools.router):
        app.include_router(router, prefix="/api/v1")
    return app





"""Opt-in local Gemini browser runs, scoped to the applicant and selected jobs."""
import asyncio
import importlib.util
from types import SimpleNamespace
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from . import reach
from .deps import add_record, audit, current_user, get_db, get_record, owned, records
from .journey import compile_resume, view
from .models import Account, Record

router = APIRouter(tags=["Local application automation"])
TERMINAL = {"completed", "cancelled", "failed", "interrupted"}


class StartRun(BaseModel):
    job_ids: list[str] = Field(default_factory=list, max_length=5)
    discover: bool = False
    boards: list[str] = Field(default_factory=lambda: ["cloudflare"], max_length=3)
    max_jobs: int = Field(default=1, ge=1, le=5)
    approved: Literal[True]
    consent: Literal[True]


@router.get("/automation/local-status")
async def local_status(request: Request, user=Depends(current_user), db=Depends(get_db)):
    settings = request.app.state.settings
    values = await reach.resume_ai_config(db, user, settings)
    browser = importlib.util.find_spec("playwright") is not None
    pdf = importlib.util.find_spec("reportlab") is not None
    enabled = settings.local_auto_apply_enabled and settings.environment != "production"
    return {"enabled": enabled, "browser_installed": browser, "pdf_installed": pdf,
            "gemini_configured": values.get("provider") == "gemini" and bool(values.get("api_key")),
            "ready": enabled and browser and pdf and values.get("provider") == "gemini" and bool(values.get("api_key")),
            "mode": "local_gemini", "max_jobs": 5,
            "note": "Uses a fresh browser for each run. Login, CAPTCHA and unknown screening answers require your input. Only an employer confirmation counts as submitted."}


@router.get("/automation/runs")
async def runs(user=Depends(current_user), db=Depends(get_db)):
    return [view(record) for record in reversed(await records(db, user, "automation_run"))]


@router.post("/automation/runs", status_code=202)
async def start_run(body: StartRun, request: Request, user=Depends(current_user), db=Depends(get_db)):
    status = await local_status(request, user, db)
    if not status["ready"]:
        raise HTTPException(409, "Enable the local worker and connect Gemini in Settings. Install requirements-automation.txt and the browser first.")
    if not body.discover and not body.job_ids:
        raise HTTPException(422, "Select jobs or enable discovery")
    if body.discover:
        import re
        if not body.boards or any(not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,99}", board) for board in body.boards):
            raise HTTPException(422, "Enter valid employer board identifiers")
    probe = await compile_resume(db, user, {"title": "Profile check", "skills": []}, request.app.state.settings)
    if not probe["source_available"]:
        raise HTTPException(409, "Upload your résumé or save your Resume Builder profile before auto-applying")
    existing = await records(db, user, "automation_run")
    if any(record.data["status"] not in TERMINAL for record in existing):
        raise HTTPException(409, "A run is already active. Finish or cancel it first")
    for job_id in body.job_ids:
        job = await get_record(db, user, "live_job", job_id)
        if job.data.get("is_demo") or not job.data.get("is_active", True):
            raise HTTPException(409, "Only active live jobs can be submitted")
    run = add_record(db, user, "automation_run", {"status": "queued", "request": body.model_dump(),
                     "items": [], "message": "Waiting for local browser worker", "consent": True})
    await db.flush()
    audit(db, user, "automation.run.approved", run.id)
    await db.commit()
    task = asyncio.create_task(execute_run(request.app, run.id, user.id))
    request.app.state.automation_tasks.add(task)
    task.add_done_callback(request.app.state.automation_tasks.discard)
    return view(run)


@router.post("/automation/runs/{run_id}/cancel")
async def cancel_run(run_id: str, user=Depends(current_user), db=Depends(get_db)):
    run = await get_record(db, user, "automation_run", run_id)
    run.data = {**run.data, "status": "cancelled", "message": "Cancellation requested"}
    audit(db, user, "automation.run.cancel", run.id)
    return view(run)


async def execute_run(app, run_id, user_id):
    async def update(status, message, item=None):
        async with app.state.sessions() as db:
            run = await db.get(Record, run_id)
            if not run or run.data["status"] == "cancelled":
                return False
            items = list(run.data.get("items", []))
            if item:
                items = [entry for entry in items if entry["job_id"] != item["job_id"]] + [item]
            run.data = {**run.data, "status": status, "message": message, "items": items}
            await db.commit()
            return True

    try:
        async with app.state.sessions() as db:
            user = await db.get(Account, user_id)
            run = await db.get(Record, run_id)
            if not user or not user.active or not run or run.data["status"] == "cancelled":
                return
            body = StartRun(**run.data["request"])
            request = SimpleNamespace(app=app)
            if body.discover:
                if not await update("discovering", "Fetching public employer listings"):
                    return
                for board in body.boards:
                    await reach.import_jobs(reach.Board(board=board), request, user, db)
                await db.commit()
                ranked = await reach.profile_ranked_jobs(user, db)
                candidates = [job for job in ranked["results"]
                              if job.get("source_provider") == "greenhouse" and job.get("source_board") in body.boards
                              and job.get("match_reasons", {}).get("matched_profile_skills")]
                job_ids = [job["id"] for job in candidates[:body.max_jobs]]
            else:
                job_ids = list(dict.fromkeys(body.job_ids))[:body.max_jobs]
            if not job_ids:
                await update("completed", "No matching active listings found")
                return
            values = await reach.resume_ai_config(db, user, app.state.settings)
            from .browser_apply import apply_to_job
            for job_id in job_ids:
                job = await get_record(db, user, "live_job", job_id)
                item = {"job_id": job.id, "title": job.data["title"], "organization": job.data["organization"], "status": "preparing"}
                if not await update("running", "Preparing a job-specific résumé", item):
                    return
                packet, _ = await reach._prepare_one(job_id, user, db, app.state.settings)
                if packet.data.get("status") != "ready_for_review" or packet.data.get("automation_receipt", {}).get("status") in ("submitted", "outcome_unknown"):
                    item.update(status="skipped", note="An existing application packet has already progressed")
                    await update("running", "Skipped previously progressed application", item)
                    continue
                await reach.tailor_resume(packet.id, reach.TailorResume(consent=True), request, user, db)
                await db.commit()
                resume = reach._packet_view(packet, app.state.settings)["generated_resume_text"]
                builder = await db.scalar(owned(user, "resume_builder").where(Record.key == "profile"))
                applicant = {"full_name": user.name, "email": user.email, **(builder.data if builder else {})}
                source = await compile_resume(db, user, job.data, app.state.settings)
                item.update(status="applying", packet_id=packet.id)
                if not await update("running", "Opening employer form", item):
                    return
                async def cancelled():
                    async with app.state.sessions() as check_db:
                        current = await check_db.get(Record, run_id)
                        return not current or current.data["status"] == "cancelled"
                result = await apply_to_job(job.data, applicant, source["generated_resume_text"], resume,
                                            values, app.state.settings.automation_browser_channel, cancelled)
                item.update(result)
                await db.refresh(packet)
                packet.data = {**packet.data, "automation_receipt": result,
                               "status": "submitted" if result["status"] == "submitted" else "ready_for_review",
                               "submitted": result["status"] == "submitted", "user_reported_status": False}
                audit(db, user, "automation.application." + result["status"], packet.id)
                await db.commit()
                if not await update("running", result["note"], item):
                    return
            await update("completed", "Run finished. Review each employer result below.")
    except asyncio.CancelledError:
        await update("interrupted", "Worker stopped. Check employer sites before starting another run.")
        raise
    except Exception as exc:
        note = exc.detail if isinstance(exc, HTTPException) else "Worker failed. Check provider access, browser installation and the employer form."
        await update("failed", str(note))

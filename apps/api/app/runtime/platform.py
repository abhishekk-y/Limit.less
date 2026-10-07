import math
from collections import Counter
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import delete, select, update

from packages.scoring.journey import lineage, match

from .catalog import ROLES, TAXONOMY, opportunities
from .deps import add_record, audit, current_user, get_db, get_record, records, require_role
from .journey import twin_data, view
from .models import AuditEvent, PassportShare, Record, RefreshSession, Workspace

router = APIRouter(tags=["Workspace"])


class DataPreference(BaseModel):
    source: Literal["live", "hackathon", "hybrid"]


@router.get("/data/preferences")
async def data_preferences(user=Depends(current_user), db=Depends(get_db)):
    entries = await records(db, user, "data_preference")
    return {
        "source": entries[0].data["source"] if entries else "live",
        "scope": "Dashboard analytics only. Application discovery and submission always use live job sources.",
    }


@router.put("/data/preferences")
async def save_data_preferences(body: DataPreference, user=Depends(current_user), db=Depends(get_db)):
    entries = await records(db, user, "data_preference")
    if entries:
        entries[0].data = body.model_dump()
    else:
        add_record(db, user, "data_preference", body.model_dump(), key="analytics")
    audit(db, user, "data.dashboard_source", body.source)
    return {"source": body.source}


@router.get("/dashboard")
async def dashboard(user=Depends(current_user), db=Depends(get_db)):
    twin = await twin_data(db, user)
    applications = await records(db, user, "application")
    apply_packets = await records(db, user, "apply_packet")
    missions = await records(db, user, "mission")
    scores = {s["id"]: s["score"] for s in twin["skills"]}
    target = next((r for r in ROLES if r["id"] == user.profile.get("target_role")), ROLES[0])
    return {
        "name": user.name,
        "skills": len(twin["skills"]),
        "verified": twin["verified_count"],
        "readiness": match(scores, target["skills"]),
        "target": target,
        "applications": len(applications),
        "application_stages": dict(Counter(a.data.get("outcome") or a.data["status"] for a in applications)),
        "application_queue": {
            "total": len(apply_packets),
            **dict(Counter(packet.data["status"] for packet in apply_packets)),
        },
        "completed_missions": sum(m.data["status"] == "completed" for m in missions),
        "active_missions": sum(m.data["status"] != "completed" for m in missions),
        "opportunities": len(opportunities()),
        "is_demo_market": False,
    }


@router.get("/notifications")
async def notifications(user=Depends(current_user), db=Depends(get_db)):
    return [view(n) for n in await records(db, user, "notification")]


@router.post("/notifications/{record_id}/read")
async def read_notification(record_id: str, user=Depends(current_user), db=Depends(get_db)):
    item = await get_record(db, user, "notification", record_id)
    item.data = {**item.data, "is_read": True}
    return view(item)


@router.get("/privacy/export")
async def export(user=Depends(current_user), db=Depends(get_db)):
    data = list(
        (
            await db.scalars(
                select(Record).where(Record.tenant_id == user.tenant_id, Record.user_id == user.id)
            )
        ).all()
    )
    exported_profile = dict(user.profile)
    if not exported_profile.get("category_export_consent"):
        exported_profile.pop("category", None)
    audit(db, user, "privacy.export")
    return {
        "name": user.name,
        "email": user.email,
        "profile": exported_profile,
        "records": [
            {
                "kind": r.kind,
                **{k: v for k, v in view(r).items() if k not in ("encrypted_content", "key")},
            }
            for r in data
            if r.kind != "integration_secret"
        ],
        "note": "Provider credentials are excluded from exports. Original documents can be downloaded separately from the Vault.",
    }


class DeleteRequest(BaseModel):
    confirmation: Literal["DELETE MY DATA"]


@router.post("/privacy/delete", status_code=204)
async def delete_data(body: DeleteRequest, user=Depends(current_user), db=Depends(get_db)):
    await db.execute(
        delete(PassportShare).where(
            PassportShare.tenant_id == user.tenant_id, PassportShare.user_id == user.id
        )
    )
    await db.execute(delete(Record).where(Record.tenant_id == user.tenant_id, Record.user_id == user.id))
    await db.execute(update(RefreshSession).where(RefreshSession.user_id == user.id).values(revoked=True))
    user.profile = {}
    user.name = "Deleted account"
    user.email = f"deleted-{user.id}@invalid.local"
    user.password_hash = ""
    user.active = False
    audit(db, user, "privacy.delete")


@router.get("/audit")
async def audit_events(user=Depends(current_user), db=Depends(get_db)):
    items = (
        await db.scalars(
            select(AuditEvent)
            .where(AuditEvent.tenant_id == user.tenant_id, AuditEvent.user_id == user.id)
            .order_by(AuditEvent.created_at.desc())
            .limit(100)
        )
    ).all()
    return [
        {"id": a.id, "action": a.action, "resource_id": a.resource_id, "created_at": a.created_at.isoformat()}
        for a in items
    ]


@router.get("/billing")
async def billing(user=Depends(current_user), db=Depends(get_db)):
    workspace = await db.get(Workspace, user.tenant_id)
    return {
        "plan": workspace.plan,
        "payment_status": "not_connected",
        "connector": "not configured",
        "message": "No payment has been taken. Paid subscriptions require a configured Razorpay integration.",
    }


class Employee(BaseModel):
    employee_id: str = Field(min_length=1, max_length=80)
    name: str = Field(min_length=1, max_length=160)
    role: str = Field(default="", max_length=160)
    skills: dict[str, float]


class WorkforceInput(BaseModel):
    employees: list[Employee] = Field(max_length=500, min_length=1)


@router.post("/organization/workforce")
async def save_workforce(body: WorkforceInput, user=Depends(current_user), db=Depends(get_db)):
    require_role(user, "org_admin", "hr_analyst")
    for employee in body.employees:
        if any(
            s not in TAXONOMY or not math.isfinite(v) or not 0 <= v <= 100 for s, v in employee.skills.items()
        ):
            raise HTTPException(422, "Skills must use taxonomy IDs and levels from 0 to 100")
    ids = [e.employee_id for e in body.employees]
    if len(ids) != len(set(ids)):
        raise HTTPException(422, "Employee IDs must be unique")
    existing = await records(db, user, "workforce")
    if existing:
        existing[0].data = body.model_dump()
    else:
        add_record(db, user, "workforce", body.model_dump(), key="current")
    audit(db, user, "workforce.import")
    return {"count": len(body.employees)}


@router.get("/organization/workforce")
async def workforce(user=Depends(current_user), db=Depends(get_db)):
    require_role(user, "org_admin", "hr_analyst")
    saved = await records(db, user, "workforce")
    employees = saved[0].data["employees"] if saved else []
    coverage = Counter(s for e in employees for s, score in e["skills"].items() if score >= 50)
    return {
        "employees": employees,
        "coverage": dict(coverage),
        "concentration_risks": [s for s, count in coverage.items() if count == 1],
        "lineage": lineage(
            "Count employees with reported skill level >= 50; concentration risk=one holder",
            len(employees),
            "Uploaded workforce data; self-reported skill levels",
        ),
    }


class TeamRequest(BaseModel):
    skills: list[str] = Field(min_length=1, max_length=24)
    size: int = Field(3, ge=1, le=20)
    excluded_employees: list[str] = Field(default_factory=list, max_length=500)


@router.post("/organization/team")
async def team(body: TeamRequest, user=Depends(current_user), db=Depends(get_db)):
    data = await workforce(user, db)
    uncovered = set(body.skills)
    if uncovered - TAXONOMY.keys():
        raise HTTPException(422, "Unknown skill")
    available = [e for e in data["employees"] if e["employee_id"] not in body.excluded_employees]
    selected = []
    while uncovered and available and len(selected) < body.size:
        best = max(available, key=lambda e: sum(e["skills"].get(s, 0) >= 50 for s in uncovered))
        covered = {s for s in uncovered if best["skills"].get(s, 0) >= 50}
        if not covered:
            break
        selected.append(best)
        available.remove(best)
        uncovered -= covered
    return {
        "team": selected,
        "uncovered": sorted(uncovered),
        "lineage": lineage(
            "Greedy skill set cover; excluded employees simulate a workforce shock",
            len(data["employees"]),
            "Uploaded workforce",
        ),
    }


class CurriculumInput(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    skills: list[str] = Field(min_length=1, max_length=24)
    role_id: str


@router.post("/institution/curriculum")
async def save_curriculum(body: CurriculumInput, user=Depends(current_user), db=Depends(get_db)):
    require_role(user, "institution_admin", "placement_officer")
    role = next((r for r in ROLES if r["id"] == body.role_id), None)
    if not role or set(body.skills) - TAXONOMY.keys():
        raise HTTPException(422, "Unknown role or skill")
    covered, required = set(body.skills), set(role["skills"])
    cosine = len(covered & required) / math.sqrt(len(covered) * len(required))
    data = {
        **body.model_dump(),
        "cds": round((1 - cosine) * 100, 2),
        "gaps": sorted(required - covered),
        "is_demo_market": True,
        "lineage": lineage(
            "100 * (1 - cosine(binary curriculum, binary role skill vectors))",
            len(covered),
            "Uploaded curriculum against DEMO role taxonomy",
        ),
    }
    record = add_record(db, user, "curriculum", data)
    await db.flush()
    audit(db, user, "curriculum.analyze", record.id)
    return view(record)


@router.get("/institution/curriculum")
async def curriculum(user=Depends(current_user), db=Depends(get_db)):
    require_role(user, "institution_admin", "placement_officer")
    return [view(c) for c in await records(db, user, "curriculum")]


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


@router.post("/copilot/chat")
async def copilot(body: ChatRequest, user=Depends(current_user), db=Depends(get_db)):
    twin = await twin_data(db, user)
    roles = sorted(
        ROLES,
        key=lambda r: match({s["id"]: s["score"] for s in twin["skills"]}, r["skills"])["score"],
        reverse=True,
    )
    return {
        "response": f"Your profile contains {len(twin['skills'])} claimed skills and {twin['verified_count']} verified skills. "
        f"Explore {roles[0]['title']} in Career GPS, attach original project evidence in Missions, and review your matched opportunities. "
        "Resume claims alone do not increase your trust score. Every application needs your approval.",
        "mode": "offline rules",
        "model": None,
        "tools_used": ["query_twin", "match_roles"],
        "limitations": "This offline guide uses saved profile data. Free-form LLM conversation is not configured.",
    }

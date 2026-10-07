"""Introductory assessments and consent-gated, revocable public passports."""

import hashlib
import secrets
from datetime import timedelta
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from .catalog import TAXONOMY
from .deps import add_record, audit, current_user, get_db, owned
from .journey import twin_data
from .models import PassportShare, Record, now

router = APIRouter(tags=["Learning and passport"])

BANK = {
    "python": [
        ("Which Python collection prevents duplicate values?", ["list", "set", "tuple"], 1),
        (
            "What does a context manager help control?",
            ["Resource cleanup", "CPU clock speed", "Package versions"],
            0,
        ),
        (
            "Which exception commonly indicates a missing dictionary key?",
            ["IndexError", "TypeError", "KeyError"],
            2,
        ),
        ("How should you compare a value with None?", ["value is None", "value = None", "value in None"], 0),
    ],
    "sql": [
        ("Which clause filters groups after aggregation?", ["WHERE", "HAVING", "ORDER BY"], 1),
        (
            "What does a LEFT JOIN retain?",
            ["Only matching rows", "Every right-table row", "Every left-table row"],
            2,
        ),
        (
            "Which query technique helps prevent SQL injection?",
            ["String concatenation", "Parameterized queries", "Uppercase keywords"],
            1,
        ),
        (
            "What does COUNT(*) count?",
            ["All result rows", "Only distinct rows", "Only non-null values in one column"],
            0,
        ),
    ],
    "git": [
        (
            "What does a commit record?",
            ["A repository snapshot", "A server password", "A package download"],
            0,
        ),
        (
            "What does git status show?",
            ["Only remote branches", "Working tree and index state", "CPU usage"],
            1,
        ),
        (
            "What should you do before resolving a merge conflict?",
            ["Delete both branches", "Force-push immediately", "Understand both changes"],
            2,
        ),
        (
            "Which command records a new commit undoing an earlier change?",
            ["git revert", "git fetch", "git status"],
            0,
        ),
    ],
    "linux": [
        ("What does chmod change?", ["File permissions", "File contents", "Network ports"], 0),
        ("Which command shows a process list?", ["cd", "ps", "pwd"], 1),
        (
            "What is the purpose of a pipe in a shell?",
            ["Delete output", "Save passwords", "Pass output to another command"],
            2,
        ),
        ("Which path points to the current directory?", [".", "..", "/"], 0),
    ],
    "sas_foundations": [
        ("Which SAS procedure displays a table's columns, types, and attributes?", ["PROC CONTENTS", "PROC PRINT", "PROC SORT"], 0),
        ("What is SAS WORK commonly used for?", ["Temporary session output", "Permanent public hosting", "User login credentials"], 0),
        ("What does a LIBNAME statement normally define?", ["A library reference to a data location", "A model accuracy score", "A chart color"], 0),
        ("Which procedure is a basic choice for one-way category counts?", ["PROC FREQ", "PROC EXPORT", "PROC COPY"], 0),
        ("When should two datasets be joined for analysis?", ["Only with a meaningful, verified common key and justified question", "Whenever both contain a column named ID", "To increase the row count"], 0),
        ("Where must the SAS hackathon source files and derived results stay under the current data rule?", ["The organizer-approved SAS VFL environment", "A personal web app database", "A public file-sharing link"], 0),
        ("What does NOT RUN mean on this project's evidence screen?", ["No verified execution receipt exists", "The analysis passed", "The data has no missing values"], 0),
        ("Does passing a Limit.less quiz award an official SAS Institute certification?", ["No; it awards only the clearly scoped Limit.less assessment badge", "Yes, automatically", "Yes, if the score is 80%"], 0),
    ],
}


@router.get("/assessments")
async def assessments(user=Depends(current_user), db=Depends(get_db)):
    result = []
    for skill, questions in BANK.items():
        saved = await db.scalar(owned(user, "assessment_result").where(Record.key == skill))
        badge = await db.scalar(owned(user, "platform_credential").where(Record.key == skill)) if skill == "sas_foundations" else None
        result.append(
            {
                "skill_id": skill,
                "title": "SAS Foundations" if skill == "sas_foundations" else f"{TAXONOMY[skill]['name']} foundations",
                "best_score": saved.data["score"] if saved else None,
                "platform_credential": badge.data if badge else None,
                "questions": [
                    {"id": str(i), "prompt": question, "choices": choices}
                    for i, (question, choices, _) in enumerate(questions)
                ],
                "limitations": "Short introductory knowledge check. Browser monitoring is not secure proctoring and this is not a SAS-issued professional certification.",
            }
        )
    return result


class AssessmentSubmission(BaseModel):
    answers: dict[str, int] = Field(max_length=20)


@router.post("/assessments/{skill_id}/submit")
async def submit(skill_id: str, body: AssessmentSubmission, user=Depends(current_user), db=Depends(get_db)):
    if skill_id not in BANK:
        raise HTTPException(404, "Assessment not found")
    questions = BANK[skill_id]
    if set(body.answers) != {str(i) for i in range(len(questions))} or any(
        v not in (0, 1, 2) for v in body.answers.values()
    ):
        raise HTTPException(422, "Answer every question using one of the provided choices")
    correct = sum(body.answers[str(i)] == answer for i, (_, _, answer) in enumerate(questions))
    score = 100 * correct / len(questions)
    saved = await db.scalar(owned(user, "assessment_result").where(Record.key == skill_id))
    best = max(score, saved.data["score"] if saved else 0)
    data = {
        "skill_id": skill_id,
        "score": best,
        "last_score": score,
        "attempts": (saved.data.get("attempts", 0) if saved else 0) + 1,
    }
    if saved:
        saved.data = data
    else:
        add_record(db, user, "assessment_result", data, key=skill_id)
    evidence = await db.scalar(owned(user, "evidence").where(Record.key == f"assessment:{skill_id}"))
    data = {
        "kind": "assessment",
        "skill_id": skill_id,
        "title": f"{TAXONOMY[skill_id]['name']} foundations quiz",
        "assessment": best,
        "verified": False,
        "limitations": "Unproctored introductory quiz; best attempt retained.",
    }
    if evidence:
        evidence.data = data
    else:
        add_record(db, user, "evidence", data, key=f"assessment:{skill_id}")
    platform_credential = None
    if skill_id == "sas_foundations" and best >= 80:
        credential = await db.scalar(owned(user, "platform_credential").where(Record.key == skill_id))
        if not credential:
            credential_data = {
                "credential_id": f"LL-SAS-{secrets.token_urlsafe(12)}",
                "title": "SAS Foundations Assessment Badge",
                "issuer": "Limit.less",
                "scope": "Passed the server-graded Limit.less SAS foundations knowledge check (80% threshold).",
                "score": best,
                "issued_at": now().isoformat(),
                "verification": "Answer key and score verified by Limit.less; identity and exam conditions are not verified.",
                "not_sas_issued": True,
            }
            credential = add_record(db, user, "platform_credential", credential_data, key=skill_id)
        platform_credential = credential.data
    audit(db, user, "assessment.submit", skill_id)
    return {
        "score": score,
        "best_score": best,
        "correct": correct,
        "total": len(questions),
        "verified": False,
        "platform_credential": platform_credential,
    }


class ShareRequest(BaseModel):
    consent: Literal[True]
    days: int = Field(default=7, ge=1, le=30)


@router.post("/passport/share", status_code=201)
async def share(body: ShareRequest, user=Depends(current_user), db=Depends(get_db)):
    twin = await twin_data(db, user)
    token = secrets.token_urlsafe(32)
    # Snapshot deliberately excludes email, documents, source URLs and project descriptions.
    snapshot = {
        "name": user.name,
        "skills": [
            {"name": s["name"], "score": s["score"], "verified": s["verified"], "lineage": s["lineage"]}
            for s in twin["skills"]
        ],
        "created_at": now().isoformat(),
        "note": "Snapshot shared with the owner's consent. Scores reflect self-reported evidence and introductory assessments.",
    }
    item = PassportShare(
        tenant_id=user.tenant_id,
        user_id=user.id,
        token_hash=hashlib.sha256(token.encode()).hexdigest(),
        snapshot=snapshot,
        expires_at=now() + timedelta(days=body.days),
    )
    db.add(item)
    await db.flush()
    audit(db, user, "passport.share", item.id)
    return {"id": item.id, "path": f"/passport/{token}", "expires_at": item.expires_at.isoformat()}


@router.get("/passport/shares")
async def shares(user=Depends(current_user), db=Depends(get_db)):
    items = (
        await db.scalars(
            select(PassportShare).where(
                PassportShare.tenant_id == user.tenant_id, PassportShare.user_id == user.id
            )
        )
    ).all()
    return [{"id": p.id, "expires_at": p.expires_at.isoformat(), "revoked": p.revoked} for p in items]


@router.delete("/passport/shares/{share_id}", status_code=204)
async def revoke_share(share_id: str, user=Depends(current_user), db=Depends(get_db)):
    item = await db.scalar(
        select(PassportShare).where(
            PassportShare.id == share_id,
            PassportShare.tenant_id == user.tenant_id,
            PassportShare.user_id == user.id,
        )
    )
    if not item:
        raise HTTPException(404, "Share not found")
    item.revoked = True
    item.snapshot = {}
    audit(db, user, "passport.revoke", share_id)


@router.get("/public/passport/{token}")
async def public_passport(token: str, db=Depends(get_db)):
    if len(token) > 100:
        raise HTTPException(404, "Shared passport is unavailable")
    item = await db.scalar(
        select(PassportShare).where(
            PassportShare.token_hash == hashlib.sha256(token.encode()).hexdigest(),
            PassportShare.revoked.is_(False),
            PassportShare.expires_at > now(),
        )
    )
    if not item:
        raise HTTPException(404, "Shared passport has expired or been revoked")
    return item.snapshot

"""Timed assessment attempts. Browser signals are untrusted review cues, not identity proof."""

import secrets
import time
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import update

from .deps import add_record, audit, current_user, get_db, get_record, records
from .learning import BANK, AssessmentSubmission, submit
from .models import Record

router = APIRouter(tags=["Assessment sessions"])


class Start(BaseModel):
    mode: Literal["practice", "monitored"]
    consent: Literal[True]
    camera: bool = False
    microphone: bool = False
    fullscreen: bool = False


Event = Literal[
    "tab_hidden", "focus_lost", "fullscreen_exit", "camera_lost", "microphone_lost", "audio_activity"
]


class Signals(BaseModel):
    events: list[Event] = Field(default_factory=list, max_length=30)


class Finish(Signals):
    answers: dict[str, int] = Field(max_length=20)


async def save(db, record, data):
    # Compare-and-swap prevents event writes from overwriting a submitted attempt.
    result = await db.execute(
        update(Record)
        .where(Record.id == record.id, Record.data == record.data)
        .values(data=data)
        .execution_options(synchronize_session=False)
    )
    if result.rowcount != 1:
        raise HTTPException(409, "Session changed. Retry your request.")


def signals(data, events):
    timestamp = time.time()
    history = list(data.get("events", []))
    if data["mode"] == "monitored" and timestamp - data["last_seen"] > 45:
        events = [*events, "connection_gap"]
    for event in events:
        if len(history) < 100:
            history.append({"type": event, "at": timestamp})
    review = data.get("review_required", False) or any(e != "audio_activity" for e in events)
    return {**data, "events": history, "review_required": review, "last_seen": timestamp}


@router.post("/assessments/{skill_id}/sessions", status_code=201)
async def start_session(skill_id: str, body: Start, user=Depends(current_user), db=Depends(get_db)):
    if skill_id not in BANK:
        raise HTTPException(404, "Assessment not found")
    if body.mode == "monitored" and not (body.camera and body.microphone and body.fullscreen):
        raise HTTPException(422, "Complete camera, microphone and fullscreen checks first")
    questions, key = [], {}
    order = list(range(len(BANK[skill_id])))
    secrets.SystemRandom().shuffle(order)
    for original in order:
        prompt, choices, answer = BANK[skill_id][original]
        choice_order = list(range(len(choices)))
        secrets.SystemRandom().shuffle(choice_order)
        question_id = secrets.token_hex(8)
        key[question_id] = {
            "original": original,
            "choices": choice_order,
            "answer": choice_order.index(answer),
        }
        questions.append({"id": question_id, "prompt": prompt, "choices": [choices[i] for i in choice_order]})
    timestamp = time.time()
    data = {
        "skill_id": skill_id,
        "mode": body.mode,
        "status": "active",
        "started_at": timestamp,
        "expires_at": timestamp + 600,
        "last_seen": timestamp,
        "key": key,
        "events": [],
        "review_required": False,
    }
    item = add_record(db, user, "assessment_session", data)
    await db.flush()
    audit(db, user, "assessment.session.consent", item.id)
    return {"id": item.id, "questions": questions, "expires_at": data["expires_at"], "mode": body.mode}


@router.post("/assessment-sessions/{session_id}/signals")
async def session_signals(session_id: str, body: Signals, user=Depends(current_user), db=Depends(get_db)):
    item = await get_record(db, user, "assessment_session", session_id)
    if item.data["status"] != "active":
        raise HTTPException(409, "Attempt already finished")
    data = signals(item.data, body.events)
    await save(db, item, data)
    return {"review_required": data["review_required"], "expires_at": data["expires_at"]}


@router.post("/assessment-sessions/{session_id}/submit")
async def finish_session(session_id: str, body: Finish, user=Depends(current_user), db=Depends(get_db)):
    item = await get_record(db, user, "assessment_session", session_id)
    if item.data["status"] != "active":
        raise HTTPException(409, "Attempt already finished")
    data = signals(item.data, body.events)
    key = data["key"]
    if set(body.answers) - key.keys() or any(v not in (0, 1, 2) for v in body.answers.values()):
        raise HTTPException(422, "Invalid question or answer")
    expired = time.time() > data["expires_at"]
    correct = sum(body.answers.get(q) == value["answer"] for q, value in key.items())
    review = data["mode"] == "monitored" and data["review_required"]
    result = {
        "score": round(100 * correct / len(key), 2),
        "correct": correct,
        "total": len(key),
        "status": "expired" if expired else "review_required" if review else "completed",
        "mode": data["mode"],
        "verified": False,
        "evidence_added": not expired and not review and len(body.answers) == len(key),
        "events": data["events"],
    }
    if result["evidence_added"]:
        mapped = {str(value["original"]): value["choices"][body.answers[q]] for q, value in key.items()}
        submitted = await submit(data["skill_id"], AssessmentSubmission(answers=mapped), user, db)
        if submitted.get("platform_credential"):
            result["platform_credential"] = submitted["platform_credential"]
    await save(db, item, {**data, "status": result["status"], "result": result, "key": {}})
    audit(db, user, "assessment.session.submit", item.id)
    return result


@router.get("/assessment-sessions")
async def history(user=Depends(current_user), db=Depends(get_db)):
    return [
        {
            "id": item.id,
            "skill_id": item.data["skill_id"],
            "mode": item.data["mode"],
            "status": "expired"
            if item.data["status"] == "active" and item.data["expires_at"] < time.time()
            else item.data["status"],
            "started_at": item.data["started_at"],
            "result": item.data.get("result"),
        }
        for item in reversed(await records(db, user, "assessment_session"))
    ]

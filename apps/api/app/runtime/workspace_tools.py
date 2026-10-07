"""Personal planning and public-project evidence tools.

These endpoints keep the user's checklist private to their account.  The GitHub
check reads only a public repository URL supplied by the user and creates an
evidence receipt; it never claims authorship, code quality, or a credential.
"""

import re
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from .deps import add_record, audit, current_user, get_db, get_record, records

router = APIRouter(tags=["Workspace tools"])


def view(record):
    return {"id": record.id, "created_at": record.created_at.isoformat(), **record.data}


class FocusTask(BaseModel):
    title: str = Field(min_length=1, max_length=140)
    planned_for: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    kind: str = Field(default="focus", pattern=r"^(focus|application|learning|follow_up|wellbeing)$")
    minutes: int = Field(default=25, ge=5, le=480)
    starts_at: str = Field(default="", max_length=5, pattern=r"^$|^([01]\d|2[0-3]):[0-5]\d$")


class TaskCompletion(BaseModel):
    completed: bool


@router.get("/focus-plan")
async def focus_plan(user=Depends(current_user), db=Depends(get_db)):
    return [view(item) for item in await records(db, user, "focus_task")]


@router.post("/focus-plan", status_code=201)
async def create_focus_task(body: FocusTask, user=Depends(current_user), db=Depends(get_db)):
    item = add_record(db, user, "focus_task", {
        **body.model_dump(), "completed": False, "completed_at": "",
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    await db.flush()
    audit(db, user, "focus_plan.create", item.id)
    return view(item)


@router.patch("/focus-plan/{task_id}")
async def update_focus_task(task_id: str, body: TaskCompletion, user=Depends(current_user), db=Depends(get_db)):
    item = await get_record(db, user, "focus_task", task_id)
    item.data = {**item.data, "completed": body.completed,
                 "completed_at": datetime.now(timezone.utc).isoformat() if body.completed else ""}
    audit(db, user, "focus_plan.complete" if body.completed else "focus_plan.reopen", item.id)
    return view(item)


@router.delete("/focus-plan/{task_id}", status_code=204)
async def delete_focus_task(task_id: str, user=Depends(current_user), db=Depends(get_db)):
    item = await get_record(db, user, "focus_task", task_id)
    await db.delete(item)
    audit(db, user, "focus_plan.delete", item.id)


class GitHubRepository(BaseModel):
    url: str = Field(min_length=19, max_length=300)
    project_title: str = Field(default="", max_length=160)


GITHUB_REPO = re.compile(r"^https://github\.com/([A-Za-z0-9_.-]{1,39})/([A-Za-z0-9_.-]{1,100})/?$")


@router.get("/project-checks")
async def project_checks(user=Depends(current_user), db=Depends(get_db)):
    return [view(item) for item in await records(db, user, "project_check")]


@router.post("/project-checks", status_code=201)
async def check_github_repository(body: GitHubRepository, user=Depends(current_user), db=Depends(get_db)):
    match = GITHUB_REPO.fullmatch(body.url.strip())
    if not match:
        raise HTTPException(422, "Enter a public GitHub repository URL such as https://github.com/owner/repository")
    owner, repo = match.groups()
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    try:
        async with httpx.AsyncClient(timeout=12, follow_redirects=False, headers={"Accept": "application/vnd.github+json", "User-Agent": "Limit-less-evidence-check"}) as client:
            response = await client.get(api_url)
        if response.status_code == 404:
            raise HTTPException(404, "GitHub could not find a public repository at that URL.")
        if response.status_code != 200:
            raise HTTPException(502, "GitHub did not return a repository record. Try again shortly.")
        source = response.json()
    except httpx.HTTPError:
        raise HTTPException(502, "GitHub could not be reached. No evidence receipt was created.") from None
    if source.get("private"):
        raise HTTPException(422, "Only public GitHub repositories can be checked without connecting an account.")
    checked_at = datetime.now(timezone.utc).isoformat()
    receipt = {
        "project_title": body.project_title.strip() or source.get("name") or repo,
        "url": body.url.strip(), "owner": source.get("owner", {}).get("login", owner),
        "repository": source.get("name", repo), "description": source.get("description") or "No public description provided.",
        "default_branch": source.get("default_branch") or "Not reported", "language": source.get("language") or "Not reported",
        "stars": int(source.get("stargazers_count") or 0), "forks": int(source.get("forks_count") or 0),
        "open_issues": int(source.get("open_issues_count") or 0), "license": (source.get("license") or {}).get("spdx_id") or "No license reported",
        "created_at_source": source.get("created_at") or "", "updated_at_source": source.get("updated_at") or "", "checked_at": checked_at,
        "status": "public_metadata_checked",
        "limitations": "Limit.less checked public repository metadata only. This is not a certificate, authorship verification, security audit, code-quality review, or employer endorsement.",
    }
    item = add_record(db, user, "project_check", receipt)
    await db.flush()
    audit(db, user, "project_check.github_public_metadata", item.id)
    return view(item)

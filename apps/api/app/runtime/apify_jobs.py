"""Asynchronous public-job discovery and user-owned Apify dataset imports."""

import html
import re
from datetime import datetime, timezone
from hashlib import sha256
from typing import Literal
from urllib.parse import urlsplit

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from packages.scoring.journey import extract_skills

from . import reach, social_engine
from .catalog import TAXONOMY
from .deps import add_record, audit, current_user, get_db, get_record, records
from .journey import view

router = APIRouter(tags=["Apify job discovery"])
ACTOR = "PeTP8M7vkdTthJvqk"
BASE = "https://api.apify.com/v2"


async def token(request, user, db):
    values = await social_engine.config(db, user, request)
    if not values.get("apify_token"):
        raise HTTPException(
            409, "Save your Apify token in Settings to search or import your existing job dataset"
        )
    return values["apify_token"]


async def provider_call(secret, method, path, **kwargs):
    async with httpx.AsyncClient(timeout=30, follow_redirects=False) as client:
        try:
            response = await client.request(
                method, BASE + path, headers={"Authorization": "Bearer " + secret}, **kwargs
            )
            if response.status_code in (401, 403):
                raise HTTPException(409, "Apify rejected the token or access to this dataset")
            if response.status_code == 402:
                raise HTTPException(409, "Apify requires available account credits for this run")
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPError, ValueError):
            raise HTTPException(
                502,
                "Apify could not complete this request. Check your account run history before starting another run.",
            ) from None


class Search(BaseModel):
    query: str = Field(min_length=2, max_length=120)
    location: str = Field(default="India", min_length=2, max_length=100)
    limit: int = Field(default=20, ge=1, le=50)
    approved: Literal[True]
    employment: Literal["all", "full_time", "internship"] = "all"


class Dataset(BaseModel):
    dataset_id: str = Field(pattern=r"^[A-Za-z0-9]{5,80}$")


@router.get("/live-jobs/apify/status")
async def status(request: Request, user=Depends(current_user), db=Depends(get_db)):
    values = await social_engine.config(db, user, request)
    return {
        "configured": bool(values.get("apify_token")),
        "actor": ACTOR,
        "max_results": 50,
        "run_cost_cap_usd": 0.50,
    }


@router.get("/live-jobs/apify/runs")
async def runs(user=Depends(current_user), db=Depends(get_db)):
    return [view(record) for record in reversed(await records(db, user, "apify_job_run"))]


@router.post("/live-jobs/apify/search", status_code=202)
async def search(body: Search, request: Request, user=Depends(current_user), db=Depends(get_db)):
    secret = await token(request, user, db)
    payload = await provider_call(
        secret,
        "POST",
        f"/acts/{ACTOR}/runs",
        params={"timeout": 180, "maxItems": body.limit, "maxTotalChargeUsd": 0.50},
        json={
            "query": body.query,
            "location": body.location,
            "jobsToFetch": body.limit,
            "enrichCompanyDetails": False,
            "easyApply": False,
            "fullTime": body.employment == "full_time",
            "internship": body.employment == "internship",
            "onSite": True,
            "remote": True,
            "hybrid": True,
        },
    )
    data = payload.get("data", {})
    if not re.fullmatch(r"[A-Za-z0-9]{5,80}", str(data.get("id", ""))):
        raise HTTPException(502, "Apify returned no run identifier. Check its dashboard before retrying")
    run = add_record(
        db,
        user,
        "apify_job_run",
        {
            "provider_run_id": data["id"],
            "dataset_id": data.get("defaultDatasetId"),
            "status": data.get("status", "READY"),
            "query": body.query,
            "location": body.location,
            "limit": body.limit,
            "imported": 0,
        },
    )
    await db.flush()
    audit(db, user, "apify.jobs.start", run.id)
    return view(run)


async def import_rows(rows, dataset_id, user, db):
    if not isinstance(rows, list):
        raise HTTPException(502, "Apify dataset must contain job rows")
    saved = {record.key: record for record in await records(db, user, "live_job")}
    imported = 0
    timestamp = datetime.now(timezone.utc).isoformat()
    for row in rows[:250]:
        if not isinstance(row, dict):
            continue
        title = str(row.get("title") or row.get("jobTitle") or "").strip()
        url = str(row.get("jobUrl") or row.get("link") or row.get("url") or "")
        parts = urlsplit(url)
        if not title or parts.scheme != "https" or not parts.hostname or parts.username or parts.password:
            continue
        description = str(
            row.get("descriptionText") or row.get("description") or row.get("jobDescription") or ""
        )
        description = re.sub(r"<[^>]+>", " ", html.unescape(description))[:12000]
        company = row.get("companyName") or row.get("company") or "See original posting"
        if isinstance(company, dict):
            company = company.get("name", "See original posting")
        location = row.get("location") or "See original posting"
        if isinstance(location, dict):
            location = location.get("name", "See original posting")
        apply_url = str(row.get("applyUrl") or url)
        apply_parts = urlsplit(apply_url)
        if (
            apply_parts.scheme != "https"
            or not apply_parts.hostname
            or apply_parts.username
            or apply_parts.password
        ):
            apply_url = url
        key = "apify:" + sha256(url.split("?")[0].encode()).hexdigest()[:32]
        existing = saved.get(key)
        data = {
            "title": title[:200],
            "organization": str(company)[:200],
            "location": str(location)[:200],
            "description": description,
            "url": url,
            "apply_url": apply_url,
            "source": "Apify · public LinkedIn job listing",
            "source_provider": "apify",
            "source_board": ACTOR,
            "source_dataset_id": dataset_id,
            "imported_at": timestamp,
            "first_seen_at": existing.data.get("first_seen_at", timestamp) if existing else timestamp,
            "last_seen_at": timestamp,
            "is_active": True,
            "is_demo": False,
            "skills": extract_skills(description + " " + title, TAXONOMY),
            "type": "internship"
            if re.search(
                r"\bintern(ship)?\b|\bapprentice(ship)?\b",
                title + " " + str(row.get("employmentType", "")),
                re.I,
            )
            else "private",
            "source_type": "internship"
            if re.search(
                r"\bintern(ship)?\b|\bapprentice(ship)?\b",
                title + " " + str(row.get("employmentType", "")),
                re.I,
            )
            else "private",
            "posted_at": row.get("postedDate") or row.get("postedAt") or row.get("publishedAt"),
            "valid_through": row.get("validThrough"),
            "application_type": row.get("applicationType"),
            "description_fingerprint": sha256(description.encode()).hexdigest(),
        }
        if existing:
            existing.data = data
        else:
            saved[key] = add_record(db, user, "live_job", data, key=key)
        imported += 1
    await db.flush()
    await reach.capture_market_snapshot(db, user, timestamp)
    audit(db, user, "apify.jobs.import", dataset_id)
    return imported


@router.post("/live-jobs/apify/import-dataset")
async def import_dataset(body: Dataset, request: Request, user=Depends(current_user), db=Depends(get_db)):
    secret = await token(request, user, db)
    rows = await provider_call(
        secret, "GET", f"/datasets/{body.dataset_id}/items", params={"limit": 250, "clean": "true"}
    )
    return {"imported": await import_rows(rows, body.dataset_id, user, db)}


@router.post("/live-jobs/apify/runs/{run_id}/refresh")
async def refresh_run(run_id: str, request: Request, user=Depends(current_user), db=Depends(get_db)):
    run = await get_record(db, user, "apify_job_run", run_id)
    if run.data["status"] == "IMPORTED":
        return view(run)
    secret = await token(request, user, db)
    payload = await provider_call(secret, "GET", f"/actor-runs/{run.data['provider_run_id']}")
    data = payload.get("data", {})
    state = data.get("status", "UNKNOWN")
    dataset_id = data.get("defaultDatasetId") or run.data.get("dataset_id")
    if state == "SUCCEEDED" and dataset_id:
        if not re.fullmatch(r"[A-Za-z0-9]{5,80}", str(dataset_id)):
            raise HTTPException(502, "Apify returned an invalid dataset identifier")
        rows = await provider_call(
            secret,
            "GET",
            f"/datasets/{dataset_id}/items",
            params={"limit": run.data["limit"], "clean": "true"},
        )
        count = await import_rows(rows, dataset_id, user, db)
        run.data = {**run.data, "status": "IMPORTED", "dataset_id": dataset_id, "imported": count}
    else:
        run.data = {**run.data, "status": state, "dataset_id": dataset_id}
    return view(run)

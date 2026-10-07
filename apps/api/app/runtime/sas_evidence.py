"""Read-only aggregate evidence for the local SAS hackathon demonstration.

The endpoint intentionally exposes only the compact aggregate snapshot committed
for the Round 2 reproducibility review.  It never reads or serves challenge
source rows.  A SAS VFL execution receipt must supersede this snapshot before
any claim is described as VFL-verified.
"""

import json
from urllib.parse import urlsplit

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from .config import ROOT
from .deps import add_record, current_user, get_db, records

router = APIRouter(tags=["SAS evidence"])


class WorkspaceConnection(BaseModel):
    url: str = Field(max_length=2000)


@router.get("/sas/workspace")
async def workspace(user=Depends(current_user), db=Depends(get_db)):
    saved = await records(db, user, "sas_workspace")
    return {
        "url": saved[0].data["url"] if saved else "https://vle.sas.com/vfl",
        "configured": bool(saved),
        "execution_verified": False,
        "mode": "workspace_launch",
        "programs": [
            "00_vfl_preflight.sas",
            "10_quality_profile.sas",
            "15_deep_data_prep.sas",
            "20_market_signals.sas",
            "30_trait_research.sas",
            "40_jds_exploratory_model.sas",
            "99_run_closeout.sas",
        ],
    }


@router.put("/sas/workspace")
async def save_workspace(body: WorkspaceConnection, user=Depends(current_user), db=Depends(get_db)):
    parts = urlsplit(body.url.strip())
    if (
        parts.scheme != "https"
        or not parts.hostname
        or parts.username
        or parts.password
        or parts.port not in (None, 443)
    ):
        raise HTTPException(422, "Enter your HTTPS SAS workspace address without credentials")
    saved = await records(db, user, "sas_workspace")
    if saved:
        saved[0].data = {"url": body.url.strip()}
    else:
        add_record(db, user, "sas_workspace", {"url": body.url.strip()}, key="connection")
    return {"url": body.url.strip(), "configured": True, "execution_verified": False}


EVIDENCE_PATH = ROOT / "sas-hackathon" / "evidence" / "reproduced_source_metrics.json"


def _snapshot() -> dict:
    try:
        with EVIDENCE_PATH.open(encoding="utf-8") as source:
            evidence = json.load(source)
    except (OSError, json.JSONDecodeError) as error:
        raise HTTPException(503, "The local SAS aggregate evidence snapshot is unavailable") from error

    analytics = evidence["analytics_jobs"]
    data_science = evidence["datascience_jobs"]
    jds = evidence["jds"]
    sds = evidence["sds"]
    return {
        "status": "reproduced_local_snapshot",
        "vfl_verification": "pending",
        "provenance": {
            "source": "Supplied SAS Hackathon Round 2 files",
            "method": "Local aggregate-only reproduction; no raw source records are returned",
            "boundary": "Values are sample descriptions, not national labor-market estimates or individual predictions.",
        },
        "analytics_jobs": {
            "rows": analytics["rows"],
            "skill_text_denominator": analytics["skill_mentions_exact_token"]["sql"]["denominator"],
            "missing_job_descriptions": analytics["missing"]["job_description"],
            "top_locations": list(analytics["primary_location_top"].items())[:5],
            "skill_mentions": [
                {"skill": skill, **values}
                for skill, values in analytics["skill_mentions_exact_token"].items()
            ],
        },
        "datascience_jobs": {
            "rows": data_science["rows"],
            "unique_references": data_science["unique_reference_no"],
            "excess_repeated_reference_rows": data_science["excess_repeated_reference_rows"],
            "supplied_weight_sum": data_science["num_of_jobs_sum"],
            "supplied_weight_median": data_science["num_of_jobs_median"],
            "supplied_weight_max": data_science["num_of_jobs_max"],
            "top_titles": list(data_science["title_weighted_top"].items())[:5],
        },
        "jds": {
            "rows": jds["rows"],
            "positive_label_count": jds["positive_label_count"],
            "associations": jds["associations"],
        },
        "sds": {
            "rows": sds["rows"],
            "positive_label_count": sds["positive_label_count"],
            "associations": sds["associations"],
            "use_restriction": "Governance research only. This lane has no learner, hiring, ranking, or promotion path.",
        },
        "method_notes": evidence["method_notes"],
    }


@router.get("/sas-evidence/snapshot")
async def sas_evidence_snapshot(user=Depends(current_user)):
    """Return the approved local aggregate demonstration snapshot for this signed-in workspace."""
    return _snapshot()

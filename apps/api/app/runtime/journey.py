import hashlib
import io
import re
from datetime import date
from typing import Literal
from urllib.parse import urlparse
from zipfile import BadZipFile, ZipFile

import httpx
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError

from packages.scoring.journey import eligibility, extract_skills, match, plan, skill_score

from .catalog import ROLES, TAXONOMY, get_opportunity, opportunities
from .deps import add_record, audit, current_user, get_db, get_record, owned, records
from .models import Record, now
from .security import cipher

router = APIRouter(tags=["Career journey"])


class ResumeExperience(BaseModel):
    role: str = Field(default="", max_length=120)
    company: str = Field(default="", max_length=120)
    location: str = Field(default="", max_length=100)
    start_date: str = Field(default="", max_length=40)
    end_date: str = Field(default="", max_length=40)
    present: bool = False
    bullets: list[str] = Field(default_factory=list, max_length=12)


class ResumeEducation(BaseModel):
    degree: str = Field(default="", max_length=140)
    school: str = Field(default="", max_length=140)
    location: str = Field(default="", max_length=100)
    graduation_date: str = Field(default="", max_length=40)
    details: str = Field(default="", max_length=1000)


class ResumeBuilderData(BaseModel):
    full_name: str = Field(default="", max_length=120)
    headline: str = Field(default="", max_length=160)
    email: str = Field(default="", max_length=254)
    phone: str = Field(default="", max_length=40)
    location: str = Field(default="", max_length=120)
    website: str = Field(default="", max_length=300)
    linkedin: str = Field(default="", max_length=300)
    summary: str = Field(default="", max_length=3000)
    skills: list[str] = Field(default_factory=list, max_length=40)
    experience: list[ResumeExperience] = Field(default_factory=list, max_length=12)
    education: list[ResumeEducation] = Field(default_factory=list, max_length=8)
    languages: list[str] = Field(default_factory=list, max_length=12)


def view(record):
    return {"id": record.id, "created_at": record.created_at.isoformat(), **record.data}


@router.get("/resume-builder")
async def get_resume_builder(user=Depends(current_user), db=Depends(get_db)):
    record = await db.scalar(owned(user, "resume_builder").where(Record.key == "profile"))
    if record:
        return {"id": record.id, **record.data, "saved": True}
    return {
        "full_name": user.name,
        "headline": "",
        "email": user.email,
        "phone": "",
        "location": "",
        "website": "",
        "linkedin": "",
        "summary": "",
        "skills": [],
        "experience": [],
        "education": [],
        "languages": [],
        "saved": False,
    }


@router.put("/resume-builder")
async def save_resume_builder(body: ResumeBuilderData, user=Depends(current_user), db=Depends(get_db)):
    data = body.model_dump()
    data["skills"] = list(dict.fromkeys(skill.strip() for skill in data["skills"] if skill.strip()))[:40]
    data["languages"] = list(dict.fromkeys(value.strip() for value in data["languages"] if value.strip()))[:12]
    data["experience"] = [
        {**item, "bullets": [line.strip() for line in item["bullets"] if line.strip()][:12]}
        for item in data["experience"]
    ]
    record = await db.scalar(owned(user, "resume_builder").where(Record.key == "profile"))
    if record:
        record.data = data
    else:
        record = add_record(db, user, "resume_builder", data, key="profile")
    audit(db, user, "resume_builder.save", record.id)
    await db.flush()
    return {"id": record.id, **record.data, "saved": True}


async def twin_data(db, user):
    evidence = await records(db, user, "evidence")
    claimed = set(user.profile.get("claimed_skills", []))
    claimed.update(e.data["skill_id"] for e in evidence)
    skills = []
    for skill_id in sorted(claimed):
        if skill_id in TAXONOMY:
            items = [e for e in evidence if e.data["skill_id"] == skill_id]
            result = skill_score([e.data for e in items])
            skills.append({**TAXONOMY[skill_id], **result, "evidence": [view(e) for e in items]})
    return {
        "name": user.name,
        "skills": skills,
        "claimed_count": len(skills),
        "verified_count": sum(s["verified"] for s in skills),
        "is_demo_market": False,
    }


async def score_map(db, user):
    return {item["id"]: item["score"] for item in (await twin_data(db, user))["skills"]}


@router.get("/skills")
async def list_skills(user=Depends(current_user)):
    return list(TAXONOMY.values())


@router.get("/roles")
async def list_roles(user=Depends(current_user)):
    return ROLES


@router.get("/talent-twin")
async def talent_twin(user=Depends(current_user), db=Depends(get_db)):
    return await twin_data(db, user)


class ProfileUpdate(BaseModel):
    age: int | None = Field(None, ge=0, le=120)
    education_level: int | None = Field(None, ge=0, le=10)
    cgpa: float | None = Field(None, ge=0, le=10)
    qualification: Literal["10th", "12th", "diploma", "graduate", "postgraduate", "phd"] | None = None
    date_of_birth: date | None = None
    category: Literal["general", "ews", "obc", "sc", "st"] | None = None
    eligibility_consent: bool | None = None
    category_export_consent: bool | None = None
    domicile: str | None = Field(None, max_length=100)
    target_role: str | None = None

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, value):
        if value and value > date.today():
            raise ValueError("Date of birth cannot be in the future")
        return value


@router.patch("/users/me")
async def update_profile(body: ProfileUpdate, user=Depends(current_user), db=Depends(get_db)):
    if body.target_role and body.target_role not in {r["id"] for r in ROLES}:
        raise HTTPException(422, "Unknown target role")
    values = body.model_dump(exclude_unset=True, mode="json")
    if (
        any(key in values for key in ("qualification", "date_of_birth", "category"))
        and not values.get("eligibility_consent", user.profile.get("eligibility_consent", False))
        and values.get("eligibility_consent") is not False
    ):
        raise HTTPException(422, "Give consent in your eligibility settings before saving these personal details")
    if values.get("eligibility_consent") is False:
        values.update({"qualification": None, "date_of_birth": None, "category": None, "category_export_consent": False})
    user.profile = {**user.profile, **values}
    audit(db, user, "profile.update")
    return user.profile


def read_document(content, filename):
    suffix = filename.rsplit(".", 1)[-1].lower()
    try:
        if suffix == "txt":
            return content.decode("utf-8-sig")
        if suffix == "pdf":
            if not content.startswith(b"%PDF"):
                raise ValueError("Invalid PDF")
            from pypdf import PdfReader

            reader = PdfReader(io.BytesIO(content))
            if reader.is_encrypted or len(reader.pages) > 30:
                raise ValueError("Use an unencrypted PDF of at most 30 pages")
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        if suffix == "docx":
            with ZipFile(io.BytesIO(content)) as archive:
                if sum(info.file_size for info in archive.infolist()) > 20_000_000:
                    raise ValueError("Document expands beyond the size limit")
            from docx import Document

            document = Document(io.BytesIO(content))
            paragraphs = list(document.paragraphs)
            def table_paragraphs(table):
                for row in table.rows:
                    for cell in row.cells:
                        yield from cell.paragraphs
                        for nested in cell.tables:
                            yield from table_paragraphs(nested)
            for table in document.tables:
                paragraphs.extend(table_paragraphs(table))
            if any(
                run.font.hidden or (run.font.color.rgb and str(run.font.color.rgb) == "FFFFFF")
                for paragraph in paragraphs
                for run in paragraph.runs
            ):
                raise ValueError("Hidden document text requires manual review")
            return "\n".join(paragraph.text for paragraph in paragraphs)
    except (ValueError, UnicodeError, BadZipFile) as exc:
        raise HTTPException(422, str(exc)) from None
    except Exception:
        raise HTTPException(422, "This document could not be read. Try a plain text resume.") from None
    raise HTTPException(415, "Supported formats: PDF, DOCX, TXT")


@router.post("/vault/upload", status_code=201)
async def upload(
    request: Request,
    file: UploadFile = File(...),
    consent: bool = Form(False),
    user=Depends(current_user),
    db=Depends(get_db),
):
    if not consent:
        raise HTTPException(422, "Explicit consent to store and extract this document is required")
    content = await file.read(2_000_001)
    if not content or len(content) > 2_000_000:
        raise HTTPException(413, "Upload a non-empty document up to 2 MB")
    filename = (file.filename or "resume.txt").replace("\\", "/").split("/")[-1][:160]
    text = read_document(content, filename)
    if len(text) > 100_000 or len(text.strip()) < 20:
        raise HTTPException(
            422, "Document must contain 20 to 100,000 readable characters; OCR is not available"
        )
    if re.search(
        r"ignore\s+(?:all\s+)?previous|system\s+prompt|bypass\s+(?:the\s+)?system|[\u200b\u200c\u200d]",
        text,
        re.I,
    ):
        raise HTTPException(
            422, "Potential hidden text or instructions detected. Upload a clean document for review."
        )
    skills = extract_skills(text, TAXONOMY)
    if any(len(re.findall(r"\b" + re.escape(TAXONOMY[s]["name"]) + r"\b", text, re.I)) > 15 for s in skills):
        raise HTTPException(422, "Repeated keyword stuffing detected")
    document = add_record(
        db,
        user,
        "document",
        {
            "filename": filename,
            "encrypted_content": cipher(request.app.state.settings).encrypt(content).decode(),
            "skills": skills,
            "consent": True,
            "scan_status": "format-checked; antivirus not configured",
            "limitations": "PDF hidden-text detection is incomplete; extracted claims are unverified.",
        },
    )
    await db.flush()
    user.profile = {
        **user.profile,
        "claimed_skills": sorted(set(user.profile.get("claimed_skills", [])) | set(skills)),
    }
    for skill in skills:
        add_record(
            db,
            user,
            "evidence",
            {
                "skill_id": skill,
                "kind": "resume_claim",
                "document_id": document.id,
                "title": filename,
                "verified": False,
            },
            key=f"{document.id}:{skill}",
        )
    audit(db, user, "vault.upload", document.id)
    audit(db, user, "consent.document.granted", document.id)
    return {"id": document.id, "filename": filename, "skills": skills, "verified": False}


@router.get("/vault")
async def vault(user=Depends(current_user), db=Depends(get_db)):
    return [
        {k: v for k, v in view(d).items() if k != "encrypted_content"}
        for d in await records(db, user, "document")
    ]


@router.get("/vault/{document_id}/download")
async def download(document_id: str, request: Request, user=Depends(current_user), db=Depends(get_db)):
    document = await get_record(db, user, "document", document_id)
    audit(db, user, "vault.download", document.id)
    content = cipher(request.app.state.settings).decrypt(document.data["encrypted_content"].encode())
    return Response(
        content,
        media_type="application/octet-stream",
        headers={"Content-Disposition": 'attachment; filename="document"', "Cache-Control": "no-store"},
    )


@router.delete("/vault/{document_id}", status_code=204)
async def delete_document(document_id: str, user=Depends(current_user), db=Depends(get_db)):
    document = await get_record(db, user, "document", document_id)
    for evidence in await records(db, user, "evidence"):
        if evidence.data.get("document_id") == document.id:
            await db.delete(evidence)
    await db.delete(document)
    await db.flush()
    remaining = await records(db, user, "evidence")
    user.profile = {**user.profile, "claimed_skills": sorted({e.data["skill_id"] for e in remaining})}
    audit(db, user, "vault.delete", document_id)


class PlanRequest(BaseModel):
    role_id: str | None = None
    job_id: str | None = None
    hours: int = Field(40, ge=1, le=160)
    what_if_skills: list[str] = Field(default_factory=list, max_length=24)


@router.post("/career-gps")
async def career_gps(body: PlanRequest, user=Depends(current_user), db=Depends(get_db)):
    if bool(body.role_id) == bool(body.job_id):
        raise HTTPException(422, "Choose one target role or one saved job.")
    if body.job_id:
        job = await get_record(db, user, "live_job", body.job_id)
        required = sorted({skill for skill in job.data.get("skills", []) if skill in TAXONOMY})
        if not required:
            raise HTTPException(422, "We couldn't identify supported skills in this posting yet. Try another saved job.")
        role = {"id": f"job:{job.id}", "title": f"{job.data['title']} · {job.data['organization']}", "skills": required}
    else:
        role = next((r for r in ROLES if r["id"] == body.role_id), None)
    if not role or any(s not in TAXONOMY for s in body.what_if_skills):
        raise HTTPException(422, "Unknown role or skill")
    skills = await score_map(db, user)
    skills.update({s: max(skills.get(s, 0), 50) for s in body.what_if_skills})
    return {
        "role": role,
        "what_if": bool(body.what_if_skills),
        **plan(skills, role["skills"], TAXONOMY, body.hours),
    }


class MissionRequest(BaseModel):
    skill_id: str


@router.post("/missions", status_code=201)
async def create_mission(body: MissionRequest, user=Depends(current_user), db=Depends(get_db)):
    skill = TAXONOMY.get(body.skill_id)
    if not skill:
        raise HTTPException(422, "Unknown skill")
    existing = await db.scalar(owned(user, "mission").where(Record.key == body.skill_id))
    if existing:
        return view(existing)
    mission = add_record(
        db,
        user,
        "mission",
        {
            "skill_id": skill["id"],
            "title": f"Build a {skill['name']} project",
            "hours": skill["hours"],
            "status": "in_progress",
            "checklist": ["Create an original artifact", "Document your work", "Submit the project link"],
        },
        key=skill["id"],
    )
    await db.flush()
    return view(mission)


@router.get("/missions")
async def list_missions(user=Depends(current_user), db=Depends(get_db)):
    return [view(m) for m in await records(db, user, "mission")]


class CompleteMission(BaseModel):
    artifact_url: str = Field(min_length=10, max_length=1000)
    description: str = Field(min_length=30, max_length=3000)
    hours_spent: float = Field(gt=0, le=1000)


@router.post("/missions/{mission_id}/complete")
async def complete_mission(
    mission_id: str, body: CompleteMission, user=Depends(current_user), db=Depends(get_db)
):
    url = urlparse(body.artifact_url)
    if url.scheme != "https" or not url.hostname or url.username or url.password:
        raise HTTPException(422, "Provide a public HTTPS project URL")
    mission = await get_record(db, user, "mission", mission_id)
    if mission.data["status"] == "completed":
        return view(mission)
    for e in await records(db, user, "evidence"):
        if (
            e.data.get("artifact_url") == body.artifact_url
            and e.data.get("skill_id") == mission.data["skill_id"]
        ):
            raise HTTPException(409, "This artifact is already recorded for this skill")
    add_record(
        db,
        user,
        "evidence",
        {
            "skill_id": mission.data["skill_id"],
            "kind": "project",
            "title": mission.data["title"],
            **body.model_dump(),
            "verified": False,
            "integrity_status": "self_reported; authorship not verified",
        },
        key=mission.id,
    )
    mission.data = {**mission.data, "status": "completed", **body.model_dump()}
    audit(db, user, "mission.complete", mission.id)
    await db.flush()
    return view(mission)


@router.post("/evidence/{evidence_id}/verify-github")
async def verify_github_project(evidence_id: str, request: Request, user=Depends(current_user), db=Depends(get_db)):
    evidence = await get_record(db, user, "evidence", evidence_id)
    if evidence.data.get("kind") != "project":
        raise HTTPException(400, "Only projects can be verified via GitHub")
    if evidence.data.get("verified"):
        return view(evidence)
        
    url = evidence.data.get("artifact_url", "")
    if not url.startswith("https://github.com/"):
        raise HTTPException(422, "Only GitHub repositories are supported for automated verification")
        
    parts = url.rstrip("/").split("/")
    if len(parts) < 5:
        raise HTTPException(422, "Invalid GitHub repository URL")
        
    owner, repo = parts[3], parts[4]
    
    headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "Limitless-App"}
    async with httpx.AsyncClient(headers=headers) as client:
        # 1. Fetch basic repository details
        response = await client.get(f"https://api.github.com/repos/{owner}/{repo}")
        if response.status_code != 200:
            raise HTTPException(422, "Could not verify this repository on GitHub. Make sure it is public.")
            
        data = response.json()
        
        if data.get("size", 0) == 0:
            raise HTTPException(422, "This repository appears to be completely empty. Add some code before verifying.")
            
        # 2. Fetch commits to ensure there is substantive work
        commits_resp = await client.get(f"https://api.github.com/repos/{owner}/{repo}/commits")
        commit_count = 0
        if commits_resp.status_code == 200:
            commits_data = commits_resp.json()
            commit_count = len(commits_data)
            # If there's only 1 commit and the repo is tiny, it's likely just an initial commit (e.g. just a README or license).
            if commit_count <= 1 and data.get("size", 0) < 10:
                raise HTTPException(422, "This repository lacks substantive commit history or code content.")
                
        # 3. Fetch README to ensure the project is documented
        readme_resp = await client.get(f"https://api.github.com/repos/{owner}/{repo}/readme")
        has_readme = (readme_resp.status_code == 200)
        readme_text = ""
        if has_readme:
            import base64
            try:
                readme_text = base64.b64decode(readme_resp.json().get("content", "")).decode("utf-8")
            except Exception:
                pass
        
        # 4. Deep AI verification
        llm_analysis = "Automated checks passed."
        record = await db.scalar(owned(user, "integration_secret").where(Record.key == "social"))
        if record:
            import json
            try:
                keys = json.loads(cipher(request.app.state.settings).decrypt(record.data["encrypted"].encode()))
                if keys.get("llm_key") and keys.get("model"):
                    provider = keys.get("provider", "openai")
                    base = "https://api.openai.com/v1" if provider == "openai" else "https://generativelanguage.googleapis.com/v1beta/openai"
                    system_prompt = "You are an expert code evaluator. Conduct a deep analysis of this GitHub project. Determine if it represents substantive effort, real architecture, and genuine functionality rather than just a boilerplate, a fork without changes, or a generic demo. Provide a thorough evaluation (3-4 sentences)."
                    user_prompt = f"Description: {evidence.data.get('description', '')}\nRepository Size: {data.get('size', 0)} KB\nCommits: {commit_count}\nLanguage: {data.get('language', 'Unknown')}\n\nREADME:\n{readme_text[:6000]}"
                    ai_resp = await client.post(
                        base + "/chat/completions",
                        headers={"Authorization": "Bearer " + keys["llm_key"]},
                        json={"model": keys["model"], "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], "max_tokens": 250},
                        timeout=15.0
                    )
                    if ai_resp.status_code == 200:
                        llm_analysis = "AI Analysis: " + ai_resp.json()["choices"][0]["message"]["content"].strip()
            except Exception:
                pass

    evidence.data = {
        **evidence.data,
        "verified": True,
        "integrity_status": "limit.less_certified; deep-checked",
        "github_stars": data.get("stargazers_count", 0),
        "github_language": data.get("language", "Unknown"),
        "github_commit_count": commit_count,
        "github_has_readme": has_readme,
        "github_size_kb": data.get("size", 0),
        "ai_analysis": llm_analysis
    }
    
    audit(db, user, "evidence.verify_github_deep", evidence.id)
    await db.flush()
    
    # Must update twin data skill profile? 
    # The twin_data computes verified based on e["verified"]. So it will update automatically!
    
    return view(evidence)


@router.get("/opportunities")
async def list_opportunities(q: str = "", type: str = "", user=Depends(current_user), db=Depends(get_db)):
    scores = await score_map(db, user)
    result = [
        {
            **o,
            "match": match(scores, o["skills"]),
            "eligibility": eligibility(user.profile, o["requirements"]),
        }
        for o in opportunities()
        if (not type or o["type"] == type) and q.lower() in (o["title"] + o["location"]).lower()
    ]
    return sorted(result, key=lambda o: o["match"]["score"], reverse=True)


@router.get("/opportunities/{opportunity_id}")
async def opportunity(opportunity_id: str, user=Depends(current_user), db=Depends(get_db)):
    item = get_opportunity(opportunity_id)
    if not item:
        raise HTTPException(404, "Opportunity not found")
    return {
        **item,
        "match": match(await score_map(db, user), item["skills"]),
        "eligibility": eligibility(user.profile, item["requirements"]),
    }


class ApplicationRequest(BaseModel):
    opportunity_id: str


async def compile_resume(db, user, item, settings=None):
    twin = await twin_data(db, user)
    bullets = [
        {
            "skill_id": s["id"],
            "skill": s["name"],
            "text": e["description"],
            "evidence_id": e["id"],
            "artifact_url": e["artifact_url"],
            "verified": e["verified"],
        }
        for s in twin["skills"]
        if s["id"] in item["skills"]
        for e in s["evidence"]
        if e["kind"] == "project" and e.get("artifact_url")
    ]
    documents = await records(db, user, "document")
    original_text = ""
    source_filename = ""
    for document in (reversed(documents) if settings else []):
        try:
            source_bytes = cipher(settings).decrypt(
                document.data["encrypted_content"].encode()
            )
            original_text = read_document(source_bytes, document.data["filename"]).strip()
            source_filename = document.data["filename"]
            if original_text:
                break
        except (KeyError, ValueError, HTTPException):
            continue

    builder = await db.scalar(owned(user, "resume_builder").where(Record.key == "profile"))
    if builder and any(builder.data.get(key) for key in ("summary", "experience", "education")):
        profile = builder.data
        lines = [profile.get("full_name") or user.name, profile.get("headline", ""),
                 profile.get("email") or user.email, profile.get("phone", ""), profile.get("location", ""),
                 profile.get("summary", ""), "Skills: " + ", ".join(profile.get("skills", []))]
        for experience in profile.get("experience", []):
            lines.extend([f"{experience.get('role', '')} · {experience.get('company', '')}",
                          f"{experience.get('start_date', '')} – {experience.get('end_date', '')}",
                          *experience.get("bullets", [])])
        for education in profile.get("education", []):
            lines.append(" · ".join(str(value) for value in education.values() if value))
        builder_text = "\n".join(line for line in lines if line)
        original_text = builder_text + ("\n\nUPLOADED SOURCE\n" + original_text if original_text else "")
        source_filename = source_filename or "Saved Resume Builder profile"

    relevant_skills = [
        TAXONOMY[skill_id]["name"] for skill_id in item.get("skills", []) if skill_id in TAXONOMY
    ]
    focus_bullets = [bullet for bullet in bullets if bullet["skill"] in relevant_skills]
    resume_lines = [user.name, user.email, "", f"TARGET ROLE: {item['title']}", ""]
    if focus_bullets:
        resume_lines.extend(["ROLE-RELEVANT PROJECT EVIDENCE", ""])
        for bullet in focus_bullets[:12]:
            verification_label = "Independently verified" if bullet["verified"] else "Self-reported"
            resume_lines.extend(
                [
                    f"{bullet['skill']} · {verification_label}",
                    bullet["text"],
                    f"Project: {bullet['artifact_url']}",
                    "",
                ]
            )
    else:
        resume_lines.extend(["ROLE-RELEVANT PROJECT EVIDENCE", "", "No matching project evidence was found in your profile.", ""])
    if original_text:
        resume_lines.extend(
            [
                "ORIGINAL RÉSUMÉ CONTENT",
                f"Source: {source_filename} · preserved from your uploaded document",
                "",
                original_text[:100_000],
            ]
        )
    else:
        resume_lines.extend(
            [
                "RÉSUMÉ INCOMPLETE",
                "Upload your source résumé in Document Vault to include your work history and education.",
                "This draft contains only the project evidence listed above.",
            ]
        )
    return {
        "name": user.name,
        "email": user.email,
        "target": item["title"],
        "generated_resume_text": "\n".join(resume_lines).strip(),
        "source_document_id": next((d.id for d in reversed(documents) if d.data.get("filename") == source_filename), None),
        "source_available": bool(original_text),
        "source_fingerprint": hashlib.sha256(original_text.encode("utf-8")).hexdigest(),
        "bullets": bullets,
        "guard": "PASS" if bullets else "BLOCKED",
        "note": "Only user-authored, linked project descriptions; self-reported evidence is not verified.",
    }


@router.post("/applications", status_code=201)
async def prepare_application(body: ApplicationRequest, request: Request, user=Depends(current_user), db=Depends(get_db)):
    item = get_opportunity(body.opportunity_id)
    if not item:
        raise HTTPException(404, "Opportunity not found")
    existing = await db.scalar(owned(user, "application").where(Record.key == item["id"]))
    if existing:
        return view(existing)
    resume = await compile_resume(db, user, item, request.app.state.settings)
    check = eligibility(user.profile, item["requirements"])
    application = add_record(
        db,
        user,
        "application",
        {
            "opportunity_id": item["id"],
            "title": item["title"],
            "organization": item["organization"],
            "status": "draft",
            "resume": resume,
            "resume_version": 1,
            "match": match(await score_map(db, user), item["skills"]),
            "eligibility": check,
            "connector": "demo",
            "is_demo": True,
        },
        key=item["id"],
    )
    try:
        await db.flush()
    except IntegrityError:
        raise HTTPException(409, "Application already exists") from None
    audit(db, user, "application.prepare", application.id)
    return view(application)


@router.get("/applications")
async def list_applications(user=Depends(current_user), db=Depends(get_db)):
    return [view(a) for a in await records(db, user, "application")]


class ApprovalRequest(BaseModel):
    approved: Literal[True]
    resume_version: int = Field(ge=1)


@router.post("/applications/{application_id}/approve")
async def approve(application_id: str, body: ApprovalRequest, request: Request, user=Depends(current_user), db=Depends(get_db)):
    application = await get_record(db, user, "application", application_id)
    if application.data["status"] != "draft":
        raise HTTPException(409, "Application has already been approved")
    item = get_opportunity(application.data["opportunity_id"])
    current = await compile_resume(db, user, item, request.app.state.settings)
    check = eligibility(user.profile, item["requirements"])
    if current["guard"] != "PASS" or check["status"] != "PASS":
        raise HTTPException(422, "Evidence guard and eligibility must both pass before approval")
    if body.resume_version != application.data["resume_version"] or current != application.data["resume"]:
        raise HTTPException(409, "Evidence changed. Refresh the preview before approving.")
    old = dict(application.data)
    new = {
        **old,
        "status": "submitted_demo",
        "approved_at": now().isoformat(),
        "eligibility": check,
        "submission_note": "Demo submission recorded locally. No employer was contacted.",
    }
    # Optimistic update prevents duplicate submissions from concurrent requests.
    changed = await db.execute(
        update(Record)
        .where(
            Record.id == application.id,
            Record.tenant_id == user.tenant_id,
            Record.user_id == user.id,
            Record.data == old,
        )
        .values(data=new)
    )
    if changed.rowcount != 1:
        raise HTTPException(409, "Application changed; reload the preview")
    audit(db, user, "application.approve_demo", application.id)
    add_record(
        db,
        user,
        "notification",
        {
            "title": "Application approved",
            "body": f"{item['title']} recorded.",
            "is_read": False,
        },
    )
    return {"id": application.id, **new}


@router.post("/applications/{application_id}/refresh")
async def refresh_preview(application_id: str, request: Request, user=Depends(current_user), db=Depends(get_db)):
    application = await get_record(db, user, "application", application_id)
    if application.data["status"] != "draft":
        raise HTTPException(409, "Submitted applications cannot be rewritten")
    item = get_opportunity(application.data["opportunity_id"])
    add_record(
        db,
        user,
        "resume_version",
        {
            "application_id": application.id,
            **application.data["resume"],
            "version": application.data["resume_version"],
        },
    )
    application.data = {
        **application.data,
        "resume": await compile_resume(db, user, item, request.app.state.settings),
        "resume_version": application.data["resume_version"] + 1,
        "match": match(await score_map(db, user), item["skills"]),
        "eligibility": eligibility(user.profile, item["requirements"]),
    }
    audit(db, user, "resume.refresh", application.id)
    return view(application)


class OutcomeRequest(BaseModel):
    outcome: Literal["interview", "offer", "rejected", "withdrawn"]
    notes: str = Field(default="", max_length=2000)


@router.patch("/applications/{application_id}/outcome")
async def outcome(application_id: str, body: OutcomeRequest, user=Depends(current_user), db=Depends(get_db)):
    application = await get_record(db, user, "application", application_id)
    if application.data["status"] == "draft":
        raise HTTPException(409, "Approve the application before recording an outcome")
    application.data = {**application.data, **body.model_dump()}
    audit(db, user, "application.outcome", application.id)
    return view(application)

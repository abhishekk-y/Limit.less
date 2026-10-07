from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from .deps import audit, current_user, get_db
from .models import Account, RefreshSession, Workspace, now
from .security import decode, hash_password, is_superadmin, issue_tokens, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    name: str = Field(min_length=2, max_length=160)
    tenant_type: Literal["individual", "organization", "institution"] = "individual"
    workspace_name: str = Field(default="", max_length=160)
    consent: Literal[True]


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(max_length=4096)


async def user_view(db, user):
    workspace = await db.get(Workspace, user.tenant_id)
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": "superadmin" if is_superadmin(user) else user.role,
        "tenant_id": user.tenant_id,
        "tenant_type": workspace.type,
        "workspace_name": workspace.name,
        "plan": workspace.plan,
        "is_demo": workspace.is_demo,
        "profile": user.profile,
    }


@router.post("/register", status_code=201)
async def register(body: RegisterRequest, request: Request, db=Depends(get_db)):
    email = str(body.email).lower()
    if await db.scalar(select(Account).where(Account.email == email)):
        raise HTTPException(409, "An account with this email already exists")
    workspace = Workspace(
        name=body.workspace_name.strip() or body.name.strip(),
        type=body.tenant_type,
        is_demo=request.app.state.settings.demo_mode,
    )
    db.add(workspace)
    await db.flush()
    user = Account(
        email=email,
        name=body.name.strip(),
        password_hash=hash_password(body.password),
        tenant_id=workspace.id,
        role={"individual": "professional", "organization": "org_admin", "institution": "institution_admin"}[
            body.tenant_type
        ],
        profile={"consent": True},
    )
    db.add(user)
    try:
        await db.flush()
    except IntegrityError:
        raise HTTPException(409, "An account with this email already exists") from None
    audit(db, user, "account.register")
    audit(db, user, "consent.granted")
    tokens = await issue_tokens(db, user, request.app.state.settings)
    return {**tokens, "user": await user_view(db, user)}


@router.post("/login")
async def login(body: LoginRequest, request: Request, db=Depends(get_db)):
    user = await db.scalar(select(Account).where(Account.email == str(body.email).lower()))
    # Equalize the expensive hash path for unknown accounts.
    fallback = request.app.state.dummy_password_hash
    valid = verify_password(body.password, user.password_hash if user else fallback)
    if not user or not valid or not user.active:
        raise HTTPException(401, "Email or password is incorrect")
    audit(db, user, "account.login")
    return {**await issue_tokens(db, user, request.app.state.settings), "user": await user_view(db, user)}


@router.get("/me")
async def me(request: Request, user=Depends(current_user), db=Depends(get_db)):
    return await user_view(db, user)


@router.post("/refresh")
async def refresh(body: RefreshRequest, request: Request, db=Depends(get_db)):
    payload = decode(body.refresh_token, request.app.state.settings, "refresh")
    session = await db.get(RefreshSession, payload["jti"])
    if not session or session.user_id != payload["sub"]:
        raise HTTPException(401, "Invalid refresh session")
    result = await db.execute(
        update(RefreshSession)
        .where(
            RefreshSession.id == session.id,
            RefreshSession.revoked.is_(False),
            RefreshSession.expires_at > now(),
        )
        .values(revoked=True)
        .execution_options(synchronize_session=False)
    )
    if result.rowcount != 1:
        await db.execute(
            update(RefreshSession).where(RefreshSession.family == session.family).values(revoked=True)
        )
        await db.commit()  # Replay revocation must survive the error response.
        raise HTTPException(401, "Refresh token was already used; sign in again")
    user = await db.get(Account, session.user_id)
    if not user or not user.active:
        raise HTTPException(401, "Account unavailable")
    return await issue_tokens(db, user, request.app.state.settings, family=session.family)


@router.post("/logout", status_code=204)
async def logout(request: Request, user=Depends(current_user), db=Depends(get_db)):
    token = request.headers["authorization"].split(" ", 1)[1]
    payload = decode(token, request.app.state.settings)
    await db.execute(
        update(RefreshSession)
        .where(RefreshSession.user_id == user.id, RefreshSession.family == payload["family"])
        .values(revoked=True)
    )
    audit(db, user, "account.logout")

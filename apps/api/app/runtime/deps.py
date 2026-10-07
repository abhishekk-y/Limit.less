from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select, text

from .models import Account, AuditEvent, Record, RefreshSession, now
from .security import decode

bearer = HTTPBearer(auto_error=False)


async def get_db(request: Request):
    async with request.app.state.sessions() as db:
        try:
            yield db
            await db.commit()
        except Exception:
            await db.rollback()
            raise


async def current_user(
    request: Request, credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db=Depends(get_db)
):
    if not credentials:
        raise HTTPException(401, "Sign in to continue")
    payload = decode(credentials.credentials, request.app.state.settings)
    user = await db.get(Account, payload["sub"])
    if not user or not user.active or user.tenant_id != payload.get("tenant_id"):
        raise HTTPException(401, "Invalid account")
    active_session = await db.scalar(
        select(RefreshSession.id).where(
            RefreshSession.user_id == user.id,
            RefreshSession.family == payload.get("family"),
            RefreshSession.revoked.is_(False),
            RefreshSession.expires_at > now(),
        )
    )
    if not active_session:
        raise HTTPException(401, "Session has been signed out")
    # Never trust X-Tenant-ID supplied by a client.
    if db.bind.dialect.name == "postgresql":
        await db.execute(
            text("SELECT set_config('app.current_tenant_id', :tenant, true)"), {"tenant": user.tenant_id}
        )
    return user


def owned(user, kind):
    return select(Record).where(
        Record.tenant_id == user.tenant_id, Record.user_id == user.id, Record.kind == kind
    )


async def records(db, user, kind):
    return list((await db.scalars(owned(user, kind).order_by(Record.created_at))).all())


async def get_record(db, user, kind, record_id):
    record = await db.scalar(owned(user, kind).where(Record.id == record_id))
    if not record:
        raise HTTPException(404, "Record not found")
    return record


def add_record(db, user, kind, data, key=None):
    record = Record(tenant_id=user.tenant_id, user_id=user.id, kind=kind, data=data)
    if key is not None:
        record.key = key
    db.add(record)
    return record


def audit(db, user, action, resource_id=""):
    db.add(AuditEvent(tenant_id=user.tenant_id, user_id=user.id, action=action, resource_id=resource_id))


def require_role(user, *roles):
    if user.role not in roles:
        raise HTTPException(403, "This workspace role cannot perform that action")

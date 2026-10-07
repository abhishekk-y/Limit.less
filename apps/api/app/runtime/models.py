"""Portable, tenant-owned records for the executable vertical slice."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def new_id():
    return str(uuid4())


def now():
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Workspace(Base):
    __tablename__ = "workspaces"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(160))
    type: Mapped[str] = mapped_column(String(32))
    plan: Mapped[str] = mapped_column(String(32), default="free")
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)


class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"), index=True)
    email: Mapped[str] = mapped_column(String(254), unique=True)
    name: Mapped[str] = mapped_column(String(160))
    password_hash: Mapped[str] = mapped_column(Text)
    role: Mapped[str] = mapped_column(String(40))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    profile: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Record(Base):
    __tablename__ = "workspace_records"
    __table_args__ = (UniqueConstraint("tenant_id", "user_id", "kind", "key", name="uq_record_owner_key"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"), index=True)
    kind: Mapped[str] = mapped_column(String(40), index=True)
    key: Mapped[str] = mapped_column(String(160), default=new_id)
    data: Mapped[dict] = mapped_column(JSON().with_variant(JSONB(), "postgresql"), default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class RefreshSession(Base):
    __tablename__ = "refresh_sessions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"), index=True)
    family: Mapped[str] = mapped_column(String(36), index=True)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"), index=True)
    user_id: Mapped[str] = mapped_column(String(36))
    action: Mapped[str] = mapped_column(String(100))
    resource_id: Mapped[str] = mapped_column(String(160), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class PassportShare(Base):
    __tablename__ = "passport_shares"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    snapshot: Mapped[dict] = mapped_column(JSON)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)


class ProviderDailyUsage(Base):
    __tablename__ = "provider_daily_usage"
    provider: Mapped[str] = mapped_column(String(40), primary_key=True)
    usage_day: Mapped[str] = mapped_column(String(10), primary_key=True)
    calls: Mapped[int] = mapped_column(default=0)

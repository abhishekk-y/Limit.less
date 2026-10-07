from datetime import datetime
import uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

class TenantMixin:
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)

class SoftDeleteMixin:
    deleted_at: Mapped[datetime | None] = mapped_column(default=None)

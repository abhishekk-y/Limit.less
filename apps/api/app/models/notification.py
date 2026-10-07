from sqlalchemy import Column, String, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base, TimestampMixin, TenantMixin

class Notification(Base, TimestampMixin, TenantMixin):
    __tablename__ = "notifications"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True))
    type = Column(String)
    title = Column(String)
    body = Column(String)
    channel = Column(String)
    is_read = Column(Boolean, default=False)
    metadata_ = Column("metadata", JSON)

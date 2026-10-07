from sqlalchemy import Column, String, Float, JSON, Boolean, ARRAY
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base, TimestampMixin, TenantMixin

class Evidence(Base, TimestampMixin, TenantMixin):
    __tablename__ = "evidences"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True))
    skill_id = Column(UUID(as_uuid=True))
    type = Column(String, nullable=False)
    source_url = Column(String)
    title = Column(String)
    description = Column(String)
    metadata_ = Column("metadata", JSON)
    integrity_score = Column(Float)
    integrity_flags = Column(ARRAY(String), default=[])
    is_demo = Column(Boolean, default=False)

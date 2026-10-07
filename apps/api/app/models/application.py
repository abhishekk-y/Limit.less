from sqlalchemy import Column, String, Float, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base, TimestampMixin, TenantMixin

class Application(Base, TimestampMixin, TenantMixin):
    __tablename__ = "applications"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True))
    opportunity_id = Column(UUID(as_uuid=True))
    resume_version_id = Column(UUID(as_uuid=True))
    status = Column(String, default="draft")
    match_score = Column(Float)
    eligibility_status = Column(String)
    eligibility_details = Column(JSON)
    outcome = Column(String)
    outcome_notes = Column(String)
    is_demo = Column(Boolean, default=False)

from sqlalchemy import Column, Integer, Float, String, JSON, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base, TenantMixin

class PersonSkill(Base, TenantMixin):
    __tablename__ = "person_skills"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), index=True)
    skill_id = Column(UUID(as_uuid=True), index=True)
    claimed_level = Column(Integer)
    sts_score = Column(Float)
    sts_components = Column(JSON)
    confidence_label = Column(String)
    freshness = Column(Float)
    last_evidenced_at = Column(DateTime)
    is_verified = Column(Boolean, default=False)
    verified_by = Column(UUID(as_uuid=True))
    is_demo = Column(Boolean, default=False)

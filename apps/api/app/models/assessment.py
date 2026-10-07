from sqlalchemy import Column, String, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base, TimestampMixin, TenantMixin

class Assessment(Base, TimestampMixin, TenantMixin):
    __tablename__ = "assessments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String)

class AssessmentResult(Base, TimestampMixin, TenantMixin):
    __tablename__ = "assessment_results"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True))
    assessment_id = Column(UUID(as_uuid=True))
    score = Column(String)

from sqlalchemy import Column, String, Integer, JSON, ARRAY
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base, TimestampMixin, TenantMixin

class ResumeVersion(Base, TimestampMixin, TenantMixin):
    __tablename__ = "resume_versions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True))
    opportunity_id = Column(UUID(as_uuid=True))
    version_number = Column(Integer)
    content = Column(JSON)
    selected_skills = Column(ARRAY(UUID(as_uuid=True)))
    selected_projects = Column(ARRAY(UUID(as_uuid=True)))
    bullet_variants = Column(JSON)
    pdf_url = Column(String)

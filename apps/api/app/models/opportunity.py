from sqlalchemy import Column, String, Boolean, JSON, Float, ARRAY, DateTime
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
import uuid
from app.db.base import Base, TimestampMixin

class Opportunity(Base, TimestampMixin):
    __tablename__ = "opportunities"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    organization = Column(String)
    type = Column(String)
    location = Column(String)
    is_remote = Column(Boolean, default=False)
    skills_required = Column(JSON)
    education_required = Column(JSON)
    experience_required = Column(Float)
    salary_min = Column(Float)
    salary_max = Column(Float)
    deadline = Column(DateTime)
    source = Column(String)
    source_url = Column(String)
    category_rules = Column(JSON)
    documents_required = Column(ARRAY(String), default=[])
    eligibility_rules = Column(JSON)
    description = Column(String)
    embedding = Column(Vector(384))
    is_active = Column(Boolean, default=True)
    is_demo = Column(Boolean, default=False)

from sqlalchemy import Column, String, Integer, JSON, Boolean, ARRAY
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base

class SkillMission(Base):
    __tablename__ = "skill_missions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(String)
    skills_targeted = Column(ARRAY(UUID(as_uuid=True)), default=[])
    difficulty = Column(String)
    estimated_hours = Column(Integer)
    checklist = Column(JSON)
    project_template = Column(JSON)
    is_demo = Column(Boolean, default=False)

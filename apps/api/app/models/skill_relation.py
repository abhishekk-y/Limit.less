from sqlalchemy import Column, String, Float, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base

class SkillRelation(Base):
    __tablename__ = "skill_relations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_skill_id = Column(UUID(as_uuid=True), nullable=False)
    target_skill_id = Column(UUID(as_uuid=True), nullable=False)
    relation_type = Column(String, nullable=False)
    weight = Column(Float, default=1.0)
    version = Column(Integer, default=1)

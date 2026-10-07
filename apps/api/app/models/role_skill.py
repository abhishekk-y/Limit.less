from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base

class RoleSkill(Base):
    __tablename__ = "role_skills"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_id = Column(UUID(as_uuid=True), nullable=False)
    skill_id = Column(UUID(as_uuid=True), nullable=False)
    importance = Column(String, nullable=False)
    typical_level = Column(Integer, default=1)

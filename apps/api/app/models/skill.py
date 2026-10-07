from sqlalchemy import Column, String, Float, Integer, Boolean, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
import uuid
from app.db.base import Base

class Skill(Base):
    __tablename__ = "skills"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    canonical_name = Column(String, unique=True, index=True)
    esco_id = Column(String)
    onet_id = Column(String)
    nco_code = Column(String)
    nsqf_level = Column(Integer)
    category = Column(String)
    aliases = Column(ARRAY(String), default=[])
    embedding = Column(Vector(384))
    is_demo = Column(Boolean, default=False)
    version = Column(Integer, default=1)

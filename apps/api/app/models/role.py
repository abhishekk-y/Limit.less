from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
import uuid
from app.db.base import Base

class Role(Base):
    __tablename__ = "roles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    normalized_title = Column(String, index=True)
    onet_code = Column(String)
    role_vector = Column(Vector(384))
    category = Column(String)
    is_demo = Column(Boolean, default=False)

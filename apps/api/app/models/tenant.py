from sqlalchemy import Column, String, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base, TimestampMixin

class Tenant(Base, TimestampMixin):
    __tablename__ = "tenants"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False) # individual, organization, institution
    slug = Column(String, unique=True, index=True)
    plan = Column(String, default="free")
    settings = Column(JSON, default={})

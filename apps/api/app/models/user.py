from sqlalchemy import Column, String, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base, TimestampMixin, TenantMixin

class User(Base, TimestampMixin, TenantMixin):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    role = Column(String, nullable=False)
    avatar = Column(String)
    google_id = Column(String)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    preferences = Column(JSON, default={})
    is_demo = Column(Boolean, default=False)

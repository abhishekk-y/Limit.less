from sqlalchemy import Column, String, Integer, Boolean, ARRAY, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base, TenantMixin

class APIKey(Base, TenantMixin):
    __tablename__ = "api_keys"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key_hash = Column(String, nullable=False)
    name = Column(String)
    permissions = Column(ARRAY(String), default=[])
    rate_limit = Column(Integer)
    usage_count = Column(Integer, default=0)
    last_used_at = Column(DateTime)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)

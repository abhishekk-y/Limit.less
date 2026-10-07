from sqlalchemy import Column, String, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base, TimestampMixin, TenantMixin

class AuditLog(Base, TimestampMixin, TenantMixin):
    __tablename__ = "audit_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True))
    action = Column(String, nullable=False)
    resource_type = Column(String)
    resource_id = Column(UUID(as_uuid=True))
    old_value = Column(JSON)
    new_value = Column(JSON)
    ip_address = Column(String)
    user_agent = Column(String)

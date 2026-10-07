from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base, TenantMixin

class ConsentRecord(Base, TenantMixin):
    __tablename__ = "consent_records"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True))
    purpose = Column(String)
    granted = Column(Boolean)
    granted_at = Column(DateTime)
    revoked_at = Column(DateTime)
    ip_address = Column(String)

from sqlalchemy import Column, String, Boolean, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base, TimestampMixin, TenantMixin

class VaultDocument(Base, TimestampMixin, TenantMixin):
    __tablename__ = "vault_documents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True))
    doc_type = Column(String, nullable=False)
    file_url = Column(String)
    encrypted_file_url = Column(String)
    is_verified = Column(Boolean, default=False)
    metadata_ = Column("metadata", JSON)
    consent_given = Column(Boolean, default=False)
    consent_given_at = Column(DateTime)

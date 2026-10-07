from sqlalchemy import Column, String, Float, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base, TenantMixin

class OrgEmployee(Base, TenantMixin):
    __tablename__ = "org_employees"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(String)
    name = Column(String)
    role = Column(String)
    department = Column(String)
    skills = Column(JSON)
    skill_levels = Column(JSON)
    experience_years = Column(Float)
    is_demo = Column(Boolean, default=False)

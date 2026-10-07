from sqlalchemy import Column, String, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base, TimestampMixin, TenantMixin

class Curriculum(Base, TimestampMixin, TenantMixin):
    __tablename__ = "curriculums"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)

class Program(Base, TimestampMixin, TenantMixin):
    __tablename__ = "programs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    curriculum_id = Column(UUID(as_uuid=True))

class Semester(Base, TimestampMixin, TenantMixin):
    __tablename__ = "semesters"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    program_id = Column(UUID(as_uuid=True))

class Course(Base, TimestampMixin, TenantMixin):
    __tablename__ = "courses"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    semester_id = Column(UUID(as_uuid=True))

class LearningOutcome(Base, TimestampMixin, TenantMixin):
    __tablename__ = "learning_outcomes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description = Column(String)
    course_id = Column(UUID(as_uuid=True))

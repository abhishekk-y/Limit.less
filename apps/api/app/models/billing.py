from sqlalchemy import Column, String, JSON, DateTime, Float
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base, TimestampMixin, TenantMixin

class Subscription(Base, TimestampMixin, TenantMixin):
    __tablename__ = "subscriptions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan = Column(String)
    razorpay_subscription_id = Column(String)
    status = Column(String)
    features = Column(JSON)
    usage = Column(JSON)
    trial_ends_at = Column(DateTime)
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)

class Invoice(Base, TimestampMixin, TenantMixin):
    __tablename__ = "invoices"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    amount = Column(Float)

class Payment(Base, TimestampMixin, TenantMixin):
    __tablename__ = "payments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    amount = Column(Float)

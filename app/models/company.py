from sqlalchemy import Column, String, Text, DateTime, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.core.database import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text)
    industry = Column(String, nullable=False)
    location_city = Column(String)
    location_province = Column(String)
    location_country = Column(String)
    website_url = Column(String)
    logo_url = Column(String)
    verification_status = Column(
        String,
        CheckConstraint(
            "verification_status IN ('unverified', 'pending', 'verified', 'rejected')",
            name="check_verification_status"
        ),
        default='unverified'
    )
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
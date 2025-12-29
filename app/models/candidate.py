from sqlalchemy import Column, String, DateTime, Date, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base

class Candidate(Base):
    __tablename__ = "candidates"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    full_name = Column(String, nullable=False)
    phone = Column(String)
    birth_date = Column(Date)
    gender = Column(
        String,
        CheckConstraint(
            "gender IN ('male', 'female', 'prefer_not_to_say')",
            name="check_gender"
        )
    )
    location_city = Column(String)
    location_province = Column(String)
    location_country = Column(String)
    image_url = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
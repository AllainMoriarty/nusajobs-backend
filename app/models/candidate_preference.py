from sqlalchemy import Column, DateTime, ForeignKey, CheckConstraint, ARRAY, String
from sqlalchemy.dialects.postgresql import UUID, ARRAY, ENUM
from sqlalchemy.sql import func
from app.core.database import Base
from app.schemas.candidate_preference import JobTypeEnum, WorkModeEnum

class CandidatePreference(Base):
    __tablename__ = "candidate_preferences"
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.user_id", ondelete="CASCADE"), primary_key=True)
    job_fields = Column(ARRAY(String), nullable=True)
    job_types = Column(ARRAY(String), nullable=True)
    preferred_cities = Column(ARRAY(String))
    work_modes = Column(ARRAY(String), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
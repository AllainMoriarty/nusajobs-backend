from sqlalchemy import Column, String, DateTime, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.core.database import Base

class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"))
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.user_id", ondelete="CASCADE"))
    cv_id = Column(UUID(as_uuid=True), ForeignKey("candidate_cvs.id", ondelete="CASCADE"))

    status = Column(
        String,
        CheckConstraint(
            "status IN ('applied', 'screened', 'shortlisted', 'rejected')",
            name="check_application_status"
        ),
        default='applied'
    )

    applied_at = Column(DateTime, default=func.now())

    __table_args__ = (
        UniqueConstraint('job_id', 'candidate_id', name='uq_job_candidate'),
    )
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, CheckConstraint, Integer
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.sql import func
import uuid
from app.core.database import Base
from pgvector.sqlalchemy import Vector

class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))
    recruiter_id = Column(UUID(as_uuid=True), ForeignKey("recruiters.user_id"))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    job_field = Column(String, nullable=False)
    job_type = Column(String, nullable=False)
    location = Column(String, nullable=False)
    embedding = Column(Vector(1024))
    top_k = Column(Integer, default=5)
    status = Column(
        String,
        CheckConstraint(
            "status IN ('open', 'closed')",
            name="check_job_status"
        ),
        default='open'
    )
    closed_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
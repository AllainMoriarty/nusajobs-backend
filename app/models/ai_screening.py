from sqlalchemy import Column, Float, Integer, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.core.database import Base

class AIScreening(Base):
    __tablename__ = "ai_screenings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"))
    job_application_id = Column(UUID(as_uuid=True), ForeignKey("job_applications.id", ondelete="CASCADE"))

    score = Column(Float, nullable=False)
    rank = Column(Integer)
    reasoning = Column(Text)

    created_at = Column(DateTime, default=func.now())

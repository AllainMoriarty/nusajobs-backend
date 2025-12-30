from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.core.database import Base
from pgvector.sqlalchemy import Vector

class CandidateCV(Base):
    __tablename__ = "candidate_cvs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.user_id", ondelete="CASCADE"))

    file_url = Column(String, nullable=False)
    ocr_text = Column(Text)
    embedding = Column(Vector(1536))

    created_at = Column(DateTime, default=func.now())
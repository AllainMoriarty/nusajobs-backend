from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.core.database import Base

class Admin(Base):
    __tablename__ = "admins"

    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    company_id = Column(PG_UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), unique=True, nullable=True)
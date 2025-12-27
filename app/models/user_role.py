from sqlalchemy import Column, UUID, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.core.database import Base

class SysUserRole(Base):
    __tablename__ = "sys_user_roles"

    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(Integer, ForeignKey("sys_roles.id"), primary_key=True)
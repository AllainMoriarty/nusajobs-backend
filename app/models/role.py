from sqlalchemy import Column, String, Integer
from app.core.database import Base

class SysRole(Base):
    __tablename__ = "sys_roles"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False)
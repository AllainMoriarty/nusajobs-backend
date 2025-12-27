from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class JobCreate(BaseModel):
    title: str
    description: str
    top_k: Optional[int] = 5
    status: Optional[str] = 'open'

class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    top_k: Optional[int] = None
    status: Optional[str] = None

class JobResponse(BaseModel):
    id: UUID
    company_id: UUID
    recruiter_id: UUID
    title: str
    description: str
    top_k: int
    status: str
    closed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
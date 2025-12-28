from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class JobApplicationCreate(BaseModel):
    job_id: UUID
    cv_id: UUID

class JobApplicationUpdate(BaseModel):
    status: Optional[str] = None

class JobApplicationResponse(BaseModel):
    id: UUID
    job_id: UUID
    candidate_id: UUID
    cv_id: UUID
    status: str
    applied_at: datetime

    class Config:
        from_attributes = True
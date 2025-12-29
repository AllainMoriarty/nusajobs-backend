from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from uuid import UUID

class CandidateCreate(BaseModel):
    full_name: str
    phone: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    location: Optional[str] = None

class CandidateUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    location: Optional[str] = None

class CandidateResponse(BaseModel):
    user_id: UUID
    full_name: str
    phone: Optional[str]
    birth_date: Optional[date]
    gender: Optional[str]
    location: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
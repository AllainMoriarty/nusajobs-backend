from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.schemas.candidate import CandidateResponse

class CandidateCVSchema(BaseModel):
    id: UUID
    candidate_id: UUID
    file_url: str
    ocr_text: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class CandidateCVResponse(BaseModel):
    candidate: CandidateResponse
    candidate_cv: CandidateCVSchema

    class Config:
        from_attributes = True
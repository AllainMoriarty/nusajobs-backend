from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.schemas.job import JobResponse
from app.schemas.candidate import CandidateResponse
from app.schemas.candidate_cv import CandidateCVSchema, CandidateCVResponse
from app.schemas.job import JobResponse

class JobApplicationCreate(BaseModel):
    job_id: UUID
    cv_id: UUID

class JobApplicationUpdate(BaseModel):
    status: Optional[str] = None

class JobApplicationSchema(BaseModel):
    id: UUID
    job_id: UUID
    candidate_id: UUID
    cv_id: UUID
    status: str
    applied_at: datetime

    class Config:
        from_attributes = True

class JobApplicationResponse(BaseModel):
    job: JobResponse
    job_application: JobApplicationSchema
    candidate: CandidateResponse
    candidate_cv: CandidateCVSchema

    class Config:
        from_attributes = True

class MyApplicationItem(BaseModel):
    job: JobResponse
    job_application: JobApplicationSchema

    class Config:
        from_attributes = True

class MyApplicationsResponse(BaseModel):
    candidate: CandidateResponse
    candidate_cv: CandidateCVSchema
    applications: List[MyApplicationItem]

    class Config:
        from_attributes = True

class JobApplicationDetail(BaseModel):
    id: UUID
    job_id: UUID
    candidate_id: UUID
    cv_id: UUID
    status: str
    applied_at: datetime
    candidate: CandidateResponse
    candidate_cv: CandidateCVSchema

    class Config:
        from_attributes = True

class JobApplicationByJob(BaseModel):
    job: JobResponse
    applications: List[JobApplicationDetail]

    class Config:
        from_attributes = True
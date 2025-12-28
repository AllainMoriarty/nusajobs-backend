from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import datetime
import enum
from uuid import UUID

class JobTypeEnum(str, enum.Enum):
    internship = "internship"
    full_time = "full_time"
    part_time = "part_time"
    contract = "contract"
    freelance = "freelance"


class WorkModeEnum(str, enum.Enum):
    remote = "remote"
    hybrid = "hybrid"
    onsite = "onsite"

class CandidatePreferenceCreate(BaseModel):
    job_fields: Optional[List[str]] = []
    job_types: Optional[List[JobTypeEnum]] = []
    preferred_cities: Optional[List[str]] = []
    work_modes: Optional[List[WorkModeEnum]] = []

    @validator("job_types", each_item=True)
    def validate_job_types(cls, v):
        allowed = {item.value for item in JobTypeEnum}
        if v not in allowed:
            raise ValueError(f"Invalid job type: {v}. Allowed: {allowed}")
        return v

    @validator("work_modes", each_item=True)
    def validate_work_modes(cls, v):
        allowed = {item.value for item in WorkModeEnum}
        if v not in allowed:
            raise ValueError(f"Invalid work mode: {v}. Allowed: {allowed}")
        return v

class CandidatePreferenceUpdate(BaseModel):
    job_fields: Optional[List[str]] = None
    job_types: Optional[List[JobTypeEnum]] = None
    preferred_cities: Optional[List[str]] = None
    work_modes: Optional[List[WorkModeEnum]] = None

    @validator("job_types", each_item=True)
    def validate_job_types(cls, v):
        allowed = {item.value for item in JobTypeEnum}
        if v not in allowed:
            raise ValueError(f"Invalid job type: {v}. Allowed: {allowed}")
        return v

    @validator("work_modes", each_item=True)
    def validate_work_modes(cls, v):
        allowed = {item.value for item in WorkModeEnum}
        if v not in allowed:
            raise ValueError(f"Invalid work mode: {v}. Allowed: {allowed}")
        return v

class CandidatePreferenceResponse(BaseModel):
    candidate_id: UUID
    job_fields: List[str]
    job_types: List[str]
    preferred_cities: List[str]
    work_modes: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
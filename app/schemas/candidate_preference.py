from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import enum
from uuid import UUID

class JobFieldEnum(str, enum.Enum):
    admin_hr = "Admin & HR"
    marketing_sales = "Marketing & Sales"
    operations_logistics = "Operations & Logistics"
    finance_accounting = "Finance & Accounting"
    it_technology = "IT & Technology"
    design_creative = "Design & Creative"
    media_communications = "Media & Communications"
    engineering = "Engineering"
    healthcare = "Healthcare"
    education_training = "Education & Training"
    retail_customer_service = "Retail & Customer Service"
    legal = "Legal"
    government_ngo = "Government & NGO"
    manufacturing_industrial = "Manufacturing & Industrial"
    real_estate_construction = "Real Estate & Construction"
    transportation_aviation = "Transportation & Aviation"
    food_hospitality = "Food & Hospitality (F&B)"
    research_science = "Research & Science"
    environment_energy = "Environment & Energy"
    insurance_fintech = "Insurance & Digital Finance"
    security_safety = "Security & Safety (HSE/K3)"
    agriculture_marine = "Agriculture & Marine"
    arts_culture_entertainment = "Arts, Culture & Entertainment"
    psychology_counseling = "Psychology & Counseling"

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
    job_fields: Optional[List[JobFieldEnum]] = []
    job_types: Optional[List[JobTypeEnum]] = []
    preferred_cities: Optional[List[str]] = []
    work_modes: Optional[List[WorkModeEnum]] = []

class CandidatePreferenceUpdate(BaseModel):
    job_fields: Optional[List[JobFieldEnum]] = None
    job_types: Optional[List[JobTypeEnum]] = None
    preferred_cities: Optional[List[str]] = None
    work_modes: Optional[List[WorkModeEnum]] = None

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
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
import enum

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

class JobCreate(BaseModel):
    title: str
    job_field: JobFieldEnum
    job_type: JobTypeEnum
    description: str
    location: str
    top_k: Optional[int] = 5
    status: Optional[str] = 'open'

class JobUpdate(BaseModel):
    title: Optional[str] = None
    job_field: Optional[JobFieldEnum] = None
    job_type: Optional[JobTypeEnum] = None
    description: Optional[str] = None
    location: Optional[str] = None
    top_k: Optional[int] = None
    status: Optional[str] = None

class JobResponse(BaseModel):
    id: UUID
    company_id: UUID
    recruiter_id: UUID
    title: str
    job_field: str
    job_type: str
    description: str
    location: str
    top_k: int
    status: str
    closed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
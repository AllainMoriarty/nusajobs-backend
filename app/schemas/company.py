from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import datetime

class CompanyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    industry: str
    location_city: Optional[str] = None
    location_country: Optional[str] = None
    website_url: Optional[str] = None

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None
    location_city: Optional[str] = None
    location_country: Optional[str] = None
    website_url: Optional[str] = None
    verification_status: Optional[str] = None

class CompanyResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    industry: str
    location_city: Optional[str]
    location_country: Optional[str]
    website_url: Optional[str]
    logo_url: Optional[str]
    verification_status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
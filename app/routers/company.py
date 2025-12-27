from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.company_service import CompanyService
from app.schemas.company import CompanyResponse
from app.core.auth_middleware import get_current_user

router = APIRouter(prefix="/companies", tags=["Companies"])

company_service = CompanyService()

@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_new_company(name: str = Form(...),description: str = Form(None),industry: str = Form(...),location_city: str = Form(None),location_country: str = Form(None),website_url: str = Form(None),logo: UploadFile = File(None), current_user: dict = Depends(get_current_user),db: Session = Depends(get_db)):
    try:
        company_data = {
            "name": name,
            "description": description,
            "industry": industry,
            "location_city": location_city,
            "location_country": location_country,
            "website_url": website_url
        }

        file_data = None
        filename = None
        content_type = None

        if logo:
            file_data = await logo.read()
            filename = logo.filename
            content_type = logo.content_type

        new_company = company_service.create_company_from_form(
            db,
            company_data,
            file_data=file_data,
            filename=filename,
            content_type=content_type,
            current_user=current_user
        )
        return new_company
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company_info(company_id: str,name: str = Form(None),description: str = Form(None),industry: str = Form(None),location_city: str = Form(None),location_country: str = Form(None),website_url: str = Form(None),logo: UploadFile = File(None),current_user: dict = Depends(get_current_user),db: Session = Depends(get_db)):
    try:
        company_data = {}
        if name is not None: company_data["name"] = name
        if description is not None: company_data["description"] = description
        if industry is not None: company_data["industry"] = industry
        if location_city is not None: company_data["location_city"] = location_city
        if location_country is not None: company_data["location_country"] = location_country
        if website_url is not None: company_data["website_url"] = website_url

        file_data = None
        filename = None
        content_type = None

        if logo:
            file_data = await logo.read()
            filename = logo.filename
            content_type = logo.content_type

        updated_company = company_service.update_company_from_form(
            db,
            company_id,
            company_data,
            file_data=file_data,
            filename=filename,
            content_type=content_type,
            current_user=current_user
        )
        if not updated_company:
            raise HTTPException(status_code=404, detail="Company not found")
        return updated_company
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{company_id}", response_model=CompanyResponse)
def read_company(company_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    company = company_service.get_company_by_id(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@router.get("/", response_model=list[CompanyResponse])
def list_all_companies(skip: int = 0, limit: int = 10, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    companies = company_service.list_companies(db, skip, limit)
    return companies
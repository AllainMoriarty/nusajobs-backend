from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.job_service import JobService
from app.schemas.job import JobCreate, JobUpdate, JobResponse
from app.core.auth_middleware import get_current_user

router = APIRouter(prefix="/jobs", tags=["Jobs"])

job_service = JobService()

@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_new_job(job: JobCreate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] not in ["recruiter"]:
        raise HTTPException(status_code=403, detail="Only recruiter can create job")

    company_id = None
    if current_user["role"] == "recruiter":
        from app.models.recruiter import Recruiter
        recruiter = db.query(Recruiter).filter(Recruiter.user_id == current_user["id"]).first()
        if not recruiter:
            raise HTTPException(status_code=403, detail="Recruiter not assigned to company")
        company_id = str(recruiter.company_id)

    new_job = job_service.create_job(db, job, company_id, current_user["id"])
    return new_job

@router.get("/{job_id}", response_model=JobResponse)
def read_job(job_id: str, db: Session = Depends(get_db)):
    job = job_service.get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.put("/{job_id}", response_model=JobResponse)
def update_job_info(job_id: str, job: JobUpdate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] not in ["recruiter"]:
        raise HTTPException(status_code=403, detail="Only recruiter can update job")

    updated_job = job_service.update_job(db, job_id, job)
    if not updated_job:
        raise HTTPException(status_code=404, detail="Job not found")
    return updated_job

@router.delete("/{job_id}")
def delete_job_endpoint(job_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] not in ["recruiter"]:
        raise HTTPException(status_code=403, detail="Only recruiter can delete job")
    
    success = job_service.delete_job(db, job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"message": "Job deleted successfully"}

@router.get("/", response_model=list[JobResponse])
def list_jobs(company_id: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    jobs = job_service.list_jobs_by_company(db, company_id, skip, limit)
    return jobs

@router.post("/search")
def search_jobs(query: str, top_k: int = 5, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    company_id = None
    if current_user["role"] == "admin":
        from app.models.admin import Admin
        admin = db.query(Admin).filter(Admin.user_id == current_user["id"]).first()
        if not admin:
            raise HTTPException(status_code=403, detail="Admin not assigned to company")
        company_id = str(admin.company_id)
    elif current_user["role"] == "recruiter":
        from app.models.recruiter import Recruiter
        recruiter = db.query(Recruiter).filter(Recruiter.user_id == current_user["id"]).first()
        if not recruiter:
            raise HTTPException(status_code=403, detail="Recruiter not assigned to company")
        company_id = str(recruiter.company_id)

    jobs = job_service.search_jobs_by_similarity(db, query, company_id, top_k)
    return jobs
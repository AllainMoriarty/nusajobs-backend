from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.job_application_service import (
    create_job_application, 
    get_application_by_id, 
    get_applications_by_candidate, 
    get_applications_by_job, 
    get_application_by_job_and_candidate, 
    update_application_status, 
    delete_application
)
from app.schemas.job_application import JobApplicationCreate, JobApplicationUpdate, JobApplicationResponse
from app.core.auth_middleware import get_current_user

router = APIRouter(prefix="/job-applications", tags=["Job Applications"])

@router.post("/", response_model=JobApplicationResponse, status_code=status.HTTP_201_CREATED)
def apply_for_job(application: JobApplicationCreate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] != "candidate":
        raise HTTPException(status_code=403, detail="Only candidates can apply for jobs")

    try:
        new_application = create_job_application(db, application, current_user)
        return new_application
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/my-applications", response_model=list[JobApplicationResponse])
def list_my_applications(skip: int = 0, limit: int = 10, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] != "candidate":
        raise HTTPException(status_code=403, detail="Only candidates can access their applications")

    applications = get_applications_by_candidate(db, current_user, skip, limit)
    return applications

@router.get("/job/{job_id}", response_model=list[JobApplicationResponse])
def list_applications_for_job(job_id: str, skip: int = 0, limit: int = 10, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] not in ["recruiter"]:
        raise HTTPException(status_code=403, detail="Only recruiter can view job applications")

    from app.models.job import Job
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    company_id = None
    if current_user["role"] == "recruiter":
        from app.models.recruiter import Recruiter
        recruiter = db.query(Recruiter).filter(Recruiter.user_id == current_user["id"]).first()
        if not recruiter:
            raise HTTPException(status_code=403, detail="Recruiter not assigned to company")
        company_id = recruiter.company_id

    if str(job.company_id) != str(company_id):
        raise HTTPException(status_code=403, detail="Access denied")

    applications = get_applications_by_job(db, job_id, skip, limit)
    return applications

@router.get("/{application_id}", response_model=JobApplicationResponse)
def get_application(application_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    application = get_application_by_id(db, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    if current_user["role"] == "candidate":
        if str(application.candidate_id) != current_user["id"]:
            raise HTTPException(status_code=403, detail="Access denied")
    elif current_user["role"] in ["recruiter"]:
        from app.models.job import Job
        job = db.query(Job).filter(Job.id == application.job_id).first()
        
        company_id = None
        if current_user["role"] == "recruiter":
            from app.models.recruiter import Recruiter
            recruiter = db.query(Recruiter).filter(Recruiter.user_id == current_user["id"]).first()
            if not recruiter:
                raise HTTPException(status_code=403, detail="Recruiter not assigned to company")
            company_id = recruiter.company_id

        if str(job.company_id) != str(company_id):
            raise HTTPException(status_code=403, detail="Access denied")
    else:
        raise HTTPException(status_code=403, detail="Access denied")

    return application

@router.put("/{application_id}", response_model=JobApplicationResponse)
def update_application_status_endpoint(application_id: str, application_update: JobApplicationUpdate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        updated_application = update_application_status(db, application_id, application_update.status, current_user)
        if not updated_application:
            raise HTTPException(status_code=404, detail="Application not found")
        return updated_application
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{application_id}")
def delete_my_application(application_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] != "candidate":
        raise HTTPException(status_code=403, detail="Only candidates can delete their applications")

    success = delete_application(db, application_id, current_user)
    if not success:
        raise HTTPException(status_code=404, detail="Application not found")

    return {"message": "Application deleted successfully"}

@router.get("/job/{job_id}/candidate/{candidate_id}", response_model=JobApplicationResponse)
def get_application_by_job_and_candidate_endpoint(job_id: str, candidate_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] == "candidate":
        if candidate_id != current_user["id"]:
            raise HTTPException(status_code=403, detail="Access denied")
    elif current_user["role"] == "recruiter":
        from app.models.job import Job
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        company_id = None
        if current_user["role"] == "recruiter":
            from app.models.recruiter import Recruiter
            recruiter = db.query(Recruiter).filter(Recruiter.user_id == current_user["id"]).first()
            if not recruiter:
                raise HTTPException(status_code=403, detail="Recruiter not assigned to company")
            company_id = recruiter.company_id

        if str(job.company_id) != str(company_id):
            raise HTTPException(status_code=403, detail="Access denied")
    else:
        raise HTTPException(status_code=403, detail="Access denied")

    application = get_application_by_job_and_candidate(db, job_id, candidate_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    return application
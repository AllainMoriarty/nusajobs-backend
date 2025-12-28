from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.job_service import JobService
from app.schemas.job import JobCreate, JobUpdate, JobResponse
from app.core.auth_middleware import require_role
from app.core.exceptions import JobNotFoundError, RecruiterNotFoundError
from uuid import UUID

router = APIRouter(prefix="/jobs", tags=["Jobs"])
job_service = JobService()


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_new_job(job: JobCreate, current_user: dict = Depends(require_role(["recruiter"])), db: Session = Depends(get_db)):
    """
    Create a new job posting for the authenticated recruiter's company.
    
    Only users with the 'recruiter' role can create jobs.
    The system automatically links the job to the recruiter's company.
    """
    try:
        return job_service.create_job(db, job, current_user["id"])
    except RecruiterNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create job"
        )


@router.get("/{job_id}", response_model=JobResponse)
def read_job(job_id: UUID, db: Session = Depends(get_db)):
    """
    Retrieve a specific job by its ID.
    
    This endpoint is currently public. If jobs should be private,
    add authentication and ownership validation in the future.
    """
    job = job_service.get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.put("/{job_id}", response_model=JobResponse)
def update_job_info(job_id: UUID, job: JobUpdate, current_user: dict = Depends(require_role(["recruiter"])), db: Session = Depends(get_db)):
    """
    Update an existing job posting.
    
    Only the recruiter who created the job can modify it.
    Ensures data integrity and prevents unauthorized edits.
    """
    try:
        return job_service.update_job(db, job_id, job, current_user["id"])
    except JobNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or not authorized"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update job"
        )


@router.delete("/{job_id}")
def delete_job_endpoint(job_id: UUID, current_user: dict = Depends(require_role(["recruiter"])), db: Session = Depends(get_db)):
    """
    Delete a job posting permanently.
    
    Only the owner recruiter can delete their own job.
    Returns a success message if deletion is successful.
    """
    try:
        job_service.delete_job(db, job_id, current_user["id"])
        return {"message": "Job deleted successfully"}
    except JobNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or not authorized"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete job"
        )


@router.get("/", response_model=list[JobResponse])
def list_jobs(company_id: UUID = None, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Retrieve a paginated list of jobs.
    
    - If `company_id` is provided, only jobs from that company are returned.
    - If `company_id` is omitted, all jobs across all companies are returned (public job board).
    
    Useful for both company-specific dashboards and public listings.
    """
    if company_id:
        return job_service.list_jobs_by_company(db, company_id, skip, limit)
    else:
        return job_service.list_all_jobs(db, skip, limit)
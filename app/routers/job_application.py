from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.job_application_service import JobApplicationService
from app.schemas.job_application import JobApplicationCreate, JobApplicationUpdate, JobApplicationResponse, JobApplicationSchema, JobApplicationByJob, MyApplicationsResponse
from app.core.auth_middleware import require_role
from app.core.exceptions import JobApplicationNotFoundError, JobApplicationAlreadyExistsError, CVNotFoundError, JobApplicationPermissionError
from uuid import UUID
from app.models.job import Job
from app.models.recruiter import Recruiter

router = APIRouter(prefix="/job-applications", tags=["Job Applications"])
application_service = JobApplicationService()


@router.post("/", response_model=JobApplicationSchema, status_code=status.HTTP_201_CREATED)
def apply_to_job(application: JobApplicationCreate, current_user: dict = Depends(require_role(["candidate"])), db: Session = Depends(get_db)):
    """
    Submit a job application using a selected CV.
    
    A candidate can only apply once to the same job.
    The selected CV must belong to the candidate.
    """
    try:
        return application_service.create_application(db, application, current_user["id"])
    except JobApplicationAlreadyExistsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except CVNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to submit application")


@router.get("/me", response_model=MyApplicationsResponse)
def get_my_applications(skip: int = 0, limit: int = 10, current_user: dict = Depends(require_role(["candidate"])), db: Session = Depends(get_db)):
    """
    Retrieve all job applications submitted by the authenticated candidate.
    
    Supports pagination via 'skip' and 'limit'.
    """
    try:
        return application_service.get_my_applications(db, current_user["id"], skip, limit)
    except JobApplicationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to retrieve applications")


@router.get("/job/{job_id}", response_model=JobApplicationByJob)
def get_applications_for_job(job_id: UUID, skip: int = 0, limit: int = 10, current_user: dict = Depends(require_role(["recruiter"])), db: Session = Depends(get_db)):
    """
    Retrieve all applications for a specific job.
    
    - Recruiters can only view jobs from their company.
    - Admins can view all (future: add company validation for admin too if needed).
    """
    try:
        return application_service.get_applications_for_job(db, job_id, current_user, skip, limit)
    except JobApplicationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except JobApplicationPermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to retrieve applications")


@router.get("/{application_id}", response_model=JobApplicationResponse)
def get_application(application_id: UUID, current_user: dict = Depends(require_role(["candidate", "recruiter"])), db: Session = Depends(get_db)):
    """
    Retrieve a specific job application by ID.
    
    - Candidates can only view their own applications.
    - Recruiters can view applications to their company's jobs.
    """
    try:
        app = application_service.get_application_by_id(db, application_id, current_user)
        return app
    except JobApplicationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except JobApplicationPermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to retrieve application")


@router.patch("/{application_id}", response_model=JobApplicationSchema)
def update_application_status(application_id: UUID, update: JobApplicationUpdate, current_user: dict = Depends(require_role(["recruiter"])), db: Session = Depends(get_db)):
    """
    Update the status of a job application (e.g., 'shortlisted', 'rejected').
    
    Only recruiters from the job's company can update the status.
    """
    if not update.status:
        raise HTTPException(status_code=400, detail="Status field is required")

    try:
        return application_service.update_application_status(
            db, application_id, update.status, current_user["id"])
    except JobApplicationPermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except JobApplicationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to update application status")


@router.delete("/{application_id}")
def delete_application(application_id: UUID, current_user: dict = Depends(require_role(["candidate"])), db: Session = Depends(get_db)):
    """
    Only the candidate who submitted the application can delete it.
    """
    try:
        application_service.delete_my_application(db, application_id, current_user["id"])
        return {"message": "Application deleted successfully"}
    except JobApplicationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to delete application")
from sqlalchemy.orm import Session
from app.models.job_application import JobApplication
from app.models.candidate_cv import CandidateCV
from app.models.job import Job
from app.schemas.job_application import JobApplicationCreate, JobApplicationUpdate
from uuid import UUID

def create_job_application(db: Session, application_data: JobApplicationCreate, current_user: dict = None):
    if current_user["role"] != "candidate":
        raise Exception("Only candidates can apply for jobs")
    
    existing_application = db.query(JobApplication).filter(
        JobApplication.job_id == application_data.job_id,
        JobApplication.candidate_id == current_user["id"]
    ).first()
    
    if existing_application:
        raise Exception("Candidate already applied to this job")
    
    cv = db.query(CandidateCV).filter(
        CandidateCV.id == application_data.cv_id,
        CandidateCV.candidate_id == current_user["id"]
    ).first()
    
    if not cv:
        raise Exception("CV not found or doesn't belong to candidate")

    db_application = JobApplication(
        job_id=application_data.job_id,
        candidate_id=current_user["id"],
        cv_id=application_data.cv_id
    )
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application

def get_application_by_id(db: Session, application_id: str):
    return db.query(JobApplication).filter(JobApplication.id == application_id).first()

def get_applications_by_candidate(db: Session, current_user: dict, skip: int = 0, limit: int = 10):
    return (
        db.query(JobApplication)
        .filter(JobApplication.candidate_id == current_user["id"])
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_applications_by_job(db: Session, job_id: str, skip: int = 0, limit: int = 10):
    return (
        db.query(JobApplication)
        .filter(JobApplication.job_id == job_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_application_by_job_and_candidate(db: Session, job_id: str, candidate_id: str):
    return db.query(JobApplication).filter(
        JobApplication.job_id == job_id,
        JobApplication.candidate_id == candidate_id
    ).first()

def update_application_status(db: Session, application_id: str, status: str, current_user: dict):
    db_application = db.query(JobApplication).filter(JobApplication.id == application_id).first()
    if not db_application:
        return None

    if current_user["role"] not in ["recruiter"]:
        raise Exception("Only recruiter can update application status")

    job = db.query(Job).filter(Job.id == db_application.job_id).first()

    if current_user["role"] == "recruiter":
        from app.models.recruiter import Recruiter
        recruiter = db.query(Recruiter).filter(Recruiter.user_id == current_user["id"]).first()
        if not recruiter:
            raise Exception("Recruiter not assigned to company")

    if str(job.company_id) != current_user["id"]:
        raise Exception("Cannot update application for job outside your company")

    db_application.status = status
    db.commit()
    db.refresh(db_application)
    return db_application

def delete_application(db: Session, application_id: str, current_user: dict):
    if current_user["role"] != "candidate":
        raise Exception("Only candidates can delete their applications")

    db_application = db.query(JobApplication).filter(
        JobApplication.id == application_id,
        JobApplication.candidate_id == current_user["id"]
    ).first()
    
    if not db_application:
        return False

    db.delete(db_application)
    db.commit()
    return True
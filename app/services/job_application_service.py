from sqlalchemy.orm import Session
from app.models.job_application import JobApplication
from app.models.candidate_cv import CandidateCV
from app.models.job import Job
from app.models.recruiter import Recruiter
from app.schemas.job_application import JobApplicationCreate, JobApplicationUpdate
from uuid import UUID
from app.core.exceptions import JobApplicationNotFoundError, JobApplicationAlreadyExistsError, CVNotFoundError, JobApplicationPermissionError


class JobApplicationService:
    def create_application(self, db: Session, application_data: JobApplicationCreate, candidate_id: UUID):
        existing = db.query(JobApplication).filter(JobApplication.job_id == application_data.job_id,JobApplication.candidate_id == candidate_id).first()
        if existing:
            raise JobApplicationAlreadyExistsError("Candidate already applied to this job")

        cv = db.query(CandidateCV).filter(CandidateCV.id == application_data.cv_id,CandidateCV.candidate_id == candidate_id).first()
        if not cv:
            raise CVNotFoundError("CV not found or doesn't belong to candidate")

        db_application = JobApplication(
            job_id=application_data.job_id,
            candidate_id=candidate_id,
            cv_id=application_data.cv_id
        )
        db.add(db_application)
        db.commit()
        db.refresh(db_application)
        return db_application

    def get_application_by_id(self, db: Session, application_id: UUID, current_user: dict):
        app = db.query(JobApplication).filter(JobApplication.id == application_id).first()
        if not app:
            raise JobApplicationNotFoundError("Job application not found")
        
        if current_user["role"] == "candidate" and app.candidate_id != current_user["id"]:
            raise JobApplicationPermissionError("Not authorized to view this application")
        
        if current_user["role"] == "recruiter":
            job = db.query(Job).filter(Job.id == app.job_id).first()
            if not job:
                raise JobApplicationNotFoundError("Associated job not found")
            recruiter = db.query(Recruiter).filter(Recruiter.user_id == current_user["id"]).first()
            if not recruiter or recruiter.company_id != job.company_id:
                raise JobApplicationPermissionError("Not authorized to view this application")

        return app

    def get_my_applications(self, db: Session, candidate_id: UUID, skip: int = 0, limit: int = 10):
        return (
            db.query(JobApplication)
            .filter(JobApplication.candidate_id == candidate_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_applications_for_job(self, db: Session, job_id: UUID, skip: int = 0, limit: int = 10):
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise JobApplicationNotFoundError("Job not found")

        return (
            db.query(JobApplication)
            .filter(JobApplication.job_id == job_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_application_status(self, db: Session, application_id: UUID, status: str, user_id: UUID):
        app = db.query(JobApplication).filter(JobApplication.id == application_id).first()
        if not app:
            raise JobApplicationNotFoundError("Job application not found")

        # Validasi: recruiter hanya boleh update job dari perusahaannya
        job = db.query(Job).filter(Job.id == app.job_id).first()
        if not job:
            raise JobApplicationNotFoundError("Associated job not found")

        recruiter = db.query(Recruiter).filter(Recruiter.user_id == user_id).first()
        if not recruiter or recruiter.company_id != job.company_id:
            raise JobApplicationPermissionError("Cannot update application for job outside your company")

        app.status = status
        db.commit()
        db.refresh(app)
        return app

    def delete_my_application(self, db: Session, application_id: UUID, candidate_id: UUID):
        app = db.query(JobApplication).filter(
            JobApplication.id == application_id,
            JobApplication.candidate_id == candidate_id
        ).first()
        if not app:
            raise JobApplicationNotFoundError("Job application not found or not owned by you")

        db.delete(app)
        db.commit()
        return True
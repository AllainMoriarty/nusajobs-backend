from sqlalchemy.orm import Session, joinedload
from app.models.job_application import JobApplication
from app.models.candidate_cv import CandidateCV
from app.models.job import Job
from app.models.recruiter import Recruiter
from app.models.candidate import Candidate
from app.schemas.job_application import JobApplicationCreate, JobApplicationUpdate
from uuid import UUID
from app.core.exceptions import JobApplicationNotFoundError, JobApplicationAlreadyExistsError, CVNotFoundError, JobApplicationPermissionError, CandidateNotFoundError


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
        # Fetch the application
        app = db.query(JobApplication).filter(JobApplication.id == application_id).first()
        if not app:
            raise JobApplicationNotFoundError("Job application not found")

        # Authorization checks
        if current_user["role"] == "candidate" and app.candidate_id != current_user["id"]:
            raise JobApplicationPermissionError("Not authorized to view this application")

        if current_user["role"] == "recruiter":
            job = db.query(Job).filter(Job.id == app.job_id).first()
            if not job:
                raise JobApplicationNotFoundError("Associated job not found")
            recruiter = db.query(Recruiter).filter(Recruiter.user_id == current_user["id"]).first()
            if not recruiter or recruiter.company_id != job.company_id:
                raise JobApplicationPermissionError("Not authorized to view this application")

        # Fetch related data
        candidate = db.query(Candidate).filter(Candidate.user_id == app.candidate_id).first()
        if not candidate:
            raise CandidateNotFoundError("Candidate profile not found")

        cv = db.query(CandidateCV).filter(CandidateCV.id == app.cv_id).first()  # Fixed filter
        if not cv:
            raise CVNotFoundError("CV not found")

        job = db.query(Job).filter(Job.id == app.job_id).first()
        if not job:
            raise JobApplicationNotFoundError("Associated job not found")

        # Return a dictionary or object compatible with JobApplicationDetailResponse
        return {
            "job": job,
            "candidate": candidate,
            "candidate_cv": cv,
            "job_application": app
        }

    def get_my_applications(self, db: Session, candidate_id: UUID, skip: int = 0, limit: int = 10):
        applications = (
            db.query(JobApplication, Job)
            .join(Job, Job.id == JobApplication.job_id)
            .filter(JobApplication.candidate_id == candidate_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

        if not applications:
            raise JobApplicationNotFoundError("Job Application not found")

        candidate = (
            db.query(Candidate)
            .filter(Candidate.user_id == candidate_id)
            .first()
        )
        if not candidate:
            raise CandidateNotFoundError("Candidate profile not found")
        
        cv = db.query(CandidateCV).filter(CandidateCV.candidate_id == candidate_id).first()

        applied = []

        for app, job in applications:
            applied.append({
                "job": job,
                "job_application": app
            })

        results = {
            "candidate": candidate,
            "candidate_cv": cv,
            "applications": applied

        }

        return results


    def get_applications_for_job(self, db: Session, job_id: UUID, current_user: dict, skip: int = 0, limit: int = 10):
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise JobApplicationNotFoundError("Job not found")
        
        recruiter = db.query(Recruiter).filter(Recruiter.user_id == current_user["id"]).first()
        if not recruiter or recruiter.company_id != job.company_id:
            raise JobApplicationPermissionError("Cannot see application for job outside your company")
        
        applications = (
            db.query(JobApplication, Candidate, CandidateCV).join(Candidate, Candidate.user_id == JobApplication.candidate_id)
            .join(CandidateCV, CandidateCV.candidate_id == JobApplication.candidate_id).filter(JobApplication.job_id == job_id)
            .offset(skip).limit(limit).all())

        if not applications:
            raise JobApplicationNotFoundError("Job Application not found")
        
        applicants = []
        for app, candidate, cv in applications:
            applicants.append({
                "id": app.id,
                "job_id": app.job_id,
                "candidate_id": app.candidate_id,
                "cv_id": app.cv_id,
                "status": app.status,
                "applied_at": app.applied_at,
                "candidate": candidate,
                "candidate_cv": cv,
            })

        return {
            "job": job,
            "applications": applicants
        }

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
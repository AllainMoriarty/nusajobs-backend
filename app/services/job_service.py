from sqlalchemy.orm import Session
from app.models.job import Job
from app.schemas.job import JobCreate, JobUpdate
from uuid import UUID
from app.services.embedding_service import embedding_service
from datetime import datetime
from app.models.recruiter import Recruiter
from app.core.exceptions import JobNotFoundError, RecruiterNotFoundError
import logging

logger = logging.getLogger(__name__)


class JobService:
    def create_job(self, db: Session, job_data: JobCreate, recruiter_id: UUID):
        logger.info("user_id type:", type(recruiter_id))
        logger.info("Sample DB user_id type:", type(db.query(Recruiter.user_id).first()))
        recruiter = db.query(Recruiter).filter(Recruiter.user_id == recruiter_id).first()
        if not recruiter:
            raise RecruiterNotFoundError("Recruiter profile not found for this user")

        embedding = embedding_service.encode(job_data.description)
        closed_at = datetime.utcnow() if job_data.status == 'closed' else None

        db_job = Job(
            title=job_data.title,
            job_field=job_data.job_field,
            job_type=job_data.job_type,
            description=job_data.description,
            location=job_data.location,
            embedding=embedding,
            top_k=job_data.top_k,
            status=job_data.status,
            closed_at=closed_at,
            company_id=recruiter.company_id,
            recruiter_id=recruiter_id
        )
        db.add(db_job)
        db.commit()
        db.refresh(db_job)
        return db_job

    def get_job_by_id(self, db: Session, job_id: UUID):
        return db.query(Job).filter(Job.id == job_id).first()

    def update_job(self, db: Session, job_id: UUID, job_data: JobUpdate, recruiter_id: UUID):
        db_job = db.query(Job).filter(
            Job.id == job_id,
            Job.recruiter_id == recruiter_id
        ).first()
        if not db_job:
            raise JobNotFoundError()

        for key, value in job_data.dict(exclude_unset=True).items():
            setattr(db_job, key, value)

        if job_data.description:
            embedding = embedding_service.encode(job_data.description)
            db_job.embedding = embedding

        if job_data.status:
            if job_data.status == 'closed' and db_job.closed_at is None:
                db_job.closed_at = datetime.utcnow()
            elif job_data.status == 'open':
                db_job.closed_at = None

        db.commit()
        db.refresh(db_job)
        return db_job

    def delete_job(self, db: Session, job_id: UUID, recruiter_id: UUID):
        db_job = db.query(Job).filter(
            Job.id == job_id,
            Job.recruiter_id == recruiter_id
        ).first()
        if not db_job:
            raise JobNotFoundError()

        db.delete(db_job)
        db.commit()
        return True

    def list_jobs_by_company(self, db: Session, company_id: UUID, skip: int = 0, limit: int = 10):
        return db.query(Job).filter(Job.company_id == company_id).offset(skip).limit(limit).all()
    
    def list_all_jobs(self, db: Session, skip: int = 0, limit: int = 10):
        return db.query(Job).offset(skip).limit(limit).all()
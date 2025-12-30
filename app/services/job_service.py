from sqlalchemy.orm import Session
from app.models.job import Job
from app.schemas.job import JobCreate, JobUpdate
from uuid import UUID
from app.services.embedding_service import embedding_service
from datetime import datetime
from app.models.recruiter import Recruiter
from app.core.exceptions import JobNotFoundError, RecruiterNotFoundError, JobApplicationNotFoundError, JobNotFoundError, AIScreeningNotFoundError, AIInterviewQuestionNotFoundError, AIScreeningNotReadyError
import logging
from app.models.job_application import JobApplication
from app.services.job_application_service import JobApplicationService
from app.models.ai_screening import AIScreening
from app.models.ai_interview_question import AIInterviewQuestion
from app.services.ai_screening_service import AIScreeningService
from app.models.company import Company

logger = logging.getLogger(__name__)

ai_screening_service = AIScreeningService()

class JobService:
    def create_job(self, db: Session, job_data: JobCreate, recruiter_id: UUID):
        logger.info("user_id type: %s", type(recruiter_id))
        logger.info("Sample DB user_id type: %s", type(db.query(Recruiter.user_id).first()))
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
        job, company = db.query(Job, Company).join(Company, Company.id == Job.company_id).filter(Job.id == job_id).first()
        return {
            "job": job,
            "company": company
        }

    def update_job(self, db: Session, job_id: UUID, job_data: JobUpdate, recruiter_id: UUID):
        job = (db.query(Job).filter(Job.id == job_id, Job.recruiter_id == recruiter_id).first())
        if not job:
            raise JobNotFoundError()

        previous_status = job.status

        for key, value in job_data.dict(exclude_unset=True).items():
            setattr(job, key, value)

        if job_data.description:
            job.embedding = embedding_service.encode(job_data.description)

        if job_data.status:
            if job_data.status == "closed" and job.closed_at is None:
                job.closed_at = datetime.utcnow()
            elif job_data.status == "open":
                job.closed_at = None

        db.commit()
        db.refresh(job)

        if previous_status != "closed" and job.status == "closed":
            logger.info(f"Running AI screening for job {job.id}")
            ai_screening_service.run(db, job)

        return job
    
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
        jobs = db.query(Job).filter(Job.company_id == company_id).offset(skip).limit(limit).all()
        company = db.query(Company).filter(Company.id == company_id).first()
        if not jobs:
            raise JobNotFoundError()
        return {
            "company": company,
            "jobs": jobs
        }
    
    def list_all_jobs(self, db: Session, skip: int = 0, limit: int = 10):
        rows = db.query(Job, Company).join(Company, Company.id == Job.company_id).offset(skip).limit(limit).all()

        results = []
        for job, company in rows:
            results.append({
                "job": job,
                "company": company
            })
        
        return results
    
    def get_ai_results_by_job_id(self, db: Session, job_id: UUID, recruiter_id: UUID):
        job = (db.query(Job).filter(Job.id == job_id, Job.recruiter_id == recruiter_id).first())
        if not job:
            raise JobNotFoundError()

        if job.status != "closed":
            raise AIScreeningNotReadyError("Job is not closed yet")

        screenings = (db.query(AIScreening, JobApplication.candidate_id).join(JobApplication, AIScreening.job_application_id == JobApplication.id)
                      .filter(AIScreening.job_id == job_id).order_by(AIScreening.rank).all())

        if not screenings:
            raise AIScreeningNotFoundError()

        screening_items = [
            {
                "job_application_id": screening.job_application_id,
                "candidate_id": candidate_id,
                "score": screening.score,
                "rank": screening.rank,
                "reasoning": screening.reasoning
            }
            for screening, candidate_id in screenings
        ]

        interview_questions = (db.query(AIInterviewQuestion).filter(AIInterviewQuestion.job_id == job_id).all())

        if not interview_questions:
            raise AIInterviewQuestionNotFoundError()

        question_items = [
            {
                "candidate_id": iq.candidate_id,
                "questions": iq.questions
            }
            for iq in interview_questions
        ]

        return {
            "job_id": job_id,
            "screenings": screening_items,
            "interview_questions": question_items,
            "generated_at": job.closed_at
        }
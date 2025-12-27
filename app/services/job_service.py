from sqlalchemy.orm import Session
from app.models.job import Job
from app.schemas.job import JobCreate, JobUpdate
from uuid import UUID
from app.services.embedding_service import embedding_service
from datetime import datetime

class JobService:
    def create_job(self, db: Session, job_data: JobCreate, company_id: str, recruiter_id: str):
        try:
            db.begin()
            
            embedding = embedding_service.encode(job_data.description)

            closed_at = datetime.utcnow() if job_data.status == 'closed' else None

            db_job = Job(
                title=job_data.title,
                description=job_data.description,
                embedding=embedding,
                top_k=job_data.top_k,
                status=job_data.status,
                closed_at=closed_at,
                company_id=company_id,
                recruiter_id=recruiter_id)
            db.add(db_job)
            db.commit()
            db.refresh(db_job)
            return db_job

        except Exception as e:
            db.rollback()
            raise e

    def get_job_by_id(self, db: Session, job_id: str):
        return db.query(Job).filter(Job.id == UUID(job_id)).first()

    def update_job(self, db: Session, job_id: str, job_data: JobUpdate):
        try:
            db.begin()
            
            db_job = db.query(Job).filter(Job.id == UUID(job_id)).first()
            if not db_job:
                return None

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

        except Exception as e:
            db.rollback()
            raise e

    def delete_job(self, db: Session, job_id: str):
        try:
            db.begin()
            
            db_job = db.query(Job).filter(Job.id == UUID(job_id)).first()
            if not db_job:
                return False
            db.delete(db_job)
            db.commit()
            return True

        except Exception as e:
            db.rollback()
            raise e

    def list_jobs_by_company(self, db: Session, company_id: str, skip: int = 0, limit: int = 10):
        return db.query(Job).filter(Job.company_id == UUID(company_id)).offset(skip).limit(limit).all()

    def search_jobs_by_similarity(self, db: Session, query: str, company_id: str, top_k: int = 5):
        query_embedding = embedding_service.encode(query)

        jobs = db.query(Job).filter(Job.company_id == UUID(company_id)).all()

        job_similarities = []
        for job in jobs:
            similarity = embedding_service.cosine_similarity(query_embedding, job.embedding)
            job_similarities.append((job, similarity))

        job_similarities.sort(key=lambda x: x[1], reverse=True)

        return [job for job, _ in job_similarities[:top_k]]
from sqlalchemy.orm import Session
from app.models.candidate_cv import CandidateCV
from app.services.cv_processing_service import cv_processing_service
from app.services.s3_service import s3_service
import uuid

async def upload_cv_file(db: Session, file_data: bytes, filename: str, candidate_id: str):
    """Upload CV file, process it, and save to database"""
    # Upload to S3
    s3_filename = f"cvs/{candidate_id}/{uuid.uuid4()}.pdf"
    file_url = s3_service.upload_file(file_data, s3_filename, "application/pdf")

    if not file_url:
        raise Exception("Failed to upload file to S3")

    # Process CV file (extract text, get summary, generate embedding)
    ocr_text, llm_summary, embedding = await cv_processing_service.process_cv_file(file_data, filename)

    # Create CV record
    db_cv = CandidateCV(
        candidate_id=candidate_id,
        file_url=file_url,
        ocr_text=ocr_text,
        llm_summary=llm_summary,
        embedding=embedding
    )
    db.add(db_cv)
    db.commit()
    db.refresh(db_cv)
    return db_cv

def get_cv_by_id(db: Session, cv_id: str):
    return db.query(CandidateCV).filter(CandidateCV.id == cv_id).first()

def get_cvs_by_candidate(db: Session, candidate_id: str, skip: int = 0, limit: int = 10):
    return (
        db.query(CandidateCV)
        .filter(CandidateCV.candidate_id == candidate_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def delete_cv(db: Session, cv_id: str, candidate_id: str):
    db_cv = db.query(CandidateCV).filter((CandidateCV.id == cv_id),CandidateCV.candidate_id == candidate_id).first()
    
    if not db_cv:
        return False

    # Delete file from S3
    try:
        # Extract filename from URL
        s3_key = db_cv.file_url.split('/')[-2] + '/' + db_cv.file_url.split('/')[-1]
        s3_service.delete_file(s3_key)
    except Exception as e:
        print(f"Error deleting file from S3: {e}")

    db.delete(db_cv)
    db.commit()
    return True
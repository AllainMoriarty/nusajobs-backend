from sqlalchemy.orm import Session
from app.models.candidate_cv import CandidateCV
from app.services.cv_processing_service import cv_processing_service
from app.services.s3_service import s3_service
from uuid import UUID
from app.core.exceptions import CVNotFoundError, CVUploadError, CVDownloadError
import uuid


class CandidateCVService:
    async def upload_cv(self, db: Session, file_data: bytes, filename: str, candidate_id: UUID):
        """
        Upload CV baru. Hanya bisa jika belum pernah upload.
        """
        # Cek apakah candidate sudah punya CV
        existing_cv = db.query(CandidateCV).filter(CandidateCV.candidate_id == candidate_id).first()
        
        if existing_cv:
            raise CVUploadError("You have already uploaded a CV. Please use the update endpoint to replace it.")
        
        # Upload file ke S3
        s3_filename = f"cvs/{candidate_id}/{uuid.uuid4()}.pdf"
        file_url = s3_service.upload_file(file_data, s3_filename, "application/pdf")
        if not file_url:
            raise CVUploadError("Failed to upload file to S3")

        try:
            # Process CV: OCR, LLM summary, embedding
            ocr_text, llm_summary, embedding = await cv_processing_service.process_cv_file(file_data, filename)
        except Exception as e:
            # Hapus file dari S3 jika processing gagal
            s3_service.delete_file(s3_filename)
            raise CVUploadError(f"Failed to process CV: {str(e)}")

        # Buat record baru
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

    async def update_cv(self, db: Session, file_data: bytes, filename: str, candidate_id: UUID):
        """
        Update CV yang sudah ada. Hanya bisa jika sudah pernah upload.
        """
        # Cek apakah candidate sudah punya CV
        existing_cv = db.query(CandidateCV).filter(CandidateCV.candidate_id == candidate_id).first()
        
        if not existing_cv:
            raise CVNotFoundError("You haven't uploaded a CV yet. Please use the upload endpoint first.")
        
        # Upload file baru ke S3
        s3_filename = f"cvs/{candidate_id}/{uuid.uuid4()}.pdf"
        file_url = s3_service.upload_file(file_data, s3_filename, "application/pdf")
        if not file_url:
            raise CVUploadError("Failed to upload file to S3")

        try:
            # Process CV: OCR, LLM summary, embedding
            ocr_text, llm_summary, embedding = await cv_processing_service.process_cv_file(file_data, filename)
        except Exception as e:
            # Hapus file baru dari S3 jika processing gagal
            s3_service.delete_file(s3_filename)
            raise CVUploadError(f"Failed to process CV: {str(e)}")

        # Hapus semua file lama dari S3 berdasarkan prefix candidate_id
        # Kecuali file yang baru saja di-upload
        try:
            old_files = s3_service.list_files_by_prefix(f"cvs/{candidate_id}/")
            for old_file in old_files:
                if old_file != s3_filename:  # Jangan hapus file yang baru di-upload
                    s3_service.delete_file(old_file)
        except Exception as e:
            print(f"Warning: Failed to delete old S3 files: {e}")
        
        # Update existing record
        existing_cv.file_url = file_url
        existing_cv.ocr_text = ocr_text
        existing_cv.llm_summary = llm_summary
        existing_cv.embedding = embedding
        
        db.commit()
        db.refresh(existing_cv)
        return existing_cv

    def get_my_cv(self, db: Session, candidate_id: UUID):
        """
        Get CV milik candidate (hanya 1 CV per candidate)
        """
        return db.query(CandidateCV).filter(CandidateCV.candidate_id == candidate_id).first()

    def get_cv_by_id(self, db: Session, cv_id: UUID):
        cv = db.query(CandidateCV).filter(CandidateCV.id == cv_id).first()
        if not cv:
            raise CVNotFoundError("CV not found")
        return cv

    def delete_cv(self, db: Session, candidate_id: UUID):
        """
        Delete CV milik candidate
        """
        cv = db.query(CandidateCV).filter(CandidateCV.candidate_id == candidate_id).first()
        if not cv:
            raise CVNotFoundError("CV not found")

        # Delete semua file dari S3 berdasarkan prefix candidate_id
        try:
            s3_service.delete_files_by_prefix(f"cvs/{candidate_id}/")
        except Exception as e:
            print(f"Warning: Failed to delete S3 files: {e}")

        db.delete(cv)
        db.commit()
        return True
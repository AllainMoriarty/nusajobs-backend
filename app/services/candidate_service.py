from sqlalchemy.orm import Session
from app.models.candidate import Candidate
from app.schemas.candidate import CandidateCreate, CandidateUpdate
from app.services.s3_service import s3_service
from uuid import UUID, uuid4
from app.core.exceptions import CandidateNotFoundError, CandidateAlreadyExistsError


class CandidateService:
    def create_candidate(self, db: Session, candidate_data: CandidateCreate, user_id: UUID):
        existing = db.query(Candidate).filter(Candidate.user_id == user_id).first()
        if existing:
            raise CandidateAlreadyExistsError("Candidate profile already exists")

        db_candidate = Candidate(
            user_id=user_id,
            **candidate_data.model_dump()
        )
        db.add(db_candidate)
        db.commit()
        db.refresh(db_candidate)
        return db_candidate

    def get_my_profile(self, db: Session, user_id: UUID):
        candidate = db.query(Candidate).filter(Candidate.user_id == user_id).first()
        if not candidate:
            raise CandidateNotFoundError("Candidate profile not found")
        return candidate

    def get_candidate_by_id(self, db: Session, candidate_id: UUID):
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate:
            raise CandidateNotFoundError("Candidate profile not found")
        return candidate

    def update_profile_with_image(self, db: Session, candidate_data: dict, file_data: bytes = None, filename: str = None, content_type: str = None, user_id: UUID = None):
        """
        Update candidate profile dengan image upload
        """
        db_candidate = db.query(Candidate).filter(Candidate.user_id == user_id).first()
        if not db_candidate:
            raise CandidateNotFoundError("Candidate profile not found")

        try:
            # Update data candidate
            for key, value in candidate_data.items():
                if value is not None:
                    setattr(db_candidate, key, value)

            # Flush untuk mendapatkan ID jika belum ada
            db.flush()

            # Handle image upload jika ada
            new_image_filename = None
            if file_data and filename and content_type:
                file_ext = filename.split('.')[-1] if '.' in filename else 'jpg'
                new_image_filename = f"candidates/{db_candidate.user_id}/profile/{uuid4().hex}.{file_ext}"

                image_url = s3_service.upload_file(file_data, new_image_filename, content_type)

                if not image_url:
                    raise Exception("Failed to upload image to S3")

                # Hapus semua image lama dari S3 berdasarkan prefix
                try:
                    old_files = s3_service.list_files_by_prefix(f"candidates/{db_candidate.user_id}/profile/")
                    for old_file in old_files:
                        if old_file != new_image_filename:  # Jangan hapus file yang baru di-upload
                            s3_service.delete_file(old_file)
                except Exception as e:
                    print(f"Warning: Failed to delete old image files: {e}")

                db_candidate.image_url = image_url

            db.commit()
            db.refresh(db_candidate)
            return db_candidate

        except Exception as e:
            db.rollback()
            
            # Hapus file baru dari S3 jika ada error
            if new_image_filename:
                try:
                    s3_service.delete_file(new_image_filename)
                except Exception as s3_error:
                    print(f"Warning: Failed to delete image during rollback: {s3_error}")
            
            raise e

    def delete_my_profile(self, db: Session, user_id: UUID):
        db_candidate = db.query(Candidate).filter(Candidate.user_id == user_id).first()
        if not db_candidate:
            raise CandidateNotFoundError("Candidate profile not found")

        # Delete semua file dari S3 berdasarkan prefix user_id
        try:
            s3_service.delete_files_by_prefix(f"candidates/{db_candidate.user_id}/")
        except Exception as e:
            print(f"Warning: Failed to delete S3 files: {e}")

        db.delete(db_candidate)
        db.commit()
        return True
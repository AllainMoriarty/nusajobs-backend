from sqlalchemy.orm import Session
from app.models.candidate import Candidate
from app.schemas.candidate import CandidateCreate, CandidateUpdate
from uuid import UUID
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

    def update_my_profile(self, db: Session, candidate_data: CandidateUpdate, user_id: UUID):
        db_candidate = db.query(Candidate).filter(Candidate.user_id == user_id).first()
        if not db_candidate:
            raise CandidateNotFoundError("Candidate profile not found")

        for key, value in candidate_data.model_dump(exclude_unset=True).items():
            setattr(db_candidate, key, value)

        db.commit()
        db.refresh(db_candidate)
        return db_candidate

    def delete_my_profile(self, db: Session, user_id: UUID):
        db_candidate = db.query(Candidate).filter(Candidate.user_id == user_id).first()
        if not db_candidate:
            raise CandidateNotFoundError("Candidate profile not found")

        db.delete(db_candidate)
        db.commit()
        return True
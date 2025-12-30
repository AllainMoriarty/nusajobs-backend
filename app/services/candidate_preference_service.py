from sqlalchemy.orm import Session
from app.models.candidate import Candidate
from app.models.candidate_preference import CandidatePreference
from app.schemas.candidate_preference import CandidatePreferenceCreate, CandidatePreferenceUpdate
from uuid import UUID
from app.core.exceptions import CandidatePreferenceNotFoundError, CandidatePreferenceAlreadyExistsError


class CandidatePreferenceService:
    def create_preference(self, db: Session, preference_data: CandidatePreferenceCreate, candidate_id: UUID):
        existing = db.query(CandidatePreference).filter(CandidatePreference.candidate_id == candidate_id).first()
        if existing:
            raise CandidatePreferenceAlreadyExistsError("Candidate preferences already exist")

        db_preference = CandidatePreference(
            candidate_id=candidate_id,
            **preference_data.model_dump()
        )
        db.add(db_preference)
        db.commit()
        db.refresh(db_preference)
        return db_preference

    def get_my_preference(self, db: Session, candidate_id: UUID):
        preference = db.query(CandidatePreference).filter(CandidatePreference.candidate_id == candidate_id).first()
        if not preference:
            raise CandidatePreferenceNotFoundError("Candidate preferences not found")
        
        candidate = db.query(Candidate).filter(Candidate.user_id == candidate_id).first()
        return {
            "candidate": candidate,
            "candidate_preference": preference
        }

    def get_candidate_preference(self, db: Session, candidate_id: UUID):
        preference = db.query(CandidatePreference).filter(CandidatePreference.candidate_id == candidate_id).first()
        if not preference:
            raise CandidatePreferenceNotFoundError("Candidate preferences not found")
        
        candidate = db.query(Candidate).filter(Candidate.user_id == candidate_id).first()
        return {
            "candidate": candidate,
            "candidate_preference": preference
        }

    def update_my_preference(self, db: Session, candidate_data: CandidatePreferenceUpdate, candidate_id: UUID):
        db_preference = db.query(CandidatePreference).filter(CandidatePreference.candidate_id == candidate_id).first()
        if not db_preference:
            raise CandidatePreferenceNotFoundError("Candidate preferences not found")

        for key, value in candidate_data.model_dump(exclude_unset=True).items():
            setattr(db_preference, key, value)

        db.commit()
        db.refresh(db_preference)
        return db_preference

    def delete_my_preference(self, db: Session, candidate_id: UUID):
        db_preference = db.query(CandidatePreference).filter(CandidatePreference.candidate_id == candidate_id).first()
        if not db_preference:
            raise CandidatePreferenceNotFoundError("Candidate preferences not found")

        db.delete(db_preference)
        db.commit()
        return True
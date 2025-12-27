from sqlalchemy.orm import Session
from app.models.candidate_preference import CandidatePreference
from app.schemas.candidate_preference import CandidatePreferenceCreate, CandidatePreferenceUpdate
from uuid import UUID

class CandidatePreferenceService:
    def create_candidate_preference(self, db: Session, preference_data: CandidatePreferenceCreate, candidate_id: str):
        try:
            db_preference = CandidatePreference(
                candidate_id=candidate_id,
                **preference_data.model_dump()
            )
            db.add(db_preference)
            db.commit()
            db.refresh(db_preference)
            return db_preference

        except Exception as e:
            db.rollback()
            raise e

    def get_candidate_preference(self, db: Session, candidate_id: str):
        return db.query(CandidatePreference).filter(
            CandidatePreference.candidate_id == candidate_id
        ).first()

    def update_candidate_preference(self, db: Session, candidate_id: str, preference_data: CandidatePreferenceUpdate):
        try:
            db_preference = db.query(CandidatePreference).filter(
                CandidatePreference.candidate_id == candidate_id
            ).first()
            
            if not db_preference:
                return None

            for key, value in preference_data.model_dump(exclude_unset=True).items():
                setattr(db_preference, key, value)

            db.commit()
            db.refresh(db_preference)
            return db_preference

        except Exception as e:
            db.rollback()
            raise e

    def delete_candidate_preference(self, db: Session, candidate_id: str):
        try:
            db_preference = db.query(CandidatePreference).filter(
                CandidatePreference.candidate_id == candidate_id
            ).first()
            
            if not db_preference:
                return False
                
            db.delete(db_preference)
            db.commit()
            return True

        except Exception as e:
            db.rollback()
            raise e
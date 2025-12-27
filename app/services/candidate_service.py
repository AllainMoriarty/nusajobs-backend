from sqlalchemy.orm import Session
from app.models.candidate import Candidate
from app.schemas.candidate import CandidateCreate, CandidateUpdate

class CandidateService:
    def create_candidate(self, db: Session, candidate_data: CandidateCreate, current_user: dict = None):
        try:
            db.begin()
            
            if current_user["role"] not in ["candidate"]:
                raise Exception("Unauthorized: Only candidate can be job applicant")

            db_candidate = Candidate(
                user_id=current_user["id"],
                **candidate_data.model_dump()
            )
            db.add(db_candidate)
            db.commit()
            db.refresh(db_candidate)
            return db_candidate

        except Exception as e:
            db.rollback()
            raise e

    def get_candidate_by_user_id(self, db: Session, current_user: dict = None):
        if current_user["role"] not in ["candidate"]:
            raise Exception("Unauthorized: Only candidate can find himself")
        
        if current_user["role"] == "candidate":
            return db.query(Candidate).filter(Candidate.user_id == current_user["id"]).first()

    def get_candidate_by_id(self, db: Session, user_id: str, current_user: dict = None):
        if current_user["role"] not in ["admin", "recruiter"]:
            raise Exception("Only admin or recruiter can view other profiles")
        return db.query(Candidate).filter(Candidate.id == user_id).first()

    def update_candidate(self, db: Session, candidate_data: CandidateUpdate, current_user: dict = None):
        try:
            db.begin()
            
            if current_user["role"] not in ["candidate"]:
                raise Exception("Unauthorized: Only candidate can edit their profile")
            
            db_candidate = db.query(Candidate).filter(Candidate.user_id == current_user["id"]).first()
            if not db_candidate:
                return None

            for key, value in candidate_data.model_dump(exclude_unset=True).items():
                setattr(db_candidate, key, value)

            db.commit()
            db.refresh(db_candidate)
            return db_candidate

        except Exception as e:
            db.rollback()
            raise e

    def delete_candidate(self, db: Session, current_user: dict = None):
        try:
            db.begin()
            
            if current_user["role"] not in ["candidate"]:
                raise Exception("Unauthorized: Only candidate can delete their profile")
            
            db_candidate = db.query(Candidate).filter(Candidate.user_id == current_user["id"]).first()
            if not db_candidate:
                return False
            db.delete(db_candidate)
            db.commit()
            return True

        except Exception as e:
            db.rollback()
            raise e
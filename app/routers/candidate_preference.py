from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.candidate_preference_service import CandidatePreferenceService
from app.schemas.candidate_preference import (CandidatePreferenceCreate, CandidatePreferenceUpdate, CandidatePreferenceResponse)
from app.core.auth_middleware import get_current_user

router = APIRouter(prefix="/candidate-preferences", tags=["Candidate Preferences"])

candidate_preference_service = CandidatePreferenceService()

@router.post("/", response_model=CandidatePreferenceResponse, status_code=status.HTTP_201_CREATED)
def create_preference(preference: CandidatePreferenceCreate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] != "candidate":
        raise HTTPException(status_code=403, detail="Only candidates can create preferences")

    existing_preference = candidate_preference_service.get_candidate_preference(db, current_user["id"])
    if existing_preference:
        raise HTTPException(status_code=400, detail="Candidate preferences already exist")

    new_preference = candidate_preference_service.create_candidate_preference(db, preference, current_user["id"])
    return new_preference

@router.get("/me", response_model=CandidatePreferenceResponse)
def get_my_preferences(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] != "candidate":
        raise HTTPException(status_code=403, detail="Only candidates can access preferences")

    preference = candidate_preference_service.get_candidate_preference(db, current_user["id"])
    if not preference:
        raise HTTPException(status_code=404, detail="Candidate preferences not found")

    return preference

@router.put("/me", response_model=CandidatePreferenceResponse)
def update_my_preferences(preference: CandidatePreferenceUpdate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] != "candidate":
        raise HTTPException(status_code=403, detail="Only candidates can update preferences")

    updated_preference = candidate_preference_service.update_candidate_preference(db, current_user["id"], preference)
    if not updated_preference:
        raise HTTPException(status_code=404, detail="Candidate preferences not found")

    return updated_preference

@router.delete("/me")
def delete_my_preferences(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] != "candidate":
        raise HTTPException(status_code=403, detail="Only candidates can delete preferences")

    success = candidate_preference_service.delete_candidate_preference(db, current_user["id"])
    if not success:
        raise HTTPException(status_code=404, detail="Candidate preferences not found")

    return {"message": "Candidate preferences deleted successfully"}

@router.get("/{candidate_id}", response_model=CandidatePreferenceResponse)
def get_candidate_preferences(candidate_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] not in ["admin", "recruiter"]:
        raise HTTPException(status_code=403, detail="Only admin or recruiter can view other preferences")

    preference = candidate_preference_service.get_candidate_preference(db, candidate_id)
    if not preference:
        raise HTTPException(status_code=404, detail="Candidate preferences not found")

    return preference
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.candidate_service import CandidateService
from app.schemas.candidate import CandidateCreate, CandidateUpdate, CandidateResponse
from app.core.auth_middleware import get_current_user

router = APIRouter(prefix="/candidates", tags=["Candidates"])

candidate_service = CandidateService()

@router.post("/", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
def create_profile(candidate: CandidateCreate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    existing_candidate = candidate_service.get_candidate_by_user_id(db, current_user)
    if existing_candidate:
        raise HTTPException(status_code=400, detail="Candidate profile already exists")

    new_candidate = candidate_service.create_candidate(db, candidate, current_user)
    return new_candidate

@router.get("/me", response_model=CandidateResponse)
def get_my_profile(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] != "candidate":
        raise HTTPException(status_code=403, detail="Only candidates can access profile")

    candidate = candidate_service.get_candidate_by_user_id(db, current_user)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate profile not found")

    return candidate

@router.put("/me", response_model=CandidateResponse)
def update_my_profile(candidate: CandidateUpdate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] != "candidate":
        raise HTTPException(status_code=403, detail="Only candidates can update profile")

    updated_candidate = candidate_service.update_candidate(db, candidate, current_user)
    if not updated_candidate:
        raise HTTPException(status_code=404, detail="Candidate profile not found")

    return updated_candidate

@router.delete("/me")
def delete_my_profile(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] != "candidate":
        raise HTTPException(status_code=403, detail="Only candidates can delete profile")

    success = candidate_service.delete_candidate(db, current_user)
    if not success:
        raise HTTPException(status_code=404, detail="Candidate profile not found")

    return {"message": "Candidate profile deleted successfully"}

@router.get("/{user_id}", response_model=CandidateResponse)
def get_candidate_profile(user_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] not in ["admin", "recruiter"]:
        raise HTTPException(status_code=403, detail="Only admin or recruiter can view other profiles")

    candidate = candidate_service.get_candidate_by_id(db, user_id, current_user)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate profile not found")

    return candidate
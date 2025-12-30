from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.candidate_preference_service import CandidatePreferenceService
from app.schemas.candidate_preference import CandidatePreferenceCreate,CandidatePreferenceUpdate, CandidatePreferenceSchema, CandidatePreferenceResponse
from app.core.auth_middleware import require_role
from app.core.exceptions import CandidatePreferenceNotFoundError, CandidatePreferenceAlreadyExistsError
from uuid import UUID

router = APIRouter(prefix="/candidate-preferences", tags=["Candidate Preferences"])
preference_service = CandidatePreferenceService()


@router.post("/", response_model=CandidatePreferenceSchema, status_code=status.HTTP_201_CREATED)
def create_preference(preference: CandidatePreferenceCreate, current_user: dict = Depends(require_role(["candidate"])), db: Session = Depends(get_db)):
    """
    Create job preferences for the authenticated candidate.
    
    Each candidate can only have one preference profile.
    Only users with the 'candidate' role are allowed.
    """
    try:
        return preference_service.create_preference(db, preference, current_user["id"])
    except CandidatePreferenceAlreadyExistsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to create candidate preferences"
        )


@router.get("/me", response_model=CandidatePreferenceResponse)
def get_my_preferences(current_user: dict = Depends(require_role(["candidate"])), db: Session = Depends(get_db)):
    """
    Retrieve the authenticated candidate's own job preferences.
    
    Only accessible to users with the 'candidate' role.
    """
    try:
        return preference_service.get_my_preference(db, current_user["id"])
    except CandidatePreferenceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve preferences"
        )


@router.put("/me", response_model=CandidatePreferenceSchema)
def update_my_preferences(preference: CandidatePreferenceUpdate, current_user: dict = Depends(require_role(["candidate"])), db: Session = Depends(get_db)):
    """
    Update the authenticated candidate's job preferences.
    
    Only the owner can modify their preferences.
    """
    try:
        return preference_service.update_my_preference(db, preference, current_user["id"])
    except CandidatePreferenceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to update preferences"
        )


@router.delete("/me")
def delete_my_preferences(current_user: dict = Depends(require_role(["candidate"])), db: Session = Depends(get_db)):
    """
    Delete the authenticated candidate's job preferences permanently.
    
    Only the owner can delete their preferences.
    """
    try:
        preference_service.delete_my_preference(db, current_user["id"])
        return {"message": "Candidate preferences deleted successfully"}
    except CandidatePreferenceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to delete preferences"
        )


@router.get("/{candidate_id}", response_model=CandidatePreferenceResponse)
def get_candidate_preferences(candidate_id: UUID, current_user: dict = Depends(require_role(["admin", "recruiter"])), db: Session = Depends(get_db)):
    """
    Retrieve job preferences of a specific candidate by ID.
    
    Only accessible to 'admin' or 'recruiter' roles.
    Used for matching or reviewing candidate preferences.
    """
    try:
        return preference_service.get_candidate_preference(db, candidate_id)
    except CandidatePreferenceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve candidate preferences"
        )
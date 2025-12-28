from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.candidate_service import CandidateService
from app.schemas.candidate import CandidateCreate, CandidateUpdate, CandidateResponse
from app.core.auth_middleware import require_role
from app.core.exceptions import CandidateNotFoundError, CandidateAlreadyExistsError
from uuid import UUID

router = APIRouter(prefix="/candidates", tags=["Candidates"])
candidate_service = CandidateService()


@router.post("/", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
def create_profile(candidate: CandidateCreate, current_user: dict = Depends(require_role(["candidate"])), db: Session = Depends(get_db)):
    """
    Create a candidate profile for the authenticated user.
    
    Only users with the 'candidate' role can create a profile.
    Each user can only have one candidate profile.
    """
    try:
        return candidate_service.create_candidate(db, candidate, current_user["id"])
    except CandidateAlreadyExistsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to create candidate profile"
        )


@router.get("/me", response_model=CandidateResponse)
def get_my_profile(current_user: dict = Depends(require_role(["candidate"])), db: Session = Depends(get_db)):
    """
    Retrieve the authenticated candidate's own profile.
    
    Only accessible to users with the 'candidate' role.
    """
    try:
        return candidate_service.get_my_profile(db, current_user["id"])
    except CandidateNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve profile"
        )


@router.put("/me", response_model=CandidateResponse)
def update_my_profile(candidate: CandidateUpdate, current_user: dict = Depends(require_role(["candidate"])), db: Session = Depends(get_db)):
    """
    Update the authenticated candidate's profile.
    
    Only the profile owner (candidate) can make changes.
    """
    try:
        return candidate_service.update_my_profile(db, candidate, current_user["id"])
    except CandidateNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to update profile"
        )


@router.delete("/me")
def delete_my_profile(current_user: dict = Depends(require_role(["candidate"])), db: Session = Depends(get_db)):
    """
    Delete the authenticated candidate's profile permanently.
    
    Only the profile owner can delete it.
    """
    try:
        candidate_service.delete_my_profile(db, current_user["id"])
        return {"message": "Candidate profile deleted successfully"}
    except CandidateNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to delete profile"
        )


@router.get("/{candidate_id}", response_model=CandidateResponse)
def get_candidate_profile(
    candidate_id: UUID,
    current_user: dict = Depends(require_role(["admin", "recruiter"])),
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific candidate's profile by ID.
    
    Only accessible to 'admin' or 'recruiter' roles.
    Used for reviewing applicant profiles.
    """
    try:
        return candidate_service.get_candidate_by_id(db, candidate_id)
    except CandidateNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve candidate profile"
        )
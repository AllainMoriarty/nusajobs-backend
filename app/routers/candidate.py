from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.candidate_service import CandidateService
from app.schemas.candidate import CandidateCreate, CandidateResponse
from app.core.auth_middleware import require_role
from app.core.exceptions import CandidateNotFoundError, CandidateAlreadyExistsError
from uuid import UUID
from datetime import date
from typing import Optional

router = APIRouter(prefix="/candidates", tags=["Candidates"])
candidate_service = CandidateService()


@router.post("/", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
def create_profile(
    candidate: CandidateCreate,
    current_user: dict = Depends(require_role(["candidate"])),
    db: Session = Depends(get_db)
):
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
def get_my_profile(
    current_user: dict = Depends(require_role(["candidate"])),
    db: Session = Depends(get_db)
):
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
async def update_my_profile(
    full_name: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    birth_date: Optional[date] = Form(None),
    gender: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    image: UploadFile = File(None),
    current_user: dict = Depends(require_role(["candidate"])),
    db: Session = Depends(get_db)
):
    """
    Update the authenticated candidate's profile with optional image upload.
    
    Allows updating profile data and uploading/replacing profile image.
    Old images are automatically deleted when a new one is uploaded.
    """
    try:
        candidate_data = {}
        if full_name is not None:
            candidate_data["full_name"] = full_name
        if phone is not None:
            candidate_data["phone"] = phone
        if birth_date is not None:
            candidate_data["birth_date"] = birth_date
        if gender is not None:
            candidate_data["gender"] = gender
        if location is not None:
            candidate_data["location"] = location

        file_data = None
        filename = None
        content_type = None

        if image:
            file_data = await image.read()
            filename = image.filename
            content_type = image.content_type

        updated_candidate = candidate_service.update_profile_with_image(
            db,
            candidate_data,
            file_data=file_data,
            filename=filename,
            content_type=content_type,
            user_id=current_user["id"]
        )
        return updated_candidate
    except CandidateNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/me")
def delete_my_profile(
    current_user: dict = Depends(require_role(["candidate"])),
    db: Session = Depends(get_db)
):
    """
    Delete the authenticated candidate's profile permanently.
    
    Only the profile owner can delete it.
    Also deletes all associated files from S3 (profile images).
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
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.candidate_cv_service import CandidateCVService
from app.schemas.candidate_cv import CandidateCVSchema, CandidateCVResponse
from app.core.auth_middleware import require_role
from app.core.exceptions import CVNotFoundError, CVUploadError, CVDownloadError
from uuid import UUID

router = APIRouter(prefix="/candidate-cvs", tags=["Candidate CVs"])
cv_service = CandidateCVService()


@router.post("/", response_model=CandidateCVSchema, status_code=status.HTTP_201_CREATED)
async def upload_cv(
    file: UploadFile = File(...), 
    current_user: dict = Depends(require_role(["candidate"])), 
    db: Session = Depends(get_db)
):
    """
    Upload CV baru (hanya untuk kandidat yang belum pernah upload CV).
    
    Jika sudah pernah upload CV, gunakan endpoint PUT untuk update.
    
    The system will:
    - Store the file in cloud storage (S3/IPFS)
    - Extract text using OCR
    - Generate a summary using LLM
    - Create an embedding for matching
    
    Only PDF files are allowed.
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    file_data = await file.read()
    if len(file_data) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        return await cv_service.upload_cv(db, file_data, file.filename, current_user["id"])
    except CVUploadError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.put("/", response_model=CandidateCVSchema, status_code=status.HTTP_200_OK)
async def update_cv(
    file: UploadFile = File(...), 
    current_user: dict = Depends(require_role(["candidate"])), 
    db: Session = Depends(get_db)
):
    """
    Update CV yang sudah ada (replace file lama dengan file baru).
    
    Jika belum pernah upload CV, gunakan endpoint POST untuk upload pertama kali.
    
    The system will:
    - Delete the old file from cloud storage
    - Upload and process the new file
    - Update all CV data (OCR text, summary, embedding)
    
    Only PDF files are allowed.
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    file_data = await file.read()
    if len(file_data) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        return await cv_service.update_cv(db, file_data, file.filename, current_user["id"])
    except CVNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CVUploadError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/me", response_model=CandidateCVResponse)
def get_my_cv(
    current_user: dict = Depends(require_role(["candidate"])), 
    db: Session = Depends(get_db)
):
    """
    Get CV milik candidate yang sedang login.
    
    Returns 404 jika belum upload CV.
    """
    cv = cv_service.get_my_cv(db, current_user["id"])
    if not cv:
        raise HTTPException(status_code=404, detail="You haven't uploaded a CV yet")
    return cv


@router.get("/{cv_id}", response_model=CandidateCVResponse)
def get_cv(
    cv_id: UUID, 
    current_user: dict = Depends(require_role(["candidate", "admin", "recruiter"])), 
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific CV by ID.
    
    - Candidates can only view their own CV.
    - Admins and recruiters can view any CV (for matching purposes).
    """
    cv = cv_service.get_cv_by_id(db, cv_id)

    # Candidate hanya boleh akses CV-nya sendiri
    if current_user["role"] == "candidate" and str(cv.candidate_id) != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")

    return cv


@router.delete("/", status_code=status.HTTP_200_OK)
def delete_my_cv(
    current_user: dict = Depends(require_role(["candidate"])), 
    db: Session = Depends(get_db)
):
    """
    Delete CV milik candidate yang sedang login.
    
    Associated file in cloud storage will also be removed.
    After deletion, you can upload a new CV using the POST endpoint.
    """
    try:
        cv_service.delete_cv(db, current_user["id"])
        return {"message": "CV deleted successfully"}
    except CVNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete CV: {str(e)}")
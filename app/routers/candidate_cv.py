from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.candidate_cv_service import upload_cv_file, get_cv_by_id, get_cvs_by_candidate, delete_cv
from app.schemas.candidate_cv import CandidateCVResponse
from app.core.auth_middleware import get_current_user

router = APIRouter(prefix="/candidate-cvs", tags=["Candidate CVs"])

@router.post("/", response_model=CandidateCVResponse, status_code=status.HTTP_201_CREATED)
async def upload_cv(file: UploadFile = File(...), current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] != "candidate":
        raise HTTPException(status_code=403, detail="Only candidates can upload CVs")

    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    file_data = await file.read()

    try:
        cv_record = await upload_cv_file(db, file_data, file.filename, current_user["id"])
        return cv_record
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process CV: {str(e)}")

@router.get("/", response_model=list[CandidateCVResponse])
def list_my_cvs(skip: int = 0, limit: int = 10, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] != "candidate":
        raise HTTPException(status_code=403, detail="Only candidates can access their CVs")

    cvs = get_cvs_by_candidate(db, current_user["id"], skip, limit)
    return cvs

@router.get("/{cv_id}", response_model=CandidateCVResponse)
def get_cv(cv_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    cv_record = get_cv_by_id(db, cv_id)
    if not cv_record:
        raise HTTPException(status_code=404, detail="CV not found")

    if current_user["role"] not in ["admin", "recruiter"]:
        if str(cv_record.candidate_id) != current_user["id"]:
            raise HTTPException(status_code=403, detail="Access denied")

    return cv_record

@router.delete("/{cv_id}")
def delete_cv_file(cv_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] != "candidate":
        raise HTTPException(status_code=403, detail="Only candidates can delete their CVs")

    success = delete_cv(db, cv_id, current_user["id"])
    if not success:
        raise HTTPException(status_code=404, detail="CV not found")

    return {"message": "CV deleted successfully"}
from fastapi import APIRouter, HTTPException, status, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
import os
import shutil
from datetime import datetime

from backend.database.connection import SessionLocal
from backend.database.models import FIRRecord, CaseDocument

router = APIRouter(prefix="/api/cases", tags=["Case Management System"])

# Directory to store uploaded case documents
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

class CaseDocumentResponse(BaseModel):
    id: int
    filename: str
    uploaded_at: str
    uploaded_by: Optional[str]

class CaseResponse(BaseModel):
    id: int
    city: str
    crime_description: str
    timestamp: str
    risk_level_label: str
    assigned_officer: Optional[str]
    documents: List[CaseDocumentResponse] = []

@router.get("/", response_model=List[CaseResponse])
def get_all_cases():
    """Returns a list of all cases in the system with their attached documents."""
    db = SessionLocal()
    try:
        cases = db.query(FIRRecord).order_by(FIRRecord.id.desc()).all()
        response = []
        for case in cases:
            docs = db.query(CaseDocument).filter(CaseDocument.fir_id == case.id).all()
            doc_responses = [
                CaseDocumentResponse(
                    id=d.id, 
                    filename=d.filename, 
                    uploaded_at=d.uploaded_at.strftime("%Y-%m-%d %H:%M"),
                    uploaded_by=d.uploaded_by
                ) for d in docs
            ]
            response.append(
                CaseResponse(
                    id=case.id,
                    city=case.city,
                    crime_description=case.crime_description,
                    timestamp=case.timestamp.strftime("%Y-%m-%d") if case.timestamp else "",
                    risk_level_label=case.risk_level_label,
                    assigned_officer=case.assigned_officer,
                    documents=doc_responses
                )
            )
        return response
    finally:
        db.close()

@router.post("/{case_id}/upload")
async def upload_case_document(case_id: int, file: UploadFile = File(...), officer_name: str = "Unknown"):
    """Uploads a document to a specific case."""
    db = SessionLocal()
    try:
        case = db.query(FIRRecord).filter(FIRRecord.id == case_id).first()
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        
        file_path = os.path.join(UPLOAD_DIR, f"case_{case_id}_{file.filename}")
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        doc = CaseDocument(
            fir_id=case_id,
            filename=file.filename,
            file_path=file_path,
            uploaded_by=officer_name
        )
        db.add(doc)
        
        # Auto-assign officer if case is unassigned
        if not case.assigned_officer and officer_name != "Unknown":
            case.assigned_officer = officer_name
            
        db.commit()
        return {"status": "success", "message": f"File {file.filename} uploaded to Case {case_id}"}
    finally:
        db.close()

from fastapi import APIRouter, HTTPException, status, UploadFile, File
from pydantic import BaseModel
from datetime import datetime
from backend.database.connection import SessionLocal
from backend.database.models import FIRRecord
import os

router = APIRouter(prefix="/api/fir", tags=["FIR Casual Text Extraction"])

@router.post("/predict-and-save", status_code=status.HTTP_200_OK)
async def predict_and_save_fir(file: UploadFile = File(...)):
    try:
        from data_processor import read_pdf_bytes_to_string
        file_bytes = await file.read()
        raw_text = read_pdf_bytes_to_string(file_bytes) if file.filename.lower().endswith(".pdf") else file_bytes.decode('utf-8', errors='ignore')
        from app import execute_core_inference
        from backend.services.ai_service import extract_fir_features_with_gemini

        # 1. AI Extraction
        extracted_data = extract_fir_features_with_gemini(raw_text)
        
        dt = datetime.strptime(extracted_data['timestamp'], "%Y-%m-%d %H:%M:%S")
        
        # 2. Risk Prediction
        inference = execute_core_inference(
            hour=dt.hour, day_of_week=dt.weekday(), month=dt.month,
            crime_key=extracted_data['crime_description'],
            city_key=extracted_data['city'],
            victim_age=extracted_data['victim_age']
        )
        
        # 3. Save to DB
        db = SessionLocal()
        new_record = FIRRecord(
            raw_text=raw_text[:2000], # store a snippet
            timestamp=dt,
            crime_description=extracted_data['crime_description'],
            city=extracted_data['city'],
            victim_age=extracted_data['victim_age'],
            risk_level_code=inference['risk_level_code'],
            risk_level_label=inference['risk_level_label'],
            probability_score=inference['probability_score'],
            latitude=inference['spatial_footprint']['latitude'],
            longitude=inference['spatial_footprint']['longitude']
        )
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        db.close()
        
        return {
            "status": "success",
            "extracted_data": extracted_data,
            "prediction": inference,
            "database_id": new_record.id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

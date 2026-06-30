from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
import os

router = APIRouter(prefix="/api/assistant", tags=["KSP AI Assistant"])

from typing import Optional
from backend.database.connection import SessionLocal
from backend.database.models import FIRRecord

class ChatInput(BaseModel):
    message: str
    fir_id: Optional[int] = None

@router.post("/chat")
def chat_with_assistant(payload: ChatInput):
    API_KEY = os.getenv("GEMINI_API_KEY")
    if not API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not configured.")
    
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        system_context = "You are the KSP (Karnataka State Police) AI Assistant. Provide highly professional, concise, and tactical advice to law enforcement officers based on crime patterns, anomalies, and patrol routing."
        
        if payload.fir_id:
            db = SessionLocal()
            try:
                case = db.query(FIRRecord).filter(FIRRecord.id == payload.fir_id).first()
                if case:
                    system_context += f"\n\nYou are currently assisting with Case #{case.id}.\n"
                    system_context += f"Crime Description: {case.crime_description}\n"
                    system_context += f"City: {case.city}\n"
                    system_context += f"Assigned Officer: {case.assigned_officer or 'Unassigned'}\n"
                    system_context += f"Risk Level: {case.risk_level_label} (Probability: {case.probability_score})\n"
                    if case.raw_text:
                        system_context += f"Case Notes / FIR Text Snippet:\n{case.raw_text[:1000]}\n"
            finally:
                db.close()
        
        prompt = f"{system_context}\n\nOfficer: {payload.message}\nAssistant:"
        response = model.generate_content(prompt)
        
        return {"response": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

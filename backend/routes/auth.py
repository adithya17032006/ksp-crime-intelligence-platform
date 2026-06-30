"""
Authentication API routes for KSP Crime Intelligence Platform.
Handles officer registration, login, and profile retrieval.
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from backend.services.auth_service import (
    register_officer, login_officer, logout_officer, get_allowed_modules
)
from backend.database.connection import SessionLocal
from backend.database.models import OfficerProfile

router = APIRouter(prefix="/api/auth", tags=["Officer Authentication"])


class RegisterInput(BaseModel):
    email: str
    password: str
    police_id: str
    full_name: str
    designation: str
    badge_number: Optional[str] = ""
    district: Optional[str] = ""
    police_station: Optional[str] = ""
    phone: Optional[str] = ""


class LoginInput(BaseModel):
    email: str
    password: str


class LogoutInput(BaseModel):
    access_token: str


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterInput):
    """Registers a new KSP officer account with Supabase Auth."""
    valid_designations = ["SP", "DSP", "Inspector", "SI", "PSI", "HC", "PC"]
    if payload.designation not in valid_designations:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid designation. Must be one of: {', '.join(valid_designations)}"
        )
    try:
        result = register_officer(
            email=payload.email,
            password=payload.password,
            police_id=payload.police_id,
            full_name=payload.full_name,
            designation=payload.designation,
            badge_number=payload.badge_number,
            district=payload.district,
            police_station=payload.police_station,
            phone=payload.phone,
        )
        return {
            "status": "success",
            "message": f"Officer {payload.full_name} registered successfully.",
            "officer": result,
            "allowed_modules": get_allowed_modules(result["access_level"]),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration error: {e}")


@router.post("/login")
def login(payload: LoginInput):
    """Authenticates an officer and returns their session + profile."""
    try:
        result = login_officer(email=payload.email, password=payload.password)
        return {
            "status": "success",
            "message": f"Welcome back, {result['full_name']}!",
            "officer": result,
            "allowed_modules": get_allowed_modules(result["access_level"]),
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login error: {e}")


@router.post("/logout")
def logout(payload: LogoutInput):
    """Signs out the officer from Supabase."""
    logout_officer(payload.access_token)
    return {"status": "success", "message": "Logged out successfully."}


@router.get("/designations")
def get_designations():
    """Returns all valid police designations and their access levels."""
    return {
        "designations": [
            {"value": "SP",        "label": "SP — Superintendent of Police",        "access_level": 5},
            {"value": "DSP",       "label": "DSP — Deputy Superintendent of Police", "access_level": 4},
            {"value": "Inspector", "label": "Inspector",                              "access_level": 3},
            {"value": "SI",        "label": "SI — Sub-Inspector",                    "access_level": 2},
            {"value": "PSI",       "label": "PSI — Police Sub-Inspector",            "access_level": 2},
            {"value": "HC",        "label": "HC — Head Constable",                   "access_level": 1},
            {"value": "PC",        "label": "PC — Police Constable",                 "access_level": 1},
        ]
    }

@router.get("/officers")
def get_all_officers():
    """Returns all registered officers from the database."""
    db = SessionLocal()
    try:
        officers = db.query(OfficerProfile).order_by(OfficerProfile.created_at.desc()).all()
        return [
            {
                "police_id": o.police_id,
                "full_name": o.full_name,
                "designation": o.designation,
                "access_level": o.access_level,
                "district": o.district,
                "police_station": o.police_station,
                "phone": o.phone,
                "created_at": o.created_at.isoformat() if o.created_at else None
            } for o in officers
        ]
    finally:
        db.close()

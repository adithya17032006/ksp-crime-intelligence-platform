"""
Supabase Auth Service for KSP Crime Intelligence Platform.
Handles officer registration, login, session management via Supabase Auth.
"""
import os
from dotenv import load_dotenv
from backend.database.connection import SessionLocal
from backend.database.models import OfficerProfile

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")

# Access level map per designation
DESIGNATION_ACCESS = {
    "SP":          5,
    "DSP":         4,
    "Inspector":   3,
    "SI":          2,
    "PSI":         2,
    "HC":          1,
    "PC":          1,
}

# Modules visible per access level (cumulative from level 1 up)
ACCESS_MODULES = {
    5: [   # SP — full access
        "📊 Executive Dashboard",
        "⚠️ Crime Risk Dashboard",
        "🔥 Hotspot Intelligence Dashboard",
        "🛡️ Patrol Recommendation Dashboard",
        "📅 Temporal Trend Dashboard",
        "📍 GIS Map Dashboard",
        "🔮 Crime Prediction",
        "🧬 Feature Importance",
        "📂 Case Management System",
        "🧠 AI Assistant & FIR Processing",
        "⚙️ Admin Panel",
    ],
    4: [   # DSP
        "📊 Executive Dashboard",
        "⚠️ Crime Risk Dashboard",
        "🔥 Hotspot Intelligence Dashboard",
        "🛡️ Patrol Recommendation Dashboard",
        "📅 Temporal Trend Dashboard",
        "📍 GIS Map Dashboard",
        "🔮 Crime Prediction",
        "🧬 Feature Importance",
        "📂 Case Management System",
        "🧠 AI Assistant & FIR Processing",
    ],
    3: [   # Inspector
        "📊 Executive Dashboard",
        "⚠️ Crime Risk Dashboard",
        "🔥 Hotspot Intelligence Dashboard",
        "🛡️ Patrol Recommendation Dashboard",
        "📅 Temporal Trend Dashboard",
        "📍 GIS Map Dashboard",
        "🔮 Crime Prediction",
        "🧬 Feature Importance",
        "📂 Case Management System",
        "🧠 AI Assistant & FIR Processing",
    ],
    2: [   # SI / PSI
        "📊 Executive Dashboard",
        "⚠️ Crime Risk Dashboard",
        "🔥 Hotspot Intelligence Dashboard",
        "📅 Temporal Trend Dashboard",
        "📂 Case Management System",
        "🧠 AI Assistant & FIR Processing",
    ],
    1: [   # HC / PC
        "🧠 AI Assistant & FIR Processing",
    ],
}


def _get_client():
    """Lazily creates and returns the Supabase client."""
    if not SUPABASE_URL or "your-project" in SUPABASE_URL:
        raise ValueError(
            "SUPABASE_URL and SUPABASE_ANON_KEY are not configured. "
            "Please update your .env file with your Supabase credentials."
        )
    from supabase import create_client
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


def register_officer(
    email: str,
    password: str,
    police_id: str,
    full_name: str,
    designation: str,
    badge_number: str,
    district: str,
    police_station: str,
    phone: str,
) -> dict:
    """
    Registers a new officer via Supabase Auth, then inserts their
    profile into the officer_profiles table.
    """
    client = _get_client()

    access_level = DESIGNATION_ACCESS.get(designation, 1)

    # 1. Create auth user
    try:
        auth_response = client.auth.sign_up({
            "email": email,
            "password": password,
        })
    except Exception as e:
        raise ValueError(f"Auth registration failed: {e}")

    user = auth_response.user
    if not user:
        raise ValueError("Registration failed: no user returned from Supabase.")

    # 2. Insert officer profile into the main PostgreSQL database
    db = SessionLocal()
    try:
        existing = db.query(OfficerProfile).filter(OfficerProfile.police_id == police_id).first()
        if existing:
            raise ValueError(f"Police ID {police_id} is already registered.")
            
        new_profile = OfficerProfile(
            id=str(user.id),
            police_id=police_id,
            full_name=full_name,
            designation=designation,
            access_level=access_level,
            badge_number=badge_number,
            district=district,
            police_station=police_station,
            phone=phone,
        )
        db.add(new_profile)
        db.commit()
    except Exception as e:
        db.rollback()
        raise ValueError(f"Profile creation failed: {e}")
    finally:
        db.close()

    return {
        "user_id": str(user.id),
        "email": email,
        "full_name": full_name,
        "designation": designation,
        "access_level": access_level,
        "police_id": police_id,
        "badge_number": badge_number,
        "district": district,
        "police_station": police_station,
        "phone": phone,
    }


def login_officer(email: str, password: str) -> dict:
    """
    Authenticates officer via Supabase Auth and fetches their profile.
    Returns a dict with session token + officer profile data.
    """
    client = _get_client()

    try:
        auth_response = client.auth.sign_in_with_password({
            "email": email,
            "password": password,
        })
    except Exception as e:
        raise ValueError(f"Login failed: {e}")

    session = auth_response.session
    user = auth_response.user

    if not session or not user:
        raise ValueError("Invalid credentials. Please check your email and password.")

    # Fetch officer profile from the main PostgreSQL database
    db = SessionLocal()
    try:
        profile = db.query(OfficerProfile).filter(OfficerProfile.id == str(user.id)).first()
        if not profile:
            raise ValueError("Officer profile not found. Please contact your administrator.")
            
        return {
            "access_token": session.access_token,
            "user_id": str(user.id),
            "email": user.email,
            "full_name": profile.full_name,
            "designation": profile.designation,
            "access_level": profile.access_level,
            "police_id": profile.police_id,
            "badge_number": profile.badge_number,
            "district": profile.district,
            "police_station": profile.police_station,
            "phone": profile.phone,
        }
    finally:
        db.close()


def logout_officer(access_token: str):
    """Signs out the officer from Supabase."""
    try:
        client = _get_client()
        client.auth.sign_out()
    except Exception:
        pass  # Silently handle — local session will be cleared regardless


def get_allowed_modules(access_level: int) -> list:
    """Returns the list of navigation modules for a given access level."""
    return ACCESS_MODULES.get(access_level, ACCESS_MODULES[1])

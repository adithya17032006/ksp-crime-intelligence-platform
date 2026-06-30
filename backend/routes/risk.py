from fastapi import APIRouter
from backend.services.risk_service import get_risk_data

router = APIRouter()

@router.get("/district-risk")
def district_risk():

    return get_risk_data()
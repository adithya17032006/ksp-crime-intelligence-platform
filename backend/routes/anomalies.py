from fastapi import APIRouter
from backend.services.anomaly_service import get_anomaly_data

router = APIRouter()

@router.get("/anomalies")
def anomalies():

    return get_anomaly_data()
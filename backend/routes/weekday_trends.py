from fastapi import APIRouter
from backend.services.trend_service import get_weekday_trends

router = APIRouter()

@router.get("/crime/weekday-trends")
def weekday_trends():

    return get_weekday_trends()
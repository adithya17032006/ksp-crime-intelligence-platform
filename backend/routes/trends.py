from fastapi import APIRouter
from services.trend_service import get_monthly_trends

router = APIRouter()

@router.get("/crime/monthly-trends")
def monthly_trends():

    return get_monthly_trends()
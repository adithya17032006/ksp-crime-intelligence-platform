from fastapi import APIRouter
from services.hotspot_service import get_hotspot_data

router = APIRouter()

@router.get("/hotspots")
def hotspots():

    return get_hotspot_data()
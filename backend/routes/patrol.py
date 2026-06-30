from fastapi import APIRouter
from backend.services.patrol_service import get_patrol_data

router = APIRouter()

@router.get("/patrol-priority")
def patrol_priority():

    return get_patrol_data()
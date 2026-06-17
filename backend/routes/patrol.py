from fastapi import APIRouter
from services.patrol_service import get_patrol_data

router = APIRouter()

@router.get("/patrol-priority")
def patrol_priority():

    return get_patrol_data()
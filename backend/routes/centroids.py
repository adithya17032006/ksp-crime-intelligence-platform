from fastapi import APIRouter
from services.centroid_service import get_hotspot_centroids

router = APIRouter()

@router.get("/hotspot-centroids")
def hotspot_centroids():
    return get_hotspot_centroids()
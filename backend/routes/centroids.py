from fastapi import APIRouter
from backend.services.centroid_service import get_hotspot_centroids

router = APIRouter()

@router.get("/hotspot-centroids")
def hotspot_centroids():
    return get_hotspot_centroids()
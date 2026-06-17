from fastapi import APIRouter
import pandas as pd

router = APIRouter()

@router.get("/hotspots")
def get_hotspots():

    df = pd.read_csv(
        "../data/processed/crime_hotspots.csv"
    )

    return df.to_dict(
        orient="records"
    )
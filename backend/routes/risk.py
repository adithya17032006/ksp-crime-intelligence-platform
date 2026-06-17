from fastapi import APIRouter
import pandas as pd

router = APIRouter()

@router.get("/district-risk")
def get_district_risk():

    df = pd.read_csv(
        "../data/processed/crime_risk_scores.csv"
    )

    return df.to_dict(
        orient="records"
    )
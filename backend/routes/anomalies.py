from fastapi import APIRouter
import pandas as pd

router = APIRouter()

@router.get("/anomalies")
def get_anomalies():

    df = pd.read_csv(
        "../data/processed/district_anomalies.csv"
    )

    return df.to_dict(
        orient="records"
    )
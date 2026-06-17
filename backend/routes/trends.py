from fastapi import APIRouter
import pandas as pd

router = APIRouter()

@router.get("/crime/monthly-trends")
def get_monthly_trends():

    df = pd.read_csv(
        "../data/processed/monthly_crime_trends.csv"
    )

    return df.to_dict(
        orient="records"
    )
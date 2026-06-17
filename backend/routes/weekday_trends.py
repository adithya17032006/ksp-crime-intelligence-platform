from fastapi import APIRouter
import pandas as pd

router = APIRouter()

@router.get("/crime/weekday-trends")
def get_weekday_trends():

    df = pd.read_csv(
        "../data/processed/weekday_crime_trends.csv"
    )

    return df.to_dict(
        orient="records"
    )
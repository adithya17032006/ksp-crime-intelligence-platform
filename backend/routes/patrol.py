from fastapi import APIRouter
import pandas as pd

router = APIRouter()

@router.get("/patrol-priority")
def get_patrol_priority():

    df = pd.read_csv(
        "../data/processed/district_patrol_priority.csv"
    )

    return df.to_dict(
        orient="records"
    )
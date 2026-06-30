import pandas as pd
from backend.database.connection import engine


def get_risk_data():

    df = pd.read_sql(
        "SELECT * FROM district_risk_scores",
        engine
    )

    return df.to_dict(orient="records")
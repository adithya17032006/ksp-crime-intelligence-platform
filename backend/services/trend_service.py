import pandas as pd
from database.connection import engine

def get_monthly_trends():

    df = pd.read_sql(
        "SELECT * FROM monthly_crime_trends",
        engine
    )

    return df.to_dict(orient="records")


def get_weekday_trends():

    df = pd.read_sql(
        "SELECT * FROM weekday_crime_trends",
        engine
    )

    return df.to_dict(orient="records")
    
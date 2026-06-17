import pandas as pd

def get_monthly_trends():

    df = pd.read_csv(
        "../data/processed/monthly_crime_trends.csv"
    )

    return df.to_dict(
        orient="records"
    )

def get_weekday_trends():

    df = pd.read_csv(
        "../data/processed/weekday_crime_trends.csv"
    )

    return df.to_dict(
        orient="records"
    )
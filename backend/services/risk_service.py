import pandas as pd

def get_risk_data():

    df = pd.read_csv(
        "../data/processed/crime_risk_scores.csv"
    )

    return df.to_dict(
        orient="records"
    )
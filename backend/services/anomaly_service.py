import pandas as pd

def get_anomaly_data():

    df = pd.read_csv(
        "../data/processed/district_anomalies.csv"
    )

    return df.to_dict(
        orient="records"
    )
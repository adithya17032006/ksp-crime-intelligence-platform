import pandas as pd

def get_hotspot_data():

    df = pd.read_csv(
        "../data/processed/crime_hotspots.csv"
    )

    return df.to_dict(
        orient="records"
    )
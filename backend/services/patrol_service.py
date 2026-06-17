import pandas as pd

def get_patrol_data():

    df = pd.read_csv(
        "../data/processed/district_patrol_priority.csv"
    )

    return df.to_dict(
        orient="records"
    )
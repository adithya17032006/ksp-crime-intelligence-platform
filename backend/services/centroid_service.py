import pandas as pd
from database.connection import engine

def get_hotspot_centroids():

    df = pd.read_sql(
        "SELECT * FROM hotspot_centroids",
        engine
    )

    return df.to_dict(
        orient="records"
    )
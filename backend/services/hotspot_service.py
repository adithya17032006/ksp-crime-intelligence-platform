import pandas as pd
from backend.database.connection import engine

def get_hotspot_data():

    df = pd.read_sql(
        "SELECT * FROM crime_hotspots",
        engine
    )

    return df.to_dict(orient="records")
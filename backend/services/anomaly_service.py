import pandas as pd
from database.connection import engine

def get_anomaly_data():

    df = pd.read_sql(
        "SELECT * FROM district_anomalies",
        engine
    )

    return df.to_dict(orient="records")
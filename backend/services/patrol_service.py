import pandas as pd
from database.connection import engine

def get_patrol_data():

    df = pd.read_sql(
        "SELECT * FROM patrol_priority",
        engine
    )

    return df.to_dict(orient="records")
import pandas as pd
from connection import engine

tables = [
    "district_risk_scores",
    "crime_hotspots",
    "district_anomalies",
    "patrol_priority",
    "monthly_crime_trends",
    "weekday_crime_trends",
    "hotspot_centroids"
]

for table in tables:

    print(f"\n===== {table} =====")

    df = pd.read_sql(
        f"SELECT * FROM {table}",
        engine
    )

    print(df.head())
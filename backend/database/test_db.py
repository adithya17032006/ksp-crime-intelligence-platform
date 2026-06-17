import pandas as pd

from connection import engine

print("\nDISTRICT RISK SCORES\n")

risk_df = pd.read_sql(
    "SELECT * FROM district_risk_scores",
    engine
)

print(risk_df.head())

print("\nHOTSPOTS\n")

hotspot_df = pd.read_sql(
    "SELECT * FROM crime_hotspots",
    engine
)

print(hotspot_df.head())

print("\nANOMALIES\n")

anomaly_df = pd.read_sql(
    "SELECT * FROM district_anomalies",
    engine
)

print(anomaly_df.head())

print("\nPATROL PRIORITY\n")

patrol_df = pd.read_sql(
    "SELECT * FROM patrol_priority",
    engine
)

print(patrol_df.head())
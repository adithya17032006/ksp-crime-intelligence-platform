import pandas as pd

from connection import engine

print("Loading datasets into database...")

# District Risk Scores
risk_df = pd.read_csv(
    "../../data/processed/crime_risk_scores.csv"
)

risk_df.to_sql(
    "district_risk_scores",
    engine,
    if_exists="replace",
    index=False
)

print("✓ District Risk Scores Loaded")

# Crime Hotspots
hotspot_df = pd.read_csv(
    "../../data/processed/crime_hotspots.csv"
)

hotspot_df.to_sql(
    "crime_hotspots",
    engine,
    if_exists="replace",
    index=False
)

print("✓ Crime Hotspots Loaded")

# District Anomalies
anomaly_df = pd.read_csv(
    "../../data/processed/district_anomalies.csv"
)

anomaly_df.to_sql(
    "district_anomalies",
    engine,
    if_exists="replace",
    index=False
)

print("✓ District Anomalies Loaded")

# Patrol Priority
patrol_df = pd.read_csv(
    "../../data/processed/district_patrol_priority.csv"
)

patrol_df.to_sql(
    "patrol_priority",
    engine,
    if_exists="replace",
    index=False
)

print("✓ Patrol Priority Loaded")

print("\nAll datasets loaded successfully!")
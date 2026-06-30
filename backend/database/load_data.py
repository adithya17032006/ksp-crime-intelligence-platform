import os
import pandas as pd
from connection import engine

print("Loading datasets into database...")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data", "processed")

# District Risk Scores
risk_df = pd.read_csv(
    os.path.join(DATA_DIR, "crime_risk_scores.csv")
)

risk_df.to_sql(
    "district_risk_scores",
    engine,
    if_exists="replace",
    index=False
)

print("[OK] District Risk Scores Loaded")

# Crime Hotspots
hotspot_df = pd.read_csv(
    os.path.join(DATA_DIR, "crime_hotspots.csv")
)

hotspot_df.to_sql(
    "crime_hotspots",
    engine,
    if_exists="replace",
    index=False
)

print("[OK] Crime Hotspots Loaded")

# District Anomalies
anomaly_df = pd.read_csv(
    os.path.join(DATA_DIR, "district_anomalies.csv")
)

anomaly_df.to_sql(
    "district_anomalies",
    engine,
    if_exists="replace",
    index=False
)

print("[OK] District Anomalies Loaded")

# Patrol Priority
patrol_df = pd.read_csv(
    os.path.join(DATA_DIR, "district_patrol_priority.csv")
)

patrol_df.to_sql(
    "patrol_priority",
    engine,
    if_exists="replace",
    index=False
)

print("[OK] Patrol Priority Loaded")

# Monthly Trends
monthly_df = pd.read_csv(
    os.path.join(DATA_DIR, "monthly_crime_trends.csv")
)

monthly_df.to_sql(
    "monthly_crime_trends",
    engine,
    if_exists="replace",
    index=False
)

print("[OK] Monthly Trends Loaded")

# Weekday Trends
weekday_df = pd.read_csv(
    os.path.join(DATA_DIR, "weekday_crime_trends.csv")
)

weekday_df.to_sql(
    "weekday_crime_trends",
    engine,
    if_exists="replace",
    index=False
)

print("[OK] Weekday Trends Loaded")

# Hotspot Centroids
centroid_df = pd.read_csv(
    os.path.join(DATA_DIR, "hotspot_centroids.csv")
)

centroid_df.to_sql(
    "hotspot_centroids",
    engine,
    if_exists="replace",
    index=False
)

print("[OK] Hotspot Centroids Loaded")

print("\nAll datasets loaded successfully!")
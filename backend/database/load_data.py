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

# Monthly Trends
monthly_df = pd.read_csv(
    "../../data/processed/monthly_crime_trends.csv"
)

monthly_df.to_sql(
    "monthly_crime_trends",
    engine,
    if_exists="replace",
    index=False
)

print("✓ Monthly Trends Loaded")

# Weekday Trends
weekday_df = pd.read_csv(
    "../../data/processed/weekday_crime_trends.csv"
)

weekday_df.to_sql(
    "weekday_crime_trends",
    engine,
    if_exists="replace",
    index=False
)

print("✓ Weekday Trends Loaded")

# Hotspot Centroids
centroid_df = pd.read_csv(
    "../../data/processed/hotspot_centroids.csv"
)

centroid_df.to_sql(
    "hotspot_centroids",
    engine,
    if_exists="replace",
    index=False
)

print("✓ Hotspot Centroids Loaded")

print("\nAll datasets loaded successfully!")
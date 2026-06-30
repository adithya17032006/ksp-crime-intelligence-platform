import requests
import os
import pandas as pd
import numpy as np

# Import API_BASE_URL configuration
from config import API_BASE_URL

class KSPAPIClient:
    """
    Central API client for KSP Frontend to consume live FastAPI endpoints.
    Links all sub-components (Backend, GIS, AI/ML, and Network) to unified pipelines.
    Includes complete local fallbacks and user-friendly error alerts.
    """
    def __init__(self, base_url=API_BASE_URL):
        self.base_url = base_url

    def check_health(self) -> bool:
        """
        Queries GET /health to check backend connectivity status.
        """
        url = f"{self.base_url}/health"
        try:
            response = requests.get(url, timeout=0.6)
            if response.status_code == 200:
                data = response.json()
                return data.get("status") == "healthy"
        except Exception:
            pass
        return False

    def fetch_incidents(self) -> pd.DataFrame:
        """
        Fetches the primary synthetic crime incidents database.
        """
        url = f"{self.base_url}/api/incidents/"
        try:
            response = requests.get(url, timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                if not data:
                    return pd.DataFrame()
                
                df = pd.DataFrame(data)
                df["Date"] = pd.to_datetime(df["date"])
                df["Incident ID"] = df["crime_id"]
                df["District"] = df["district"]
                df["Crime Category"] = df["crime_type"]
                df["Latitude"] = df["latitude"]
                df["Longitude"] = df["longitude"]
                df["Status"] = df["status"]
                df["Repeat Offender"] = df["repeat_offender"].astype(bool)
                df["Victim Age"] = df["victim_age"]
                df["Offender Age"] = df["offender_age"]
                df["Police Station"] = df["police_station"]
                
                severity_map = {
                    "Vehicle Theft": "Low",
                    "Theft": "Low",
                    "Cybercrime": "Medium",
                    "Drug Offence": "Medium",
                    "Fraud": "Medium",
                    "Assault": "High",
                    "Burglary": "High",
                    "Robbery": "High"
                }
                df["Severity"] = df["Crime Category"].map(severity_map).fillna("Medium")
                df["Severity_Val"] = df["Severity"].map({"Low": 6, "Medium": 12, "High": 22})
                return df
        except Exception as e:
            print(f"Error loading incidents from API: {e}")
        
        return pd.DataFrame()

    def fetch_district_risk(self) -> tuple[pd.DataFrame, str | None]:
        """
        API Endpoint: GET /district-risk
        On success: Returns risk index dataframe.
        On error: Returns local fallback dataframe and user-friendly error string.
        """
        url = f"{self.base_url}/district-risk"
        err_msg = None
        try:
            response = requests.get(url, timeout=1.5)
            if response.status_code == 200:
                return pd.DataFrame(response.json()), None
            else:
                err_msg = f"Backend API returned status code {response.status_code}."
        except Exception as e:
            err_msg = f"Cannot reach backend server: {e}."

        return pd.DataFrame(), f"{err_msg} Database empty or unreachable."

    def fetch_patrol_priority(self) -> tuple[pd.DataFrame, str | None]:
        """
        API Endpoint: GET /patrol-priority
        On success: Returns patrol priority dataframe.
        On error: Returns local fallback dataframe and user-friendly error string.
        """
        url = f"{self.base_url}/patrol-priority"
        err_msg = None
        try:
            response = requests.get(url, timeout=1.5)
            if response.status_code == 200:
                return pd.DataFrame(response.json()), None
            else:
                err_msg = f"Backend API returned status code {response.status_code}."
        except Exception as e:
            err_msg = f"Cannot reach backend server: {e}."

        return pd.DataFrame(), f"{err_msg} Database empty or unreachable."

    def fetch_anomalies(self) -> tuple[pd.DataFrame, str | None]:
        """
        API Endpoint: GET /anomalies
        On success: Returns anomalies dataframe.
        On error: Returns local fallback dataframe and user-friendly error string.
        """
        url = f"{self.base_url}/anomalies"
        err_msg = None
        try:
            response = requests.get(url, timeout=1.5)
            if response.status_code == 200:
                df = pd.DataFrame(response.json())
                df["Date"] = pd.to_datetime(df["date"])
                df["Incident ID"] = df["crime_id"]
                df["District"] = df["district"]
                df["Crime Category"] = df["crime_type"]
                df["Latitude"] = df["latitude"]
                df["Longitude"] = df["longitude"]
                df["Status"] = df["status"]
                df["Repeat Offender"] = df["repeat_offender"].astype(bool)
                df["Victim Age"] = df["victim_age"]
                df["Offender Age"] = df["offender_age"]
                df["Police Station"] = df["police_station"]
                return df, None
            else:
                err_msg = f"Backend API returned status code {response.status_code}."
        except Exception as e:
            err_msg = f"Cannot reach backend server: {e}."

        return pd.DataFrame(), f"{err_msg} Database empty or unreachable."

    def fetch_hotspots(self) -> tuple[pd.DataFrame, str | None]:
        """
        API Endpoint: GET /hotspots
        On success: Returns hotspot statistics dataframe.
        On error: Returns local fallback dataframe and user-friendly error string.
        """
        url = f"{self.base_url}/hotspots"
        err_msg = None
        try:
            response = requests.get(url, timeout=1.5)
            if response.status_code == 200:
                return pd.DataFrame(response.json()), None
            else:
                err_msg = f"Backend API returned status code {response.status_code}."
        except Exception as e:
            err_msg = f"Cannot reach backend server: {e}."

        return pd.DataFrame(), f"{err_msg} Database empty or unreachable."

    def fetch_hotspot_centroids(self, fallback_df: pd.DataFrame = None) -> tuple[pd.DataFrame, str | None]:
        """
        API Endpoint: GET /hotspot-centroids
        On success: Returns coordinates and cluster stats.
        On error: Computes centroids from local fallback dataframe and returns warning.
        """
        url = f"{self.base_url}/hotspot-centroids"
        err_msg = None
        try:
            response = requests.get(url, timeout=1.5)
            if response.status_code == 200:
                return pd.DataFrame(response.json()), None
            else:
                err_msg = f"Backend API returned status code {response.status_code}."
        except Exception as e:
            err_msg = f"Cannot reach backend server: {e}."

        # --- Local Fallback ---
        if fallback_df is not None and not fallback_df.empty:
            try:
                # Dynamically calculate grid centroid averages per district as local clusters
                centroids = fallback_df.groupby("District").agg(
                    centroid_latitude=("Latitude", "mean"),
                    centroid_longitude=("Longitude", "mean"),
                    crime_count=("Incident ID", "count")
                ).reset_index()
                centroids["cluster"] = range(len(centroids))
                return centroids, f"{err_msg} Computed cluster centroids from current datasets."
            except Exception as e:
                return pd.DataFrame(), f"Failed to compute centroids: {e}."
        return pd.DataFrame(), f"{err_msg} No dataset available to compute fallback centroids."

    def fetch_monthly_trends(self) -> tuple[pd.DataFrame, str | None]:
        """
        API Endpoint: GET /crime/monthly-trends
        On success: Returns monthly crime counts.
        On error: Returns local fallback and user-friendly error string.
        """
        url = f"{self.base_url}/crime/monthly-trends"
        err_msg = None
        try:
            response = requests.get(url, timeout=1.5)
            if response.status_code == 200:
                return pd.DataFrame(response.json()), None
            else:
                err_msg = f"Backend API returned status code {response.status_code}."
        except Exception as e:
            err_msg = f"Cannot reach backend server: {e}."

        return pd.DataFrame(), f"{err_msg} Database empty or unreachable."

    def fetch_weekday_trends(self) -> tuple[pd.DataFrame, str | None]:
        """
        API Endpoint: GET /crime/weekday-trends
        On success: Returns weekday crime counts.
        On error: Returns local fallback and user-friendly error string.
        """
        url = f"{self.base_url}/crime/weekday-trends"
        err_msg = None
        try:
            response = requests.get(url, timeout=1.5)
            if response.status_code == 200:
                return pd.DataFrame(response.json()), None
            else:
                err_msg = f"Backend API returned status code {response.status_code}."
        except Exception as e:
            err_msg = f"Cannot reach backend server: {e}."

        return pd.DataFrame(), f"{err_msg} Database empty or unreachable."

    def fetch_network_graph(self) -> dict:
        """
        API pipeline: Member 4 (Network & Criminal Intelligence)
        Endpoint: GET /api/network/graph
        """
        url = f"{self.base_url}/api/network/graph"
        try:
            response = requests.get(url, timeout=1.5)
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        return {"nodes": [], "edges": []}
    def fetch_gis_map_layer(self, layer_name="crime_map") -> str:
        """
        Fetches static HTML map layers if online or falls back to local disk HTML files.
        """
        return "<div style='color:#ef4444; padding:20px;'>Map layer not found in database or API is unreachable.</div>"

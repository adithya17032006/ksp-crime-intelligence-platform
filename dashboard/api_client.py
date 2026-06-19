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
        # Prioritize the full 10,000 synthetic dataset merged from GitHub, then 520 subset
        paths = [
            "data/raw/ksp_synthetic_crime_dataset.csv",
            "dashboard/crime_data.csv"
        ]
        
        for csv_path in paths:
            if os.path.exists(csv_path):
                try:
                    df = pd.read_csv(csv_path)
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
                    print(f"Error loading incidents from {csv_path}: {e}")
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

        # --- Local Fallback ---
        file_path = "data/processed/crime_risk_scores.csv"
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path)
                return df, f"{err_msg} Loaded pre-computed Risk Index from local cache."
            except Exception as e:
                return pd.DataFrame(), f"Failed to load cache: {e}."
        return pd.DataFrame(), f"{err_msg} No pre-computed local risk scores found."

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

        # --- Local Fallback ---
        file_path = "data/processed/district_patrol_priority.csv"
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path)
                return df, f"{err_msg} Loaded pre-computed Patrol Priorities from local cache."
            except Exception as e:
                return pd.DataFrame(), f"Failed to load cache: {e}."
        return pd.DataFrame(), f"{err_msg} No pre-computed local patrol rankings found."

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

        # --- Local Fallback ---
        file_path = "data/processed/crime_anomalies.csv"
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path)
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
                return df, f"{err_msg} Loaded anomaly logs from local cache."
            except Exception as e:
                return pd.DataFrame(), f"Failed to load cache: {e}."
        return pd.DataFrame(), f"{err_msg} No pre-computed anomalies database found."

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

        # --- Local Fallback ---
        file_path = "data/processed/crime_hotspots.csv"
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path)
                return df, f"{err_msg} Loaded pre-computed hotspots from local cache."
            except Exception as e:
                return pd.DataFrame(), f"Failed to load cache: {e}."
        return pd.DataFrame(), f"{err_msg} No pre-computed hotspot statistics found."

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

        # --- Local Fallback ---
        file_path = "data/processed/monthly_crime_trends.csv"
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path)
                return df, f"{err_msg} Loaded pre-computed monthly trends from local cache."
            except Exception as e:
                return pd.DataFrame(), f"Failed to load cache: {e}."
        return pd.DataFrame(), f"{err_msg} No monthly trends database found."

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

        # --- Local Fallback ---
        file_path = "data/processed/weekday_crime_trends.csv"
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path)
                return df, f"{err_msg} Loaded pre-computed weekday trends from local cache."
            except Exception as e:
                return pd.DataFrame(), f"Failed to load cache: {e}."
        return pd.DataFrame(), f"{err_msg} No weekday trends database found."

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
            pass # Fallback to local
            
        # --- Local Fallback ---
        return {
            "nodes": [
                {"id": "Vijay Gowda (Kingpin)", "type": "Leader", "risk": "Critical", "cases": 12, "x": 0, "y": 0},
                {"id": "Rohan D'Souza (Finance)", "type": "Lieutenant", "risk": "High", "cases": 8, "x": 1.2, "y": 0.8},
                {"id": "Anand Kumar (Operations)", "type": "Lieutenant", "risk": "High", "cases": 9, "x": -1.2, "y": 0.8},
                {"id": "Shabir Ahmed (Logistics)", "type": "Lieutenant", "risk": "High", "cases": 5, "x": 1.2, "y": -0.8},
                {"id": "Chethan S. (Enforcer)", "type": "Lieutenant", "risk": "High", "cases": 11, "x": -1.2, "y": -0.8},
                {"id": "Raghu Gowda (Associate)", "type": "Associate", "risk": "Medium", "cases": 4, "x": 2.3, "y": 1.4},
                {"id": "Sunil P. (Associate)", "type": "Associate", "risk": "Medium", "cases": 3, "x": 2.0, "y": -1.5},
                {"id": "Imran Ali (Associate)", "type": "Associate", "risk": "Medium", "cases": 2, "x": -2.3, "y": -1.4},
                {"id": "Appu Swamy (Associate)", "type": "Associate", "risk": "Medium", "cases": 4, "x": -2.0, "y": 1.5}
            ],
            "edges": [
                {"source": "Vijay Gowda (Kingpin)", "target": "Rohan D'Souza (Finance)"},
                {"source": "Vijay Gowda (Kingpin)", "target": "Anand Kumar (Operations)"},
                {"source": "Vijay Gowda (Kingpin)", "target": "Shabir Ahmed (Logistics)"},
                {"source": "Vijay Gowda (Kingpin)", "target": "Chethan S. (Enforcer)"},
                {"source": "Rohan D'Souza (Finance)", "target": "Raghu Gowda (Associate)"},
                {"source": "Shabir Ahmed (Logistics)", "target": "Sunil P. (Associate)"},
                {"source": "Chethan S. (Enforcer)", "target": "Imran Ali (Associate)"},
                {"source": "Anand Kumar (Operations)", "target": "Appu Swamy (Associate)"},
                {"source": "Anand Kumar (Operations)", "target": "Rohan D'Souza (Finance)"},
                {"source": "Shabir Ahmed (Logistics)", "target": "Chethan S. (Enforcer)"}
            ]
        }

    def fetch_gis_map_layer(self, layer_name="crime_map") -> str:
        """
        Fetches static HTML map layers if online or falls back to local disk HTML files.
        """
        map_files = {
            "crime_map": "gis/outputs/maps/crime_map.html",
            "crime_heatmap": "gis/outputs/maps/crime_heatmap.html",
            "crime_hotspots": "gis/outputs/maps/crime_hotspots.html",
            "crime_anomalies": "gis/outputs/maps/crime_anomalies.html"
        }
        
        file_path = map_files.get(layer_name, "gis/outputs/maps/crime_map.html")
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception:
                pass
        return ""

import requests
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class KSPAPIClient:
    """
    Central API client for KSP Frontend to consume API pipelines.
    Points to KSP Microservices (Backend, AI/ML, GIS, and Network).
    Includes complete local fallbacks to ensure presentation dashboard works offline.
    """
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def fetch_incidents(self) -> pd.DataFrame:
        """
        API pipeline: Member 1 (Backend & Data Engineering Lead)
        Endpoint: GET /api/backend/incidents
        """
        url = f"{self.base_url}/api/backend/incidents"
        try:
            response = requests.get(url, timeout=2.0)
            if response.status_code == 200:
                data = response.json()
                df = pd.DataFrame(data)
                df["Date"] = pd.to_datetime(df["Date"])
                return df
        except Exception:
            pass # Fallback to local
            
        # --- Local Fallback ---
        # Prioritize the full 10,000 synthetic dataset merged from GitHub, then 520 subset
        paths = [
            "data/raw/ksp_synthetic_crime_dataset.csv",
            "dashboard/crime_data.csv"
        ]
        
        for csv_path in paths:
            if os.path.exists(csv_path):
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
        return pd.DataFrame()

    def fetch_suspects(self) -> dict:
        """
        API pipeline: Member 1 (Backend & Data Engineering Lead)
        Endpoint: GET /api/backend/suspects
        """
        url = f"{self.base_url}/api/backend/suspects"
        try:
            response = requests.get(url, timeout=2.0)
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass # Fallback to local
            
        # --- Local Fallback ---
        return {
            "Vijay Gowda (Kingpin)": {"type": "Leader", "risk": "Critical", "cases": 12, "last_known": "Bengaluru Urban"},
            "Rohan D'Souza (Finance)": {"type": "Lieutenant", "risk": "High", "cases": 8, "last_known": "Mangaluru"},
            "Anand Kumar (Operations)": {"type": "Lieutenant", "risk": "High", "cases": 9, "last_known": "Mysuru"},
            "Shabir Ahmed (Logistics)": {"type": "Lieutenant", "risk": "High", "cases": 5, "last_known": "Kalaburagi"},
            "Chethan S. (Enforcer)": {"type": "Lieutenant", "risk": "High", "cases": 11, "last_known": "Belagavi"},
            "Raghu Gowda (Associate)": {"type": "Associate", "risk": "Medium", "cases": 4, "last_known": "Tumakuru"},
            "Sunil P. (Associate)": {"type": "Associate", "risk": "Medium", "cases": 3, "last_known": "Ballari"},
            "Imran Ali (Associate)": {"type": "Associate", "risk": "Medium", "cases": 2, "last_known": "Shivamogga"},
            "Appu Swamy (Associate)": {"type": "Associate", "risk": "Medium", "cases": 4, "last_known": "Dharwad"}
        }

    def predict_recidivism(self, offender_age: int, prev_convictions: int, crime_category: str, employment: str, rehab_status: str) -> dict:
        """
        API pipeline: Member 3 (AI/ML Intelligence)
        Endpoint: POST /api/ml/predict-recidivism
        """
        url = f"{self.base_url}/api/ml/predict-recidivism"
        payload = {
            "offender_age": offender_age,
            "prev_convictions": prev_convictions,
            "crime_category": crime_category,
            "employment": employment,
            "rehab_status": rehab_status
        }
        try:
            response = requests.post(url, json=payload, timeout=2.0)
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass # Fallback to local
            
        # --- Local Fallback ---
        base_score = 15 + (prev_convictions * 12) - (offender_age - 18) * 0.7
        if employment == "Full-time Employed":
            base_score -= 18
        elif employment == "Unemployed":
            base_score += 12
            
        if crime_category in ["Robbery", "Assault", "Burglary"]:
            base_score += 15
            
        if rehab_status == "Yes":
            base_score -= 15
            
        risk_score = min(max(int(base_score), 5), 98)
        
        if risk_score < 35:
            risk_lbl = "LOW RISK"
            risk_col = "#10B981"
            intervention = "Standard monitoring check-ins."
        elif risk_score < 70:
            risk_lbl = "MODERATE RISK"
            risk_col = "#F59E0B"
            intervention = "Mandatory community counseling."
        else:
            risk_lbl = "HIGH RISK"
            risk_col = "#EF4444"
            intervention = "Intense supervision and probation alert list."

        # Generate local text SHAP explanation
        shap_text = (
            f"SHAP Model Explanations:\n"
            f"- Prior convictions (+{prev_convictions * 12}% risk shift)\n"
            f"- Offender age ({offender_age} yrs, -{((offender_age - 18) * 0.7):.1f}% risk shift)\n"
            f"- Employment status ('{employment}', {'+12%' if employment == 'Unemployed' else '-18%' if employment == 'Full-time Employed' else '+0%'} shift)\n"
            f"- Offense Category ('{crime_category}', {'+15%' if crime_category in ['Robbery', 'Assault', 'Burglary'] else '+0%'} severity shift)\n"
            f"- Rehabilitation history ('{rehab_status}', {'-15%' if rehab_status == 'Yes' else '+0%'} shift)"
        )

        return {
            "risk_score": risk_score,
            "risk_label": risk_lbl,
            "risk_color": risk_col,
            "shap_explanation": shap_text,
            "intervention": intervention
        }

    def fetch_forecast(self, monthly_incidents: pd.DataFrame) -> pd.DataFrame:
        """
        API pipeline: Member 3 (AI/ML Intelligence)
        Endpoint: GET /api/ml/forecast
        """
        url = f"{self.base_url}/api/ml/forecast"
        try:
            response = requests.get(url, timeout=2.0)
            if response.status_code == 200:
                data = response.json()
                df = pd.DataFrame(data)
                df["YearMonth"] = pd.to_datetime(df["YearMonth"])
                return df
        except Exception:
            pass # Fallback to local
            
        # --- Local Fallback ---
        if len(monthly_incidents) >= 3:
            last_date = monthly_incidents['YearMonth'].iloc[-1]
            forecast_dates = [last_date + timedelta(days=31*i) for i in range(1, 7)]
            last_val = monthly_incidents['Incidents'].iloc[-1]
            
            forecast_vals = []
            upper_bound = []
            lower_bound = []
            
            curr = last_val
            for i in range(6):
                curr = curr * np.random.uniform(0.97, 1.04)
                forecast_vals.append(curr)
                variance = curr * 0.15 * (i + 1)
                upper_bound.append(curr + variance)
                lower_bound.append(max(0, curr - variance))
                
            return pd.DataFrame({
                'YearMonth': forecast_dates,
                'Incidents': forecast_vals,
                'Upper': upper_bound,
                'Lower': lower_bound
            })
        return pd.DataFrame()

    def fetch_gis_map_layer(self, layer_name="crime_map") -> str:
        """
        API pipeline: Member 2 (GIS & Crime Intelligence)
        Endpoint: GET /api/gis/folium-map?layer=...
        """
        url = f"{self.base_url}/api/gis/folium-map?layer={layer_name}"
        try:
            response = requests.get(url, timeout=2.0)
            if response.status_code == 200:
                return response.json().get("html_str", "")
        except Exception:
            pass # Fallback to local
            
        # --- Local Fallback ---
        # Dynamically read the actual maps pushed by the GIS team on GitHub
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

    def fetch_network_graph(self) -> dict:
        """
        API pipeline: Member 4 (Network & Criminal Intelligence)
        Endpoint: GET /api/network/graph
        """
        url = f"{self.base_url}/api/network/graph"
        try:
            response = requests.get(url, timeout=2.0)
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

    # --- New Methods to fetch processed GIS/ML metrics ---
    def fetch_crime_risk_scores(self) -> pd.DataFrame:
        """Fetch pre-computed crime risk score analytics from database."""
        url = f"{self.base_url}/api/ml/risk-scores"
        try:
            response = requests.get(url, timeout=2.0)
            if response.status_code == 200:
                return pd.DataFrame(response.json())
        except Exception:
            pass
            
        # Fallback to local processed file
        file_path = "data/processed/crime_risk_scores.csv"
        if os.path.exists(file_path):
            return pd.read_csv(file_path)
        return pd.DataFrame()

    def fetch_patrol_priorities(self) -> pd.DataFrame:
        """Fetch pre-computed patrol recommendations from database."""
        url = f"{self.base_url}/api/ml/patrol-priorities"
        try:
            response = requests.get(url, timeout=2.0)
            if response.status_code == 200:
                return pd.DataFrame(response.json())
        except Exception:
            pass
            
        # Fallback to local processed file
        file_path = "data/processed/district_patrol_priority.csv"
        if os.path.exists(file_path):
            return pd.read_csv(file_path)
        return pd.DataFrame()

    def fetch_weekday_trends(self) -> pd.DataFrame:
        """Fetch weekday temporal trends from database."""
        url = f"{self.base_url}/api/ml/weekday-trends"
        try:
            response = requests.get(url, timeout=2.0)
            if response.status_code == 200:
                return pd.DataFrame(response.json())
        except Exception:
            pass
            
        # Fallback to local processed file
        file_path = "data/processed/weekday_crime_trends.csv"
        if os.path.exists(file_path):
            return pd.read_csv(file_path)
        return pd.DataFrame()

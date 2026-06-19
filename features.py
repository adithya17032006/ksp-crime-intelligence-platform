# features.py
from datetime import datetime
import pandas as pd
from config import PipelineConfig, CRIME_MAPPING, CITY_MAPPING, CITY_COORDINATES

def format_inference_features(timestamp_str: str, crime_desc: str, city_name: str, victim_age: int) -> pd.DataFrame:
    """
    Constructs a calibrated, position-ordered feature vector sequence 
    matching the exact internal signatures required by crime_rf_model.pkl.
    """
    try:
        dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%SS" if len(timestamp_str) > 16 else "%Y-%m-%d %H:%M:%S")
    except ValueError:
        dt = datetime.now()

    crime_upper = crime_desc.strip().upper()
    city_upper = city_name.strip().upper()
    
    crime_encoded = CRIME_MAPPING.get(crime_upper, 9)     # Default fallback index
    district_encoded = CITY_MAPPING.get(city_upper, 4)    # Default fallback index
    
    coords = CITY_COORDINATES.get(city_upper, CITY_COORDINATES['DEFAULT'])
    
    # Pack array variables matching internal feature indices sequentially
    feature_values = [
        dt.hour,
        dt.weekday(),
        dt.month,
        crime_encoded,
        district_encoded,
        coords['Lat'],
        coords['Lon'],
        int(victim_age)
    ]
    
    return pd.DataFrame([feature_values], columns=PipelineConfig.FEATURE_COLUMNS)
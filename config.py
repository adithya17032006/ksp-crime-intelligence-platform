# config.py
import os

class PipelineConfig:
    RANDOM_STATE = 42
    MODEL_EXPORT_PATH = "ml/crime_rf_model.pkl"
    PROCESSED_DATA_PATH = "ml/intelligence_processed_data.csv"
    IMAGE_EXPORT_PATH = "ml/feature_importances.png"
    CSV_EXPORT_PATH = "ml/feature_importances.csv"
    
    # Precise 8-dimensional sequence expected by crime_rf_model.pkl
    FEATURE_COLUMNS = [
        'Hour', 'Day_of_Week', 'Month', 'Crime_Type_Encoded', 
        'District_Encoded', 'Latitude', 'Longitude', 'Victim_Age'
    ]
    
    # Evaluation constraints for base Crime Risk Index calculations
    SEVERITY_WEIGHTS = {
        'ASSAULT': 8, 'BURGLARY': 6, 'CYBERCRIME': 7, 'FRAUD': 6,
        'HOMICIDE': 10, 'IDENTITY THEFT': 7, 'KIDNAPPING': 9,
        'PUBLIC INTOXICATION': 2, 'ROBBERY': 7, 'THEFT': 4, 'TRAFFIC VIOLATION': 3
    }

# Immutable Label Encoding Dictionaries
CRIME_MAPPING = {
    'ASSAULT': 0, 'BURGLARY': 1, 'CYBERCRIME': 2, 'FRAUD': 3,
    'HOMICIDE': 4, 'IDENTITY THEFT': 5, 'KIDNAPPING': 6,
    'PUBLIC INTOXICATION': 7, 'ROBBERY': 8, 'THEFT': 9, 'TRAFFIC VIOLATION': 10
}

CITY_MAPPING = {
    'AHMEDABAD': 0, 'BAGALKOT': 1, 'CHENNAI': 2, 'GHAZIABAD': 3,
    'HASSAN': 4, 'LUDHIANA': 5, 'MUMBAI': 6, 'PUNE': 7
}

# Geofenced Centroid Maps for Spatial Coordinate Conversion Layers
CITY_COORDINATES = {
    'AHMEDABAD': {'Lat': 23.0225, 'Lon': 72.5714},
    'CHENNAI':   {'Lat': 13.0827, 'Lon': 80.2707},
    'LUDHIANA':  {'Lat': 30.9010, 'Lon': 75.8573},
    'PUNE':      {'Lat': 18.5204, 'Lon': 73.8567},
    'GHAZIABAD': {'Lat': 28.6692, 'Lon': 77.4538},
    'MUMBAI':    {'Lat': 19.0760, 'Lon': 72.8777},
    'HASSAN':    {'Lat': 13.0055, 'Lon': 76.1004},
    'BAGALKOT':  {'Lat': 16.1817, 'Lon': 75.6958},
    'DEFAULT':   {'Lat': 12.9716, 'Lon': 77.5946}
}
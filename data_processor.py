# data_processor.py
import re
import numpy as np
import pandas as pd
from datetime import datetime
from config import PipelineConfig, CRIME_MAPPING, CITY_MAPPING, CITY_COORDINATES

def clean_and_build_training_dataframe(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Normalizes raw input tables and maps calculated metrics to categorical flags."""
    print("🧹 [Processor] Aligning array records and compiling metric signatures...")
    df = pd.DataFrame()
    
    # Chronological Sync Layers
    if 'Time of Occurrence' in raw_df.columns:
        df['Timestamp'] = pd.to_datetime(raw_df['Time of Occurrence'], errors='coerce')
    elif 'Date of Occurrence' in raw_df.columns:
        df['Timestamp'] = pd.to_datetime(raw_df['Date of Occurrence'], errors='coerce')
    else:
        df['Timestamp'] = pd.Timestamp.now()
    df['Timestamp'] = df['Timestamp'].fillna(pd.Timestamp('2026-01-01 00:00:00'))

    # Feature Matrix Splitting
    df['Hour'] = df['Timestamp'].dt.hour
    df['Day_of_Week'] = df['Timestamp'].dt.dayofweek
    df['Month'] = df['Timestamp'].dt.month

    # Map Labels
    df['Crime_Type'] = raw_df['Crime Description'].fillna('THEFT').str.strip().str.upper()
    df['District'] = raw_df['City'].fillna('HASSAN').str.strip().str.upper()

    df['Crime_Type_Encoded'] = df['Crime_Type'].map(CRIME_MAPPING).fillna(9).astype(int)
    df['District_Encoded'] = df['District'].map(CITY_MAPPING).fillna(4).astype(int)

    # Calculate Regional Telemetry Coordinates
    lats, lons = [], []
    for city in df['District']:
        coords = CITY_COORDINATES.get(city, CITY_COORDINATES['DEFAULT'])
        lats.append(coords['Lat'] + np.random.uniform(-0.005, 0.005))
        lons.append(coords['Lon'] + np.random.uniform(-0.005, 0.005))
    df['Latitude'] = lats
    df['Longitude'] = lons

    df['Victim_Age'] = pd.to_numeric(raw_df['Victim Age'], errors='coerce').fillna(35).astype(int)

    # Derive Crime Risk Target Thresholds (CRI Formulation)
    cri_scores = []
    for _, row in df.iterrows():
        base = PipelineConfig.SEVERITY_WEIGHTS.get(row['Crime_Type'], 4)
        multiplier = 1.35 if (row['Hour'] >= 22 or row['Hour'] <= 4) else 1.0
        cri_scores.append(base * multiplier)
        
    df['CRI_Score'] = cri_scores
    df['Is_High_Risk'] = (df['CRI_Score'] > df['CRI_Score'].median()).astype(int)
    
    return df

def decode_unstructured_text_to_dictionary(text: str) -> dict:
    """
    Decodes raw unstructured text strings or document outputs from an FIR PDF.
    Extracts core data features using pattern matching for English and Kannada keywords.
    """
    text_upper = text.upper()
    
    # 1. Location / District Matcher
    detected_city = "HASSAN"
    for city_key in CITY_MAPPING.keys():
        pattern = r"\b" + re.escape(city_key) + r"\b"
        if re.search(pattern, text_upper):
            detected_city = city_key
            break

    # 2. Classification Mapping Identification
    detected_crime = "THEFT"
    for crime_key in CRIME_MAPPING.keys():
        if re.search(r"\b" + re.escape(crime_key) + r"\b", text_upper):
            detected_crime = crime_key
            break
            
    # 3. Temporal Tracking Extraction (DD-MM-YYYY / HH:MM)
    detected_dt = datetime.now()
    date_match = re.search(r"\b(\d{2})[-/](\d{2})[-/](\d{4})\b", text)
    time_match = re.search(r"\b(\d{2}):(\d{2})(?::(\d{2}))?\b", text)
    if date_match:
        try:
            d_str = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
            t_str = time_match.group(0) if time_match else "12:00:00"
            detected_dt = datetime.strptime(f"{d_str} {t_str}", "%d-%m-%Y %H:%M:%S" if len(t_str) > 5 else "%d-%m-%Y %H:%M")
        except:
            pass

    # 4. Demographic Variable Context (Supports tokens like English 'Age' or local Kannada 'ವಯಸ್ಸು' / 'ವರ್ಷ')
    detected_age = 35
    age_regex_patterns = [
        r"\b(\d{2})\s*(?:YEARS|YEARS\s*OLD|ವರ್ಷ|ವಯಸ್ಸು)\b",
        r"(?:AGE|ವಯಸ್ಸು)\s*:\s*(\d{2})"
    ]
    for pattern in age_regex_patterns:
        age_match = re.search(pattern, text_upper)
        if age_match:
            detected_age = int(next(g for g in age_match.groups() if g is not None))
            break

    return {
        "timestamp": detected_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "crime_description": detected_crime,
        "city": detected_city,
        "victim_age": detected_age
    }

import io
import PyPDF2

def read_pdf_bytes_to_string(file_bytes: bytes) -> str:
    """Extracts text from PDF bytes using PyPDF2."""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text if text.strip() else file_bytes.decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"PyPDF2 Extraction Error: {e}")
        return file_bytes.decode('utf-8', errors='ignore')
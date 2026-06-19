# api_routes.py
import os
import pickle
import pandas as pd
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, status

from config import PipelineConfig, CITY_COORDINATES
from data_processor import decode_unstructured_text_to_dictionary
from features import format_inference_features

router = APIRouter(prefix="/api/predict", tags=["Crime Analytics ML Intelligence Layer"])
MODEL_CACHE = None

def get_loaded_model():
    """Mounts the compiled pickle artifact safely into the active application memory."""
    global MODEL_CACHE
    if MODEL_CACHE is None:
        if not os.path.exists(PipelineConfig.MODEL_EXPORT_PATH):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Classification binary asset unmounted at target path: '{PipelineConfig.MODEL_EXPORT_PATH}'"
            )
        with open(PipelineConfig.MODEL_EXPORT_PATH, "rb") as f:
            MODEL_CACHE = pickle.load(f)
    return MODEL_CACHE

# ==========================================
# INGESTION CONTRACT SPECIFICATIONS (PYDANTIC)
# ==========================================
class CrimePredictionInput(BaseModel):
    timestamp: Optional[str] = Field(None, example="2026-06-17 23:45:00", description="Target Pattern: YYYY-MM-DD HH:MM:SS")
    crime_description: Optional[str] = Field(None, example="ROBBERY")
    city: Optional[str] = Field(None, example="HASSAN")
    victim_age: Optional[int] = Field(None, ge=0, le=120, example=28)
    
    # Text field to accept plain narrative text or text extracted from an FIR PDF
    raw_text: Optional[str] = Field(
        None, 
        example="FIR Context Details: Incident happened on 15-02-2026 at 21:00 near Hassan district boundaries.",
        description="Provide unmapped raw string logs here for dynamic heuristic extraction processing."
    )

# ==========================================
# OPERATIONAL ENDPOINT ROUTING BLOCKS
# ==========================================

@router.post("/crime-risk", status_code=status.HTTP_200_OK)
def predict_crime_risk(payload: CrimePredictionInput):
    """
    Ingests structured variables OR raw narrative text strings, formats 
    the extraction vectors, and executes binary risk assessments.
    """
    model = get_loaded_model()

    # Step 1: Check validation layout mode selection
    if payload.raw_text and not (payload.timestamp and payload.crime_description and payload.city):
        extracted = decode_unstructured_text_to_dictionary(payload.raw_text)
        time_str = extracted["timestamp"]
        crime_str = extracted["crime_description"]
        city_str = extracted["city"]
        age_int = extracted["victim_age"]
        ingestion_source = "unstructured_text_nlp"
    else:
        if not (payload.timestamp and payload.crime_description and payload.city):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Validation Error: Supply complete explicit parameters OR a valid raw_text string."
            )
        time_str = payload.timestamp
        crime_str = payload.crime_description
        city_str = payload.city
        age_int = payload.victim_age if payload.victim_age is not None else 35
        ingestion_source = "structured_json_payload"

    # Step 2: Validate temporal configurations
    try:
        dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%SS" if len(time_str) > 16 else "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Malformed Timestamp formatting structure. Follow pattern: 'YYYY-MM-DD HH:MM:SS'."
        )

    # Step 3: Parse inputs into position-ordered data vectors
    input_df = format_inference_features(
        timestamp_str=time_str, 
        crime_desc=crime_str, 
        city_name=city_str, 
        victim_age=age_int
    )

    # Step 4: Execute model calculations
    try:
        prediction_code = int(model.predict(input_df)[0])
        probabilities = model.predict_proba(input_df)[0]
        confidence_metric = float(probabilities[prediction_code])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Inference execution engine calculation failure: {str(e)}"
        )

    # Step 5: Map regional spatial coordinates
    coords = CITY_COORDINATES.get(city_str.strip().upper(), CITY_COORDINATES['DEFAULT'])

    return {
        "status": "success",
        "ingestion_mode": ingestion_source,
        "extracted_features": {
            "resolved_timestamp": time_str,
            "resolved_crime": crime_str.strip().upper(),
            "resolved_city": city_str.strip().upper(),
            "resolved_victim_age": age_int
        },
        "prediction_results": {
            "risk_level_code": prediction_code,
            "risk_level_label": "High Risk" if prediction_code == 1 else "Low Risk",
            "probability_score": round(confidence_metric, 4)
        },
        "geospatial_footprint": {
            "latitude": round(coords['Lat'], 4),
            "longitude": round(coords['Lon'], 4)
        }
    }


@router.get("/feature-importance", status_code=status.HTTP_200_OK)
def get_model_feature_importance():
    """
    Extracts sorted model parameter rankings to dynamically populate 
    visualization charts on the frontend.
    """
    model = get_loaded_model()
    try:
        raw_importances = model.feature_importances_
        rankings = [
            {"feature": name, "importance_weight": round(float(weight), 6)}
            for name, weight in zip(PipelineConfig.FEATURE_COLUMNS, raw_importances)
        ]
        sorted_rankings = sorted(rankings, key=lambda x: x['importance_weight'], reverse=True)
        
        return {
            "status": "success",
            "model_architecture": "RandomForestClassifier",
            "feature_rankings": sorted_rankings
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to compile ranking matrix metrics: {str(e)}"
        )
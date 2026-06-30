# app.py
import os
import pickle
import pandas as pd
from datetime import datetime
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from config import PipelineConfig, CRIME_MAPPING, CITY_MAPPING, CITY_COORDINATES
from data_processor import decode_unstructured_text_to_dictionary, read_pdf_bytes_to_string

from backend.routes.risk import router as risk_router
from backend.routes.patrol import router as patrol_router
from backend.routes.anomalies import router as anomaly_router
from backend.routes.trends import router as trends_router
from backend.routes.hotspots import router as hotspot_router
from backend.routes.weekday_trends import router as weekday_router
from backend.routes.centroids import router as centroid_router
from backend.routes.fir import router as fir_router
from backend.routes.assistant import router as assistant_router
from backend.routes.cases import router as cases_router
from backend.routes.auth import router as auth_router
from backend.routes.incidents import router as incidents_router
from api_routes import router as ml_router

app = FastAPI(
    title="KSP Crime Intelligence Platform - Core Multi-Modal Gateway",
    description="Exposes structured predictive modeling analytics alongside real-time raw PDF FIR decoding modules.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(risk_router)
app.include_router(patrol_router)
app.include_router(anomaly_router)
app.include_router(trends_router)
app.include_router(hotspot_router)
app.include_router(weekday_router)
app.include_router(centroid_router)
app.include_router(fir_router)
app.include_router(assistant_router)
app.include_router(cases_router)
app.include_router(auth_router)
app.include_router(incidents_router)
app.include_router(ml_router)

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/")
def root():
    """Redirect root requests to the Streamlit dashboard."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="http://localhost:8501", status_code=302)


model = None

@app.on_event("startup")
def load_ml_assets():
    """Mounts the compiled Random Forest core binary layer into current memory context on startup."""
    global model
    if not os.path.exists(PipelineConfig.MODEL_EXPORT_PATH):
        raise RuntimeError(f"CRITICAL: Binary asset file '{PipelineConfig.MODEL_EXPORT_PATH}' not found.")
    with open(PipelineConfig.MODEL_EXPORT_PATH, "rb") as f:
        model = pickle.load(f)
    print("Unstructured Text Decoding Engine & ML Pipeline Context mounted successfully.")

# ==========================================
# PYDANTIC HIGH-SPEED INTERFACE VALIDATIONS
# ==========================================
class StructuredPredictionInput(BaseModel):
    timestamp: str = Field(..., example="2026-06-17 23:45:00", description="Expected string format: 'YYYY-MM-DD HH:MM:SS'")
    crime_description: str = Field(..., example="ROBBERY", description="Raw threat profile string classification key")
    city: str = Field(..., example="HASSAN", description="Target district hub city matching tracking bounds")
    victim_age: int = Field(..., ge=0, le=120, example=28, description="Target demographic context tracking metric")

# ==========================================
# CORE INFERENCE INTERNAL UTILITY PIPELINE
# ==========================================
def execute_core_inference(hour: int, day_of_week: int, month: int, crime_key: str, city_key: str, victim_age: int):
    """Executes categorical integer translations and passes extracted arrays to the ML model core."""
    crime_encoded = CRIME_MAPPING.get(crime_key, 9)     # Falls back cleanly to 'THEFT'
    district_encoded = CITY_MAPPING.get(city_key, 4)    # Falls back cleanly to 'HASSAN'

    coords = CITY_COORDINATES.get(city_key, CITY_COORDINATES['DEFAULT'])
    latitude = coords['Lat']
    longitude = coords['Lon']

    feature_values = [
        hour, day_of_week, month, crime_encoded, 
        district_encoded, latitude, longitude, victim_age
    ]
    input_dataframe = pd.DataFrame([feature_values], columns=PipelineConfig.FEATURE_COLUMNS)

    binary_class_result = int(model.predict(input_dataframe)[0])
    probabilities_array = model.predict_proba(input_dataframe)[0]
    confidence_metric = float(probabilities_array[binary_class_result])
    
    return {
        "risk_level_code": binary_class_result,
        "risk_level_label": "High Risk" if binary_class_result == 1 else "Low Risk",
        "probability_score": round(confidence_metric, 4),
        "spatial_footprint": {"latitude": round(latitude, 4), "longitude": round(longitude, 4)},
        "resolved_features": {"hour": hour, "day_of_week": day_of_week, "month": month}
    }

# ==========================================
# PRODUCTION SYSTEM CORE API ROUTE NODES
# ==========================================

@app.post("/predict-from-doc", status_code=status.HTTP_200_OK)
async def predict_risk_from_raw_document(file: UploadFile = File(...)):
    """
    Accepts an unstructured binary file upload stream (such as a raw state police FIR PDF or text sheet).
    Extracts core features on the fly and returns structured classification vectors for your frontend dashboard.
    """
    if model is None:
        raise HTTPException(status_code=500, detail="Prediction module model layers are unmounted.")
    
    # Read the incoming upload stream buffer
    file_bytes = await file.read()
    filename_lower = file.filename.lower()
    
    # Extract raw text frames based on incoming document MIME extension structures
    if filename_lower.endswith('.pdf'):
        document_text = read_pdf_bytes_to_string(file_bytes)
    else:
        document_text = file_bytes.decode('utf-8', errors='ignore')
        
    if not document_text.strip():
        raise HTTPException(status_code=400, detail="Failed to isolate or parse meaningful text arrays from document source.")

    # Execute text extraction regex transformations
    extracted_data = decode_unstructured_text_to_dictionary(document_text)
    
    # Process structured variables out of extracted attributes
    dt = datetime.strptime(extracted_data['timestamp'], "%Y-%m-%d %H:%M:%S")
    
    # Execute prediction inference matching pipeline schema constraints
    inference_payload = execute_core_inference(
        hour=dt.hour, day_of_week=dt.weekday(), month=dt.month,
        crime_key=extracted_data['crime_description'],
        city_key=extracted_data['city'],
        victim_age=extracted_data['victim_age']
    )
    
    return {
        "status": "success",
        "document_name": file.filename,
        "extracted_attributes": extracted_data,
        "analytics_prediction": inference_payload
    }

@app.post("/predict-crime", status_code=status.HTTP_200_OK)
def predict_crime_risk_via_json(payload: StructuredPredictionInput):
    """Fallback endpoint for handling structured JSON parameter objects directly from the client interface."""
    if model is None:
        raise HTTPException(status_code=500, detail="ML Core model engine layer is currently unavailable.")
    
    try:
        # Flexible timestamp parser - handles both 'YYYY-MM-DD HH:MM' and 'YYYY-MM-DD HH:MM:SS'
        ts = payload.timestamp.strip()
        try:
            dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            dt = datetime.strptime(ts, "%Y-%m-%d %H:%M")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date layout. Use: 'YYYY-MM-DD HH:MM:SS'.")

    inference_payload = execute_core_inference(
        hour=dt.hour, day_of_week=dt.weekday(), month=dt.month,
        crime_key=payload.crime_description.strip().upper(),
        city_key=payload.city.strip().upper(),
        victim_age=payload.victim_age
    )
    
    return {
        "status": "success",
        "analytics_prediction": inference_payload
    }

@app.get("/feature-importance", status_code=status.HTTP_200_OK)
def get_feature_importance_rankings():
    """Returns dynamic model feature importance weights to populate UI analytical graphs directly."""
    if model is None:
        raise HTTPException(status_code=500, detail="Inference engine binary components are unmounted.")
    
    try:
        rankings = [
            {"feature": name, "importance_weight": round(float(w), 6)}
            for name, w in zip(PipelineConfig.FEATURE_COLUMNS, model.feature_importances_)
        ]
        return {
            "status": "success",
            "model_architecture": "RandomForestClassifier",
            "feature_rankings": sorted(rankings, key=lambda x: x['importance_weight'], reverse=True)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract metric layers: {str(e)}")
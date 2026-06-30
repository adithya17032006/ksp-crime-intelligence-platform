from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd
from io import BytesIO
from datetime import datetime
from backend.database.connection import SessionLocal
from backend.database.models import CrimeIncident

router = APIRouter(prefix="/api/incidents", tags=["Crime Incidents Data"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_incidents_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Accepts a CSV file of crime incidents and bulk inserts them into PostgreSQL.
    Expects columns: crime_id, date, district, crime_type, latitude, longitude, status, repeat_offender, victim_age, offender_age, police_station
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")
        
    try:
        contents = await file.read()
        df = pd.read_csv(BytesIO(contents))
        
        # Validate required columns
        required_cols = {'crime_id', 'date', 'district', 'crime_type'}
        if not required_cols.issubset(set(df.columns)):
            missing = required_cols - set(df.columns)
            raise HTTPException(status_code=400, detail=f"Missing required columns: {missing}")
            
        # Convert dates
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Replace NaNs with None for SQL insertion
        df = df.where(pd.notnull(df), None)
        
        incidents = []
        for _, row in df.iterrows():
            incidents.append(CrimeIncident(
                crime_id=str(row['crime_id']),
                date=row['date'],
                district=row.get('district'),
                crime_type=row.get('crime_type'),
                latitude=row.get('latitude'),
                longitude=row.get('longitude'),
                status=row.get('status'),
                repeat_offender=str(row.get('repeat_offender', 'False')),
                victim_age=row.get('victim_age'),
                offender_age=row.get('offender_age'),
                police_station=row.get('police_station')
            ))
            
        # Clear existing table to refresh data (since user wanted to feed everything from CSV)
        db.query(CrimeIncident).delete()
        
        # Bulk save
        db.bulk_save_objects(incidents)
        db.commit()
        
        return {"status": "success", "message": f"Successfully loaded {len(incidents)} incidents into the database."}
        
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="The uploaded CSV file is empty.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to process CSV: {str(e)}")

@router.get("/")
def get_incidents(db: Session = Depends(get_db), limit: int = 5000):
    """
    Returns the crime incidents from the PostgreSQL database.
    """
    incidents = db.query(CrimeIncident).order_by(CrimeIncident.date.desc()).limit(limit).all()
    
    # Format to match the previous CSV structure expected by frontend
    result = []
    for inc in incidents:
        result.append({
            "crime_id": inc.crime_id,
            "date": inc.date.isoformat() if inc.date else None,
            "district": inc.district,
            "crime_type": inc.crime_type,
            "latitude": inc.latitude,
            "longitude": inc.longitude,
            "status": inc.status,
            "repeat_offender": True if inc.repeat_offender and inc.repeat_offender.lower() in ('true', '1', 'yes', 't') else False,
            "victim_age": inc.victim_age,
            "offender_age": inc.offender_age,
            "police_station": inc.police_station
        })
        
    return result

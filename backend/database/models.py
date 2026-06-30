from sqlalchemy import Column, Integer, String, Float, DateTime, Date
from backend.database.connection import Base
from datetime import datetime

class CrimeIncident(Base):
    __tablename__ = "crime_incidents"

    id = Column(Integer, primary_key=True, index=True)
    crime_id = Column(String, unique=True, index=True)
    date = Column(DateTime)
    district = Column(String, index=True)
    crime_type = Column(String, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    status = Column(String)
    repeat_offender = Column(String)
    victim_age = Column(Integer, nullable=True)
    offender_age = Column(Integer, nullable=True)
    police_station = Column(String, nullable=True)

class OfficerProfile(Base):
    __tablename__ = "officer_profiles"

    id = Column(String, primary_key=True, index=True) # Supabase User UUID
    police_id = Column(String, unique=True, index=True)
    full_name = Column(String)
    designation = Column(String)
    access_level = Column(Integer)
    badge_number = Column(String, nullable=True)
    district = Column(String, nullable=True)
    police_station = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    joined_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class FIRRecord(Base):
    __tablename__ = "fir_records"

    id = Column(Integer, primary_key=True, index=True)
    raw_text = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    crime_description = Column(String, index=True)
    city = Column(String, index=True)
    victim_age = Column(Integer)
    risk_level_code = Column(Integer)
    risk_level_label = Column(String)
    probability_score = Column(Float)
    latitude = Column(Float)
    longitude = Column(Float)
    assigned_officer = Column(String, nullable=True)

class CaseDocument(Base):
    __tablename__ = "case_documents"

    id = Column(Integer, primary_key=True, index=True)
    fir_id = Column(Integer, index=True) # Foreign key equivalent logic
    filename = Column(String)
    file_path = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    uploaded_by = Column(String, nullable=True)

from backend.database.connection import engine
from sqlalchemy import text

# Safe migration: create tables and add missing columns without dropping data
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Schema creation warning: {e}")

# Run ALTER TABLE migrations for new columns (safe to run multiple times due to IF NOT EXISTS)
try:
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE fir_records ADD COLUMN IF NOT EXISTS assigned_officer VARCHAR"))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS case_documents (
                id SERIAL PRIMARY KEY,
                fir_id INTEGER,
                filename VARCHAR,
                file_path VARCHAR,
                uploaded_at TIMESTAMP DEFAULT NOW(),
                uploaded_by VARCHAR
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS officer_profiles (
                id VARCHAR PRIMARY KEY,
                police_id VARCHAR UNIQUE,
                full_name VARCHAR,
                designation VARCHAR,
                access_level INTEGER,
                badge_number VARCHAR,
                district VARCHAR,
                police_station VARCHAR,
                phone VARCHAR,
                joined_date DATE,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS crime_incidents (
                id SERIAL PRIMARY KEY,
                crime_id VARCHAR UNIQUE,
                date TIMESTAMP,
                district VARCHAR,
                crime_type VARCHAR,
                latitude FLOAT,
                longitude FLOAT,
                status VARCHAR,
                repeat_offender VARCHAR,
                victim_age INTEGER,
                offender_age INTEGER,
                police_station VARCHAR
            )
        """))
        conn.commit()
except Exception as e:
    print(f"Migration warning (non-fatal): {e}")


from sqlalchemy import Column, String, Integer, Float, Text
from sqlalchemy.orm import declarative_base

from connection import engine

Base = declarative_base()


class DistrictRiskScore(Base):
    __tablename__ = "district_risk_scores"

    district = Column(String, primary_key=True)
    crime_count = Column(Integer)
    repeat_offenders = Column(Integer)
    crime_score = Column(Float)
    offender_score = Column(Float)
    cri = Column(Float)
    risk_level = Column(String)


class CrimeHotspot(Base):
    __tablename__ = "crime_hotspots"

    cluster = Column(Integer, primary_key=True)
    crime_count = Column(Integer)


class DistrictAnomaly(Base):
    __tablename__ = "district_anomalies"

    district = Column(String, primary_key=True)
    anomaly_count = Column(Integer)


class PatrolPriority(Base):
    __tablename__ = "patrol_priority"

    district = Column(String, primary_key=True)
    cri = Column(Float)
    anomaly_count = Column(Integer)
    priority_score = Column(Float)
    patrol_rank = Column(Integer)
    recommendation = Column(Text)


Base.metadata.create_all(engine)

print("All database tables created successfully!")
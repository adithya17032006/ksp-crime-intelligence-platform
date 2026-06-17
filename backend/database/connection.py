from sqlalchemy import create_engine

DATABASE_URL = "sqlite:///database/crime_intelligence.db"

engine = create_engine(
    DATABASE_URL,
    echo=True
)
from fastapi import FastAPI

# Import routers
from routes.risk import router as risk_router
from routes.patrol import router as patrol_router
from routes.anomalies import router as anomaly_router
from routes.trends import router as trends_router
from routes.hotspots import router as hotspot_router
from routes.weekday_trends import router as weekday_router

# Create FastAPI app
app = FastAPI(
    title="KSP Crime Intelligence API",
    version="1.0",
    description="Backend APIs for Crime Risk Analysis, Hotspots, Anomalies, Patrol Recommendations, and Crime Trends"
)

# Register routers
app.include_router(risk_router)
app.include_router(patrol_router)
app.include_router(anomaly_router)
app.include_router(trends_router)
app.include_router(hotspot_router)
app.include_router(weekday_router)

# Home Endpoint
@app.get("/")
def home():
    return {
        "message": "KSP Crime Intelligence API Running",
        "version": "1.0",
        "status": "healthy"
    }

# Health Check Endpoint
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "KSP Crime Intelligence Backend"
    }
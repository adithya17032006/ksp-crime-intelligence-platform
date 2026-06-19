import os

# Base URL for the FastAPI Backend Services
# Defaults to local testing address, but can be overridden by environment variable for production
API_BASE_URL = os.getenv("KSP_API_BASE_URL", "http://127.0.0.1:8000")

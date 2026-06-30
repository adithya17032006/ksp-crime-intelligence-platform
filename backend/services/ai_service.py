import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

def extract_fir_features_with_gemini(text: str) -> dict:
    """Uses Gemini to extract structured JSON from unstructured casual FIR text."""
    if not API_KEY:
        raise ValueError("GEMINI_API_KEY is not set in the environment.")
    
    prompt = f"""
    Extract the following incident features from this unstructured FIR or casual report text. 
    Return strictly in valid JSON format, with no markdown formatting.
    
    Keys required:
    - timestamp: the date and time of the incident in 'YYYY-MM-DD HH:MM:SS' format. If no time is found, default to 12:00:00.
    - crime_description: one of [ASSAULT, BURGLARY, CYBERCRIME, FRAUD, HOMICIDE, IDENTITY THEFT, KIDNAPPING, PUBLIC INTOXICATION, ROBBERY, THEFT, TRAFFIC VIOLATION].
    - city: one of [AHMEDABAD, BAGALKOT, CHENNAI, GHAZIABAD, HASSAN, LUDHIANA, MUMBAI, PUNE]. If missing, default to HASSAN.
    - victim_age: integer representing the victim's age. Default to 35 if missing.

    Text:
    "{text}"
    """
    
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(prompt)
    
    # Clean the response to ensure valid JSON (remove markdown ticks if present)
    clean_resp = response.text.replace('```json', '').replace('```', '').strip()
    return json.loads(clean_resp)

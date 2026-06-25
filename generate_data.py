# generate_data.py
import random
import pandas as pd
from datetime import datetime, timedelta

def create_synthetic_csv(target_path="crime_dataset_india.csv", count=1000):
    """Generates synthetic baseline records for training and integration verification."""
    print(f"📦 Generating {count} mock records for testing...")
    cities = ['Ahmedabad', 'Chennai', 'Ludhiana', 'Pune', 'Ghaziabad', 'Mumbai', 'Hassan', 'Bagalkot']
    crimes = ['ASSAULT', 'BURGLARY', 'CYBERCRIME', 'FRAUD', 'HOMICIDE', 'IDENTITY THEFT', 'KIDNAPPING', 'PUBLIC INTOXICATION', 'ROBBERY', 'THEFT', 'TRAFFIC VIOLATION']
    
    start_date = datetime(2025, 1, 1)
    rows = []
    
    for idx in range(1, count + 1):
        offset = start_date + timedelta(days=random.randint(0, 400), hours=random.randint(0, 23))
        rows.append({
            "Report Number": 90000 + idx,
            "Date of Occurrence": offset.strftime('%d-%m-%Y'),
            "Time of Occurrence": offset.strftime('%d-%m-%Y %H:%M'),
            "City": random.choice(cities),
            "Crime Description": random.choice(crimes),
            "Victim Age": random.randint(18, 75)
        })
        
    pd.DataFrame(rows).to_csv(target_path, index=False)
    print(f"🚀 Synthetic data asset ready at: '{target_path}'")

if __name__ == "__main__":
    create_synthetic_csv()
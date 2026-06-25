# generate_data.py
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_mock_police_dataset(num_records=5000, output_filename="crime_dataset_india.csv"):
    """
    Generates a completely randomized dataset matching the exact structure
    and header definitions of the real 'crime_dataset_india.csv' asset.
    """
    print(f"🎲 Initializing standalone data generation matrix for {num_records} records...")
    
    # Secure exact seed for reproducible testing evaluations
    np.random.seed(42)
    
    # Domain categorical sets mapped explicitly to match pipeline expectations
    cities = ['Ahmedabad', 'Chennai', 'Ludhiana', 'Pune', 'Ghaziabad', 'Mumbai', 'Hassan', 'Bagalkot']
    crime_descriptions = [
        'IDENTITY THEFT', 'HOMICIDE', 'KIDNAPPING', 'BURGLARY', 
        'ROBBERY', 'THEFT', 'FRAUD', 'PUBLIC INTOXICATION', 
        'TRAFFIC VIOLATION', 'ASSAULT'
    ]
    genders = ['M', 'F', 'Other']
    weapons = ['None', 'Firearm', 'Knife', 'Blunt Object', 'Poison']
    domains = ['Violent Crime', 'Property Crime', 'Cyber Crime', 'White Collar Crime', 'Traffic Fatality', 'Other Crime']
    
    start_date = datetime(2024, 1, 1)
    
    # Initialize baseline structure map
    data = {
        'Report Number': range(100001, 100001 + num_records),
        'Date Reported': [],
        'Date of Occurrence': [],
        'Time of Occurrence': [],
        'City': np.random.choice(cities, size=num_records, p=[0.15, 0.15, 0.10, 0.15, 0.10, 0.15, 0.10, 0.10]),
        'Crime Code': np.random.randint(100, 600, size=num_records),
        'Crime Description': np.random.choice(crime_descriptions, size=num_records, p=[0.10, 0.05, 0.05, 0.15, 0.15, 0.20, 0.10, 0.05, 0.10, 0.05]),
        'Victim Age': np.random.randint(16, 75, size=num_records),
        'Victim Gender': np.random.choice(genders, size=num_records, p=[0.49, 0.49, 0.02]),
        'Weapon Used': np.random.choice(weapons, size=num_records),
        'Crime Domain': np.random.choice(domains, size=num_records),
        'Police Deployed': np.random.randint(2, 18, size=num_records),
        'Case Closed': np.random.choice(['Yes', 'No'], size=num_records, p=[0.65, 0.35]),
        'Date Case Closed': []
    }
    
    print("⏳ Reconstructing timestamps and situational event records...")
    # Loop to build correlated, realistic timestamps
    for i in range(num_records):
        # Stagger incidents throughout a 2-year window
        random_days = np.random.randint(0, 700)
        random_hours = np.random.randint(0, 24)
        random_minutes = np.random.randint(0, 60)
        
        occurrence_dt = start_date + timedelta(days=random_days, hours=random_hours, minutes=random_minutes)
        # Reporting happens shortly after or same day
        reported_dt = occurrence_dt + timedelta(days=np.random.randint(0, 3), hours=np.random.randint(1, 8))
        
        # Format strings cleanly to make sure pandas strings parse smoothly
        data['Date of Occurrence'].append(occurrence_dt.strftime('%d-%m-%Y %H:%M'))
        data['Time of Occurrence'].append(occurrence_dt.strftime('%d-%m-%Y %H:%M'))
        data['Date Reported'].append(reported_dt.strftime('%d-%m-%Y %H:%M'))
        
        # Calculate case resolution timestamp constraints if checked 'Yes'
        if data['Case Closed'][i] == 'Yes':
            resolution_dt = reported_dt + timedelta(days=np.random.randint(5, 120))
            data['Date Case Closed'].append(resolution_dt.strftime('%d-%m-%Y %H:%M'))
        else:
            data['Date Case Closed'].append('')
            
    # Compile dataframe block
    df = pd.DataFrame(data)
    
    # Save directly into your working folder space
    df.to_csv(output_filename, index=False)
    print(f"\n💾 Generation complete! File successfully generated.")
    print(f"👉 Absolute path destination: {os.path.abspath(output_filename)}")

if __name__ == "__main__":
    # You can change the 5000 value to any scale row size you require to stress-test your analytics
    generate_mock_police_dataset(num_records=5000, output_filename="crime_dataset_india.csv")
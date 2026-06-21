\# GIS \& Crime Intelligence Module



\## Overview



This module provides GIS-based crime analysis and machine learning-driven crime intelligence for the Karnataka State Police Datathon 2026.



The objective is to transform raw crime records into actionable intelligence through geospatial visualization, hotspot detection, crime risk assessment, and anomaly detection.



\---



\## Dataset



\*\*Source:\*\* Synthetic Karnataka Crime Dataset



\*\*Records:\*\* 10,000 Crime Incidents



\### Features



\* Crime ID

\* District

\* Police Station

\* Crime Type

\* Date

\* Latitude

\* Longitude

\* Victim Age

\* Offender Age

\* Status

\* Repeat Offender



\---



\## Module 1: Crime Heatmaps



\### Objective



Visualize crime concentration across Karnataka.



\### Tools Used



\* Python

\* Folium



\### Outputs



\* crime\_map.html

\* crime\_heatmap.html



\### Benefits



\* Geographic crime visualization

\* Identification of high-density crime regions

\* Improved situational awareness



\---



\## Module 2: Crime Risk Index (CRI)



\### Objective



Generate district-level crime risk scores.



\### Method



Risk scores are calculated using:



\* Crime Count

\* Repeat Offenders

\* Offender Severity Indicators



\### Outputs



\* crime\_risk\_scores.csv



\### Benefits



\* District risk ranking

\* Strategic planning

\* Resource allocation support



\---



\## Module 3: Crime Hotspot Detection



\### Objective



Identify spatial crime clusters.



\### Algorithm



DBSCAN (Density-Based Spatial Clustering)



\### Outputs



\* crime\_hotspots.csv

\* crime\_hotspots.html



\### Benefits



\* Automatic hotspot discovery

\* Patrol route optimization

\* High-risk area identification



\---



\## Module 4: Crime Prediction



\### Objective



Analyze crime patterns using machine learning.



\### Algorithm



Random Forest Classifier



\### Features Used



\* Location Features

\* Age Features

\* Police Station Information

\* Time Features



\### Benefits



\* Predictive analytics

\* Pattern discovery

\* Crime intelligence support



\---



\## Module 5: Crime Anomaly Detection



\### Objective



Detect unusual crime incidents.



\### Algorithm



Isolation Forest



\### Results



\* 9800 Normal Records

\* 200 Anomalous Records



\### Outputs



\* crime\_anomalies.csv

\* district\_anomalies.csv

\* crime\_anomalies.html



\### Benefits



\* Early warning system

\* Investigation prioritization

\* Detection of suspicious activity



\---
## Module 6: Feature Importance Analysis

### Objective

Identify the most influential factors contributing to crime prediction outcomes.

### Method

Random Forest Feature Importance Analysis

### Key Findings

Top contributing features include:

* Longitude
* Latitude
* Victim Age
* Offender Age
* Police Station

### Benefits

* Improved model interpretability
* Better understanding of crime drivers
* Support for data-driven policing strategies

---

## Module 7: Patrol Recommendation System

### Objective

Provide district-level patrol prioritization based on crime intelligence indicators.

### Inputs

* Crime Risk Index (CRI)
* District Anomaly Counts

### Outputs

* district_patrol_priority.csv

### Benefits

* Patrol prioritization
* Resource allocation support
* Operational planning assistance

---

## Module 8: Temporal Crime Intelligence

### Objective

Analyze crime occurrence patterns over time.

### Analysis Performed

* Monthly Crime Trends
* Weekday Crime Trends
* Crime Frequency Distribution

### Outputs

* monthly_crime_trends.csv
* weekday_crime_trends.csv

### Benefits

* Patrol scheduling support
* Seasonal crime monitoring
* Temporal pattern identification



\## Technology Stack



\### Programming



\* Python



\### Data Processing



\* Pandas

\* NumPy



\### GIS Visualization



\* Folium



\### Machine Learning



\* Scikit-Learn

\* DBSCAN

\* Random Forest

\* Isolation Forest



\### Tools



\* Jupyter Notebook

\* GitHub

\* Anaconda



\---



## Achievements

* Crime Heatmap Generation
* District-Level Crime Risk Index
* DBSCAN Hotspot Detection
* Random Forest Crime Prediction
* Isolation Forest Anomaly Detection
* Feature Importance Analysis
* Patrol Recommendation System
* Temporal Crime Intelligence
* Interactive GIS Maps
* Crime Intelligence Datasets




\---
## Future Improvements

* Real-Time Crime Monitoring
* Dashboard Integration
* Predictive Crime Forecasting
* Patrol Route Optimization
* Criminal Network Analysis
* Explainable AI (SHAP/LIME)
* Real-Time Alert Generation
* Integration with Official KSP Datasets







\---



\## Contributor



\*\*Adithya H S\*\*



GIS \& Crime Intelligence Developer



Karnataka State Police Datathon 2026




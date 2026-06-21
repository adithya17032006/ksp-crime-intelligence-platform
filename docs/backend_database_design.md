# KSP Crime Intelligence Platform Database Design

## 1. crime_records

Stores raw crime incidents.

| Column          | Type                    |
| --------------- | ----------------------- |
| crime_id        | VARCHAR(20) PRIMARY KEY |
| district        | VARCHAR(100)            |
| police_station  | VARCHAR(100)            |
| crime_type      | VARCHAR(100)            |
| date            | DATE                    |
| latitude        | FLOAT                   |
| longitude       | FLOAT                   |
| victim_age      | INTEGER                 |
| offender_age    | INTEGER                 |
| status          | VARCHAR(50)             |
| repeat_offender | BOOLEAN                 |

---

## 2. district_risk_scores

Stores Crime Risk Index results.

| Column           | Type                     |
| ---------------- | ------------------------ |
| district         | VARCHAR(100) PRIMARY KEY |
| crime_count      | INTEGER                  |
| repeat_offenders | INTEGER                  |
| crime_score      | FLOAT                    |
| offender_score   | FLOAT                    |
| cri              | FLOAT                    |
| risk_level       | VARCHAR(50)              |

---

## 3. crime_hotspots

Stores hotspot detection results.

| Column      | Type    |
| ----------- | ------- |
| cluster     | INTEGER |
| crime_count | INTEGER |

---

## 4. district_anomalies

Stores anomaly detection summary.

| Column        | Type                     |
| ------------- | ------------------------ |
| district      | VARCHAR(100) PRIMARY KEY |
| anomaly_count | INTEGER                  |

---

## 5. patrol_priority

Stores patrol recommendations.

| Column         | Type                     |
| -------------- | ------------------------ |
| district       | VARCHAR(100) PRIMARY KEY |
| cri            | FLOAT                    |
| anomaly_count  | INTEGER                  |
| priority_score | FLOAT                    |
| patrol_rank    | INTEGER                  |
| recommendation | TEXT                     |

---

## Future Tables

### feature_importance

Stores ML explainability outputs.

### prediction_logs

Stores future prediction requests and responses.

### users

Stores dashboard login accounts.

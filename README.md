# 🌍 EnviroScan: AI-Powered Pollution Source Identifier

EnviroScan is an AI-driven decision-support system that predicts the **dominant source of air pollution** at a location (industrial, vehicular, agricultural burning, residential burning, or natural) using ambient air-quality data, weather conditions, and geospatial context. [file:649] It helps authorities and urban planners move from basic concentration monitoring to **actionable, source-aware insights** for targeted interventions. [file:648]

---

## 📌 Project Overview

Traditional monitoring networks report pollutant levels (PM2.5, PM10, NO₂, SO₂, etc.) but rarely indicate *why* the air is polluted at a given time and place. EnviroScan combines: [file:649]

- Historical and live air-quality measurements  
- Weather parameters such as temperature, humidity, and pressure  
- Geospatial features from OpenStreetMap (roads, industries, agricultural fields, dump sites, and distances to them)  

A trained machine learning model uses these inputs to predict the **dominant pollution source**, visualize hotspots on a map, and support alerting and reporting workflows. [file:647][file:649]

---

## 📂 Project Structure

```text
EnviroScan/
├── app.py                          # Main Streamlit dashboard for predictions & visualization
├── EnviroScan/Air-Quality-Dataset-2021-2023_with_preds.csv  # Cleaned data used for model
├── enviro_scan_pollution_map.html  # Pre-rendered geospatial pollution map for embedding
├── .gitignore                      # Ignore venv, cache, large/raw data, etc.
├── requirements.txt                # Python dependencies
├── data/
│   ├── Air Quality Dataset 2021-2023.xlsx  # Raw AQ, weather, and OSM CSVs
│   └── Air Quality Dataset 2021-2023.csv   # Cleaned & feature-engineered datasets
|   └── Air_Quality_with_OSM_Features_5KM.xlsx
|   └── Data Extraction code for Physical features with in 5 km radius .ipynb
├── model/
│   ├── xgb_pollution_source.joblib # Trained XGBoost classifier
│   └── label_encoder.joblib        # Encoder for dominant source labels
├── notebooks/
│   └── EnviroScan-AI-Powered-Pollution-Source-Identifier-using-Geospatial-Analytics.ipynb
│                                   # EDA, feature engineering, and model training
├── reports/
│   ├── AI-EnviroScan-1.pdf         # Project report
│   └── EnviroScan-*.pptx           # Presentation slides
├── requirements.txt                # Python dependencies
└── README.md                       # Project overview (this file)
```

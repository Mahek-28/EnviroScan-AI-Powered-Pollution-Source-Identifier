# 🌍 EnviroScan: AI-Powered Pollution Source Identifier

EnviroScan is an AI-driven decision-support system that predicts the **dominant source of air pollution** at a location (industrial, vehicular, agricultural burning, residential burning, or natural) using ambient air-quality data, weather conditions, and geospatial context. It helps authorities and urban planners move from basic concentration monitoring to **actionable, source-aware insights** for targeted interventions.

---

## 📌 Project Overview

Traditional monitoring networks report pollutant levels (PM2.5, PM10, NO₂, SO₂, etc.) but rarely indicate *why* the air is polluted at a given time and place. EnviroScan combines: 

- Historical and live air-quality measurements  
- Weather parameters such as temperature, humidity, and pressure  
- Geospatial features from OpenStreetMap (roads, industries, agricultural fields, dump sites, and distances to them)  

A trained machine learning model uses these inputs to predict the **dominant pollution source**, visualize hotspots on a map, and support alerting and reporting workflows. 

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
---

## ✨ Key Features
### Source classification
- Predicts the dominant pollution source class for each record using an XGBoost classifier trained on air-quality, weather, and OSM-based features. 

### Geospatial hotspot mapping
- Embeds an interactive pollution map (EnviroScan/enviro_scan_pollution_map.html) to explore spatial patterns, hotspots, and source risk across locations. 

### Real-time data integration
- Fetches live pollution and weather data from the OpenWeather Air Pollution and Current Weather APIs given coordinates or city selections. 

### Interactive Streamlit dashboard
- Offers city selection, coordinate input, or location search, visual summaries (metrics, bar charts, gauges, radar charts, pies), and alert messages based on AQI. 

### Threshold-based alerts
- Displays GOOD / MODERATE / UNHEALTHY alert banners depending on the predicted or live AQI value. 
### Automated reporting
- Exports CSV, Excel, and PDF reports with charts (bar, pie, radar, gauge) and key metrics using Plotly and FPDF.
  
---

## 🧠 Machine Learning Approach
### Target variable:
- Dominant source – categorical label representing the most likely pollution source for each observation. 

### Input features (examples): 

- Air-quality metrics: SO2, NO2, PM10, PM2.5, AQI.

- Weather variables: Temperature C, Humidity, Pressure hPa.

- Geospatial / OSM features: distances (distnearestroadm, distnearestindm, distnearestdumpm, distnearestagrim).

### Model pipeline:

- Preprocessing: handling missing values, cleaning pollutant and AQI fields, feature engineering, scaling/encoding where required. 

- Model: XGBoost classifier trained on the processed dataset and saved as xgb_pollution_source.joblib. 

- Label encoder: maps numeric class indices back to human-readable source labels and is stored as label_encoder.joblib. 

### Predictions in the app:

- Builds a feature vector from live API data or historical records.

- Returns predicted label, confidence score (max class probability), and full probability distribution for visualization and PDF export.

---

## 🛠️ Tech Stack
- Language: Python

- Core libraries: pandas, numpy, scikit-learn, xgboost, joblib

- Visualization: matplotlib, seaborn, plotly

- Geospatial & maps: geopandas, osmnx, folium

- Web app: streamlit (main app in app.py)

- APIs & I/O: requests, openpyxl, fpdf2, io utilities

- Data sources: CPCB/air-quality datasets and OpenStreetMap-derived geospatial layers.

---

## 📦 Installation and Setup
### 1️⃣ Clone the Repository
```bash
git clone https://github.com/ryadavnitb/Batch-6.git
cd Batch-6

# Switch to your branch
git checkout Mahek

# Go into the EnviroScan project folder
cd EnviroScan
```
### 2️⃣ Create and Activate Virtual Environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```
### 3️⃣ Install Python Dependencies
```bash
pip install -r requirements.txt
```
This installs all required packages for the notebook and app.py (Streamlit, XGBoost, geospatial libs, Plotly, FPDF, etc.).
### 4️⃣ Configure OpenWeather API Key
In app.py, set your OpenWeather key:
- OPENWEATHER_API_KEY = "PUT_YOUR_KEY_HERE"
### 5️⃣ Run the EnviroScan Dashboard
```bash
streamlit run app.py
```
- Then open the URL shown in the terminal (usually http://localhost:8501) to use the EnviroScan app.
---
### From the UI you can:

- Select a city, enter coordinates, or search a location.

- Fetch live pollution and weather features for that point.

- Get the predicted dominant pollution source with confidence.

- View visual summaries (metrics, bar charts, gauge, radar, pie, trends).

- Explore the embedded geospatial pollution map.

- Download CSV, Excel, and PDF reports for the selected city or live location.

---

## 📈 Future Enhancements

- Integrate continuous streaming of sensor data instead of on-demand API calls.

- Add SHAP or similar explainability tools directly into the dashboard for per-prediction explanations.

- Containerize the application with Docker for smoother deployment.

- Extend the model to more cities, pollutants, and finer-grained source categories.

---

## 👥 Credits

This project was developed as part of the **Infosys Springboard** project.  
- **Project Title:** EnviroScan: AI-Powered Pollution Source Identifier  
- **Author:** Mahek Rana  
- **Platform:** Infosys Springboard – Data Science / AI Project Track  

---

## 📜 License

This project is licensed under the **MIT License**.  
See the `LICENSE` file in this repository for full license text.


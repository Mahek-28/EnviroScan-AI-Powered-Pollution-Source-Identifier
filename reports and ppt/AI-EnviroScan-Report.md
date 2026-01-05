```
EnviroScan is an AI-powered system that identifies the dominant source of air pollution (Agricultural, Burning, Industrial, Natural, Vehicular) using air-quality, weather, and geospatial features, and serves the results through an interactive Streamlit dashboard.
​

1. Project Objective
The project aims to go beyond traditional AQI reporting by predicting which source is most responsible for observed pollution at each monitoring location and time.
​
By combining CPCB air-quality data, weather parameters, and OSM-based proximity features (roads, industries, agricultural fields, dump sites), EnviroScan supports targeted interventions, hotspot analysis, and automated reporting for planners and authorities.
​

2. Data & Feature Engineering
Air-quality data: 2021–2023 CPCB dataset with pollutants such as SO₂, NO₂, PM₁₀, PM₂.₅, AQI and AQI category for Indian cities.
​

Weather data: Temperature, humidity, pressure, wind speed, wind direction, and weather condition merged with each record.
​

Geospatial features: Road counts, industrial-zone counts, dump-site and agricultural-field counts, urban density, industrial presence, pollution risk score, and distances to nearest road, industry, dump site, and agricultural area derived from OpenStreetMap.
​

Missing values in pollutants and AQI indices are cleaned using median imputation, and additional features such as green-area ratio and standardized numerical variables are created to stabilize model training.
​

3. Machine Learning Model Performance
A multi-class XGBoost classifier is trained to predict the dominant pollution source label using the engineered feature set.
​

Overall accuracy: ≈ 0.985 on the test set.
​

Macro-average F1-score: ≈ 0.98, indicating strong performance across all five classes.
​

Class-wise F1-scores are high: Agricultural 0.95, Burning 0.97, Industrial 1.00, Natural 0.99, Vehicular 1.00, with very few misclassifications in the confusion matrix.
​

The confusion matrix shows that almost all samples fall on the diagonal, with only a couple of Natural cases misclassified and virtually no confusion between Industrial, Vehicular, and other classes.
​

4. System Architecture & Workflow
The solution follows a modular data-to-decision pipeline:
​

Data ingestion:

OpenAQ / AQ datasets → PM₂.₅, PM₁₀, NO₂, SO₂ and AQI.

Weather API → temperature, humidity, wind, pressure.

OSM / geospatial extraction → nearby roads, industries, land use and distance metrics.

Feature unification: All streams are merged into a unified feature dataframe + labels, producing model-ready records.
​

Model layer: XGBoost model predicts the dominant pollution source for each feature vector.
​

Application layer: The EnviroScan Streamlit dashboard consumes the trained model to provide live predictions, heatmaps, alerts, and downloadable reports.
​

5. EnviroScan Dashboard Functionality
The Streamlit app (app.py) offers a dark-themed, card-based UI for interactive analysis.
​

Location input modes:

Select a city from the historical dataset.

Enter latitude/longitude manually.

Search by location name.
​

Live data fetching: For any selected point, the app calls OpenWeather’s Air Pollution and Current Weather APIs to obtain live pollutants and meteorology, and uses OSMnx to compute distance to nearest road (and placeholders for other distances).
​

Real-time alerts & summary:

A status banner classifies current AQI as GOOD, MODERATE, UNHEALTHY FOR SENSITIVE GROUPS, or UNHEALTHY.
​

Summary cards display dominant source, confidence, PM₂.₅, current AQI, number of stations analysed, and data source type (live/hybrid).
​

Visual analytics:

Bar chart of Key Pollutants (PM₂.₅, PM₁₀, NO₂, SO₂).
​

Bar chart of Source probabilities for all classes.
​

AQI gauge and polar radar chart tracking pollutant mix for the live location.
​

AQI trend line by year plus a pie chart of pollutant contribution.
​

Embedded geospatial pollution map (enviro_scan_pollution_map.html) showing hot spots and source risk on a map.
​

Reporting: Users can export data for the selected city/location to CSV, Excel, or a multi-page PDF report that includes KPIs and the generated charts.
​

6. Conclusion
EnviroScan demonstrates that combining geospatial analytics, weather information, and machine learning can accurately attribute pollution to specific source categories, with around 98–99% test accuracy across five classes.
​
The integrated dashboard turns these predictions into an operational tool that surfaces live alerts, interactive maps, and rich reports, making it suitable for city administrators, environmental agencies, and academic analysis.
```

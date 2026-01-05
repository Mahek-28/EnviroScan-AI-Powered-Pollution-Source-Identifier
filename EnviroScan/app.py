import streamlit as st
import pandas as pd
from joblib import load
import streamlit.components.v1 as components
import plotly.express as px
from io import BytesIO
from fpdf import FPDF
import requests
import numpy as np
import osmnx as ox
import plotly.graph_objects as go
import io


# ==========================
# OpenWeather configuration
# ==========================
OPENWEATHER_API_KEY = "Your OPEN WEATHER API KEY"  # <- put your key here
OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
OPENWEATHER_AIR_URL = "https://api.openweathermap.org/data/2.5/air_pollution"  # [web:454]

print("DEBUG OPENWEATHER_API_KEY:", OPENWEATHER_API_KEY)


# ==========================
# Live data helpers
# ==========================
def fetch_air_quality_from_api(lat: float, lon: float):
    """Live pollutants + AQI from OpenWeather Air Pollution API."""
    params = {"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY}
    r = requests.get(OPENWEATHER_AIR_URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()

    lst = data.get("list", [])
    if not lst:
        return {"SO2": np.nan, "NO2": np.nan, "PM2.5": np.nan, "PM10": np.nan, "AQI": np.nan}

    comp = lst[0].get("components", {})
    so2 = float(comp.get("so2", np.nan))
    no2 = float(comp.get("no2", np.nan))
    pm25 = float(comp.get("pm2_5", np.nan))
    pm10 = float(comp.get("pm10", np.nan))
    aqi_index = lst[0].get("main", {}).get("aqi", np.nan)  # 1–5 index [web:454]

    return {"SO2": so2, "NO2": no2, "PM2.5": pm25, "PM10": pm10, "AQI": float(aqi_index)}


def fetch_weather_from_api(lat: float, lon: float):
    """Live temperature, humidity, pressure from current weather API."""
    params = {"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY, "units": "metric"}  # [web:370][web:373]
    r = requests.get(OPENWEATHER_URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    main = data.get("main", {})
    temp_c = float(main.get("temp", np.nan))
    humidity = float(main.get("humidity", np.nan))
    pressure = float(main.get("pressure", np.nan))
    return {"Temperature (°C)": temp_c, "Humidity (%)": humidity, "Pressure (hPa)": pressure}


def fetch_osm_distances(lat: float, lon: float, dist_m: int = 3000):
    """Distance to nearest road using OSMnx drive network."""
    G = ox.graph_from_point((lat, lon), dist=dist_m, network_type="drive", simplify=True)
    _, d_road = ox.distance.nearest_edges(G, X=[lon], Y=[lat], return_dist=True)  # [web:368][web:380]
    dist_nearest_road_m = float(d_road[0])

    dist_nearest_ind_m = np.nan
    dist_nearest_dump_m = np.nan
    dist_nearest_agri_m = np.nan

    return {
        "dist_nearest_road_m": dist_nearest_road_m,
        "dist_nearest_ind_m": dist_nearest_ind_m,
        "dist_nearest_dump_m": dist_nearest_dump_m,
        "dist_nearest_agri_m": dist_nearest_agri_m,
    }


def get_live_features_for_coordinates(lat: float, lon: float):
    aq = fetch_air_quality_from_api(lat, lon)
    wx = fetch_weather_from_api(lat, lon)
    osm = fetch_osm_distances(lat, lon)
    feats = {**aq, **wx, **osm}
    return feats


# ======================================
# 1. Page config + dark theme styling
# ======================================
st.set_page_config(page_title="EnviroScan Dashboard", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background-color: #050816; color: #e5e7eb; }
    .main { padding-top: 0.5rem; padding-left: 2rem; padding-right: 2rem; }

    section[data-testid="stSidebar"] {
        background: radial-gradient(circle at top left, #020617, #00010a);
        color: #e5e7eb;
        border-right: 1px solid #111827;
        border-top: 1px solid #111827;
    }
    section[data-testid="stSidebar"] * {
        font-family: "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 0.9rem;
        color: #e5e7eb !important;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #f9fafb !important;
        font-weight: 700;
    }
    section[data-testid="stSidebar"] h2::before { content: "• "; color: #22c55e; }

    div[data-baseweb="input"] {
        background-color: #ffffff !important;
        border-radius: 0.7rem;
        border: 1px solid #cbd5f5;
        color: #0f172a !important;
    }
    div[data-baseweb="input"] input { color: #0f172a !important; font-weight: 500; }
    div[data-baseweb="input"] svg { color: #0f172a !important; }

    div[data-baseweb="select"] {
        background-color: #ffffff !important;
        border-radius: 0.7rem;
        border: 1px solid #cbd5f5;
        box-shadow: 0 0 0 1px rgba(15,23,42,0.08);
    }
    div[data-baseweb="select"] div[role="button"] span {
        color: #0f172a !important;
        font-weight: 500;
    }
    div[data-baseweb="select"] svg { color: #0f172a !important; }
    ul[role="listbox"] {
        background-color: #020617 !important;
        border: 1px solid #1f2937 !important;
    }
    ul[role="listbox"] li { color: #e5e7eb !important; font-size: 0.9rem; }
    ul[role="listbox"] li:hover { background-color: #1e293b !important; }

    div[role="radiogroup"] label { color: #e5e7eb !important; font-weight: 500; }

    .stSlider > div[data-baseweb="slider"] > div > div { background: #111827 !important; }
    .stSlider [data-baseweb="slider"] div[role="slider"] {
        background-color: #22c55e !important;
        box-shadow: 0 0 0 3px rgba(34,197,94,.4);
    }
    .stSlider span[data-testid="stSliderValue"],
    .stSlider span[data-testid="stTickBarMin"],
    .stSlider span[data-testid="stTickBarMax"] {
        color: #f9fafb !important;
        font-weight: 600;
    }
    .stSlider label { color: #e5e7eb !important; }

    .env-card {
        background: radial-gradient(circle at top left, #111827, #020617);
        border-radius: 0.75rem;
        padding: 0.75rem 1rem;
        border: 1px solid #1f2937;
        box-shadow: 0 10px 25px rgba(0,0,0,0.7);
        margin-bottom: 0.75rem;
    }
    .env-card h3 { margin-top: 0; font-size: 1rem; }
    .env-card, .env-card * { color: #e5e7eb !important; }

    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #020617, #111827);
        border-radius: 0.75rem;
        padding: 0.5rem 0.75rem;
        border: 1px solid #1e293b;
    }
    [data-testid="stMetric"] > div { color: #e5e7eb; }

    .stButton button {
        border-radius: 999px;
        border: 1px solid #22c55e;
        background: linear-gradient(90deg, #16a34a, #22c55e);
        color: white;
        font-weight: 600;
    }
    .stButton button:hover {
        background: linear-gradient(90deg, #22c55e, #4ade80);
        border-color: #4ade80;
    }

    .stDownloadButton button {
        color: #e5e7eb !important;
        background: #0f172a;
        border-radius: 999px;
        border: 1px solid #22c55e;
    }
    .stDownloadButton button:hover {
        background: #16a34a;
        border-color: #4ade80;
        color: #f9fafb !important;
    }

    .stAlert { border-radius: 0.75rem; padding: 0.5rem 0.75rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ======================================
# 2. Load data, model, label encoder
# ======================================
@st.cache_data
def load_data():
    return pd.read_csv("Air-Quality-Dataset-2021-2023_with_preds.csv")


@st.cache_resource
def load_model():
    return load("xgb_pollution_source.joblib")


@st.cache_resource
def load_label_encoder():
    return load("label_encoder.joblib")


df = load_data()
model = load_model()
label_encoder = load_label_encoder()

feature_cols = [
    "SO2", "NO2", "PM2.5", "PM10", "AQI",
    "Temperature (°C)", "Humidity (%)", "Pressure (hPa)",
    "dist_nearest_road_m", "dist_nearest_ind_m",
    "dist_nearest_dump_m", "dist_nearest_agri_m",
]


# ======================================
# 3. Header + status banner
# ======================================
st.title("🌍 EnviroScan – AI‑Powered Pollution Source Identifier")
st.markdown(
    "EnviroScan uses air quality, weather, and geospatial distance features "
    "to predict the dominant pollution source at a selected location."
)

st.markdown(
    """
    <div class="env-card" style="padding:0.4rem 0.8rem;
         background:linear-gradient(90deg,#16a34a,#166534);
         color:#ecfdf5; font-size:0.9rem;">
         ✅ Data fetched from historical EnviroScan dataset and Live APIs | Last updated: 2023‑12‑31
    </div>
    """,
    unsafe_allow_html=True,
)


# ======================================
# Helper: historical features by nearest station
# ======================================
def get_features_for_location(lat, lon):
    d2 = (df["Latitude"] - lat) ** 2 + (df["Longitude"] - lon) ** 2
    base = df.loc[d2.idxmin()]

    feats = {
        "SO2": float(base["SO2"]),
        "NO2": float(base["NO2"]),
        "PM2.5": float(base["PM2.5"]),
        "PM10": float(base["PM10"]),
        "AQI": float(base["AQI"]),
        "Temperature (°C)": float(base["Temperature (°C)"]),
        "Humidity (%)": float(base["Humidity (%)"]),
        "Pressure (hPa)": float(base["Pressure (hPa)"]),
        "dist_nearest_road_m": float(base["dist_nearest_road_m"]),
        "dist_nearest_ind_m": float(base["dist_nearest_ind_m"]),
        "dist_nearest_dump_m": float(base["dist_nearest_dump_m"]),
        "dist_nearest_agri_m": float(base["dist_nearest_agri_m"]),
    }
    return feats, base


def predict_and_decode(feats_dict):
    X_live = pd.DataFrame([feats_dict], columns=feature_cols)
    proba = model.predict_proba(X_live)[0]
    y_encoded = int(model.predict(X_live)[0])
    label = label_encoder.inverse_transform([y_encoded])[0]
    conf = float(proba[y_encoded])
    return label, conf, proba


# ======================================
# 4. Sidebar – location selection
# ======================================
st.sidebar.header("Location Selection")

mode = st.sidebar.radio(
    "Select input method:",
    ["Choose City", "Enter Coordinates", "Search Location"],
)

# ======================================
# 5. Location context
# ======================================
ref_row = None
df_city = None
aqi_live = None

y_label = None
confidence = None
y_proba = None
feats = None

# ---------- Mode 1: Choose City ----------
if mode == "Choose City":
    city_live = st.sidebar.selectbox(
        "Select a city",
        sorted(df["City / town / village"].dropna().unique().tolist()),
    )
    df_city = df[df["City / town / village"] == city_live]

    if not df_city.empty:
        # use mean coordinates of the city as target point
        lat_city = df_city["Latitude"].mean()
        lon_city = df_city["Longitude"].mean()

        try:
            feats = get_live_features_for_coordinates(lat_city, lon_city)
        except Exception as e:
            st.error(f"Failed to fetch live data: {e}")
            st.stop()

        aqi_live = feats["AQI"]
        y_label, confidence, y_proba = predict_and_decode(feats)

        # choose a representative historical row for context
        ref_row = df_city.sort_values("AQI", ascending=False).iloc[0]

# ---------- Mode 2: Enter Coordinates ----------
elif mode == "Enter Coordinates":
    lat_live = st.sidebar.number_input("Latitude", value=float(df["Latitude"].mean()))
    lon_live = st.sidebar.number_input("Longitude", value=float(df["Longitude"].mean()))

    if st.sidebar.button("📡 Fetch Air Quality Data"):
        try:
            feats = get_live_features_for_coordinates(lat_live, lon_live)
        except Exception as e:
            st.error(f"Failed to fetch live data: {e}")
            st.stop()

        st.markdown("### 🌦 Live pollution and weather inputs")
        col1, col2 = st.columns(2)
        with col1:
            feats["PM2.5"] = st.number_input(
                "PM2.5 (µg/m³)", value=float(feats["PM2.5"]), min_value=0.0
            )
            feats["PM10"] = st.number_input(
                "PM10 (µg/m³)", value=float(feats["PM10"]), min_value=0.0
            )
            feats["SO2"] = st.number_input(
                "SO2 (µg/m³)", value=float(feats["SO2"]), min_value=0.0
            )
        with col2:
            feats["NO2"] = st.number_input(
                "NO2 (µg/m³)", value=float(feats["NO2"]), min_value=0.0
            )
            feats["Temperature (°C)"] = st.number_input(
                "Temperature (°C)", value=float(feats["Temperature (°C)"])
            )
            feats["Humidity (%)"] = st.number_input(
                "Humidity (%)", value=float(feats["Humidity (%)"])
            )
            feats["AQI"] = st.number_input(
                "AQI", value=float(feats["AQI"]), min_value=0.0
            )

        aqi_live = feats["AQI"]
        y_label, confidence, y_proba = predict_and_decode(feats)

        # synthetic city for live location so trend/pie work
        df_city = pd.DataFrame(
            [
                {
                    "Year": pd.Timestamp.now().year,
                    "AQI": aqi_live,
                    "Dominant_source": y_label,
                    "City / town / village": "Live location",
                }
            ]
        )
        ref_row = df_city.iloc[0]

# ---------- Mode 3: Search Location ----------
elif mode == "Search Location":
    search_text = st.sidebar.text_input("Search location name")
    if search_text:
        df_match = df[df["Location"].str.contains(search_text, case=False, na=False)]
        if not df_match.empty:
            ref_row = df_match.iloc[0]
            df_city = df[df["City / town / village"] == ref_row["City / town / village"]]

            lat_loc = float(ref_row["Latitude"])
            lon_loc = float(ref_row["Longitude"])

            try:
                feats = get_live_features_for_coordinates(lat_loc, lon_loc)
            except Exception as e:
                st.error(f"Failed to fetch live data: {e}")
                st.stop()

            aqi_live = feats["AQI"]
            y_label, confidence, y_proba = predict_and_decode(feats)

# ======================================
# 6. Real-time alerts (card)
# ======================================
st.markdown('<div class="env-card">', unsafe_allow_html=True)
st.markdown("### 🚨 Real-Time Alerts")

if aqi_live is not None:
    aqi_val = aqi_live
    if aqi_val <= 50:
        st.success("Air Quality Status: GOOD – All pollutant levels are within safe limits.")
    elif aqi_val <= 100:
        st.info("Air Quality Status: MODERATE – Sensitive groups should take care.")
    elif aqi_val <= 200:
        st.warning("Air Quality Status: UNHEALTHY FOR SENSITIVE GROUPS.")
    else:
        st.error("Air Quality Status: UNHEALTHY – Avoid outdoor exposure.")
else:
    st.info("Select a location to see real-time alerts.")
st.markdown('</div>', unsafe_allow_html=True)

# ======================================
# 7. Air Quality Summary (metrics + charts)
# ======================================
if y_label is not None and feats is not None:
    st.markdown('<div class="env-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Air Quality Summary")

    c1, c2, c3, c4, c5 = st.columns([1.3, 1, 1, 1, 1])

    with c1:
        st.markdown("**🚗 Dominant Source**")
        st.metric("", y_label, f"{confidence*100:.1f}% confidence")

    with c2:
        st.markdown("**🌫 PM2.5 (µg/m³)**")
        st.metric("", f"{feats['PM2.5']:.1f}", "concentration")

    with c3:
        st.markdown("**📈 AQI (current)**")
        st.metric("", f"{aqi_live:.1f}" if aqi_live is not None else "N/A")

    with c4:
        stations = len(df_city) if df_city is not None and not df_city.empty else len(df)
        st.markdown("**📡 Stations**")
        st.metric("", str(stations), "analyzed")

    with c5:
        st.markdown("**🛰 Data Source**")
        st.metric("", "Live APIs + EnviroScan", "hybrid")

    st.markdown("#### 🧪 Key Pollutants")
    pol_df = pd.DataFrame(
        {
            "Pollutant": ["PM2.5", "PM10", "NO2", "SO2"],
            "Value": [feats["PM2.5"], feats["PM10"], feats["NO2"], feats["SO2"]],
        }
    )
    pol_fig = px.bar(pol_df, x="Pollutant", y="Value", color="Pollutant", height=220)
    pol_fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.8)",
        font_color="#e5e7eb",
    )
    st.plotly_chart(pol_fig, use_container_width=True)

    st.markdown("#### 🎯 Source probabilities")
    class_labels = label_encoder.inverse_transform(model.classes_.astype(int))
    prob_fig = px.bar(
        x=class_labels,
        y=y_proba,
        labels={"x": "Source", "y": "Probability"},
        height=260,
    )
    prob_fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.8)",
        font_color="#e5e7eb",
    )
    st.plotly_chart(prob_fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ======================================
# 8. Trend chart & source mix (card)
# ======================================
st.markdown('<div class="env-card">', unsafe_allow_html=True)
st.markdown("### 📉 AQI Trend & Source Mix")

left, right = st.columns(2)

with left:
    if df_city is not None and not df_city.empty and "Year" in df_city.columns:
        trend = df_city.groupby("Year")["AQI"].mean().sort_index()
        trend_df = trend.reset_index()
        trend_fig = px.line(
            trend_df, x="Year", y="AQI", markers=True, title="Average AQI by year"
        )
        trend_fig.update_layout(
            margin=dict(l=10, r=10, t=40, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15,23,42,0.8)",
            font_color="#e5e7eb",
            xaxis_title="Year",
            yaxis_title="AQI",
        )
        trend_fig.update_traces(line=dict(color="#22c55e", width=3))
        st.plotly_chart(trend_fig, use_container_width=True)
    else:
        st.info("Trend chart will appear after selecting a city/location with data.")

with right:
    if feats is not None:
        # Live pollutant contribution pie
        pol_pie_df = pd.DataFrame(
            {
                "Pollutant": ["PM2.5", "PM10", "NO2", "SO2"],
                "Value": [
                    float(feats["PM2.5"]),
                    float(feats["PM10"]),
                    float(feats["NO2"]),
                    float(feats["SO2"]),
                ],
            }
        )

        pie_fig = px.pie(
            pol_pie_df,
            names="Pollutant",
            values="Value",
            title="Live pollutant contribution",
            hole=0.35,
        )
        pie_fig.update_traces(textposition="inside", textinfo="percent+label")
        pie_fig.update_layout(
            margin=dict(l=10, r=10, t=40, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15,23,42,0.8)",
            font_color="#e5e7eb",
        )
        st.plotly_chart(pie_fig, use_container_width=True)
    else:
        st.info("Pollutant contribution will appear after you run a live prediction.")


st.markdown('</div>', unsafe_allow_html=True)

# ======================================
# 6b. Live AQI Gauge & Pollutant Radar
# ======================================
if aqi_live is not None and feats is not None:
    st.markdown('<div class="env-card">', unsafe_allow_html=True)
    st.markdown("### 🎨 Live AQI & Pollutant Radar")

    col_left, col_right = st.columns(2)

    # ----- Left: colorful AQI gauge -----
    with col_left:
        fig_gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=float(aqi_live),
                title={"text": "AQI"},
                gauge={
                    "axis": {"range": [0, 500]},
                    "bar": {"color": "#22c55e"},
                    "steps": [
                        {"range": [0, 50], "color": "#16a34a"},
                        {"range": [51, 100], "color": "#84cc16"},
                        {"range": [101, 150], "color": "#eab308"},
                        {"range": [151, 200], "color": "#f97316"},
                        {"range": [201, 300], "color": "#ef4444"},
                        {"range": [301, 500], "color": "#7f1d1d"},
                    ],
                },
            )
        )
        fig_gauge.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#e5e7eb",
            margin=dict(l=10, r=10, t=10, b=10),
            height=260,
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    # ----- Right: radar (spider) chart of pollutants -----
    with col_right:
        pol_names = ["PM2.5", "PM10", "NO2", "SO2"]
        pol_values = [
            float(feats["PM2.5"]),
            float(feats["PM10"]),
            float(feats["NO2"]),
            float(feats["SO2"]),
        ]

        # close the loop for radar chart
        pol_names_closed = pol_names + [pol_names[0]]
        pol_values_closed = pol_values + [pol_values[0]]

        radar_fig = go.Figure(
            data=go.Scatterpolar(
                r=pol_values_closed,
                theta=pol_names_closed,
                fill="toself",
                line=dict(color="#22c55e"),
                fillcolor="rgba(34,197,94,0.4)",
            )
        )
        radar_fig.update_layout(
            title="Live pollutant radar",
            polar=dict(
                bgcolor="rgba(15,23,42,0.8)",
                radialaxis=dict(
                    visible=True,
                    showgrid=True,
                    gridcolor="rgba(148,163,184,0.3)",
                    linecolor="rgba(148,163,184,0.7)",
                ),
                angularaxis=dict(
                    linecolor="rgba(148,163,184,0.7)",
                    gridcolor="rgba(148,163,184,0.3)",
                ),
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#e5e7eb",
            margin=dict(l=10, r=10, t=40, b=10),
            height=260,
        )
        st.plotly_chart(radar_fig, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ======================================
# 10. Geospatial pollution map (card)
# ======================================
st.markdown('<div class="env-card">', unsafe_allow_html=True)
st.markdown("### 🗺 Geospatial pollution map")

try:
    with open("enviro_scan_pollution_map.html", "r", encoding="utf-8") as f:
        map_html = f.read()
    components.html(map_html, height=550, scrolling=True)
except FileNotFoundError:
    st.info("Map file 'enviro_scan_pollution_map.html' not found in the app folder.")
st.markdown('</div>', unsafe_allow_html=True)

# ======================================
# 11. Download report – CSV, Excel, PDF
# ======================================
st.markdown('<div class="env-card">', unsafe_allow_html=True)
st.markdown("### 📦 Export pollution report")
st.markdown(
    "Download the EnviroScan data for the selected city in CSV, Excel, or PDF summary format."
)


@st.cache_data
def to_csv_bytes(df_in):
    return df_in.to_csv(index=False).encode("utf-8")


@st.cache_data
def to_excel_bytes(df_in):
    buffer = BytesIO()
    df_in.to_excel(buffer, index=False, sheet_name="EnviroScan")
    buffer.seek(0)
    return buffer.getvalue()


def to_pdf_bytes(
    df_in,
    city_name,
    summary_dict,
    feats_dict,
    y_label,
    confidence,
    y_proba,
    aqi_live,
    model,
    label_encoder,
):
    import tempfile
    import os

    def to_latin1(s: str) -> str:
        return s.encode("latin-1", "replace").decode("latin-1")

    # ========= Create temp files for images =========
    tmp_dir = tempfile.mkdtemp()

    # 1) Key pollutants bar
    pol_df = pd.DataFrame(
        {
            "Pollutant": ["PM2.5", "PM10", "NO2", "SO2"],
            "Value": [
                float(feats_dict["PM2.5"]),
                float(feats_dict["PM10"]),
                float(feats_dict["NO2"]),
                float(feats_dict["SO2"]),
            ],
        }
    )
    pol_fig = px.bar(
        pol_df,
        x="Pollutant",
        y="Value",
        color="Pollutant",
        title="Key Pollutants (Live)",
        height=300,
    )
    pol_fig.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="rgba(230,230,230,0.4)",
        font_color="#000000",
        margin=dict(l=40, r=20, t=40, b=40),
    )
    pol_path = os.path.join(tmp_dir, "pol_bar.png")
    pol_fig.write_image(pol_path, format="png", width=700, height=300)

    # 2) Source probabilities bar
    class_labels = label_encoder.inverse_transform(model.classes_.astype(int))
    prob_fig = px.bar(
        x=class_labels,
        y=y_proba,
        labels={"x": "Source", "y": "Probability"},
        title="Pollution Source Probabilities",
        height=300,
    )
    prob_fig.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="rgba(230,230,230,0.4)",
        font_color="#000000",
        margin=dict(l=40, r=20, t=40, b=40),
    )
    prob_path = os.path.join(tmp_dir, "source_probs.png")
    prob_fig.write_image(prob_path, format="png", width=700, height=300)

    # 3) Pollutant radar
    pol_names = ["PM2.5", "PM10", "NO2", "SO2"]
    pol_values = [
        float(feats_dict["PM2.5"]),
        float(feats_dict["PM10"]),
        float(feats_dict["NO2"]),
        float(feats_dict["SO2"]),
    ]
    pol_names_closed = pol_names + [pol_names[0]]
    pol_values_closed = pol_values + [pol_values[0]]

    radar_fig = go.Figure(
        data=go.Scatterpolar(
            r=pol_values_closed,
            theta=pol_names_closed,
            fill="toself",
            line=dict(color="#22c55e"),
            fillcolor="rgba(34,197,94,0.4)",
        )
    )
    radar_fig.update_layout(
        title="Live Pollutant Radar",
        polar=dict(
            bgcolor="white",
            radialaxis=dict(visible=True, showgrid=True, gridcolor="lightgray"),
        ),
        paper_bgcolor="white",
        font_color="#000000",
        margin=dict(l=40, r=20, t=40, b=40),
        height=300,
    )
    radar_path = os.path.join(tmp_dir, "radar.png")
    radar_fig.write_image(radar_path, format="png", width=700, height=300)

    # 4) AQI gauge
    gauge_fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=float(aqi_live),
            title={"text": "AQI"},
            gauge={
                "axis": {"range": [0, 500]},
                "bar": {"color": "#22c55e"},
                "steps": [
                    {"range": [0, 50], "color": "#16a34a"},
                    {"range": [51, 100], "color": "#84cc16"},
                    {"range": [101, 150], "color": "#eab308"},
                    {"range": [151, 200], "color": "#f97316"},
                    {"range": [201, 300], "color": "#ef4444"},
                    {"range": [301, 500], "color": "#7f1d1d"},
                ],
            },
        )
    )
    gauge_fig.update_layout(
        paper_bgcolor="white",
        font_color="#000000",
        margin=dict(l=40, r=20, t=40, b=40),
        height=300,
    )
    gauge_path = os.path.join(tmp_dir, "gauge.png")
    gauge_fig.write_image(gauge_path, format="png", width=700, height=300)

    # 5) Pollutant contribution pie
    pol_pie_df = pd.DataFrame(
        {
            "Pollutant": ["PM2.5", "PM10", "NO2", "SO2"],
            "Value": pol_values,
        }
    )
    pie_fig = px.pie(
        pol_pie_df,
        names="Pollutant",
        values="Value",
        title="Pollutant Contribution (Live)",
        hole=0.35,
        height=300,
    )
    pie_fig.update_layout(
        paper_bgcolor="white",
        font_color="#000000",
        margin=dict(l=40, r=20, t=40, b=40),
    )
    pie_path = os.path.join(tmp_dir, "pie.png")
    pie_fig.write_image(pie_path, format="png", width=700, height=300)

    # ========= Build PDF =========
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # PAGE 1
    pdf.add_page()
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 12, to_latin1(f"EnviroScan Air Quality Report ({city_name})"), ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(
        0,
        8,
        to_latin1(f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}"),
        ln=True,
    )
    pdf.ln(4)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, to_latin1("1. Summary metrics"), ln=True)
    pdf.ln(2)

    pdf.set_font("Arial", "", 10)
    col_w1, col_w2 = 70, 100
    pdf.set_fill_color(34, 197, 94)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(col_w1, 7, "Metric", border=1, fill=True)
    pdf.cell(col_w2, 7, "Value", border=1, ln=True, fill=True)
    pdf.set_text_color(0, 0, 0)

    for key, value in summary_dict.items():
        pdf.cell(col_w1, 7, to_latin1(str(key)), border=1)
        pdf.cell(col_w2, 7, to_latin1(str(value)), border=1, ln=True)
    pdf.ln(4)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, to_latin1("2. Live measurements"), ln=True)
    pdf.ln(2)

    pdf.set_font("Arial", "", 10)
    feats_list = [
        ("PM2.5 (µg/m³)", f"{feats_dict['PM2.5']:.2f}"),
        ("PM10 (µg/m³)", f"{feats_dict['PM10']:.2f}"),
        ("NO2 (µg/m³)", f"{feats_dict['NO2']:.2f}"),
        ("SO2 (µg/m³)", f"{feats_dict['SO2']:.2f}"),
        ("Temperature (°C)", f"{feats_dict['Temperature (°C)']:.2f}"),
        ("Humidity (%)", f"{feats_dict['Humidity (%)']:.2f}"),
        ("Pressure (hPa)", f"{feats_dict['Pressure (hPa)']:.2f}"),
        ("Distance to nearest road (m)", f"{feats_dict['dist_nearest_road_m']:.0f}"),
    ]
    for name, val in feats_list:
        pdf.cell(col_w1, 6, to_latin1(name), border=1)
        pdf.cell(col_w2, 6, to_latin1(val), border=1, ln=True)
    pdf.ln(4)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, to_latin1("3. Key pollutants (bar chart)"), ln=True)
    pdf.ln(2)
    pdf.image(pol_path, x=10, w=190)

    # PAGE 2
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, to_latin1("4. AQI gauge (live)"), ln=True)
    pdf.ln(2)
    pdf.image(gauge_path, x=10, w=190)
    pdf.ln(4)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, to_latin1("5. Pollutant radar (live)"), ln=True)
    pdf.ln(2)
    pdf.image(radar_path, x=10, w=190)

    # PAGE 3
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, to_latin1("6. Pollution source probabilities"), ln=True)
    pdf.ln(2)
    pdf.image(prob_path, x=10, w=190)
    pdf.ln(4)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, to_latin1("7. Pollutant contribution pie"), ln=True)
    pdf.ln(2)
    pdf.image(pie_path, x=10, w=190)

    pdf.ln(6)
    pdf.set_font("Arial", "I", 9)
    pdf.cell(
        0,
        5,
        to_latin1(
            "Report generated by EnviroScan – AI‑Powered Pollution Source Identifier"
        ),
        ln=True,
    )

    return pdf.output(dest="S").encode("latin-1", "replace")


# pick slice for export
if df_city is not None and not df_city.empty:
    export_df = df_city
    city_name = str(df_city["City / town / village"].iloc[0]).replace(" ", "_")
else:
    export_df = df
    city_name = "all_locations"

summary_dict = {
    "Dominant source": y_label if y_label is not None else "N/A",
    "Confidence": f"{confidence*100:.1f}%" if confidence is not None else "N/A",
    "AQI (current)": round(float(aqi_live), 1) if aqi_live is not None else "N/A",
    "PM2.5 (µg/m³)": round(float(feats["PM2.5"]), 1) if feats is not None else "N/A",
    "Stations in city": len(df_city) if df_city is not None and not df_city.empty else len(df),
}

csv_bytes = to_csv_bytes(export_df)
xlsx_bytes = to_excel_bytes(export_df)

if feats is not None and y_label is not None and aqi_live is not None:
    pdf_bytes = to_pdf_bytes(
        export_df,
        city_name,
        summary_dict,
        feats,
        y_label,
        confidence,
        y_proba,
        aqi_live,
        model,
        label_encoder,
    )
else:
    pdf_bytes = None

c_csv, c_xlsx, c_pdf = st.columns(3)

with c_csv:
    st.download_button(
        label="⬇️ CSV",
        data=csv_bytes,
        file_name=f"enviro_scan_report_{city_name}.csv",
        mime="text/csv",
    )

with c_xlsx:
    st.download_button(
        label="⬇️ Excel",
        data=xlsx_bytes,
        file_name=f"enviro_scan_report_{city_name}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

with c_pdf:
    if pdf_bytes is not None:
        st.download_button(
            label="⬇️ PDF (detailed summary)",
            data=pdf_bytes,
            file_name=f"enviro_scan_report_{city_name}.pdf",
            mime="application/pdf",
        )
    else:
        st.info("Run a prediction to enable PDF export.")

st.markdown('</div>', unsafe_allow_html=True)

# ======================================
# 12. Global footer (copyright & links)
# ======================================
footer_html = """
<style>
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background: linear-gradient(90deg, #020617, #111827);
    color: #9ca3af;
    text-align: center;
    padding: 6px 10px;
    font-size: 0.75rem;
    border-top: 1px solid #1f2937;
    z-index: 100;
}
.footer a {
    color: #22c55e;
    text-decoration: none;
}
.footer a:hover {
    text-decoration: underline;
}
</style>

<div class="footer">
    <span>© 2026 EnviroScan. All rights reserved.</span>
    &nbsp;|&nbsp;
    <span>Built with Streamlit & OpenWeather APIs</span>
    &nbsp;|&nbsp;
    <span>Contact: <a href="mailto:enviroscan.support@example.com">enviroscan.support@example.com</a></span>
</div>
"""

st.markdown(footer_html, unsafe_allow_html=True)


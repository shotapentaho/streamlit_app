import streamlit as st
import requests
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
from st_ui_theme import apply_theme

st.set_page_config(layout="wide")
st.title("🌦️  5-Day Weather Forecast, Air Quality & Map — Seedometer AQI")
apply_theme()

# Get API key from Streamlit secrets
API_KEY = st.secrets["open_weather"]["api_key"]

bubble_style = """
<style>
.air-bubble {
    display: inline-block;
    padding: 18px 20px;
    margin: 8px;
    border-radius: 50%;
    background: linear-gradient(135deg, #87e0fd 0%, #53cbf1 100%);
    color: #0083B0;
    font-size: 1.1em;
    font-weight: bold;
    box-shadow: 0 2px 8px rgba(135,224,253,0.3);
    text-align: center;
    min-width: 90px;
}
.chem-title {
    font-size: 1em;
    color: #03506F;
    margin-bottom: 4px;
}
.seedometer-caption {
    font-size: 0.95rem;
    color: #034a5f;
    margin-top: 6px;
}
</style>
"""

chemical_names = {
    "co": "CO (Carbon Monoxide)",
    "no": "NO (Nitric Oxide)",
    "no2": "NO₂ (Nitrogen Dioxide)",
    "o3": "O₃ (Ozone)",
    "so2": "SO₂ (Sulphur Dioxide)",
    "pm2_5": "PM₂.₅ (Fine particles)",
    "pm10": "PM₁₀ (Coarse particles)",
    "nh3": "NH₃ (Ammonia)"
}

def get_coordinates(city, api_key):
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}"
    response = requests.get(url)
    if response.status_code != 200:
        return None, None
    data = response.json()
    if data:
        return data[0]["lat"], data[0]["lon"]
    return None, None

def get_air_quality(lat, lon, api_key):
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return response.json()

def create_seedometer_no_pointer(aqi_value: float):
    """
    Seedometer without any pointer/needle — shows colored gauge segments and
    the numeric AQI in the center (with the status in the number suffix).
    """
    status_labels = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
    colors = ["#00E400", "#FFFF00", "#FF7E00", "#FF0000", "#8F3F97"]

    clamped = max(0.0, min(5.0, float(aqi_value)))

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=clamped,
        number={
            "suffix": f"  ({status_labels.get(int(round(clamped)), 'Unknown')})",
            "font": {"size": 20}
        },
        gauge={
            "axis": {
                "range": [0, 5],
                "tickmode": "array",
                "tickvals": [1, 2, 3, 4, 5],
                "ticktext": ["1", "2", "3", "4", "5"],
                "tickfont": {"size": 12}
            },
            "bar": {"color": "rgba(0,0,0,0.25)", "thickness": 0.2},
            "steps": [
                {"range": [0, 1], "color": colors[0]},
                {"range": [1, 2], "color": colors[1]},
                {"range": [2, 3], "color": colors[2]},
                {"range": [3, 4], "color": colors[3]},
                {"range": [4, 5], "color": colors[4]},
            ],
            "threshold": {
                "line": {"color": "black", "width": 2},
                "thickness": 0.0,
                "value": clamped
            }
        },
        title={"text": "<b> Air Quality Index (1–5)</b>", "font": {"size": 14}}
    ))

    fig.update_layout(
        height=340,
        margin={"l": 10, "r": 10, "t": 50, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "#034a5f", "family": "Arial"}
    )

    return fig

st.markdown(bubble_style, unsafe_allow_html=True)

# Function to get 5-day weather forecast
def get_weather_forecast(city_name):
    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city_name,
        "appid": API_KEY,
        "units": "imperial"  # Fahrenheit
    }
    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        return None
    return response.json()

# Function to display the weather forecast by day (side by side)
def display_forecast(data):
    forecast_data = data["list"]
    forecast_by_day = {}
    for entry in forecast_data:
        dt = datetime.utcfromtimestamp(entry["dt"])
        date_str = dt.date().strftime("%Y-%m-%d")
        if date_str not in forecast_by_day:
            forecast_by_day[date_str] = {"temps": [], "icons": [], "description": []}
        forecast_by_day[date_str]["temps"].append(entry["main"]["temp"])
        forecast_by_day[date_str]["icons"].append(entry["weather"][0]["icon"])
        forecast_by_day[date_str]["description"].append(entry["weather"][0]["description"])

    cols = st.columns(5)
    for idx, (date, forecast) in enumerate(list(forecast_by_day.items())[:5]):
        min_temp = min(forecast["temps"])
        max_temp = max(forecast["temps"])
        min_temp_c = (min_temp - 32) * 5 / 9
        max_temp_c = (max_temp - 32) * 5 / 9
        description = " / ".join(set(forecast["description"]))
        icon = forecast["icons"][0]
        icon_url = f"http://openweathermap.org/img/wn/{icon}@2x.png"

        with cols[idx]:
            st.image(icon_url, width=50)
            st.write(f"**{date}**")
            st.write(f"🌡️  Min: **{min_temp:.1f}°F ~ {min_temp_c:.1f}°C**")
            st.write(f"🌡️  Max: **{max_temp:.1f}°F ~ {max_temp_c:.1f}°C**")
            st.write(f"💬 Conditions: {description.capitalize()}")

# Streamlit user input
city = st.text_input("Enter a city (specify also Country):", "New York City")
get_aqi = st.button("Forecast & Air Quality")

if "get_aqi" not in st.session_state:
    st.session_state["get_aqi"] = False

if get_aqi:
    st.session_state["get_aqi"] = True
    st.session_state["city"] = city

if get_aqi and not city:
    st.error("Please enter a city name to get the AQI and pollutant concentrations.")
    st.stop()

if st.session_state.get("get_aqi", False):
    data = get_weather_forecast(city)
    if not data:
        st.error("Could not retrieve weather data. Please check the city name or your API key.")
        st.stop()

    coord = data["city"]["coord"]

    # Display weather forecast and map
    if data.get("cod") == "200":
        col1, col2 = st.columns([6, 4])
        with col2:
            st.map(data=pd.DataFrame([{"lat": coord["lat"], "lon": coord["lon"]}]))
        with col1:
            display_forecast(data)
    else:
        st.error("City not found. Please check the name.")
        st.stop()

    # Air Quality (Seedometer) section
    lat, lon = coord["lat"], coord["lon"]
    if lat is None or lon is None:
        st.error("Could not determine coordinates for the city.")
        st.stop()

    aqi_data = get_air_quality(lat, lon, API_KEY)
    if not aqi_data or "list" not in aqi_data or len(aqi_data["list"]) == 0:
        st.error("Could not retrieve AQI data.")
        st.stop()

    air = aqi_data["list"][0]
    aqi = float(air["main"]["aqi"])  # 1..5 (use float in case)
    pollutants = air.get("components", {})

    # Layout: left = seedometer, right = pollutants
    st.write("### Air Quality Index(AQI)")
    left, right = st.columns([1, 2])
    with left:
        fig = create_seedometer_no_pointer(aqi)
        st.plotly_chart(fig, use_container_width=True)
        status_map = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
        st.markdown(
            f"<div class='seedometer-caption'>AQI: <b>{int(round(aqi))}</b> — {status_map.get(int(round(aqi)), 'Unknown')}</div>",
            unsafe_allow_html=True,
        )

    with right:
        st.write("### Pollutant Concentrations (μg/m³):")
        bubbles_html = '<div style="display:flex;flex-wrap:wrap;gap:18px;margin-bottom:20px;">'
        for chem, value in pollutants.items():
            bubbles_html += (
                f'<div class="air-bubble">'
                f'<span class="chem-title">{chemical_names.get(chem, chem)}</span><br>'
                f'{value:.2f}'
                f'</div>'
            )
        bubbles_html += "</div>"
        st.markdown(bubbles_html, unsafe_allow_html=True)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          1,22          Top

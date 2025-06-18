import streamlit as st
import requests

st.title("Air Quality Control Dashboard")

st.write("""
Enter a city name to get the current Air Quality Index (AQI) and major pollutant concentrations.
""")

city = st.text_input("City Name", "London")
# Your OpenWeatherMap API key here
API_KEY = st.secrets["api"]["OPENWEATHER_API_KEY"]

def get_coordinates(city, api_key):
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}"
    response = requests.get(url)
    data = response.json()
    if data:
        return data[0]['lat'], data[0]['lon']
    else:
        return None, None

def get_air_quality(lat, lon, api_key):
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
    response = requests.get(url)
    return response.json()

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

st.markdown(bubble_style, unsafe_allow_html=True)

if st.button("Get Air Quality"):
    lat, lon = get_coordinates(city, API_KEY)
    if lat and lon:
        aqi_data = get_air_quality(lat, lon, API_KEY)
        if "list" in aqi_data and len(aqi_data["list"]) > 0:
            air = aqi_data["list"][0]
            aqi = air["main"]["aqi"]
            pollutants = air["components"]
            aqi_status = {
                1: "Good",
                2: "Fair",
                3: "Moderate",
                4: "Poor",
                5: "Very Poor"
            }
            st.subheader("AQI", f"{aqi} ({aqi_status.get(aqi, 'Unknown')})")
            st.write("### Pollutant Concentrations (μg/m³):")
            cols = st.columns(len(pollutants))
            for i, (chem, value) in enumerate(pollutants.items()):
                with cols[i]:
                    st.markdown(
                        f'<div class="air-bubble"><span class="chem-title">{chemical_names.get(chem, chem)}</span><br>{value:.2f}</div>',
                        unsafe_allow_html=True
                    )
        else:
            st.error("Could not retrieve AQI data.")
    else:
        st.error("Could not find the city. Please check the name.")

st.caption("Powered by OpenWeatherMap API")

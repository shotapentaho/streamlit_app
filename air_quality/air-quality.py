import streamlit as st
import requests
st.set_page_config(
    page_title="Air Quality",
    page_icon=":cloud_with_snow:",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("Air Quality: AQI, Pollutant concentrations - Realtime")


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

st.markdown(bubble_style, unsafe_allow_html=True)

col1, col3, col2 = st.columns([2, 1, 4])

with col1:
    #st.write(""" city: """)
    city = st.text_input("City Name:", key="city_input")
    get_aqi = st.button("Get Air Quality")

with col2:
    if 'get_aqi' not in st.session_state:
        st.session_state['get_aqi'] = False

    if get_aqi:
        st.session_state['get_aqi'] = True
        st.session_state['city'] = city

    if get_aqi and not city:
        st.error("Please enter a city name to get the AQI and pollutant concentrations.")
        st.stop()

    if st.session_state.get('get_aqi', False):
        city = st.session_state.get(city)
        API_KEY = st.secrets["api"]["OPENWEATHER_API_KEY"]
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
                st.metric("Air Quality Index", f"AQI status:  {aqi} ({aqi_status.get(aqi, 'Unknown')})")
                st.write("### Pollutant Concentrations (μg/m³):")
                # Pollutant bubbles
                bubbles_html = '<div style="display: flex; flex-wrap: wrap; gap: 18px; margin-bottom: 20px;">'
                for chem, value in pollutants.items():
                    bubbles_html += (
                        f'<div class="air-bubble">'
                        f'<span class="chem-title">{chemical_names.get(chem, chem)}</span><br>'
                        f'{value:.2f}'
                        f'</div>'
                    )
                bubbles_html += '</div>'
                st.markdown(bubbles_html, unsafe_allow_html=True)
            else:
                st.error("Could not retrieve AQI data.")
        else:
            st.error("Could not find the city. Please check the name.")

st.caption("Powered by: OpenWeatherMap API")
import streamlit as st
import requests

st.title("Air Quality Control Display")

st.write("""
Enter a city name to get the current Air Quality Index (AQI) and major pollutant concentrations.
""")

# User input
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
            st.metric("AQI", f"{aqi} ({aqi_status.get(aqi, 'Unknown')})")
            st.write("### Pollutant Concentrations (μg/m³):")
            st.json(pollutants)
        else:
            st.error("Could not retrieve AQI data.")
    else:
        st.error("Could not find the city. Please check the name.")

st.caption("Powered by OpenWeatherMap API")
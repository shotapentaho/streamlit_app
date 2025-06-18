import streamlit as st
import requests
from datetime import datetime
import pandas as pd

st.set_page_config(layout="wide")
st.title("🌦️ 5-Day Weather Forecast, Air Quality & Map")

# Get API key from Streamlit secrets
API_KEY = st.secrets["api"]["OPENWEATHER_API_KEY"]


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
# Function to get 5-day weather forecast
def get_weather_forecast(city_name):
    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city_name,
        "appid": API_KEY,
        "units": "imperial"  # Fahrenheit
    }
    
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        return response.json()  # Return the JSON response with forecast data
    else:
        st.error(f"Error: {response.status_code} - {response.text}")
        return None

# Function to display the weather forecast by day (side by side)
def display_forecast(data):
    forecast_data = data['list']  # List of weather data points for 5 days
    
    # Group by date
    forecast_by_day = {}
    for entry in forecast_data:
        dt = datetime.utcfromtimestamp(entry['dt'])
        date_str = dt.date().strftime('%Y-%m-%d')
        
        if date_str not in forecast_by_day:
            forecast_by_day[date_str] = {
                'temps': [],
                'icons': [],
                'description': []
            }
        
        forecast_by_day[date_str]['temps'].append(entry['main']['temp'])
        forecast_by_day[date_str]['icons'].append(entry['weather'][0]['icon'])
        forecast_by_day[date_str]['description'].append(entry['weather'][0]['description'])
    
    # Create a row of columns for each day's weather
    cols = st.columns(5)  # Create 5 columns for the 5 days forecast
    
    for idx, (date, forecast) in enumerate(list(forecast_by_day.items())[:5]):
        # Get daily summary
        avg_temp = sum(forecast['temps']) / len(forecast['temps'])
        min_temp = min(forecast['temps'])
        max_temp = max(forecast['temps'])
        # Convert to Celsius
        min_temp_c = (min_temp - 32) * 5 / 9
        max_temp_c = (max_temp - 32) * 5 / 9

        description = " / ".join(set(forecast['description']))  # Unique descriptions for the day
        icon = forecast['icons'][0]  # Use the first icon of the day
        
        # Show the icon
        icon_url = f"http://openweathermap.org/img/wn/{icon}@2x.png"
        
        with cols[idx]:  # For each column (day)
            st.image(icon_url, width=50)  # Display icon with width
            st.write(f"**{date}**")
            st.write(f"🌡️ Min: **{min_temp:.1f}°F~{min_temp_c:.1f}°C**")
            st.write(f"🌡️ Max: **{max_temp:.1f}°F~{max_temp_c:.1f}°C**")
            #st.write(f"🌡️ Avg Temp: {avg_temp:.1f}°F")
            st.write(f"💬 Conditions: {description.capitalize()}")

# Streamlit user input for city name
city = st.text_input("Enter a city (specify also Country):", "Shrewsbury, US")
get_aqi = st.button("Forecast & Air Quality")

if 'get_aqi' not in st.session_state:
    st.session_state['get_aqi'] = False

if get_aqi:
    st.session_state['get_aqi'] = True
    st.session_state['city'] = city

if get_aqi and not city:
    st.error("Please enter a city name to get the AQI and pollutant concentrations.")
    st.stop()

if st.session_state.get('get_aqi', False):

    data = get_weather_forecast(city)
    ##################################Weather 5Days Forecast ##################################
    if data:
        if data.get("cod") == "200":
            col1, col2 = st.columns([6,4])
            
            with col2:
                # Show map with city location
                coord = data['city']['coord']
                st.map(data=pd.DataFrame([{
                    'lat': coord['lat'],
                    'lon': coord['lon']
                }]))
            with col1:
                display_forecast(data)
        else:
            st.error("City not found. Please check the name.")

 ##################################Air Quality Index (AQI) Section##################################

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
                st.metric("", f"AQI status:  {aqi} ({aqi_status.get(aqi, 'Unknown')})")
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
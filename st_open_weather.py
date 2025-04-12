import streamlit as st
import requests
from datetime import datetime

# Get API key from Streamlit secrets
API_KEY = st.secrets["api"]["OPENWEATHER_API_KEY"]

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
                'icons

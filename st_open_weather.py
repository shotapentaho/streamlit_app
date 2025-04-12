import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Weather Forecast App", layout="wide")
st.title("🌤️Weather App Next 5days!")

API_KEY = st.secrets["api"]["OPENWEATHER_API_KEY"]

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

def display_forecast(data):
    # Get the 5-day forecast (we're interested in 3-hour intervals)
    forecast_data = data['list']  # The forecast list is in the 'list' key
    
    # Group data by date (since each entry is a 3-hour interval)
    forecast_by_date = {}
    for entry in forecast_data:
        # Extract date from the timestamp
        dt = datetime.utcfromtimestamp(entry['dt'])
        date_str = dt.date().strftime('%Y-%m-%d')
        
        if date_str not in forecast_by_date:
            forecast_by_date[date_str] = []
        
        forecast_by_date[date_str].append(entry)
    
    # Display the forecast for each day
    for date, forecasts in forecast_by_date.items():
        st.subheader(f"Weather for {date}")
        for forecast in forecasts:
            dt = datetime.utcfromtimestamp(forecast['dt'])
            temp = forecast['main']['temp']
            description = forecast['weather'][0]['description']
            time = dt.strftime("%I:%M %p")  # Format time for better readability
            st.write(f"{time} - 🌡️ {temp}°F, {description.capitalize()}")
        st.write("---")  # Add a separator between days

# Streamlit user input for city name
city = st.text_input("Enter a city:", "New York")

if st.button("Get 5-Day Forecast") and city:
    data = get_weather_forecast(city)    
    # Check if the data is valid before displaying
    if data:
        if data.get("cod") == "200":
            display_forecast(data)
        else:
            st.error("City not found. Please check the name.")

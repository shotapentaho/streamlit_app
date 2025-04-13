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
        description = " / ".join(set(forecast['description']))  # Unique descriptions for the day
        icon = forecast['icons'][0]  # Use the first icon of the day
        
        # Show the icon
        icon_url = f"http://openweathermap.org/img/wn/{icon}@2x.png"
        
        with cols[idx]:  # For each column (day)
            st.image(icon_url, width=50)  # Display icon with width
            st.write(f"**{date}**")
            st.write(f"🌡️ Avg Temp: {avg_temp:.1f}°F")
            st.write(f"💬 Conditions: {description.capitalize()}")

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
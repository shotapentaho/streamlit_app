import streamlit as st
import requests
from datetime import datetime

API_KEY = st.secrets["api"]["OPENWEATHER_API_KEY"]

def get_weather_forecast(city_name):
    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city_name,
        "appid": API_KEY,
        "units": "imperial"
    }
    
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error: {response.status_code} - {response.text}")
        return None

def display_forecast(data):
    forecast_data = data['list']
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
    
    cols = st.columns(5)
    
    for idx, (date, forecast) in enumerate(forecast_by_day.items()):
        if not forecast['temps'] or not forecast['icons'] or not forecast['description']:
            continue  # Skip this day if any data is missing

        avg_temp = sum(forecast['temps']) / len(forecast['temps'])
        descriptions = list(set(forecast['description']))
        icon = forecast['icons'][0]
        icon_url = f"http://openweathermap.org/img/wn/{icon}@2x.png"
        
        desc_combined = " / ".join(descriptions).capitalize()
        is_sunny = any("clear" in desc or "sun" in desc for desc in descriptions)

        with cols[idx]:
            if is_sunny:
                st.markdown(f"<div style='text-align:center'><h3>☀️ Sunny!</h3></div>", unsafe_allow_html=True)
                st.image(icon_url, width=100)
                st.write(f"**{date}**")
                st.write(f"🌡️ Avg Temp: **{avg_temp:.1f}°F**")
                st.write(f"💬 {desc_combined}")
            else:
                st.image(icon_url, width=60)
                st.write(f"**{date}**")
                st.write(f"🌡️ Avg Temp: {avg_temp:.1f}°F")
                st.write(f"💬 {desc_combined}")
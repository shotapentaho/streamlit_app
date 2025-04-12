import streamlit as st
import requests
import os

st.set_page_config(page_title="Weather App", layout="wide")
st.title("🌤️Your Weather App")

API_KEY = st.secrets["api"]["OPENWEATHER_API_KEY"]

# Input field
city = st.text_input("Enter a city:", "Shrewsbury, NYC etc..")

def get_weather(city_name):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city_name,
        "appid": API_KEY,
        "units": "imperial"  # Change to 'metric' for Celsius
    }
    response = requests.get(base_url, params=params)
    #st.write("Response:", response.status_code)
    #st.write("Response:", response.text)
    return response.json()

if st.button("Get Weather"):
    if city:
        data = get_weather(city)
        if data.get("cod") == 200:
            st.subheader(f"Weather in {data['name']}, {data['sys']['country']}")
            st.write(f"🌡️ Temperature: {data['main']['temp']} °F")
            st.write(f"💧 Humidity: {data['main']['humidity']}%")
            st.write(f"💨 Wind Speed: {data['wind']['speed']} mph")
            st.write(f"📖 Description: {data['weather'][0]['description'].title()}")
        else:    
            st.error("City not found. Please check the name.")

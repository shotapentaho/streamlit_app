import streamlit as st
from datetime import datetime
import pytz
import time

# Layout
st.set_page_config(page_title="🌍 Global Clock", layout="centered")
st.title("🕒 Global Timezones")
st.write("Live time in selected cities around the world.")

# Timezone list (popular ones)
city_timezones = {
    "New York": "America/New_York",
    "London": "Europe/London",
    "Paris": "Europe/Paris",
    "Dubai": "Asia/Dubai",
    "Mumbai": "Asia/Kolkata",
    "Tokyo": "Asia/Tokyo",
    "Sydney": "Australia/Sydney",
    "San Francisco": "America/Los_Angeles"
}

select_all = st.checkbox("Select all cities", value=True)

if select_all:
    selected_cities = st.multiselect("Choose cities:", list(city_timezones.keys()), default=list(city_timezones.keys()))
else:
    selected_cities = st.multiselect("Choose cities:", list(city_timezones.keys()), default=[])	

# Clock loop
placeholder = st.empty()

def get_time_in_city(tz_name):
    tz = pytz.timezone(tz_name)
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

while True:
    with placeholder.container():
        for city in selected_cities:
            tz = city_timezones[city]
            current_time = get_time_in_city(tz)
            st.metric(label=f"🕓 {city}", value=current_time)

    time.sleep(1)
    placeholder.empty()

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import pytz
import time

def draw_analog_clock(hour, minute, second):
    fig, ax = plt.subplots(figsize=(3, 3))
    ax.axis("off")
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)

    # Clock circle
    clock_face = plt.Circle((0, 0), 1, fill=False, linewidth=3)
    ax.add_patch(clock_face)

    # Ticks
    for angle in range(0, 360, 30):
        x = np.cos(np.radians(angle))
        y = np.sin(np.radians(angle))
        ax.plot([0.9 * x, x], [0.9 * y, y], 'k', lw=2)

    # Convert to radians
    hour_angle = np.radians((hour % 12 + minute / 60) * 30)
    minute_angle = np.radians(minute * 6)
    second_angle = np.radians(second * 6)

    # Hour hand
    ax.plot([0, 0.5 * np.sin(hour_angle)], [0, 0.5 * np.cos(hour_angle)], 'k', lw=4)
    # Minute hand
    ax.plot([0, 0.8 * np.sin(minute_angle)], [0, 0.8 * np.cos(minute_angle)], 'k', lw=2)
    # Second hand
    ax.plot([0, 0.9 * np.sin(second_angle)], [0, 0.9 * np.cos(second_angle)], 'r', lw=1)

    st.pyplot(fig)

# App
st.set_page_config(layout="wide")
st.title("🕰️ Dial Clock – World Time")

city_timezones = {
    "New York": "America/New_York",
    "London": "Europe/London",
    "Mumbai": "Asia/Kolkata",
    "Tokyo": "Asia/Tokyo",
    "Sydney": "Australia/Sydney"
}

select_all = st.checkbox("Select all cities", value=True)

if select_all:
    selected_cities = st.multiselect("Choose cities:", list(city_timezones.keys()), default=list(city_timezones.keys()))
else:
    selected_cities = st.multiselect("Choose cities:", list(city_timezones.keys()), default=[])	
    
placeholder = st.empty()

while True:
    with placeholder.container():
        col_layout = st.columns(len(selected_cities))
        for i, city in enumerate(selected_cities):
            tz = pytz.timezone(city_timezones[city])
            now = datetime.now(tz)
            col_layout[i].subheader(f"{city}")
            draw_analog_clock(now.hour, now.minute, now.second)
    time.sleep(1)
    placeholder.empty()

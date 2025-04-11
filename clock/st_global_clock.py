import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import pytz
import time

# ========== Configuration ==========
st.set_page_config(page_title="Dial Clocks", layout="wide")
st.title("🌍🕰️ Global Time")
#st.markdown("Showing real-time analog clocks for selected world cities.")

# ========== City Timezones ==========
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

# Pre-select all cities
selected_cities = list(city_timezones.keys())

# ========== Clock Drawing Function ==========
def draw_analog_clock(hour, minute, second):
    fig, ax = plt.subplots(figsize=(3, 3))
    ax.axis("off")
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)

    # Clock circle
    clock_face = plt.Circle((0, 0), 1, fill=False, linewidth=3)
    ax.add_patch(clock_face)

    # Tick marks
    for angle in range(0, 360, 30):
        x = np.cos(np.radians(angle))
        y = np.sin(np.radians(angle))
        ax.plot([0.9 * x, x], [0.9 * y, y], 'k', lw=2)

    # Angles
    hour_angle = np.radians((hour % 12 + minute / 60) * 30)
    minute_angle = np.radians(minute * 6)
    second_angle = np.radians(second * 6)

    # Hands
    ax.plot([0, 0.5 * np.sin(hour_angle)], [0, 0.5 * np.cos(hour_angle)], 'k', lw=4)
    ax.plot([0, 0.8 * np.sin(minute_angle)], [0, 0.8 * np.cos(minute_angle)], 'k', lw=2)
    ax.plot([0, 0.9 * np.sin(second_angle)], [0, 0.9 * np.cos(second_angle)], 'r', lw=1)

    return fig

# ========== Live Update Section ==========
placeholder = st.empty()

while True:
    with placeholder.container():
        cols = st.columns(len(selected_cities))
        for i, city in enumerate(selected_cities):
            tz = pytz.timezone(city_timezones[city])
            now = datetime.now(tz)
            with cols[i]:
                st.markdown(f"### {city}")
                fig = draw_analog_clock(now.hour, now.minute, now.second)
                st.pyplot(fig, clear_figure=True)
    time.sleep(1)
    placeholder.empty()

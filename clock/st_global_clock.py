from streamlit_autorefresh import st_autorefresh
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import pytz

# ✅ MUST be first Streamlit command
st.set_page_config(page_title="🕰️ Global Clocks", layout="wide")
# Auto-refresh every 5000 ms (5 sec)
st_autorefresh(interval=5000, key="clock-refresh")
st.title("🌍🕰️ samaya..as time ")

city_timezones = {
    "[NYC Boston Miami]": "America/New_York",    
    "[Delhi Mumbai]": "Asia/Kolkata",
    "[SFO Seattle]": "America/Los_Angeles",
    "London": "Europe/London",
    "Paris": "Europe/Paris",
    "Dubai": "Asia/Dubai",
    "Tokyo": "Asia/Tokyo",
    "Sydney": "Australia/Sydney"   
}


def draw_analog_clock(hour, minute, second):
    fig, ax = plt.subplots(figsize=(2.5, 2.5))
    ax.axis("off")
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)

    for angle in range(0, 360, 30):
        x = np.cos(np.radians(angle))
        y = np.sin(np.radians(angle))
        ax.plot([0.9 * x, x], [0.9 * y, y], 'k', lw=1.5)

    # Clock hands
    h_angle = np.radians((hour % 12 + minute / 60) * 30)
    m_angle = np.radians(minute * 6)
    s_angle = np.radians(second * 6)

    ax.plot([0, 0.5 * np.sin(h_angle)], [0, 0.5 * np.cos(h_angle)], 'k', lw=3)
    ax.plot([0, 0.8 * np.sin(m_angle)], [0, 0.8 * np.cos(m_angle)], 'k', lw=2)
    ax.plot([0, 0.9 * np.sin(s_angle)], [0, 0.9 * np.cos(s_angle)], 'r', lw=1)

    return fig

cols = st.columns(len(city_timezones))
for i, (city, tz_str) in enumerate(city_timezones.items()):
    tz = pytz.timezone(tz_str)
    now = datetime.now(tz)
    with cols[i]:
        st.markdown(f"#### {city}")
        st.markdown(f"**📅 {now.strftime('%A, %d %B')} 🕒 {now.strftime('%I:%M:%S %p')}**" )        
        fig = draw_analog_clock(now.hour, now.minute, now.second)
        st.pyplot(fig, clear_figure=True)


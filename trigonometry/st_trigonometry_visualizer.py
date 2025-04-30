import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("📐 Trigonometry Visualizer")

# Sidebar controls
angle_deg = st.slider("Select angle (degrees)", 0, 360, 45)
angle_rad = np.radians(angle_deg)
function = st.selectbox("Choose function", ["sin", "cos", "tan"])

# Calculate value
if function == "sin":
    value = np.sin(angle_rad)
elif function == "cos":
    value = np.cos(angle_rad)
else:
    value = np.tan(angle_rad)

st.write(f"**{function}({angle_deg}°)** = `{value:.3f}`")

# Plot function over 0-360 degrees
x = np.linspace(0, 2*np.pi, 360)
fig, ax = plt.subplots()

if function == "sin":
    y = np.sin(x)
elif function == "cos":
    y = np.cos(x)
else:
    y = np.tan(x)
    y[np.abs(y) > 10] = np.nan  # Limit tan overflow

ax.plot(np.degrees(x), y)
ax.axvline(angle_deg, color='r', linestyle='--')
ax.axhline(value, color='g', linestyle='--')
ax.set_title(f"{function}(θ) plot")
ax.set_xlabel("Angle (degrees)")
ax.set_ylabel(f"{function}(θ)")

st.pyplot(fig)

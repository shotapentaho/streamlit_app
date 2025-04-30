import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("📐 Trigonometry Visualizer with All 6 Functions")

# Sidebar input
angle_deg = st.slider("Select angle (in degrees)", 0, 360, 45)
angle_rad = np.radians(angle_deg)

functions = {
    "sin": lambda x: np.sin(x),
    "cos": lambda x: np.cos(x),
    "tan": lambda x: np.tan(x),
    "cot": lambda x: 1 / np.tan(x),
    "sec": lambda x: 1 / np.cos(x),
    "cosec": lambda x: 1 / np.sin(x),
}

selected_func = st.selectbox("Choose a trigonometric function", list(functions.keys()))
calculate = functions[selected_func]

# Handle undefined values
try:
    val = calculate(angle_rad)
    if np.isinf(val) or np.isnan(val):
        result_str = f"⚠️ {selected_func}({angle_deg}°) is undefined."
    else:
        result_str = f"{selected_func}({angle_deg}°) = `{val:.3f}`"
except ZeroDivisionError:
    result_str = f"⚠️ {selected_func}({angle_deg}°) is undefined."

st.markdown(result_str)

# Generate function plot
x = np.linspace(0, 2 * np.pi, 1000)
x_deg = np.degrees(x)

# Avoiding overflows in plots
try:
    y = calculate(x)
    y = np.where(np.abs(y) > 10, np.nan, y)
except Exception:
    y = np.full_like(x, np.nan)

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(x_deg, y, label=f"{selected_func}(θ)")
ax.axvline(angle_deg, color='red', linestyle='--', label=f"θ = {angle_deg}°")
ax.axhline(0, color='gray', linewidth=0.5)

ax.set_title(f"{selected_func}(θ) from 0° to 360°")
ax.set_xlabel("Angle (°)")
ax.set_ylabel(f"{selected_func}(θ)")
ax.set_xlim([0, 360])
ax.legend()
ax.grid(True)

st.pyplot(fig)

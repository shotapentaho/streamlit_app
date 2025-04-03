import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Set up Streamlit page
st.set_page_config(page_title="Sector Area Calculator ", layout="wide")
st.title("📐 Sector Area of Circle Calculator: π×r×r ×(θ/360)")

# Split the screen into two columns
col1, col2 = st.columns([0.5, 0.5])  # 50-50 split


# Sliders for user input
with col1:
    radius = st.slider("Select Radius (r):", min_value=1, max_value=100, value=10, step=1)
    angle = st.slider("Select Angle (θ) in degrees:", min_value=1, max_value=360, value=90, step=1)

    # Calculate Sector Area
    sector_area = np.pi * radius**2 * (angle / 360)

    # Display Results
    st.write(f"### ✅ Sector Area: **{sector_area:.2f} square units**")

with col2:
    # Visualization
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    theta = np.linspace(0, np.radians(angle), 100)  # Convert degrees to radians
    r = np.full_like(theta, radius)

    ax.plot(theta, r, color='b', linewidth=2)  # Draw the arc
    ax.fill_between(theta, 0, r, color='blue', alpha=0.3)  # Fill the sector

    ax.set_title("Sector Representation", fontsize=14)
    ax.set_xticklabels([])  # Hide angle labels
    ax.set_yticklabels([])  # Hide radius labels

    st.pyplot(fig)

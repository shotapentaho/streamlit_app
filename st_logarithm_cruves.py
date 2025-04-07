import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")  # Optional for full-width layout
st.title("📊 Compare Multiple Logarithmic Curves")
col1, col2 = st.columns(2)

# 🔹 Column 1: UI controls
with col1:
    # Choose range
    x_min = st.slider("Start of x (must be > 0)", 0.1, 10.0, 1.0, step=0.1)
    x_max = st.slider("End of x", x_min + 1.0, 100.0, 10.0, step=1.0)
    x = np.linspace(x_min, x_max, 500)

    # Select which log curves to plot
    options = st.multiselect(
        "Select log curves to plot:",
        ["log(x)", "log10(x)", "log2(x)", "log5(x)"],
        default=["log(x)", "log10(x)"]
    )

# 🔹 Column 2: Plot
with col2:
    # Plot setup
    fig, ax = plt.subplots()

    if "log(x)" in options:
        ax.plot(x, np.log(x), label="log(x) — Natural Log", color="blue")
    if "log10(x)" in options:
        ax.plot(x, np.log10(x), label="log10(x) — Base 10", color="green")
    if "log2(x)" in options:
        ax.plot(x, np.log2(x), label="log2(x) — Base 2", color="red")
    if "log5(x)" in options:
        ax.plot(x, np.log5(x), label="log5(x) — Base 5", color="Purple")

    ax.set_title("Multiple Logarithmic Functions")
    ax.set_xlabel("x")
    ax.set_ylabel("log(x)")
    ax.grid(True)
    ax.legend()
    
    st.pyplot(fig)

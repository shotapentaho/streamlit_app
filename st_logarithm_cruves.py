import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("📊 Compare Multiple Logarithmic Curves")

# Choose range
x_min = st.slider("Start of x (must be > 0)", 0.1, 10.0, 1.0, step=0.1)
x_max = st.slider("End of x", x_min + 1.0, 100.0, 10.0, step=1.0)
x = np.linspace(x_min, x_max, 500)

# Select which log curves to plot
options = st.multiselect(
    "Select log curves to plot:",
    ["log(x)", "log10(x)", "log2(x)"],
    default=["log(x)", "log10(x)"]
)

# Plot setup
fig, ax = plt.subplots()

if "log(x)" in options:
    ax.plot(x, np.log(x), label="log(x) — Natural Log", color="blue")

if "log10(x)" in options:
    ax.plot(x, np.log10(x), label="log10(x) — Base 10", color="green")

if "log2(x)" in options:
    ax.plot(x, np.log2(x), label="log2(x) — Base 2", color="red")

ax.set_title("Multiple Logarithmic Functions")
ax.set_xlabel("x")
ax.set_ylabel("log(x)")
ax.grid(True)
ax.legend()

st.pyplot(fig)

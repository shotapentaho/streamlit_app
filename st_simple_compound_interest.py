import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Set page config to full-width layout
st.set_page_config(page_title="Simple and Compound Interest Calculator", layout="wide")

# User Inputs with Sliders
P = st.slider("Select Principal Amount (P):", min_value=1000, max_value=100000, value=10000, step=1000)
R = st.slider("Select Rate of Interest (R) in %:", min_value=0.5, max_value=10.0, value=3.0, step=0.1)
T = st.slider("Select Time (T) in months:", min_value=1, max_value=120, value=10, step=1)

# Split the screen into two columns
col1, col2 = st.columns([0.5, 0.5])  # 50-50 split

### SIMPLE INTEREST SECTION ###
with col1:
    st.title("💰 Simple Interest Calculator")
    st.subheader(" **SI = (P × R × T) / (100 × 12)** ")

    # Compute Simple Interest
    SI = (P * R * T) / (100 * 12)
    total_amount_si = P + SI

    st.write(f"### ✅ Simple Interest: **${SI:.2f}**")
    st.write(f"### 💰 Total Amount after Interest: **${total_amount_si:.2f}**")

    # Generate Data for Graph
    months = np.arange(1, T + 1)
    amounts_si = P + (P * R * months) / (100 * 12)  # Total amount over months

    # Plot Graph
    fig, ax = plt.subplots()
    ax.plot(months, amounts_si, marker="o", linestyle="-", color="b", label="Total Amount (Simple Interest)")

    # Add Labels on Each Point
    for i, txt in enumerate(amounts_si):
        ax.annotate(f"${txt:.2f}", (months[i], amounts_si[i]), textcoords="offset points", xytext=(0,10), ha='center', fontsize=8, color="black")

    ax.set_xlabel("Time (months)")
    ax.set_ylabel("Total Amount ($)")
    ax.set_title("Simple Interest Growth Over Time")
    ax.legend()
    ax.grid(True)

    # Display Simple Interest Plot in Streamlit
    st.pyplot(fig)

### COMPOUND INTEREST SECTION ###
with col2:
    st.title("💰 Compound Interest Calculator")
    st.subheader(" **A = P (1 + R/1200) ^ T** ")

    # Compute Compound Interest
    A = P * (1 + R / 1200) ** T
    CI = A - P  # Compound Interest Amount
    total_amount_ci = A

    st.write(f"### ✅ Compound Interest: **${CI:.2f}**")
    st.write(f"### 💰 Total Amount after Interest: **${total_amount_ci:.2f}**")

    # Generate Data for Graph
    months = np.arange(1, T + 1)
    amounts_ci = P * (1 + R / 1200) ** months  # Compound Interest Growth

    # Plot Graph
    fig_ci, ax_ci = plt.subplots()
    ax_ci.plot(months, amounts_ci, marker="o", linestyle="-", color="g", label="Total Amount (Compound Interest)")

    # Add Labels on Each Point
    for i, txt in enumerate(amounts_ci):
        ax_ci.annotate(f"${txt:.2f}", (months[i], amounts_ci[i]), textcoords="offset points", xytext=(0,10), ha='center', fontsize=8, color="black")

    ax_ci.set_xlabel("Time (months)")
    ax_ci.set_ylabel("Total Amount ($)")
    ax_ci.set_title("Compound Interest Growth Over Time")
    ax_ci.legend()
    ax_ci.grid(True)

    # Display the Plot in Streamlit
    st.pyplot(fig_ci)

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Streamlit UI
st.title("💰 Simple Interest Calculator with Visualization")
st.write("Formula: **SI = (P × R × T) / 100**")

# User Inputs
P = st.number_input("Enter Principal Amount (P):", min_value=0.0, value=1000.0)
R = st.number_input("Enter Rate of Interest (R) in %:", min_value=0.0, value=5.0)
T = st.number_input("Enter Time (T) in years:", min_value=0.0, value=10.0)

# Compute Simple Interest for Each Year
years = np.arange(1, int(T) + 1)  # Time in years
amounts = P + (P * R * years) / 100  # Total amount over years

# Display Results
SI = (P * R * T) / 100
total_amount = P + SI
st.write(f"### ✅ Simple Interest: **₹{SI:.2f}**")
st.write(f"### 💰 Total Amount after Interest: **₹{total_amount:.2f}**")

# Plot Graph
fig, ax = plt.subplots()
ax.plot(years, amounts, marker="o", linestyle="-", color="b", label="Total Amount")
ax.set_xlabel("Time (years)")
ax.set_ylabel("Total Amount (₹)")
ax.set_title("Simple Interest Growth Over Time")
ax.legend()
ax.grid(True)

# Display the Plot in Streamlit
st.pyplot(fig)

################## Compound Interest ###################

# Streamlit UI
st.title("💰 Compound Interest Calculator with Visualization")
st.write("Formula: **A = P (1 + R/100) ^ T**")

# Compute Compound Interest for Each Year
years = np.arange(1, int(T) + 1)  # Time in years
amounts = P * (1 + R / 100) ** years  # Compound Interest Calculation

# Final Amount
A = P * (1 + R / 100) ** T
CI = A - P

# Display Results
st.write(f"### ✅ Compound Interest: **₹{CI:.2f}**")
st.write(f"### 💰 Total Amount after Interest: **₹{A:.2f}**")

# Plot Graph
fig_ci, ax_ci = plt.subplots()
ax_ci.plot(years, amounts, marker="o", linestyle="-", color="g", label="Total Amount (Compound Interest)")

# Add Labels on Each Point
for i, txt in enumerate(amounts):
    ax_ci.annotate(f"₹{txt:.2f}", (years[i], amounts[i]), textcoords="offset points", xytext=(0,10), ha='center', fontsize=9, color="black")

ax_ci.set_xlabel("Time (years)")
ax_ci.set_ylabel("Total Amount (₹)")
ax_ci.set_title("Compound Interest Growth Over Time")
ax_ci.legend()
ax_ci.grid(True)

# Display the Plot in Streamlit
st.pyplot(fig_ci)

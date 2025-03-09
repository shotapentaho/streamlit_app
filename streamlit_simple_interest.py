import streamlit as st

# Streamlit UI
st.title("💰 Simple Interest Calculator")
st.write("Calculate simple interest using the formula: **SI = (P × R × T) / 100**")

# User Inputs
P = st.number_input("Enter Principal Amount (P):", min_value=0.0, value=1000.0)
R = st.number_input("Enter Rate of Interest (R) in %:", min_value=0.0, value=5.0)
T = st.number_input("Enter Time (T) in years:", min_value=0.0, value=2.0)

# Calculation
SI = (P * R * T) / 100
total_amount = P + SI

# Display Results
st.write(f"### ✅ Simple Interest: **₹{SI:.2f}**")
st.write(f"### 💰 Total Amount after Interest: **₹{total_amount:.2f}**")

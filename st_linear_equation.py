import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Streamlit UI
st.title("📈 Linear Equation Solver")
st.write("Solve and visualize a linear equation of the form: **y = ax + b**")

# User Input for Coefficients
a = st.number_input("Enter coefficient 'a':", value=1.0)
b = st.number_input("Enter coefficient 'b':", value=0.0)

# Generate X and Y values
x = np.linspace(-10, 10, 100)
y = a * x + b

# Display the equation
st.write(f"### Equation: **y = {a}x + {b}**")

# Plot the Linear Equation
fig, ax = plt.subplots()
ax.plot(x, y, label=f"y = {a}x + {b}", color="blue")
ax.axhline(0, color='black', linewidth=0.5)  # X-axis
ax.axvline(0, color='black', linewidth=0.5)  # Y-axis
ax.grid(True, linestyle='--', linewidth=0.5)
ax.legend()
plt.xlabel("X-axis")
plt.ylabel("Y-axis")
plt.title("Graph of the Linear Equation")

# Display the Plot in Streamlit
st.pyplot(fig)

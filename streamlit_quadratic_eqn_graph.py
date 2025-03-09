import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Streamlit UI
st.title("📈 Quadratic Equation Solver & Grapher")

# User Inputs for Coefficients
a = st.number_input("Enter coefficient a:", value=1.0)
b = st.number_input("Enter coefficient b:", value=-3.0)
c = st.number_input("Enter coefficient c:", value=2.0)

# Calculate Discriminant
D = b**2 - 4*a*c  # Discriminant

# Solve the Quadratic Equation
if D > 0:
    root1 = (-b + np.sqrt(D)) / (2*a)
    root2 = (-b - np.sqrt(D)) / (2*a)
    roots = [root1, root2]
    result_text = f"✅ Two real roots: **{root1:.2f}** and **{root2:.2f}**"
elif D == 0:
    root = -b / (2*a)
    roots = [root]
    result_text = f"✅ One real root: **{root:.2f}**"
else:
    roots = []
    result_text = "❌ No real roots (Complex numbers)."

# Display Result
st.write(result_text)

# Plot the Quadratic Function
x = np.linspace(-10, 10, 400)  # X-axis range
y = a*x**2 + b*x + c  # Quadratic equation

fig, ax = plt.subplots()
ax.plot(x, y, label=f"${a}x^2 + {b}x + {c}$", color="blue")

# Mark the Roots
for root in roots:
    ax.scatter(root, 0, color="red", zorder=3, label=f"Root: {root:.2f}")

ax.axhline(0, color="black", linewidth=1)  # X-axis
ax.axvline(0, color="black", linewidth=1)  # Y-axis

ax.set_xlabel("x")
ax.set_ylabel("f(x)")
ax.legend()
ax.grid(True)

# Display Plot in Streamlit
st.pyplot(fig)

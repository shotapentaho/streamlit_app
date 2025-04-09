import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Set page config to full-width layout
st.set_page_config(page_title="Quadratic Equation Solver & Grapher", layout="wide")
st.title("📈 Quadratic Equation Solver & Grapher : axx+bx+c=0 ")

# Split the screen into two columns
col1, col2 = st.columns([0.5, 0.5])  # 50-50 split

with col1:
    # User Inputs with Sliders
    a = st.slider("Enter coefficient a:", min_value=-100.0,  max_value=100.0,  value=1.0,  step=1.0)
    b = st.slider("Enter coefficient b:", min_value=-100.0,  max_value=100.0,  value=-3.0,  step=1.0)
    c = st.slider("Enter coefficient c:", min_value=-100.0,  max_value=100.0,  value=2.0,  step=1.0)

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

with col2:
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

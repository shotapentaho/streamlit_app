import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Set page config to full-width layout
st.set_page_config(page_title="Linear Equation Solver & Grapher", layout="wide")
st.title("📈 Linear Equation Solver & Grapher : y = ax + b")


# Split the screen into two columns
col1, col2 = st.columns([0.5, 0.5])  # 50-50 split

with col1:

    # User Inputs with Sliders
    a = st.slider("Enter coefficient a:", min_value=-100.0,  max_value=500.0,  value=1.0,  step=1.0)
    b = st.slider("Enter coefficient b:", min_value=-100.0,  max_value=500.0,  value=0.0,  step=1.0)
        
    # Generate X and Y values
    x = np.linspace(-10, 10, 100)
    y = a * x + b

    # Display the equation
    st.write(f"### Equation: **y = {a}x + {b}**")

with col2:
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

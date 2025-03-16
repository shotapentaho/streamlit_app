import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("🔺 Triangle Calculator & Visualizer")

# Sidebar Inputs for Triangle Sides
st.sidebar.header("Triangle Side Lengths")
a = st.sidebar.number_input("Enter side a:", min_value=1.0, value=3.0)
b = st.sidebar.number_input("Enter side b:", min_value=1.0, value=4.0)
c = st.sidebar.number_input("Enter side c:", min_value=1.0, value=5.0)

# Check if the sides form a valid triangle
def is_valid_triangle(a, b, c):
    return a + b > c and a + c > b and b + c > a

if is_valid_triangle(a, b, c):
    st.success("✅ The given sides form a valid triangle.")

    # Compute Perimeter
    perimeter = a + b + c
    st.write(f"### Perimeter: **{perimeter}** units")

    # Compute Area using Heron's Formula
    s = perimeter / 2
    area = np.sqrt(s * (s - a) * (s - b) * (s - c))
    st.write(f"### Area: **{area:.2f}** square units")

    # Triangle Type Classification
    if a == b == c:
        triangle_type = "Equilateral"
    elif a == b or b == c or a == c:
        triangle_type = "Isosceles"
    else:
        triangle_type = "Scalene"

    st.write(f"### Triangle Type: **{triangle_type}**")

    # Triangle Visualization
    st.subheader("📊 Triangle Visualization")
    
    # Compute triangle coordinates
    A = np.array([0, 0])  # First point at origin

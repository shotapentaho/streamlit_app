import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("🔺 Triangle Calculator & Visualizer (Using Coordinates)")

# Sidebar Inputs for Triangle Vertices
st.sidebar.header("Enter the (x, y) coordinates of the 3 vertices:")

# User Inputs with Sliders
x1 = st.slider("X1:", min_value=-100.0,  max_value=100.0,  value=1.0,  step=1.0)
y1 = st.slider("Y1:", min_value=-100.0,  max_value=100.0,  value=0.0,  step=1.0)
x2 = st.slider("X2:", min_value=-100.0,  max_value=100.0,  value=4.0,  step=1.0)
y2 = st.slider("Y2:", min_value=-100.0,  max_value=100.0,  value=0.0,  step=1.0)
x3 = st.slider("X3:", min_value=-100.0,  max_value=100.0,  value=2.0,  step=1.0)
y3 = st.slider("Y3:", min_value=-100.0,  max_value=100.0,  value=3.0,  step=1.0)

# Compute side lengths
def distance(x1, y1, x2, y2):
    return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

a = distance(x2, y2, x3, y3)
b = distance(x1, y1, x3, y3)
c = distance(x1, y1, x2, y2)

# Check if the points form a valid triangle
def is_valid_triangle(a, b, c):
    return a + b > c and a + c > b and b + c > a

if is_valid_triangle(a, b, c):
    st.success("✅ The given points form a valid triangle.")

    # Compute Perimeter
    perimeter = a + b + c
    st.write(f"### Perimeter: **{perimeter:.2f}** units")

    # Compute Area using determinant formula
    area = 0.5 * abs(x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
    st.write(f"### Area: **{area:.2f}** square units")

    # Classify the Triangle
    if a == b == c:
        triangle_type = "Equilateral"
    elif a == b or b == c or a == c:
        triangle_type = "Isosceles"
    else:
        triangle_type = "Scalene"
    
    # Check for Right-Angled Triangle
    sides = sorted([a, b, c])  # Sort sides to check Pythagoras theorem
    if np.isclose(sides[2]**2, sides[0]**2 + sides[1]**2):
        triangle_type += " & Right-angled"

    st.write(f"### Triangle Type: **{triangle_type}**")

    # Triangle Visualization
    st.subheader("📊 Triangle Visualization")
    
    fig, ax = plt.subplots()
    triangle_x = [x1, x2, x3, x1]
    triangle_y = [y1, y2, y3, y1]
    
    ax.plot(triangle_x, triangle_y, "bo-")  # Blue dots and lines
    ax.fill(triangle_x, triangle_y, "skyblue", alpha=0.3)  # Filled triangle
    ax.set_xlim(min(triangle_x) - 1, max(triangle_x) + 1)
    ax.set_ylim(min(triangle_y) - 1, max(triangle_y) + 1)
    ax.set_title("Triangle Visualization")
    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")

    st.pyplot(fig)

else:
    st.error("❌ The given points do not form a valid triangle. Please adjust the values.")

import streamlit as st
from PIL import Image

# Load and show logo
logo = Image.open("./media/logo.png")
st.image(logo, use_column_width=True)
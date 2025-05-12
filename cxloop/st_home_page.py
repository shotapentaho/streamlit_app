import streamlit as st
from PIL import Image

# Load and show logo
logo = Image.open("./cxloop/media/cxloop_logo.png")
st.image(logo, use_container_width=True)
import streamlit as st
from PIL import Image

# Load and show logo
logo = Image.open("./cxloop/media/cxloop_logo.png")
st.image(logo, use_container_width=True)

# Title
st.markdown("## 🔐 👷 🔄 Contractor Xperiences")
st.markdown("### Login or Register (new here)")

# Navigation button
if st.button("🔑 Go to Login/Register Page"):
    st.switch_page("https://cxloop-enter.streamlit.app/")  # or replace with actual filename
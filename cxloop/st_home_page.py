import streamlit as st
from PIL import Image

# Load and show logo
logo = Image.open("./cxloop/media/cxloop_logo.png")
st.image(logo, use_container_width=True)

# Top-right button with CSS
st.markdown("""
    <style>
    .top-right-button {
        position: absolute;
        top: 20px;
        right: 20px;
        z-index: 9999;
    }
    </style>

    <div class="top-right-button">
        <a href="https://cxloop-enter.streamlit.app/" target="_blank">
            <button style='font-size:16px;padding:8px 16px;'>🔑 Login/Register</button>
        </a>
    </div>
""", unsafe_allow_html=True)
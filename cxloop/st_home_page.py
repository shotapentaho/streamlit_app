hide_default_header = """
        <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """
hide_default_footer = """
    <style>
    footer, .st-emotion-cache-1gulkj5 {display: none; visibility: hidden;}
    .css-qri22k {display: none; visibility: hidden;}
    .stDeployButton {display: none;}
    .viewerBadge_link__1S137 {display: none;}
    </style>
"""
import streamlit as st
st.markdown(hide_default_header, unsafe_allow_html=True)
st.markdown(hide_default_footer, unsafe_allow_html=True)
from PIL import Image

# Load and show logo
cxloop_logo = Image.open("./cxloop/media/cxloop_logo.png")
brain_python_openai_logo = Image.open("./cxloop/media/human_python_openai.png")

    
st.image(cxloop_logo, use_container_width=True)


# Top-right button with CSS
st.markdown("""
    <style>
    .top-right-button {
        position: absolute;
        top: 0px;
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
# Create two columns: left wide, right narrow (logo)
col1, col2 = st.columns([2, 8])
with col1:
    st.image(brain_python_openai_logo, use_container_width=True)
#with col2:
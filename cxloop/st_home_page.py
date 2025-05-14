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

 
# Container for header
with st.container():
    # Row for header: logo left, button right
    col1, col2 = st.columns([9, 1])
    with col1:
        st.image(cxloop_logo, use_column_width=True)
    with col2:
        st.markdown("""
            <a href="https://cxloop-enter.streamlit.app/" target="_blank">
                <button style='font-size:18px;padding:8px 16px;margin-top:10px;'>🔑 Login/Register</button>
            </a>
        """, unsafe_allow_html=True)

# Create two columns: left wide, right narrow (logo)
st.write("")
st.write("")
st.write("")
col1, col2 = st.columns([20, 2])
with col2:
    st.image(brain_python_openai_logo, use_container_width=True)
#with col2:
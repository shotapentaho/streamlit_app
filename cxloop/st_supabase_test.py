hide_default_footer = """
    <style>
    footer, .st-emotion-cache-1gulkj5 {display: none; visibility: hidden;}
    .css-qri22k {display: none; visibility: hidden;}
    .stDeployButton {display: none;}
    .viewerBadge_link__1S137 {display: none;}
    </style>
"""
hide_default_header = """
        <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
"""

import streamlit as st
from supabase import create_client
import pandas as pd
st.markdown(hide_default_footer, unsafe_allow_html=True)
st.markdown(hide_default_header, unsafe_allow_html=True)

sb_url = st.secrets["supabase"]["url"]
anon_key = st.secrets["supabase"]["key"]
def get_connection():
    return create_client(sb_url, anon_key)  

conn = get_connection()

# Fetch data from a table
response = conn.table("users").select("*").execute()

# Convert to DataFrame
df = pd.DataFrame(response.data)

# Display using Streamlit
st.dataframe(df)
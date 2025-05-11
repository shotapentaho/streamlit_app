from supabase import create_client
import streamlit as st
import pandas as pd

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
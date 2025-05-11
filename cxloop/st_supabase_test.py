import streamlit as st
import psycopg2
import pandas as pd

# Load credentials from secrets.toml
config = st.secrets["supabase"]

@st.cache_resource
def connect():
    # Connect to Supabase PostgreSQL using the secrets
    return psycopg2.connect(
        host=config["host"],
        dbname=config["database"],
        user=config["user"],
        password=config["password"],
        port=config["port"]
    )

# Establish connection
conn = connect()

# Query a table (e.g., contractors)
df = pd.read_sql("SELECT * FROM cxloop.users", conn)

# Display the table
st.dataframe(df)
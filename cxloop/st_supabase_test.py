import streamlit as st
import psycopg2
import pandas as pd


def get_connection():
    # Connect to Supabase PostgreSQL using the secrets
    return psycopg2.connect(
        host=st.secrets["supabase"]["host"],
        database=st.secrets["supabase"]["database"],
        port=st.secrets["supabase"]["port"],
        user=st.secrets["supabase"]["user"],
        password=st.secrets["supabase"]["password"]
    )

# Establish connection
conn = get_connection()

# Query a table (e.g., contractors)
df = pd.read_sql("SELECT * FROM cxloop.users", conn)

# Display the table
st.dataframe(df)
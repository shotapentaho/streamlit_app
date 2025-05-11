import streamlit as st
import psycopg2
import pandas as pd


def get_connection():
    # Connect to Supabase PostgreSQL using the secrets
    return psycopg2.connect(
        user=st.secrets["supabase"]["user"],
        password=st.secrets["supabase"]["password"],
        host=st.secrets["supabase"]["host"],
        port=st.secrets["supabase"]["port"],
        database=st.secrets["supabase"]["database"]
    )

# Establish connection
conn = get_connection()

# Query a table (e.g., contractors)
df = pd.read_sql("SELECT * FROM cxloop.users", conn)

# Display the table
st.dataframe(df)
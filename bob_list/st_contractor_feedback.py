import streamlit as st
import snowflake.connector
import pandas as pd
from datetime import date

st.set_page_config(layout="wide")

# Connect to Snowflake using Streamlit secrets
@st.cache_resource
def get_connection():
    return snowflake.connector.connect(
        user=st.secrets["snowflake"]["user"],
        password=st.secrets["snowflake"]["password"],
        account=st.secrets["snowflake"]["account"],
        warehouse=st.secrets["snowflake"]["warehouse"],
        database=st.secrets["snowflake"]["database"],
        schema=st.secrets["snowflake"]["schema"]
    )

conn = get_connection()
cur = conn.cursor()

# Create table if it doesn't exist
cur.execute("""
    CREATE TABLE IF NOT EXISTS TEST.PUBLIC.engagements (
        customer_name STRING,
        street STRING,
        city STRING,
        state STRING,
        zip_code STRING,
        engagement_type STRING,
        activity_date DATE,
        feedback STRING,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
    )
""")

st.title("Customer feedback here")

# Form fields
with st.form("engagement_form"):
    customer_name = st.text_input("Customer Name")
    
    col4, col1, col2, col3 = st.columns([2, 2, 1, 2])
    with col4:
        street = st.text_input("Street:")
    with col1:
        city = st.text_input("City:")
    with col2:
        state = st.selectbox("State:", options=[
            "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
            "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
            "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
            "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
            "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
        ])
    with col3:
        zip_code = st.text_input("ZIP:")

    col4, col5 = st.columns([1,2])
    with col4:
        engagement_type = st.selectbox("Type of work:", ["Electrical", "Painting", "Plumbing"])
    with col5:
        activity_date = st.date_input("Activity performed on:", value=date.today())
    feedback = st.text_area("Feedback (if any) on customer:")

    submitted = st.form_submit_button("Submit")

    if submitted:
        if not (customer_name and street and city and zip_code):
            st.warning("Please fill out all required fields.")
        else:
            insert_sql = """
                INSERT INTO TEST.PUBLIC.engagements (
                    customer_name, street, city, state, zip_code, 
                    engagement_type, activity_date, feedback
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cur.execute(insert_sql, (
                customer_name, street, city, state, zip_code,
                engagement_type, activity_date.isoformat(), feedback
            ))
            conn.commit()
            st.success("Submission saved to Snowflake.")

# Retrieve and display existing data
st.subheader("All Engagements:")
cur.execute("SELECT * FROM TEST.PUBLIC.engagements ORDER BY submitted_at DESC")
df = cur.fetch_pandas_all()
st.dataframe(df, use_container_width=True)

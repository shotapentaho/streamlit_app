import streamlit as st
import duckdb
import pandas as pd
from datetime import date

# US States and Engagements
us_states = [
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
    'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
    'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
]
engagement_types = ["Electrical", "Painting", "Plumbing"]
DB_FILE = "engagements.duckdb"

# Initialize DB
def init_db():
    with duckdb.connect(DB_FILE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS engagements (
                street TEXT,
                city TEXT,
                state TEXT,
                zip_code TEXT,
                engagement_type TEXT,
                activity_date DATE,
                feedback TEXT,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
init_db()

# UI
st.title("📬 US Address & Engagement Form")

# Address Inputs
street = st.text_input("Street Address", placeholder="123 Main St")

col1, col2, col3 = st.columns([3, 1, 2])
with col1:
    city = st.text_input("City", placeholder="Springfield")
with col2:
    state = st.selectbox("State", us_states)
with col3:
    zip_code = st.text_input("ZIP Code", placeholder="90210")

# Other Inputs
engagement = st.selectbox("Type of Engagement", engagement_types)
activity_date = st.date_input("Date of Activity", value=date.today())
feedback = st.text_area("Feedback about the customer", placeholder="e.g., Very polite, always on time...")

# Submit
if st.button("Submit"):
    if not (street and city and zip_code):

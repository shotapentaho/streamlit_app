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
        conn.execute("DROP TABLE IF EXISTS engagements")
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
st.title("📬 Customer Feedbacks...")

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
        st.warning("Please fill out all required fields.")
    else:
        with duckdb.connect(DB_FILE) as conn:
            conn.execute("""
                INSERT INTO engagements (street, city, state, zip_code, engagement_type, activity_date, feedback)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (street, city, state, zip_code, engagement, activity_date, feedback))
        st.success("Form submitted and saved to database!")

        # Display summary
        st.markdown(f"""
        **Address**: {street}, {city}, {state} {zip_code}  
        **Engagement**: {engagement}  
        **Activity Date**: {activity_date.strftime('%Y-%m-%d')}  
        **Customer Feedback**: _{feedback or "No feedback provided."}_
        """)

# View stored data
st.subheader("📊 All Submitted Engagements")
with duckdb.connect(DB_FILE) as conn:
    df = conn.execute("SELECT * FROM engagements ORDER BY submitted_at DESC").fetchdf()

if df.empty:
    st.info("No submissions yet.")
else:
    st.dataframe(df, use_container_width=True)

import streamlit as st
import snowflake.connector
import pandas as pd
from datetime import date
#from st_star_rating import st_star_rating

st.set_page_config(layout="wide")
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

st.write(len(st.query_params))
if st.query_params=="{}":
    st.error("You must be logged in to access this page.")
    st.stop()  # Stops the app execution here if the user is not logged in.

# Update session state based on the URL parameter
if st.query_params["logged_in"] == "true":
    st.session_state.logged_in = True
else:
    st.error("You must be logged in to access this page.")
    st.stop()  # Stops the app execution here if the user is not logged in.
    st.session_state.logged_in = False

# Check if the user is logged in
#if "logged_in" not in st.session_state or not st.session_state.logged_in:


# Main app content
st.title("Welcome to the Bob's List!")

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

# ---- Query contractor companies ----
def get_contractor_companies(conn):
    query = """
    SELECT contractor_id, contractor_name as name
    FROM test.public.contractors 
    ORDER BY name
    """
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    return [{"label": name, "contractor_id": cid} for cid, name in rows]

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

st.title("Rating customers..")

contractors = get_contractor_companies(conn)

# Create label list for dropdown
contractor_labels = [c["label"] for c in contractors]
selected_label = st.selectbox("Contractor Company:", contractor_labels)
# Retrieve ID of selected contractor
selected_contractor = next((c for c in contractors if c["label"] == selected_label), None)
 #Debuggingif selected_contractor:    
                #st.info(f"Selected Contractor ID: {selected_contractor['contractor_id']}")

col_0, col_1 = st.columns([1,2])
with col_0:
    engagement_type = st.selectbox("Type of work:", ["Electrical", "Painting", "Plumbing", "Power Wash", "Handyman", "Misc"])
with col_1:
    activity_date = st.date_input("Performed on:", value=date.today())

# Form fields
with st.form("engagement_form"):

    col_name, col_ignore = st.columns([1,1])
    with col_name:
        customer_name = st.text_input("Customer Name:")
    with col_ignore:
        st.write("")

    col4, col1, col2, col3 = st.columns([2, 1, 1, 1])
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



    # Inside your form
    col_rating, col_feedback = st.columns([1, 3])
    with col_rating:
        rating = st.selectbox("Star rating:", ["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"])
        star_rating = len(rating)
        #star_rating = st_star_rating(label="Customer Rating", maxValue=5, defaultValue=3, key="rating")

    with col_feedback:
        feedback = st.text_area("Additional feedback (from last activity):")


    submitted = st.form_submit_button("Submit")

    if submitted:
        if not (customer_name and street and city and zip_code):
            st.warning("Please fill out all required fields.")
        else:
            insert_sql = """
                INSERT INTO TEST.PUBLIC.engagements (
                    contractor_id, customer_name, street, city, state, zip_code, 
                    engagement_type, activity_date, rating, feedback
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cur.execute(insert_sql, (
                selected_contractor['contractor_id'], customer_name, street, city, state, zip_code,
                engagement_type, activity_date.isoformat(), star_rating, feedback
            ))
            conn.commit()
            st.success("Submission saved to Snowflake.")

flag_to_display = 0
if flag_to_display:
# Retrieve and display existing data
    st.subheader("All Engagements:")
    cur.execute("SELECT * FROM TEST.PUBLIC.engagements ORDER BY submitted_at DESC")
    df = cur.fetch_pandas_all()
    st.dataframe(df, use_container_width=True)

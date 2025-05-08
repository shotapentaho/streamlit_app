import streamlit as st
import snowflake.connector
import pandas as pd
from datetime import date

st.set_page_config(layout="wide")
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

st.write()
if len(st.query_params)> 1:
     # Update session state based on the URL parameter
    if st.query_params["logged_in"] == "true":
        st.session_state.logged_in = True      
else:
    st.error("You must be logged in to access this page.")
    st.stop()  # Stops the app execution here if the user is not logged in.
    st.session_state.logged_in = False


# Connect to Snowflake using Streamlit secrets
def get_connection():
    return snowflake.connector.connect(
        user=st.secrets["snowflake"]["user"],
        password=st.secrets["snowflake"]["password"],
        account=st.secrets["snowflake"]["account"],
        warehouse=st.secrets["snowflake"]["warehouse"],
        database=st.secrets["snowflake"]["database"],
        schema=st.secrets["snowflake"]["schema"]
    )

# Check password received in URL
def is_valid_user(hash_password_str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT username FROM TEST.PUBLIC.users WHERE hashed_password = %s", (hash_password_str,))
    row = cur.fetchone()
    if not row:
        return False, None
    else:
        username = row
        return True, username
    return False, None

user_exists = is_valid_user (st.query_params["password"])
if (user_exists[0] == False):
    st.error("You must be logged in to access this page.")
    st.stop()  # Stops the app execution here if the user is not logged in.
    st.session_state.logged_in = False


conn = get_connection()
cur = conn.cursor()

st.title("Analyze, search, download data..")

# Retrieve and display existing data
st.subheader("All Engagements:")
cur.execute("""SELECT cont.contractor_name, eng.customer_name, eng.street, eng.city, eng.state, eng.zip_code, eng.engagement_type, eng.activity_date,
            eng.rating,eng.feedback
            FROM TEST.PUBLIC.engagements as eng INNER JOIN TEST.PUBLIC.contractors cont ON cont.contractor_id = eng.contractor_id
            ORDER BY cont.contractor_name, eng.activity_date DESC;
        """)

df = cur.fetch_pandas_all()
st.dataframe(df, use_container_width=True)

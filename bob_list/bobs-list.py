import streamlit as st
import st_contractor_feedback
import st_contractor_view_analyze

st.set_page_config(page_title="Customer Xperiences..", layout="wide")

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
def is_valid_user(user_str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT username FROM TEST.PUBLIC.users WHERE username = %s", (user_str,))
    row = cur.fetchone()
    if not row:
        return False, None
    else:
        username = row
        return True, username
    return False, None

user_exists = is_valid_user (st.query_params["username"])
if (user_exists[0] == False):
    st.error("You must be logged in to access this page.")
    st.stop()  # Stops the app execution here if the user is not logged in.
    st.session_state.logged_in = False

cxloop_tabs = st.tabs(["Customer Feedback", "View Analyze Feedbacks"])

with cxloop_tabs[0]:
    st_contractor_feedback.render()

with cxloop_tabs[1]:
    st_contractor_view_analyze.render()



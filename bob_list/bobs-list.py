import streamlit as st
import st_contractor_feedback
import st_contractor_view_analyze

st.set_page_config(page_title="Customer Xperiences..", layout="wide")

cxloop_tabs = st.tabs(["Customer Feedback", "View Analyze Feedbacks"])

with cxloop_tabs[0]:
    st_contractor_feedback.render()

with cxloop_tabs[1]:
    st_contractor_view_analyze.render()


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

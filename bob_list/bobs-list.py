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

cxloop_tabs = st.tabs(["Customer Feedback", "View Analyze Feedbacks"])

with cxloop_tabs[0]:
    st_contractor_feedback.render()

with cxloop_tabs[1]:
    st_contractor_view_analyze.render()
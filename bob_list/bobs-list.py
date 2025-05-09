import streamlit as st
import st_contractor_feedback
import st_contractor_view_analyze

#st.set_page_config(layout="wide")

tabs = st.tabs(["Customer Feedback", "View Analyze Feedbacks"])

with tabs[0]:
    st.write("You are on the Feedback")

    st_contractor_feedback.render()


with tabs[1]:
    st.write("You are on the View Analysis")

    st_contractor_view_analyze.render()
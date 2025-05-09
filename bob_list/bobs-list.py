import streamlit as st
import st_contractor_feedback as cx_feedback
import st_contractor_view_analyze as cx_analyze

#st.set_page_config(layout="wide")

cxloop_tabs = st.tabs(["Customer Feedback", "View Analyze Feedbacks"])

with cxloop_tabs[0]:
    st.write("You are on the Feedback")
    cx_feedback.render()


with cxloop_tabs[1]:
    st.write("You are on the View Analysis")
    cx_analyze.render()
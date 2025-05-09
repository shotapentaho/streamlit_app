import streamlit as st
import st_contractor_feedback
import st_contractor_view_analyze

st.set_page_config(layout="wide")

cxloop_tabs = st.tabs(["Customer Feedback", "View Analyze Feedbacks"])

with cxloop_tabs[0]:

    st_contractor_feedback.render()


with cxloop_tabs[1]:

    st_contractor_view_analyze.render()
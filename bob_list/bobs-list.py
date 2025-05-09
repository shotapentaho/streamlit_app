import streamlit as st
import st_contractor_feedback as cx_feedback
import st_contractor_view_analyze as cx_analyze

st.set_page_config(page_title="Customer Experiences", layout="wide")

cxloop_tabs = st.tabs(["Customer Feedback", "View Analyze Feedbacks"])

with cxloop_tabs[0]:

    cx_feedback.render()


with cxloop_tabs[1]:

    cx_analyze.render()
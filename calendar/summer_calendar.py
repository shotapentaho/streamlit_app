import streamlit as st
from streamlit_calendar import calendar
from datetime import date
import uuid

st.set_page_config(page_title="Summer Calendar 2025", layout="wide")

if "events" not in st.session_state:
    st.session_state["events"] = []

with st.sidebar:
    st.header("Add Activity")
    with st.form("add", clear_on_submit=True):
        title = st.text_input("Activity")
        event_date = st.date_input("Date", value=date(2025,6,21))
        submit = st.form_submit_button("Add")
        if submit and title:
            st.session_state["events"].append({
                "id": str(uuid.uuid4()),
                "title": title,
                "start": str(event_date),  # MUST be string
                "end": str(event_date)
            })
            st.rerun()

st.title("Summer Calendar 2025")

calendar(
    events=st.session_state["events"],
    options={
        "initialView": "dayGridMonth",
        "initialDate": "2025-06-21",
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek"
        },
        "height": 600,
    },
    key="calendar_grid"
)
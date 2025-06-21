import streamlit as st
from streamlit_calendar import calendar
from datetime import date
import uuid

st.set_page_config(page_title="Summer Calendar 2025", layout="wide")

if "events" not in st.session_state:
    st.session_state["events"] = []

st.title("Summer Calendar 2025")

with st.sidebar:
    st.header("Add Activity (as Text)")
    with st.form("add_activity", clear_on_submit=True):
        text = st.text_input("Enter activity (e.g. Tennis or Chemistry)")
        event_date = st.date_input("Date", value=date(2025, 6, 21))
        submit = st.form_submit_button("Add")
        if submit and text:
            event = {
                "id": str(uuid.uuid4()),
                "title": text,  # Just the raw text, no color/category
                "start": str(event_date),
                "end": str(event_date)
            }
            st.session_state["events"].append(event)
            st.rerun()

calendar(
    events=st.session_state["events"],
    options={
        "initialView": "dayGridMonth",
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek"
        },
        "editable": False,
        "selectable": False,
        "initialDate": "2025-06-21",
        "height": 650
    },
    key="calendar_grid_text"
)
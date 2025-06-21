import streamlit as st
from streamlit_calendar import calendar
from datetime import date
import uuid

st.set_page_config(page_title="Summer Calendar 2025", layout="wide")

CATEGORIES = {
    "Tennis": "#4CAF50",
    "Chemistry": "#9C27B0",
    "Physics": "#3F51B5",
    "Math": "#F44336",
    "Swimming": "#03A9F4",
    "Coding": "#FF9800",
    "Other": "#607D8B"
}

if "events" not in st.session_state:
    st.session_state["events"] = []

with st.sidebar:
    st.header("Add Activity")
    with st.form("add_activity", clear_on_submit=True):
        title = st.text_input("Title")
        activity = st.selectbox("Category", list(CATEGORIES.keys()))
        event_date = st.date_input("Date", value=date(2025, 6, 21))
        submit = st.form_submit_button("Add")
        if submit and title:
            event = {
                "id": str(uuid.uuid4()),
                "title": f"{title} ({activity})",
                "start": str(event_date),  # <-- must be string!
                "end": str(event_date),
                "color": CATEGORIES[activity]
            }
            st.session_state["events"].append(event)
            st.rerun()

st.title("Summer Calendar 2025")

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
    key="calendar_grid"
)

st.subheader("All Activities")
for idx, event in enumerate(st.session_state["events"]):
    col1, col2 = st.columns([5, 1])
    with col1:
        st.write(f"**{event['title']}** on {event['start']}")
    with col2:
        if st.button("🗑️ Delete", key=f"del-{event['id']}"):
            st.session_state["events"].pop(idx)
            st.rerun()
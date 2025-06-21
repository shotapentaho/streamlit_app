import streamlit as st
from streamlit_calendar import calendar
from datetime import date

st.title("Calendar: Add Event by Button (Shows as Tile)")

if "events" not in st.session_state:
    st.session_state["events"] = []

add_form = st.button("➕ Add Event")

if add_form:
    with st.form("add_event_form", clear_on_submit=True):
        event_title = st.text_input("Event Title")
        event_date = st.date_input("Event Date", value=date.today())
        submit = st.form_submit_button("Add Event")
        if submit and event_title:
            # append as dict with required keys
            st.session_state["events"].append({
                "title": event_title,
                "start": str(event_date),
                "end": str(event_date),
                "color": "blue"
            })
            st.experimental_rerun()

# Show calendar with all events as tiles
calendar(
    events=st.session_state["events"],
    options={
        "selectable": False,
        "initialView": "dayGridMonth",
        "editable": False
    },
    key="calendar"
)

if st.session_state["events"]:
    st.subheader("All Events:")
    st.json(st.session_state["events"])
else:
    st.info("Click the 'Add Event' button to create your first event.")
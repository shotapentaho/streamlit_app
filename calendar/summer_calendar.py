import streamlit as st
from streamlit_calendar import calendar
from datetime import date

st.title("Calendar: Add & Delete Events by Button")

if "events" not in st.session_state:
    st.session_state["events"] = []

# Add event via button and form
if st.button("➕ Add Event"):
    with st.form("add_event_form", clear_on_submit=True):
        event_title = st.text_input("Event Title")
        event_date = st.date_input("Event Date", value=date.today())
        submit = st.form_submit_button("Add Event")
        if submit and event_title:
            st.session_state["events"].append({
                "title": event_title,
                "start": str(event_date),
                "end": str(event_date),
                "color": "blue"
            })
            st.experimental_rerun()

# Render the calendar, events show as tiles
calendar(
    events=st.session_state["events"],
    options={
        "selectable": False,
        "initialView": "dayGridMonth",
        "editable": False
    },
    key="calendar"
)

# List events with delete buttons
if st.session_state["events"]:
    st.subheader("All Events:")
    # Show each event with a delete button
    for idx, event in enumerate(st.session_state["events"]):
        col1, col2 = st.columns([5, 1])
        with col1:
            st.write(f"**{event['title']}** on {event['start']}")
        with col2:
            if st.button("🗑️ Delete", key=f"del_{idx}"):
                st.session_state["events"].pop(idx)
                st.experimental_rerun()
else:
    st.info("Click the 'Add Event' button to create your first event.")
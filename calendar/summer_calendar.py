import streamlit as st
from streamlit_calendar import calendar
from datetime import datetime, date

st.title("Calendar with Add Event Button")

if "events" not in st.session_state:
    st.session_state["events"] = []

# Show the Add Event form when button is clicked
show_form = st.button("➕ Add Event")

if show_form:
    with st.form("add_event_form", clear_on_submit=True):
        event_title = st.text_input("Event Title")
        event_date = st.date_input("Event Date", value=date.today())
        submit = st.form_submit_button("Add Event")
        if submit and event_title:
            st.session_state["events"].append(
                {
                    "title": event_title,
                    "start": str(event_date),
                    "end": str(event_date),
                    "color": "blue"
                }
            )
            st.experimental_rerun()

# Display the calendar grid with current events
calendar(
    events=st.session_state["events"],
    options={
        "selectable": False,      # No need to select a day, since using button/form
        "initialView": "dayGridMonth",
        "editable": False         # Only add via button/form
    },
    key="calendar"
)

if st.session_state["events"]:
    st.subheader("All Events:")
    st.json(st.session_state["events"])
else:
    st.info("Click the 'Add Event' button to create your first event.")
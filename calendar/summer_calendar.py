import streamlit as st
from streamlit_calendar import calendar
from datetime import datetime

st.title("Click a day to add an event to the calendar")

# Store events in session state
if "events" not in st.session_state:
    st.session_state["events"] = []

# Render the calendar
calendar_output = calendar(
    events=st.session_state["events"],
    options={
        "selectable": True,  # Allows day selection
        "initialView": "dayGridMonth",
    },
    custom_css="""
    .fc-event { font-size: 14px; }
    """,
    key="calendar"
)

# If user selects a day, show a form to add an event
if calendar_output and "select" in calendar_output:
    selected_date = calendar_output["select"]["start"][:10]  # YYYY-MM-DD
    with st.form("Add Event"):
        st.markdown(f"**Add event for `{selected_date}`**")
        title = st.text_input("Event Title")
        submit = st.form_submit_button("Add")
        if submit and title:
            st.session_state["events"].append(
                {
                    "title": title,
                    "start": selected_date,
                    "end": selected_date,
                    "color": "green"
                }
            )
            # Rerun to refresh the calendar with new event
            st.experimental_rerun()

if st.session_state["events"]:
    st.subheader("All Events:")
    st.json(st.session_state["events"])
else:
    st.info("Click a calendar day to add your first event.")

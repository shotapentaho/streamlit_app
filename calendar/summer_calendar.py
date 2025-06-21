import streamlit as st
from streamlit_calendar import calendar
from datetime import datetime

st.title("Editable Streamlit Calendar")

# Store events in session state
if "events" not in st.session_state:
    st.session_state["events"] = []

# Render the calendar with editing enabled
calendar_output = calendar(
    events=st.session_state["events"],
    options={
        "selectable": True,      # Allows selecting days to add events
        "editable": True,        # Allows editing events (drag, resize, etc.)
        "eventClick": True,      # Allows detecting event clicks for editing
        "initialView": "dayGridMonth"
    },
    key="calendar"
)

# Handle adding a new event by clicking a day
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
            st.experimental_rerun()

# Handle event edits (move/resize/title change)
if calendar_output and "eventChange" in calendar_output:
    # eventChange returns the full list of events after edit
    st.session_state["events"] = calendar_output["eventChange"]
    st.experimental_rerun()

# Handle event click for editing title
if calendar_output and "eventClick" in calendar_output:
    idx = calendar_output["eventClick"]["event"]["_st_event_idx"]
    with st.form("Edit Event"):
        st.markdown(f"**Edit event on `{st.session_state['events'][idx]['start']}`**")
        title = st.text_input("Event Title", value=st.session_state["events"][idx]["title"])
        submit = st.form_submit_button("Save")
        if submit and title:
            st.session_state["events"][idx]["title"] = title
            st.experimental_rerun()

if st.session_state["events"]:
    st.subheader("All Events:")
    st.json(st.session_state["events"])
else:
    st.info("Click a calendar day to add your first event.")

import streamlit as st
from streamlit_calendar import calendar
from datetime import datetime

st.title("Interactive Calendar: Click a Day to Add Item")

if "events" not in st.session_state:
    st.session_state["events"] = []

# Show the calendar, enable day-click selection
calendar_output = calendar(
    events=st.session_state["events"],
    options={
        "selectable": True,
        "editable": True,
        "initialView": "dayGridMonth"
    },
    key='calendar'
)

# calendar_output will contain selection info if user clicks/drag-selects a day/time
if calendar_output and "select" in calendar_output:
    selected_date = calendar_output["select"]["start"][:10]  # format: YYYY-MM-DD
    with st.form("Add Event"):
        st.write(f"Add item for {selected_date}")
        title = st.text_input("Event Title")
        submit = st.form_submit_button("Add")
        if submit and title:
            st.session_state["events"].append(
                {
                    "title": title,
                    "start": selected_date,
                    "end": selected_date
                }
            )
            # Rerun to update calendar immediately
            st.experimental_rerun()

st.subheader("Current Events")
st.write(st.session_state["events"])
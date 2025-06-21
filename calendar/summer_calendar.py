import streamlit as st
from streamlit_calendar import calendar
from datetime import datetime

st.title("Streamlit Calendar: Add & Edit Events via Click")

if "events" not in st.session_state:
    st.session_state["events"] = []

calendar_output = calendar(
    events=st.session_state["events"],
    options={
        "selectable": True,        # Allow day selection
        "initialView": "dayGridMonth",
        "eventClick": True         # Enable event click detection
    },
    key="calendar"
)

# Add event by clicking a date
if calendar_output and "select" in calendar_output:
    selected_date = calendar_output["select"]["start"][:10]
    with st.form("add_event_form", clear_on_submit=True):
        st.write(f"Add event for {selected_date}")
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

# Edit event by clicking on it
if calendar_output and "eventClick" in calendar_output:
    event = calendar_output["eventClick"]["event"]
    idx = event.get("_st_event_idx")
    if idx is not None and idx < len(st.session_state["events"]):
        with st.form("edit_event_form", clear_on_submit=True):
            st.write(f"Edit event on {st.session_state['events'][idx]['start']}")
            new_title = st.text_input("Event Title", value=st.session_state["events"][idx]["title"])
            submit_edit = st.form_submit_button("Update")
            if submit_edit and new_title:
                st.session_state["events"][idx]["title"] = new_title
                st.experimental_rerun()

if st.session_state["events"]:
    st.subheader("All Events:")
    st.json(st.session_state["events"])
else:
    st.info("Click a calendar day to add your first event.")

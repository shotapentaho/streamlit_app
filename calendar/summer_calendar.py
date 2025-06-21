import streamlit as st
from streamlit_calendar import calendar

st.title("Test Calendar: Click a Day to Add Event")

if "events" not in st.session_state:
    st.session_state["events"] = []

calendar_output = calendar(
    events=st.session_state["events"],
    options={
        "selectable": True,
        "initialView": "dayGridMonth"
    },
    key="calendar"
)

if calendar_output and "select" in calendar_output:
    selected_date = calendar_output["select"]["start"][:10]
    with st.form("Add Event"):
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

if st.session_state["events"]:
    st.subheader("All Events:")
    st.json(st.session_state["events"])
else:
    st.info("Click a calendar day to add your first event.")
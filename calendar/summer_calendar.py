import streamlit as st
from streamlit_calendar import calendar
from datetime import date
import uuid

st.set_page_config(page_title="Vedant Summer Calendar: 2025", layout="wide")

# Activity categories and colors
ACTIVITY_COLORS = {
    "Tennis": "#4CAF50",      # green
    "Chemistry": "#9C27B0",   # purple
    "Physics": "#3F51B5",     # indigo
    "Math": "#F44336",        # red
    "Swimming": "#03A9F4",    # light blue
    "Coding": "#FF9800",      # orange
    "Biology": "#009688",     # teal
    "Other": "#607D8B"        # blue gray
}

st.title("Summer Calendar 2025")

if "events" not in st.session_state:
    st.session_state["events"] = []

with st.sidebar:
    st.header("Add New Activity")
    with st.form("add_event_form", clear_on_submit=True):
        event_title = st.text_input("Activity Title")
        event_date = st.date_input("Date", value=date(2025, 6, 21))
        event_category = st.selectbox("Activity Type", list(ACTIVITY_COLORS.keys()))
        notes = st.text_area("Notes", height=80)
        submit = st.form_submit_button("Add to Calendar")
        if submit and event_title:
            event_id = str(uuid.uuid4())
            new_event = {
                "id": event_id,
                "title": f"{event_title} ({event_category})",
                "start": str(event_date),
                "end": str(event_date),
                "color": ACTIVITY_COLORS[event_category],
                "category": event_category,
                "notes": notes
            }
            st.session_state["events"].append(new_event)
            st.rerun()

st.markdown("#### Your Summer Activities (Grid View)")
calendar(
    events=st.session_state["events"],
    options={
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,listWeek"
        },
        "initialView": "dayGridMonth",
        "selectable": False,
        "editable": False,
        "initialDate": "2025-06-21",
        "height": 650,
    },
    key="summer_calendar"
)

if st.session_state["events"]:
    st.subheader("All Events (List)")
    for idx, event in enumerate(st.session_state["events"]):
        col1, col2 = st.columns([5, 1])
        with col1:
            st.write(f"**{event['title']}** on {event['start']}")
            if event.get("notes"):
                st.caption(event["notes"])
        with col2:
            if st.button("🗑️ Delete", key=f"del_{event['id']}"):
                st.session_state["events"].pop(idx)
                st.rerun()
else:
    st.info("No activities yet. Add one from the sidebar !")
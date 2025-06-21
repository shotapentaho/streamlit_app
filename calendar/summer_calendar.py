import streamlit as st
from streamlit_calendar import calendar
from datetime import date, datetime
import uuid

st.set_page_config(page_title="Summer Calendar 2025", layout="wide")

# Activity categories and colors
ACTIVITY_COLORS = {
    "Tennis": "#4CAF50",
    "Chemistry": "#9C27B0",
    "Physics": "#3F51B5",
    "Math": "#F44336",
    "Swimming": "#03A9F4",
    "Coding": "#FF9800",
    "Biology": "#009688",
    "Other": "#607D8B"
}

st.title("Summer Calendar 2025")

if "events" not in st.session_state:
    st.session_state["events"] = []

# Helper: Get event by id
def get_event_by_id(event_id):
    for i, event in enumerate(st.session_state["events"]):
        if event["id"] == event_id:
            return i, event
    return None, None

# ---- SIDEBAR: Add or Edit ----
with st.sidebar:
    st.header("Add or Edit Activity")

    # Check if user is editing (set via session_state)
    edit_id = st.session_state.get("edit_id", None)
    editing = edit_id is not None

    if editing:
        idx, event = get_event_by_id(edit_id)
        if event:
            default_title = event["title"].rsplit(" (",1)[0]
            default_date = date.fromisoformat(event["start"])
            default_category = event["category"]
            default_notes = event.get("notes", "")
        else:
            # fallback
            editing = False
    else:
        default_title = ""
        default_date = date(2025, 6, 21)
        default_category = list(ACTIVITY_COLORS.keys())[0]
        default_notes = ""

    with st.form("event_form", clear_on_submit=True):
        event_title = st.text_input("Activity Title", value=default_title)
        event_date = st.date_input("Date", value=default_date)
        event_category = st.selectbox("Activity Type", list(ACTIVITY_COLORS.keys()), index=list(ACTIVITY_COLORS.keys()).index(default_category))
        notes = st.text_area("Notes", value=default_notes, height=80)
        submit = st.form_submit_button("Save")
        cancel = st.form_submit_button("Cancel Edit") if editing else False

        if submit and event_title:
            if editing and event:
                # Update event in-place
                st.session_state["events"][idx] = {
                    "id": edit_id,
                    "title": f"{event_title} ({event_category})",
                    "start": str(event_date),
                    "end": str(event_date),
                    "color": ACTIVITY_COLORS[event_category],
                    "category": event_category,
                    "notes": notes
                }
                st.session_state["edit_id"] = None
            else:
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
        if cancel:
            st.session_state["edit_id"] = None
            st.rerun()

# ---- CALENDAR ----
st.markdown("#### Your Summer Activities (Grid View)")
cal_result = calendar(
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
        "eventClick": True
    },
    key="summer_calendar"
)

# ---- EVENT LIST WITH EDIT & DELETE ----
if st.session_state["events"]:
    st.subheader("All Events (List)")
    for idx, event in enumerate(st.session_state["events"]):
        col1, col2, col3 = st.columns([4, 1, 1])
        with col1:
            st.write(f"**{event['title']}** on {event['start']}")
            if event.get("notes"):
                st.caption(event["notes"])
        with col2:
            if st.button("✏️ Edit", key=f"edit_{event['id']}"):
                st.session_state["edit_id"] = event["id"]
                st.rerun()
        with col3:
            if st.button("🗑️ Delete", key=f"del_{event['id']}"):
                st.session_state["events"].pop(idx)
                # If deleting the one being edited, reset edit_id
                if st.session_state.get("edit_id") == event["id"]:
                    st.session_state["edit_id"] = None
                st.rerun()
else:
    st.info("No activities yet. Add one from the sidebar!")

# ---- HANDLE CALENDAR EVENT CLICK TO EDIT ----
if cal_result and "eventClick" in cal_result:
    event_id = cal_result["eventClick"]["event"]["id"]
    st.session_state["edit_id"] = event_id
    st.rerun()
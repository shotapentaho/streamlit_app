import streamlit as st
import pandas as pd
from pathlib import Path
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import streamlit.components.v1 as components

DATA_DIR = Path("./data")
DATA_DIR.mkdir(exist_ok=True)
CSV_FILE = DATA_DIR / "summer_cal.csv"

st.set_page_config(page_title="Editable Calendar Schedule", layout="wide")

# --- Load or initialize data ---
if CSV_FILE.exists():
    df = pd.read_csv(CSV_FILE)
else:
    df = pd.DataFrame([
        {"Title": "Tennis", "Date": "2025-06-24", "Start": "09:00", "End": "10:00"},
        {"Title": "Chemistry", "Date": "2025-06-25", "Start": "10:15", "End": "11:15"},
        {"Title": "Math", "Date": "2025-06-26", "Start": "13:00", "End": "14:30"},
        {"Title": "Physics", "Date": "2025-06-27", "Start": "08:30", "End": "09:30"},
        {"Title": "Biology", "Date": "2025-06-28", "Start": "11:00", "End": "12:00"},
    ])
    df.to_csv(CSV_FILE, index=False)

st.title("📅 Editable Schedule with Calendar Grid")

# --- Editable Table with st-aggrid ---
st.subheader("Edit Schedule Table")

gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(editable=True)
gb.configure_grid_options(rowSelection='multiple')
grid_options = gb.build()

grid_response = AgGrid(
    df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.VALUE_CHANGED,
    fit_columns_on_grid_load=True,
    enable_enterprise_modules=False,
    height=320,
    reload_data=False,
)

new_df = grid_response['data']
if not new_df.equals(df):
    new_df.to_csv(CSV_FILE, index=False)
    st.success("Table updated and saved.")

# --- Add New Event ---
with st.expander("Add New Event"):
    with st.form("add_event", clear_on_submit=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1: title = st.text_input("Title")
        with col2: date = st.date_input("Date")
        with col3: start = st.text_input("Start (HH:MM)")
        with col4: end = st.text_input("End (HH:MM)")
        add = st.form_submit_button("Add")
        if add and title and date and start and end:
            row = pd.DataFrame([{
                "Title": title,
                "Date": str(date),
                "Start": start,
                "End": end
            }])
            df2 = pd.concat([new_df, row], ignore_index=True)
            df2.to_csv(CSV_FILE, index=False)
            st.success("Event added. Please refresh the page to see it in the calendar.")

# --- Delete Selected Rows ---
if grid_response['selected_rows'] is not None and len(grid_response['selected_rows']) > 0:
    if st.button("Delete selected events"):
        selected = pd.DataFrame(grid_response['selected_rows'])
        df2 = new_df[~new_df.isin(selected).all(axis=1)]
        df2.to_csv(CSV_FILE, index=False)
        st.success("Selected events deleted. Please refresh to see changes.")

# --- Calendar Grid View ---
st.subheader("Calendar Grid View")

# Prepare events for FullCalendar
events = []
for idx, row in new_df.iterrows():
    try:
        events.append({
            "id": str(idx),
            "title": row["Title"],
            "start": f"{row['Date']}T{row['Start']}",
            "end": f"{row['Date']}T{row['End']}",
            "allDay": False,
        })
    except Exception:
        continue

calendar_events = str(events).replace("'", '"')
calendar_html = f"""
<link href="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.11/index.global.min.css" rel="stylesheet"/>
<div id="calendar"></div>
<script src="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.11/index.global.min.js"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {{
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {{
        initialView: 'dayGridMonth',
        height: 720,
        events: {calendar_events},
        headerToolbar: {{
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek'
        }},
    }});
    calendar.render();
}});
</script>
"""

components.html(calendar_html, height=760)

with st.expander("Show Raw Data Table"):
    st.dataframe(new_df)
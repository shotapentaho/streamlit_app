import streamlit as st
import pandas as pd
from pathlib import Path
import streamlit.components.v1 as components

st.set_page_config(page_title="Calendar Grid from CSV", layout="wide")

CSV_FILE = Path("./data/summer_cal.csv")
if not CSV_FILE.exists():
    st.error("summer_cal.csv not found in ./data directory.")
    st.stop()

df = pd.read_csv(CSV_FILE)
df.columns = [c.strip().capitalize() for c in df.columns]
needed = ["Title", "Date", "Start", "End"]
if not all(col in df.columns for col in needed):
    st.error("CSV must have columns: Title, Date, Start, End")
    st.dataframe(df)
    st.stop()

events = []
for idx, row in df.iterrows():
    try:
        start = f"{row['Date']}T{row['Start']}"
        end = f"{row['Date']}T{row['End']}"
        events.append({
            "id": str(idx),
            "title": row["Title"],
            "start": start,
            "end": end,
            "allDay": False,
        })
    except Exception as e:
        st.warning(f"Problem with row {idx}: {e}")

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

st.title("📅 Calendar Grid View from summer_cal.csv")
components.html(calendar_html, height=760)
import streamlit as st
import pandas as pd
from pathlib import Path
import streamlit.components.v1 as components

st.set_page_config(page_title="Calendar Grid from CSV", layout="wide")

CSV_FILE = Path("./data/summer_cal.csv")
if not CSV_FILE.exists():
    st.error("summer_cal.csv not found.")
    st.stop()

df = pd.read_csv(CSV_FILE)
# Normalize column names in case user wrote 'title', 'date', etc.
df.columns = [c.strip().capitalize() for c in df.columns]
needed = ["Title", "Date", "Start", "End"]
if not all(col in df.columns for col in needed):
    st.error("CSV must have columns: Title, Date, Start, End")
    st.dataframe(df)
    st.stop()

# Convert to FullCalendar event objects
events = []
for idx, row in df.iterrows():
    date = str(row["Date"])
    start = f"{date}T{row['Start']}"
    end = f"{date}T{row['End']}"
    events.append({
        "id": str(idx),
        "title": row["Title"],
        "start": start,
        "end": end,
        "description": f"{row['Title']}<br>{date} {row['Start']}-{row['End']}"
    })

# FullCalendar HTML/JS code
calendar_events = str(events).replace("'", '"')
calendar_html = f"""
<link href="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.11/index.global.min.css" rel="stylesheet"/>
<div id="calendar"></div>
<script src="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.11/index.global.min.js"></script>
<script src="https://unpkg.com/tippy.js@6"></script>
<style>
#calendar {{
    max-width: 1100px;
    margin: 40px auto;
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(60,60,60,0.10);
    padding: 12px;
}}
.fc .fc-daygrid-day-frame {{
    background: #f8fafc;
    border-radius: 6px;
    transition: background 0.2s;
}}
.fc .fc-daygrid-day-frame:hover {{
    background: #e0e7ef;
}}
</style>
<script>
document.addEventListener('DOMContentLoaded', function() {{
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {{
        initialView: 'dayGridMonth',
        height: 780,
        events: {calendar_events},
        eventMouseEnter: function(info) {{
            if (info.event.extendedProps.description) {{
                if (!info.el._tippy) {{
                    tippy(info.el, {{
                        content: info.event.extendedProps.description,
                        allowHTML: true,
                        arrow: true,
                        placement: 'top',
                        theme: 'light-border',
                    }});
                }}
            }}
        }},
        headerToolbar: {{
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek'
        }},
        nowIndicator: true
    }});
    calendar.render();
}});
</script>
"""

st.title("📅 Calendar Grid View from summer_cal.csv")
components.html(calendar_html, height=850)

with st.expander("Show Data Table"):
    st.dataframe(df)
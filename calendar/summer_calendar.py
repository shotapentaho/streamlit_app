import streamlit as st
import pandas as pd
from pathlib import Path
import streamlit.components.v1 as components

st.set_page_config(page_title="Actual Calendar Grid (FullCalendar)", layout="wide")

CSV_FILE = Path("./data/summer_cal.csv")
if not CSV_FILE.exists():
    st.error("summer_cal.csv not found in current directory.")
    st.stop()

df = pd.read_csv(CSV_FILE)
# Normalize column names
df.columns = [c.strip().capitalize() for c in df.columns]
required_cols = ["Title", "Date", "Start", "End"]
if not all(col in df.columns for col in required_cols):
    st.error(f"CSV must have columns: {', '.join(required_cols)}")
    st.dataframe(df)
    st.stop()

# Build events for FullCalendar
events = []
for idx, row in df.iterrows():
    title = str(row["Title"])
    date = str(row["Date"])
    start_time = str(row["Start"])
    end_time = str(row["End"])
    start = f"{date}T{start_time}"
    end = f"{date}T{end_time}"
    events.append({
        "id": str(idx),
        "title": title,
        "start": start,
        "end": end,
        "allDay": False,
        "description": f"{title} {date} {start_time}-{end_time}"
    })

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
    box-shadow: 0 2px 8px rgba(60,60,60,0.1);
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

st.title("Actual Calendar Grid View (with Calendar Tiles)")
components.html(calendar_html, height=850)

with st.expander("Show Data Table"):
    st.dataframe(df)
import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import streamlit.components.v1 as components

st.set_page_config(page_title="Actual Calendar Grid", layout="wide")

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

# FullCalendar HTML/JS
calendar_events = str(events).replace("'", '"')
calendar_html = f"""
<link href="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.11/index.global.min.css" rel="stylesheet"/>
<div id="calendar"></div>
<script src="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.11/index.global.min.js"></script>
<script src="https://unpkg.com/popper.js@1"></script>
<script src="https://unpkg.com/tippy.js@6"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {{
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {{
        initialView: 'dayGridMonth',
        height: 750,
        events: {calendar_events},
        eventMouseEnter: function(info) {{
            // Show tooltip on hover
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
        eventDidMount: function(info) {{
            // Optionally show tooltip always on mount
        }},
        headerToolbar: {{
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek'
        }}
    }});
    calendar.render();
}});
</script>
"""

st.title("Actual Calendar Grid View")
components.html(calendar_html, height=800)

with st.expander("Show Data Table"):
    st.dataframe(df)
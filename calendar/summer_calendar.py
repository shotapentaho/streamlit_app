import streamlit as st
import pandas as pd
from streamlit_calendar import calendar
from io import StringIO
from pathlib import Path

st.title("Show Timetable from summer_cal.csv in Calendar")

# --- Use summer_cal.csv from current directory ---
csv_path = Path("summer_cal.csv")
if csv_path.exists():
    df = pd.read_csv(csv_path)
    source_note = "Loaded from summer_cal.csv in current directory."
else:
    # Fallback sample data if file missing
    sample_content = """title,date,start_time,end_time
Tennis,2025-06-24,09:00,10:00
Chemistry,2025-06-25,10:15,11:15
Math,2025-06-26,13:00,14:30
Physics,2025-06-27,08:30,09:30
Biology,2025-06-28,11:00,12:00
"""
    df = pd.read_csv(StringIO(sample_content))
    source_note = "summer_cal.csv not found. Loaded with sample data."

# Add weekday column (e.g. Mon, Tue, ...)
df["day"] = pd.to_datetime(df["date"]).dt.strftime('%a')

st.info(source_note)
st.write("Preview Table with Day of Week", df)

# Build events for calendar
events = []
for idx, row in df.iterrows():
    # Compose title: Title (Day)
    title = f"{row['title']} ({row['day']})"
    # Use date with (optional) time
    if pd.notnull(row.get("start_time", None)) and row["start_time"] != "":
        start = f"{row['date']}T{row['start_time']}"
        if pd.notnull(row.get("end_time", None)) and row["end_time"] != "":
            end = f"{row['date']}T{row['end_time']}"
        else:
            end = start
    else:
        start = str(row["date"])
        end = str(row["date"])
    events.append({
        "id": str(idx),
        "title": title,
        "start": start,
        "end": end,
    })

st.markdown("### Calendar View")
calendar(
    events=events,
    options={
        "initialView": "dayGridMonth",
        "initialDate": str(df['date'].min()) if len(df) > 0 else "2025-06-21",
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek"
        },
        "height": 650
    },
    key="calendar_from_duckdb_day"
)
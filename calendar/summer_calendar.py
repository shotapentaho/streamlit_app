import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="Schedule Calendar", layout="wide")

# ---- Read CSV ----
CSV_FILE = Path("./data/summer_cal.csv")
if CSV_FILE.exists():
    df = pd.read_csv(CSV_FILE)
    source_note = "Loaded from summer_cal.csv in current directory."
else:
    st.error("summer_cal.csv not found in current directory.")
    st.stop()

# ---- Prepare events ----
# Assumption: columns are Title, Date, Start, End (case-insensitive)
df.columns = [c.strip().capitalize() for c in df.columns]
if not all(col in df.columns for col in ["Title", "Date", "Start", "End"]):
    st.error("CSV must have columns: Title, Date, Start, End")
    st.dataframe(df)
    st.stop()

# Add weekday column for display
df["Day"] = pd.to_datetime(df["Date"]).dt.strftime('%a')

# Build events for calendar grid (using Plotly Timeline as workaround)
# Each event: x0=start, x1=end, y=title, color=day
events = []
for idx, row in df.iterrows():
    date_str = str(row["Date"])
    start_time = str(row["Start"])
    end_time = str(row["End"])
    try:
        start_dt = pd.to_datetime(f"{date_str} {start_time}")
        end_dt = pd.to_datetime(f"{date_str} {end_time}")
    except Exception:
        continue
    events.append(dict(
        Task=f"{row['Title']} ({row['Day']})",
        Start=start_dt,
        Finish=end_dt,
    ))

if not events:
    st.warning("No valid events found.")
else:
    import plotly.express as px
    evdf = pd.DataFrame(events)
    st.markdown("### Calendar Grid (Gantt-style)")
    fig = px.timeline(
        evdf, 
        x_start="Start", x_end="Finish", y="Task", 
        color="Task", 
        title="Schedule Calendar Grid"
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        height=max(500, 70 * len(evdf)),
        xaxis_title=None,
        yaxis_title=None,
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

# Show table for reference
with st.expander("Show Data Table"):
    st.dataframe(df)
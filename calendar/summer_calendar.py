import streamlit as st
import pandas as pd
import snowflake.connector
import datetime
from streamlit_calendar import calendar

st.set_page_config(page_title="VH: Summer Schedule", layout="wide")

# --- Snowflake connection settings ---
SNOWFLAKE_USER = st.secrets["snowflake"]["user"]
SNOWFLAKE_PASSWORD = st.secrets["snowflake"]["password"]
SNOWFLAKE_ACCOUNT = st.secrets["snowflake"]["account"]
SNOWFLAKE_WAREHOUSE = st.secrets["snowflake"]["warehouse"]
SNOWFLAKE_DATABASE = st.secrets["snowflake"]["database"]
SNOWFLAKE_SCHEMA = st.secrets["snowflake"]["schema"]
TABLE_NAME = "SUMMER_SCHEDULE"

def get_connection():
    return snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA
    )

def get_events():
    with get_connection() as conn:
        df = pd.read_sql(f"SELECT * FROM {TABLE_NAME} ORDER BY DATE, START_TIME", conn)
    return df

def insert_event(activity, date, start_time, end_time):
    with get_connection() as conn:
        conn.cursor().execute(
            f"INSERT INTO {TABLE_NAME} (ACTIVITY, DATE, START_TIME, END_TIME) VALUES (%s, %s, %s, %s)",
            (activity, date, start_time, end_time)
        )

def delete_event(row_id):
    with get_connection() as conn:
        conn.cursor().execute(
            f"DELETE FROM {TABLE_NAME} WHERE ID = %s", (row_id,)
        )

st.title("🌞 Summer Schedule Calendar")

col1, col2 = st.columns([1,2])

with col1:
    st.header("Manage Activities")
    with st.form("add_activity", clear_on_submit=True):
        activity = st.text_input("Activity")
        date = st.date_input("Date")
        start_time = st.time_input("Start Time (HH:MM)", value=datetime.time(9, 0))
        end_time = st.time_input("End Time (HH:MM)", value=datetime.time(10, 0))
        add = st.form_submit_button("Add")
        if add and activity and date and start_time and end_time:
            # Convert to 'HH:MM' format for DB
            insert_event(
                activity,
                str(date),
                start_time.strftime("%H:%M"),
                end_time.strftime("%H:%M")
            )
            st.success("Activity added!")
            st.rerun()

    df = get_events()
    st.subheader("Delete Activity")

    # Create nicely labeled options for delete dropdown
    if not df.empty:
        delete_options = [
            (
                f'{row["ACTIVITY"]} ({row["DATE"]} {row["START_TIME"]}-{row["END_TIME"]})',  # label
                str(row["ID"])                                                               # value
            )
            for _, row in df.iterrows()
        ]
        selected = st.selectbox(
            "Select activity to delete",
            options=delete_options,
            format_func=lambda x: x[0] if isinstance(x, tuple) else x,
            key="delete_activity"
        )
        delete_id = selected[1] if selected else None

        if st.button("Delete Activity") and delete_id:
            delete_event(delete_id)
            st.success("Activity deleted!")
            st.rerun()
    else:
        st.info("No activities available to delete.")

with col2:
    st.header("Calendar View")
    df = get_events()
    # Convert to calendar events format
    events = []
    for _, row in df.iterrows():
        # Defensive: ensure proper time format
        start = f'{row["DATE"]}T{row["START_TIME"]}'
        end = f'{row["DATE"]}T{row["END_TIME"]}'
        events.append({
            "title": row["ACTIVITY"],
            "start": start,
            "end": end,
        })
    calendar_options = {
        "initialView": "timeGridWeek",
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,timeGridDay"
        },
        "editable": False,
        "selectable": False,
    }
    calendar(events=events, options=calendar_options)
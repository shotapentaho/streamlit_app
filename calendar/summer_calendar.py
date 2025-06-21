import streamlit as st
import pandas as pd
import snowflake.connector
from streamlit_calendar import calendar
st.set_page_config(page_title="Summer Schedule Calendar", layout="wide")

# --- Snowflake connection settings (as before) ---
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
        start_time = st.text_input("Start Time (HH:MM)")
        end_time = st.text_input("End Time (HH:MM)")
        add = st.form_submit_button("Add")
        if add and activity and date and start_time and end_time:
            insert_event(activity, str(date), start_time, end_time)
            st.success("Activity added!")
            st.rerun()

    df = get_events()
    st.subheader("Delete Activity")
    delete_id = st.selectbox("Select activity to delete", options=df["ID"].astype(str))
    if st.button("Delete Activity"):
        delete_event(delete_id)
        st.success("Activity deleted!")
        st.rerun()


with col2:
    st.header("Calendar View")
    df = get_events()
    st.write("Loaded data:", df)  # Debug -- remove if not needed
    events = []
    for _, row in df.iterrows():
        # Defensive: check that all fields exist
        if all(k in row for k in ("ACTIVITY", "DATE", "START_TIME", "END_TIME")):
            events.append({
                "title": row["ACTIVITY"],
                "start": f'{row["DATE"]}T{str(row["START_TIME"]).zfill(5)}',
                "end": f'{row["DATE"]}T{str(row["END_TIME"]).zfill(5)}',
            })
    st.write("Calendar events:", events)  # Debug -- remove once working

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

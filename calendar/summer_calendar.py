import streamlit as st
import pandas as pd
import snowflake.connector

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

# --- Streamlit UI ---
st.title("🌞 Summer Schedule (Snowflake-backed)")

df = get_events()
st.dataframe(df)

with st.expander("Add New Activity"):
    with st.form("add_activity", clear_on_submit=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1: activity = st.text_input("Activity")
        with col2: date = st.date_input("Date")
        with col3: start_time = st.text_input("Start Time (HH:MM)")
        with col4: end_time = st.text_input("End Time (HH:MM)")
        add = st.form_submit_button("Add")
        if add and activity and date and start_time and end_time:
            insert_event(activity, str(date), start_time, end_time)
            st.success("Activity added!")
            st.rerun()

# Optional: Delete activities by selecting their IDs
delete_id = st.text_input("Delete activity by ID (optional)")
if st.button("Delete Activity") and delete_id:
    delete_event(delete_id)
    st.success("Activity deleted!")
    st.rerun()
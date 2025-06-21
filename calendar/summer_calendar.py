import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from pathlib import Path

st.set_page_config(page_title="Schedule Table (Persistent)", layout="wide")

CSV_FILE = Path("./data/summer_cal.csv")

# Load or create data
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

st.title("Editable Schedule Table (Persistent)")

# Editable grid
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
    height=350,
    width='100%',
    reload_data=False,
)

# Save whenever changed
new_df = grid_response['data']
if not new_df.equals(df):
    new_df.to_csv(CSV_FILE, index=False)
    st.info("Changes saved to summer_cal.csv.")

# Add new row
with st.form("add_row", clear_on_submit=True):
    st.write("Add a new entry")
    col1, col2, col3, col4 = st.columns(4)
    with col1: title = st.text_input("Title")
    with col2: date = st.date_input("Date")
    with col3: start = st.text_input("Start (HH:MM)")
    with col4: end = st.text_input("End (HH:MM)")
    add = st.form_submit_button("Add")
    if add and title and date and start and end:
        new_row = pd.DataFrame([{
            "Title": title,
            "Date": str(date),
            "Start": start,
            "End": end
        }])
        df = pd.concat([new_df, new_row], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)
        st.rerun()

# Delete selected rows
if grid_response['selected_rows']:
    if st.button("Delete selected rows"):
        selected = pd.DataFrame(grid_response['selected_rows'])
        df = new_df[~new_df.isin(selected).all(axis=1)]
        df.to_csv(CSV_FILE, index=False)
        st.rerun()
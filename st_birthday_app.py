import streamlit as st
import pandas as pd
import duckdb
from datetime import datetime

DB_FILE = "birthdays.duckdb"

# Connect to DuckDB
con = duckdb.connect(DB_FILE)

# Initialize table
con.execute("""
CREATE TABLE IF NOT EXISTS birthdays (
    name TEXT,
    birthday DATE
)
""")

# Helper functions
def add_birthday(name, birthday):
    con.execute("INSERT INTO birthdays (name, birthday) VALUES (?, ?)", (name, birthday))

def get_birthdays():
    return con.execute("SELECT * FROM birthdays").fetchdf()

def get_today_birthdays():
    today = datetime.today().strftime('%m-%d')
    return con.execute("""
        SELECT * FROM birthdays 
        WHERE strftime('%m-%d', birthday) = ?
    """, (today,)).fetchdf()

# UI
st.title("🎂 Birthday Reminder App")

# Check for today's birthdays
st.subheader("🎉 Birthdays Today")
today_bdays = get_today_birthdays()

if not today_bdays.empty:
    for _, row in today_bdays.iterrows():
        st.success(f"🎈 Wish {row['name']} a Happy Birthday!")
else:
    st.info("No birthdays today.")

# Add birthday form
st.subheader("➕ Add a Birthday")
with st.form("birthday_form"):
    name = st.text_input("Name")
    birthday = st.date_input("Birthday")
    submitted = st.form_submit_button("Add Birthday")

    if submitted:
        if name:
            add_birthday(name, birthday.strftime('%Y-%m-%d'))
            st.success(f"Added birthday for {name}")
        else:
            st.warning("Please enter a name.")

# Show all birthdays
st.subheader("📋 All Birthdays")
all_birthdays = get_birthdays()
st.dataframe(all_birthdays)

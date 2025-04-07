import streamlit as st
import pandas as pd
import duckdb
from datetime import datetime

DB_FILE = "birthdays.duckdb"
con = duckdb.connect(DB_FILE)

# Create table if not exists
con.execute("""
CREATE TABLE IF NOT EXISTS birthdays (
    name TEXT,
    birthday DATE
)
""")

# Helpers
def get_birthdays():
    return con.execute(""" 
                                    SELECT name, strftime('%m-%d', birthday) AS month_day, birthday,
                                        CAST(strftime('%Y', CURRENT_DATE) AS INTEGER) - CAST(strftime('%Y', birthday) AS INTEGER)
                                        - CASE 
                                            WHEN strftime('%m-%d', CURRENT_DATE) < strftime('%m-%d', birthday) THEN 1 
                                            ELSE 0 
                                        END AS age
                                    FROM birthdays 
                                    ORDER BY name asc
                                    """).fetchdf()

def get_today_birthdays():
    today = datetime.today().strftime('%m-%d')
    return con.execute("""
        SELECT * FROM birthdays 
        WHERE strftime('%m-%d', birthday) = ?
    """, (today,)).fetchdf()

def get_currentmonth_bdays():
    current_month = datetime.today().strftime('%m')
    return con.execute("""
        SELECT 
            name, 
            birthday,
            strftime('%m-%d', birthday) AS month_day
        FROM birthdays
        WHERE strftime('%m', birthday) = ?
        ORDER BY strftime('%d', birthday) ASC
    """, (current_month,)).fetchdf()

def add_birthday(name, birthday):
    existing = con.execute("SELECT COUNT(*) FROM birthdays WHERE name = ?", (name,)).fetchone()[0]
    if existing > 0:
        return False  # Duplicate found
    con.execute("INSERT INTO birthdays (name, birthday) VALUES (?, ?)", (name, birthday))
    return True

def update_birthday(old_name, new_name, new_birthday):
    con.execute("""
        UPDATE birthdays 
        SET name = ?, birthday = ? 
        WHERE name = ?
    """, (new_name, new_birthday, old_name))

# UI
current_month_abbr = datetime.today().strftime('%B')  # e.g., 'April'
st.set_page_config(layout="wide")
st.title(f"🎂 🎉Happy '{current_month_abbr}' Birthdays !!🎈 🎉")


# Birthday (month)
#st.subheader("📅 Birthdays this month!!")
current_month_bdays = get_currentmonth_bdays()

if not current_month_bdays.empty:
    for _, row in current_month_bdays.iterrows():
        st.header(f"{row['name']} 🎂 {row['month_day']}")
else:
    st.info("No birthdays this month.")

# Birthdays today
#st.subheader("🎉 Birthdays Today")
#today_bdays = get_today_birthdays()
#if not today_bdays.empty:
#    for _, row in today_bdays.iterrows():
#        st.success(f"🎈 Wish {row['name']} a Happy Birthday!")
#else:
#    st.info("No birthdays today.")

# UI display_or_no control
display_all_bdays=1
display_add_edit=1

if display_all_bdays:    
    # Load all birthdays
    df = get_birthdays()
    df = df.drop(columns=["age"])
    st.subheader("📋 All Birthdays")
    st.dataframe(df)

if display_add_edit:
    # Add new birthday
    st.subheader("➕ Add Birthday!!")
    with st.form("add_form"):
        col1, col2 = st.columns([3,1])
        with col1:
            name = st.text_input("New Member!!")
        with col2:
            birthday = st.date_input(
                "New Birthday",
                min_value=datetime(1900, 1, 1),
                max_value=datetime(2100, 12, 31)
            )
        submitted = st.form_submit_button("Add Birthday")
        if submitted:
            add_birthday(name, birthday.strftime('%Y-%m-%d'))
            st.success(f"Added {name}'s birthday!")
            st.rerun()

    # Select a name to edit
    st.subheader("✏️ Edit someone's birthday??")
    names = sorted(df["name"].tolist())
    if names:
        selected_name = st.selectbox("Let's edit somone!!", names)
        selected_row = df[df["name"] == selected_name].iloc[0]
        
        with st.form("edit_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input("Name", value=selected_row["name"])
            with col2:
                new_birthday = st.date_input(
                    "Birthday",
                    value=pd.to_datetime(selected_row["birthday"]),
                    min_value=datetime(1900, 1, 1),
                    max_value=datetime(2100, 12, 31)
                )
            save_changes = st.form_submit_button("Save Changes")

            if save_changes:
                update_birthday(selected_name, new_name, new_birthday.strftime('%Y-%m-%d'))
                st.success(f"Updated {selected_name}'s birthday!")
                st.rerun()
    else:
        st.info("No entries to edit.")


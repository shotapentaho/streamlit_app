import streamlit as st
import pandas as pd
import duckdb
from datetime import datetime

st.set_page_config(page_title="👨‍👩‍👧‍👦 Family-fun Anniversaries",layout="wide")

DB_FILE = "anniversaries.duckdb"
if "con" not in st.session_state:
    st.session_state.con = duckdb.connect(DB_FILE)

#Connection Object
con = st.session_state.con
con.execute(""" DROP TABLE IF EXISTS anniversaries """)
con.execute("""
            CREATE TABLE anniversaries AS
            SELECT * FROM read_csv_auto('./data/anniversary_export.csv', HEADER=TRUE)
            """)

# Helpers
def get_anniversaries():
    return con.execute(""" 
                                    SELECT name, strftime('%m-%d', wed_anniversary_day) AS month_day, wed_anniversary_day,
                                        CAST(strftime('%Y', CURRENT_DATE) AS INTEGER) - CAST(strftime('%Y', wed_anniversary_day) AS INTEGER)
                                        - CASE 
                                            WHEN strftime('%m-%d', CURRENT_DATE) < strftime('%m-%d', wed_anniversary_day) THEN 1 
                                            ELSE 0 
                                        END AS age
                                    FROM anniversaries 
                                    ORDER BY name asc
                                    """).fetchdf()

def get_today_anniversaries():
    today = datetime.today().strftime('%m-%d')
    return con.execute("""
        SELECT * FROM anniversaries 
        WHERE strftime('%m-%d', wed_anniversary_day) = ?
    """, (today,)).fetchdf()

def get_currentmonth_anniversaries():
    current_month = datetime.today().strftime('%m')
    return con.execute("""
        SELECT 
            name, 
            wed_anniversary_day,
            strftime('%m-%d', wed_anniversary_day) AS month_day
        FROM anniversaries
        WHERE strftime('%m', wed_anniversary_day) = ?
        ORDER BY strftime('%d', wed_anniversary_day) ASC
    """, (current_month,)).fetchdf()

def add_wed_anniversary_day(name, wed_anniversary_day):
    existing = con.execute("SELECT COUNT(*) FROM anniversaries WHERE name = ?", (name,)).fetchone()[0]
    if existing > 0:
        return False  # Duplicate found
    con.execute("INSERT INTO anniversaries (name, wed_anniversary_day) VALUES (?, ?)", (name, wed_anniversary_day))
    return True

def update_wed_anniversary_day(old_name, new_name, new_wed_anniversary_day):
    con.execute("""
        UPDATE anniversaries 
        SET name = ?, wed_anniversary_day = ? 
        WHERE name = ?
    """, (new_name, new_wed_anniversary_day, old_name))

# UI
current_month_abbr = datetime.today().strftime('%B')  # e.g., 'April'
st.title(f"🎂 🎉Happy '{current_month_abbr}' anniversaries !!🎈 🎉")
#st.audio("https://www2.cs.uic.edu/~i101/SoundFiles/Happywed_anniversary_day.mp3", format='audio/mp3')

# wed_anniversary_day (month)
current_month_anniversaries = get_currentmonth_anniversaries()

if not current_month_anniversaries.empty:    
    st.balloons()   # 🎈 balloons!
    for _, row in current_month_anniversaries.iterrows():
        st.header(f"{row['name']} 🎂 {row['month_day']}")
else:
    st.info("No anniversaries this month.")

# UI Control Sections: [display_all_anniversaries] AND [display_add_edit]
display_all_anniversaries=1


if display_all_anniversaries:    
    # Load all anniversaries
    df = get_anniversaries()
    df = df.drop(columns=["age"])
    st.subheader("📋 Family Fun wale!! 🎉")
    st.dataframe(df)

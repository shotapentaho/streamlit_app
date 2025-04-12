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

# get_anniversaries
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

# UI
current_month_abbr = datetime.today().strftime('%B')  # e.g., 'April'
st.title(f"🎂 🎉Happy '{current_month_abbr}' anniversaries !!🎈 🎉")

# wed_anniversary_day (month)
current_month_anniversaries = get_currentmonth_anniversaries()

if not current_month_anniversaries.empty:    
    st.balloons()   # 🎈 balloons!
    for _, row in current_month_anniversaries.iterrows():
        st.header(f"{row['name']} 🎂 {row['month_day']}")
else:
    st.info("No anniversaries this month.")

# UI Control Sections: [display_all_anniversaries]
display_all_anniversaries=1

if display_all_anniversaries:    
    # Load all anniversaries
    df = get_anniversaries()
    df = df.drop(columns=["age"])
    st.subheader("📋 Family Fun wale!! 🎉")
    st.dataframe(df)

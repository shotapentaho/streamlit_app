import streamlit as st
import pandas as pd
from datetime import datetime
import os

DATA_FILE = "birthdays.csv"

# Initialize the data file if it doesn't exist
if not os.path.exists(DATA_FILE):
    df_init = pd.DataFrame(columns=["Name", "Birthday"])
    df_init.to_csv(DATA_FILE, index=False)

# Load data
def load_birthdays():
    return pd.read_csv(DATA_FILE)

# Save data
def save_birthday(name, birthday):
    df = load_birthdays()
    new_entry = pd.DataFrame([[name, birthday]], columns=["Name", "Birthday"])
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

# Streamlit App
st.title("🎂 Birthday Reminder App")

# Birthday Notification
today = datetime.today().strftime("%m-%d")
df = load_birthdays()
today_bdays = df[df["Birthday"].str[5:] == today]

if not today_bdays.empty:
    st.subheader("🎉 Birthdays Today!")
    for _, row in today_bdays.iterrows():
        st.success(f"Wish {row['Name']} a happy birthday!")
else:
    st.info("No birthdays today.")

# Add Birthday Form
st.subheader("➕ Add a Birthday")
with st.form("birthday_form"):
    name = st.text_input("Name")
    birthday = st.date_input("Birthday (YYYY-MM-DD)")
    submitted = st.form_submit_button("Add")
    
    if submitted:
        if name:
            save_birthday(name, birthday.strftime("%Y-%m-%d"))
            st.success(f"Added {name}'s birthday!")
        else:
            st.warning("Please enter a name.")

# Show All Birthdays
st.subheader("📋 All Birthdays")
df = load_birthdays()
st.dataframe(df)

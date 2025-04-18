import streamlit as st
import datetime
import smtplib
import duckdb
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from apscheduler.schedulers.background import BackgroundScheduler
import time
import pandas as pd


# Initialize DuckDB and create table
conn = duckdb.connect(database='tennis_reminder.db', read_only=False)

# Function to fetch reminders
def fetch_reminders():
    result = conn.execute("SELECT * FROM reminders").fetchall()
    return result
    
# Function to delete selected reminders
def delete_reminders(selected_ids):
    for reminder_id in selected_ids:
        conn.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
    st.success("Selected reminders have been deleted.")
    
# Display reminders with checkboxes
def display_reminders():
    reminders = fetch_reminders()
    
    if reminders:
        # Create a pandas dataframe
        df = pd.DataFrame(reminders, columns=['ID', 'Game', 'Date', 'Time', 'Phone', 'Carrier', 'Notes'])

        # Display reminder list with checkboxes for deletion
        selected_ids = []
        for index, row in df.iterrows():
            checkbox = st.checkbox(f"Select {row['Game']} ({row['Date']}{' '}{row['Time']})", key=row['ID'])
            if checkbox:
                selected_ids.append(row['ID'])

        # Display the DataFrame in Streamlit
        st.write("### Current Reminders:")
        st.dataframe(df)

        # Button to delete selected reminders
        if st.button('Delete Selected Reminders'):
            if selected_ids:
                delete_reminders(selected_ids)
                # Refresh the reminder list after deletion
                st.rerun()
            else:
                st.warning("No reminders selected for deletion.")
    else:
        st.write("No reminders found.")


conn.execute("""
    CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY,
        practice_game TEXT,
        practice_date DATE,
        practice_time TIME,
        phone_number TEXT,
        carrier TEXT,
        notes TEXT
    )
""")

# Streamlit UI
st.set_page_config(page_title="Game Practice Reminder (SMS)", layout="wide")
st.title("🎾 Practice Reminder (via SMS)")

# Input Fields
game = st.selectbox("Select Your Game:", ["Tennis", "Volly", "Pickle Ball", "Gym"])
practice_date = st.date_input("Select Practice Date:", datetime.date.today())
practice_time = st.time_input("Select Practice Time:", datetime.time(14, 0))  # Default 2PM
phone_number = st.text_input("Enter Your Phone Number (USA/Canada Only):", placeholder="1234567890")
carrier = st.selectbox("Select Your Carrier:", ["AT&T", "Verizon", "T-Mobile", "Sprint", "Rogers", "Bell"])
notes = st.text_area("Add Notes (Optional)", placeholder="E.g., Bring extra water, practice serves.")

# Carrier Email Mapping
carrier_gateways = {
    "AT&T": "@txt.att.net",
    "Verizon": "@vtext.com",
    "T-Mobile": "@tmomail.net",
    "Sprint": "@messaging.sprintpcs.com",
    "Rogers": "@pcs.rogers.com",
    "Bell": "@txt.bell.ca"
}

def get_next_id():
    # Get the current maximum ID from the table
    result = conn.execute("SELECT MAX(id) FROM reminders").fetchone()
    # If there's no data yet, start with 1
    return (result[0] or 0) + 1
    
# Function to Save Reminder to DuckDB
def save_reminder(game, date, time, phone, carrier, notes):
    next_id = get_next_id()
    conn.execute("""
        INSERT INTO reminders (id, practice_game, practice_date, practice_time, phone_number, carrier,  notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (next_id, game, date, time, phone, carrier, notes))

# Function to Send SMS
def send_sms(to_phone, carrier, date, time, notes):
    if carrier not in carrier_gateways:
        st.error("⚠️ Invalid carrier selected.")
        return False

    sender_email = st.secrets["credentials"]["email"]
    sender_password = st.secrets["credentials"]["password"]
    
    to_sms = f"{to_phone}{carrier_gateways[carrier]}"
    subject = "🎾 Tennis Reminder"
    body = f"Reminder: Practice {game} on {date} at {time}. Notes: {notes}"

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_sms
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_sms, msg.as_string())
        st.success("✅ Reminder SMS Sent!")
        return True
    except Exception as e:
        st.error(f"❌ SMS sending failed: {e}")
        return False

# Function to Schedule Reminder
def schedule_reminder():
    now = datetime.datetime.now()
    practice_datetime = datetime.datetime.combine(practice_date, practice_time)
    reminder_time = practice_datetime - datetime.timedelta(hours=1)
    time_until_reminder = (reminder_time - now).total_seconds()

    if time_until_reminder > 0:
        st.success(f"⏳ Reminder scheduled for {reminder_time.strftime('%Y-%m-%d %H:%M:%S')}")
        #time.sleep(time_until_reminder)  # Wait until the reminder time
        send_sms(phone_number, carrier, practice_date, practice_time, notes)
        st.rerun()
    else:
        st.warning("⚠️ Selected practice time is in the past!")
        st.rerun()

# Scheduler Setup
scheduler = BackgroundScheduler()
scheduler.start()

# Set Reminder Button
if st.button("Set Reminder via SMS "):
    if phone_number and carrier:        
        save_reminder(game, practice_date, practice_time, phone_number, carrier, notes)
        schedule_reminder()       
    else:
        st.warning("⚠️ Please enter a valid phone number and carrier.")

# Display Saved Reminders
st.subheader("📜 Reminder History")
reminders = conn.execute("SELECT * FROM reminders ORDER BY practice_date DESC").fetchall()
if reminders:
    for reminder in reminders:
        st.write(f"📅 {reminder[1]} ⏰ {reminder[2]} 📱 {reminder[3]} ({reminder[4]}) 📝 {reminder[5]}")
else:
    st.write("No reminders set.")

# Display reminders in the Streamlit app
if __name__ == '__main__':
    st.title('Current Reminders')
    display_reminders()
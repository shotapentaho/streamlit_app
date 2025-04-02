import streamlit as st
import datetime
import smtplib
import duckdb
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from apscheduler.schedulers.background import BackgroundScheduler
import time

# Initialize DuckDB and create table
conn = duckdb.connect(database=':memory:', read_only=False)
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

# Function to Save Reminder to DuckDB
def save_reminder(game, date, time, phone, carrier, notes):
    conn.execute("""
        INSERT INTO reminders (practice_game, practice_date, practice_time, phone_number, carrier, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (game, date, time, phone, carrier, notes))

# Function to Send SMS
def send_sms(to_phone, carrier, date, time, notes):
    if carrier not in carrier_gateways:
        st.error("⚠️ Invalid carrier selected.")
        return False

    sender_email = st.secrets["credentials"]["email"]
    sender_password = st.secrets["credentials"]["password"]
    
    to_sms = f"{to_phone}{carrier_gateways[carrier]}"
    subject = "🎾 Tennis Reminder"
    body = f"Reminder: Practice on {date} at {time}. Notes: {notes}"

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
        time.sleep(time_until_reminder)  # Wait until the reminder time
        send_sms(phone_number, carrier, practice_date, practice_time, notes)
    else:
        st.warning("⚠️ Selected practice time is in the past!")

# Scheduler Setup
scheduler = BackgroundScheduler()
scheduler.start()

# Set Reminder Button
if st.button("Set Reminder via SMS (1 Hour Before)"):
    if phone_number and carrier:
        game='tennis'
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

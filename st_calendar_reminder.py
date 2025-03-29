import streamlit as st
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Streamlit UI
st.set_page_config(page_title="Tennis Reminder (SMS)", layout="wide")
st.title("🎾 Tennis Practice Reminder (SMS)")

# Input Fields
practice_date = st.date_input("Select Practice Date:", datetime.date.today())
practice_time = st.time_input("Select Practice Time:", datetime.time(18, 0))  # Default 6 PM
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

# Function to Send SMS
def send_sms(to_phone, carrier, date, time, notes):
        sender_email = st.secrets["credentials"]["email"]
        sender_password = st.secrets["credentials"]["password"]

    if carrier not in carrier_gateways:
        st.error("⚠️ Invalid carrier selected.")
        return False

    to_sms = f"{to_phone}{carrier_gateways[carrier]}"
    subject = "🎾 Tennis Reminder"
    body = f"Practice on {date} at {time}. Notes: {notes}"

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
        return True
    except Exception as e:
        st.error(f"❌ SMS sending failed: {e}")
        return False

# Set Reminder Button
if st.button("Set Reminder via SMS"):
    if phone_number and carrier:
        success = send_sms(phone_number, carrier, practice_date, practice_time, notes)
        if success:
            st.success(f"✅ SMS Reminder set for {practice_date} at {practice_time}!")
    else:
        st.warning("⚠️ Please enter a valid phone number and carrier.")

# Display Upcoming Practice
st.subheader("⏳ Upcoming Practice:")
st.write(f"📅 **Date:** {practice_date}")
st.write(f"⏰ **Time:** {practice_time}")
if notes:
    st.write(f"📝 **Notes:** {notes}")

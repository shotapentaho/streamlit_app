import streamlit as st
import snowflake.connector
import hashlib
from datetime import datetime

# Connect to Snowflake
@st.cache_resource


def get_connection():
    return snowflake.connector.connect(
        user=st.secrets["snowflake"]["user"],
        password=st.secrets["snowflake"]["password"],
        account=st.secrets["snowflake"]["account"],
        warehouse=st.secrets["snowflake"]["warehouse"],
        database=st.secrets["snowflake"]["database"],
        schema=st.secrets["snowflake"]["schema"]
    )

conn = get_connection()
cur = conn.cursor()

# Hash passwords securely
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Register a new user
def register_user(username, password, full_name):
    hashed = hash_password(password)
    cur.execute("SELECT COUNT(*) FROM TEST.PUBLIC.users WHERE username = %s", (username,))
    exists = cur.fetchone()[0]
    if exists:
        return False, "Username already exists."
    cur.execute("""
        INSERT INTO users (username, hashed_password, full_name)
        VALUES (%s, %s, %s)
    """, (username, hashed, full_name))
    conn.commit()
    return True, "User registered successfully."

# Check login
def authenticate_user(username, password):
    cur.execute("SELECT hashed_password, full_name FROM TEST.PUBLIC.users WHERE username = %s", (username,))
    row = cur.fetchone()
    if not row:
        return False, None
    stored_hash, full_name = row
    if hash_password(password) == stored_hash:
        return True, full_name
    return False, None

# Session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "full_name" not in st.session_state:
    st.session_state.full_name = ""

# UI
st.title("🔐 User Login / Register")

tab = st.radio("Choose action", ["Login", "Register"])

if tab == "Login":
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        valid, full_name = authenticate_user(username, password)
        if valid:
            st.session_state.logged_in = True
            st.session_state.full_name = full_name
            st.success(f"Welcome, {full_name}!")
            st.experimental_rerun()
        else:
            st.error("Invalid username or password.")

else:
    st.subheader("Register")
    new_username = st.text_input("Choose a username")
    new_password = st.text_input("Choose a password", type="password")
    full_name = st.text_input("Your full name")
    if st.button("Register"):
        ok, msg = register_user(new_username, new_password, full_name)
        if ok:
            st.success(msg)
        else:
            st.warning(msg)

# If logged in
if st.session_state.logged_in:
    st.success(f"Hello {st.session_state.full_name}, you're logged in!")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()

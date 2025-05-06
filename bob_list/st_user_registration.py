import streamlit as st
import snowflake.connector

# Snowflake connection function
def get_connection():
    return snowflake.connector.connect(
        user=st.secrets["snowflake"]["user"],
        password=st.secrets["snowflake"]["password"],
        account=st.secrets["snowflake"]["account"],
        warehouse=st.secrets["snowflake"]["warehouse"],
        database=st.secrets["snowflake"]["database"],
        schema=st.secrets["snowflake"]["schema"]
    )

# Function to validate user credentials from Snowflake
def validate_user(username, password, conn):
    query = f"SELECT COUNT(*) FROM users WHERE username = '{username}' AND password = '{password}'"
    cur = conn.cursor()
    cur.execute(query)
    result = cur.fetchone()
    cur.close()
    return result[0] > 0

# Check login status
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Login form
if not st.session_state.logged_in:
    st.title("Login to Access the App")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        conn = get_connection()
        if validate_user(username, password, conn):
            st.session_state.logged_in = True
            st.success("Login successful! Redirecting to the main app...")
            # Redirect to the main app
            st.experimental_rerun()
        else:
            st.error("Invalid credentials!")

# Once logged in, show confirmation or user options
if st.session_state.logged_in:
    st.success(f"Welcome {username}! You're logged in.")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

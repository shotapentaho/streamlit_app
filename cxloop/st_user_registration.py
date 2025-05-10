hide_default_footer = """
    <style>
    footer, .st-emotion-cache-1gulkj5 {display: none; visibility: hidden;}
    .css-qri22k {display: none; visibility: hidden;}
    .stDeployButton {display: none;}
    .viewerBadge_link__1S137 {display: none;}
    </style>
"""
hide_default_header = """
        <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """
import streamlit as st
st.set_page_config(page_title="Customer Xperiences..", layout="wide")
st.markdown(hide_default_footer, unsafe_allow_html=True)
st.markdown(hide_default_header, unsafe_allow_html=True)

import snowflake.connector
import hashlib
from datetime import datetime
import stripe
import os

# Register a new user
def register_user(username, password, contracting_company_name):
    hashed = hash_password(password)
    cur.execute("SELECT COUNT(*) FROM TEST.PUBLIC.users WHERE username = %s AND full_name = %s", (username, contracting_company_name))
    exists = cur.fetchone()[0]
    if exists:
        return False, "User already exists, pick a different user."
    cur.execute("""
        INSERT INTO TEST.PUBLIC.users (username, hashed_password, password_raw, full_name)
        VALUES (%s, %s, %s, %s)
    """, (username, hashed, password, contracting_company_name))
    conn.commit()
    return True, "User registered successfully."

# Register a new user
def add_contractor(contracting_company_name, contracting_company_street, contracting_company_city, contracting_company_state, contracting_company_zip):
    
    cur.execute("""
        INSERT INTO TEST.PUBLIC.contractors (contractor_id, contractor_name, street, city, state, zip)
        VALUES (TEST.PUBLIC.contractor_seq.NEXTVAL, %s, %s, %s, %s, %s)
    """, (contracting_company_name, contracting_company_street, contracting_company_city, contracting_company_state, contracting_company_zip))
    conn.commit()
    return True, "Contractor details inserted successfully."

stripe.api_key = st.secrets["stripe"]["secret_key"]
CXLOOP_APP_URL = "https://cxloop-enter.streamlit.app/" 

# ⬇️ Handle success from Stripe at the top
if st.query_params.get("page") == "success":
    session_id = st.query_params.get("session_id")

    if session_id:
        st.write(f"Success page loaded with session ID: {session_id}")
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == "paid":
                st.write(f"session.payment_status: {session.payment_status}")
                user_data = st.session_state.get("pending_user")
                st.write(f"user_data: {user_data}")
                if user_data:
                    ok, msg = register_user(user_data["username"], user_data["password"], user_data["name"])
                    if ok:
                        add_contractor(
                            user_data["name"],
                            user_data["street"],
                            user_data["city"],
                            user_data["state"],
                            user_data["zip"]
                        )
                        st.success("🎉 Registration complete! You may now log in.")
                        del st.session_state["pending_user"]
                    else:
                        st.warning(msg)
            else:
                st.error("⚠️ Payment was not completed.")
        except Exception as e:
            st.error(f"Something went wrong: {e}")
    #st.stop()  # Prevent the rest of the app from rendering on success page
    else:
        st.error("⚠️ No session ID found in the URL.")
        st.stop()  # Prevent the rest of the app from rendering on success page

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
#st.set_page_config(layout="wide")
st.title(" 🔐 👷 🔄 Contractor Xperiences.. login or register(new here)")


tab = st.radio("Choose:", ["Login", "Register", "Forgot Password"])


if tab == "Login":
    #st.subheader("Contractor  to login:")

    if not st.session_state.logged_in:
        #st.title("Login existing contractor.")

        col_0, col_1 = st.columns([1,2])
        with col_0:
            username = st.text_input("Username")
        with col_1:
            password = st.text_input("Password", type="password")
        if st.button("Login"):
            valid, full_name = authenticate_user(username, password)
            if valid:
                URL_TO_CUSTOMER_EXPERIENCE = "https://cxloop.streamlit.app?logged_in=true&username="+ username
                #URL_TO_FEEDBACK = "https://bobs-list.streamlit.app?logged_in=true&password="+ hash_password(password)
                #URL_TO_VIEW_ANALYZE = "https://bobs-analyze.streamlit.app?logged_in=true&password="+ hash_password(password)
                
                st.markdown(f"""
                    <a href="{URL_TO_CUSTOMER_EXPERIENCE}" target="_target">
                        <button style='font-size:30px;padding:10px 20px;margin-top:20px;'>Share your customer experiences..</button>
                    </a> 
                    """, unsafe_allow_html=True)
               
            else:
                st.error("Invalid username or password. If you are not registered, please register first.")

if tab == "Register":

    st.subheader("Register your company to use the service:")
    col_0, col_1 = st.columns([1,1])
    with col_0:
        new_username = st.text_input("Username:")
    with col_1:
        new_password = st.text_input("Password:", type="password")

    #Company Details
    col_11, col_12 = st.columns([1,1])
    with col_11:
        contracting_company_name = st.text_input("Contracting Company:")
    with col_12:
        contracting_company_email = st.text_input("Email:")

    col_3, col_4, col_5, col_6= st.columns([1,1,1,1])
    
    with col_3:
        contracting_company_street = st.text_input("Street:")
    with col_4:
        contracting_company_city= st.text_input("City:")
    with col_5:
        #contracting_company_state = st.text_input("State:")
        contracting_company_state = st.selectbox("State:", options=[
            "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
            "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
            "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
            "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
            "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
        ])
    with col_6:
        contracting_company_zip = st.text_input("Zip:")

    if st.button("Register & Pay"):

        # Store form data temporarily in session_state
        st.session_state["pending_user"] = {
            "username": new_username,
            "password": new_password,
            "name": contracting_company_name,
            "street": contracting_company_street,
            "city": contracting_company_city,
            "state": contracting_company_state,
            "zip": contracting_company_zip,
            "email": contracting_company_email,
        }

        # Create Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": "Registration Fee"},
                    "unit_amount": 100,  # $1.00
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"{CXLOOP_APP_URL}/?page=success&session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{CXLOOP_APP_URL}/?page=cancel",
            metadata={"username": new_username, "email": contracting_company_email, "name": contracting_company_name},
        )

        st.markdown(f"[Click here to pay →]({session.url})", unsafe_allow_html=True)
        st.stop()  # Stop further execution until payment is confirmed
        
        #ok, msg = register_user(new_username, new_password, contracting_company_name)
        #if ok:
        #    add_contractor(contracting_company_name, contracting_company_street, contracting_company_city, contracting_company_state, contracting_company_zip)
        #    st.success(msg)
        #else:
        #    st.warning(msg)


if tab == "Forgot Password":
    st.subheader("Retrieve your password:")

    username_forgotten_password = st.text_input("Username:")


    if st.button("Get Password"):

        cur.execute("SELECT password_raw FROM TEST.PUBLIC.users WHERE username = %s", (username_forgotten_password,))
        row = cur.fetchone()
        if not row:
            st.error("Invalid username. Please check and try again.")
        else:
            # Here you can implement the logic to send a reset link or code to the user's email
            password = row[0]
            st.success(f" Your Password is: {password}")

# If logged in
if st.session_state.logged_in:
    #st.success(f"Hello {st.session_state.full_name}, you're logged in!")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.success("You have been logged out.")
        st.rerun()  # Rerun the app after logout to reset to the login screen

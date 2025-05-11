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


import hashlib
from datetime import datetime, timedelta
from supabase import create_client
import stripe
import os

sb_url = st.secrets["supabase"]["url"]
anon_key = st.secrets["supabase"]["key"]

# Hash passwords securely
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_connection():
    return create_client(sb_url, anon_key)


# Register a new user
def register_user(username, password, contracting_company_name):

    conn = get_connection()
    hashed = hash_password(password)
    # Expiration date set to 1 year from now
    expiration_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d %H:%M:%S")  # <-- formatted string

    # Query the users table
    response = (
        conn
        .table("users")
        .select("id", count='exact')  # 'id' can be any column; count='exact' is key
        .eq("username", username)
        .eq("full_name", contracting_company_name)
        .execute()
    )
    # Get the count of matching rows
    count = response.count

    if count > 0:
        return True, "User exists, you may login now!"
    else:
        # Your input values
        data = {
            "username": username,
            "hashed_password": hashed,
            "password_raw": password,
            "full_name": contracting_company_name,
            "member_expiration_date": expiration_date  # Ensure it's a valid ISO 8601 string or `datetime.date`
        }

        # Insert into 'users' table
        response = conn.table("users").insert(data).execute()

        # Check result
        if response.status_code == 201:
            return True, "User registered successfully!"
        else:
            return False, "Insert failed: {response.data}"


# Add row to [contractors] table after register
def add_contractor(contracting_company_name, contracting_company_street, contracting_company_city, contracting_company_state, contracting_company_zip):

    conn = get_connection()
    response = (conn
                .table("contractors")
                .select("CONTRACTOR_ID", count="exact")  # Use any column name, 'id' is fine
                .eq("contractor_name", contracting_company_name)
                .execute()
                )
    count = response.count
    if count > 0:    
        return False, "This company is already present in the database. "
    else:

        data = {"contractor_name": contracting_company_name,
                "street": contracting_company_street,
                "city": contracting_company_city,
                "state": contracting_company_state,
                "zip": contracting_company_zip
        }
        response = conn.table("contractors").insert(data).execute()
        if response.status_code == 201:
            return True, "Contractor company details inserted successfully."

# Validate [user] to [company] before register
def validate_user_to_contractor(username, contracting_company_name):

    conn = get_connection()
    response = (
        conn
        .table("users")
        .select("user_id", count='exact')  # 'id' can be any column; count='exact' is key
        .eq("username", username)
        .eq("full_name", contracting_company_name)
        .execute()
    )
    # Get the count of matching rows
    count = response.count
    if count > 0:
        return False, "User is assoicated to this contracting company, you may choose another company to register."
    else:
        return True, "Procced to registration"

stripe.api_key = st.secrets["stripe"]["secret_key"]
CXLOOP_APP_URL = "https://cxloop-enter.streamlit.app/" 

# ⬇️ Handle success from Stripe at the top
if st.query_params.get("page") == "success":
    session_id = st.query_params.get("session_id")

    if session_id:
        #st.write(f"Success page loaded with session ID: {session_id}")
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == "paid":
                #st.write(f"session.payment_status: {session.payment_status}")
                user_data = session.metadata
                #st.write(user_data)
                if user_data:
                    ok, msg = register_user(user_data["username"], user_data["password"], user_data["name"])
                    #st.write(ok, msg)
                    if ok:
                        ok_contractor, msg_contractor = add_contractor(
                                user_data["name"],
                                user_data["street"],
                                user_data["city"],
                                user_data["state"],
                                user_data["zip"]
                            )
                        if ok_contractor:  
                            st.success("🎉 Contracting company registration complete! You may now log in.")
                        else:
                            st.error(msg_contractor)
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


# Check login
def authenticate_user(username, password):

    conn = get_connection()
    response = (
    conn
    .table("users")
    .select("hashed_password, full_name")
    .eq("username", username)
    .single()  # Assumes usernames are unique
    .execute()
    )

    # Get the count of matching rows
    count = response.count
    if count > 0:
        stored_hash = response.data["hashed_password"]
        full_name = response.data["full_name"]
        if hash_password(password) == stored_hash:
            return True, full_name
        else:
            return False, None
    else:
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
                st.error("Already user, but forgot password. Choose Forgot Password above.")

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

        # Validate user to contractor
        ok, msg = validate_user_to_contractor(new_username, contracting_company_name)
        

        if ok:

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
                        "unit_amount": 499,  # $4.99
                    },
                    "quantity": 1,
                }],
                mode="payment",
                success_url=f"{CXLOOP_APP_URL}/?page=success&session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{CXLOOP_APP_URL}/?page=cancel",
                metadata={
                    "username": new_username,
                    "password": new_password,
                    "name": contracting_company_name,
                    "street": contracting_company_street,
                    "city": contracting_company_city,
                    "state": contracting_company_state,
                    "zip": contracting_company_zip,
                    "email": contracting_company_email,
                },
            )

            st.markdown(f"[Click here to pay →]({session.url})", unsafe_allow_html=True)
            st.stop()  # Stop further execution until payment is confirmed
        else:
            st.error(msg)
             

if tab == "Forgot Password":
    st.subheader("Retrieve your password:")
    username_forgotten_password = st.text_input("Username:")

    if st.button("Get Password"):
        conn = get_connection()
        response = (
            conn
            .table("users")
            .select("password_raw")
            .eq("username", username_forgotten_password)
            .single()  # Assumes username is unique
            .execute()
        )

        # Get the count of matching rows
        count = response.count
        if count > 0:
            password_raw = response.data["password_raw"]
            st.success(f" Your Password is: {password_raw}")
        else:
            st.error("Invalid username. Please check and try again.")
        

# If logged in
if st.session_state.logged_in:
    #st.success(f"Hello {st.session_state.full_name}, you're logged in!")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.success("You have been logged out.")
        st.rerun()  # Rerun the app after logout to reset to the login screen

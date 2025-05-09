import streamlit as st
import snowflake.connector
import hashlib
from datetime import datetime


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
def register_user(username, password, contracting_company_name):
    hashed = hash_password(password)
    cur.execute("SELECT COUNT(*) FROM TEST.PUBLIC.users WHERE username = %s AND full_name = %s", (username, contracting_company_name))
    exists = cur.fetchone()[0]
    if exists:
        return False, "User already exists, pick a different user."
    cur.execute("""
        INSERT INTO TEST.PUBLIC.users (username, hashed_password, full_name)
        VALUES (%s, %s, %s)
    """, (username, hashed, contracting_company_name))
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

hide_header_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """
st.markdown(hide_header_menu_style, unsafe_allow_html=True)
hide_footer_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """
st.markdown(hide_footer_menu_style, unsafe_allow_html=True)

tab = st.radio("Choose:", ["Login", "Register (i.e for new contractor)"])

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

else:
    st.subheader("Register your company:")
    col_0, col_1 = st.columns([1,1])
    with col_0:
        new_username = st.text_input("Username:")
    with col_1:
        new_password = st.text_input("Password:", type="password")
    #Company Details
    contracting_company_name = st.text_input("Contracting Company:")
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

    if st.button("Register"):
        ok, msg = register_user(new_username, new_password, contracting_company_name)
        
        if ok:
            add_contractor(contracting_company_name, contracting_company_street, contracting_company_city, contracting_company_state, contracting_company_zip)
            st.success(msg)
        else:
            st.warning(msg)

# If logged in
if st.session_state.logged_in:
    #st.success(f"Hello {st.session_state.full_name}, you're logged in!")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.success("You have been logged out.")
        st.rerun()  # Rerun the app after logout to reset to the login screen

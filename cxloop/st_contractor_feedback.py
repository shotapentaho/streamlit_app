#Import necessary libraries
import streamlit as st
import snowflake.connector
import pandas as pd
from datetime import date
import time



if len(st.query_params)> 1:
     # Update session state based on the URL parameter
    if st.query_params["logged_in"] == "true":
        st.session_state.logged_in = True      
else:
    st.error("You must be logged in to access this page.")
    st.stop()  # Stops the app execution here if the user is not logged in.
    st.session_state.logged_in = False


# Connect to Snowflake using Streamlit secrets
def get_connection():
    return snowflake.connector.connect(
        user=st.secrets["snowflake"]["user"],
        password=st.secrets["snowflake"]["password"],
        account=st.secrets["snowflake"]["account"],
        warehouse=st.secrets["snowflake"]["warehouse"],
        database=st.secrets["snowflake"]["database"],
        schema=st.secrets["snowflake"]["schema"]
    )

# Check password received in URL
def is_valid_user(user_str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT username FROM TEST.PUBLIC.users WHERE username = %s", (user_str,))
    row = cur.fetchone()
    if not row:
        return False, None
    else:
        username = row
        return True, username
    return False, None

user_exists = is_valid_user (st.query_params["username"])
#valid_user_name = authenticated_user (st.query_params["username"])
#st.write(f"Welcome {valid_user_name[0]}")

if (user_exists[0] == False):
    st.error("You must be logged in to access this page.")
    st.stop()  # Stops the app execution here if the user is not logged in.
    st.session_state.logged_in = False

def authenticated_user(user_str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT username FROM TEST.PUBLIC.users WHERE username = %s", (user_str,))
    row = cur.fetchone()
    if not row:
        return False, None
    else:
        username = row
        return username
    return False, None



# ---- Query contractor companies ----
def get_contractor_company(conn, valid_user):
    
    conn = get_connection()
    cur = conn.cursor()

    query = """
    SELECT distinct contractor_id, contractor_name as name
    FROM test.public.contractors 
    WHERE contractor_name IN ( select full_name from test.public.users where username = %s )
    """
    cur = conn.cursor()
    cur.execute(query, (valid_user,))
    #st.print(f"Query: {query} with {valid_user}")
    rows = cur.fetchall()
    cur.close()
    return [{"label": name, "contractor_id": cid} for cid, name in rows]


conn = get_connection()
cur = conn.cursor()

#st.title("Let's rate a customer..")

def render():
    st.header("Feedback form..")
    #st.write("Inside Feedback Tab")
    hide_menu_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
    st.markdown(hide_menu_style, unsafe_allow_html=True)

    # Reset logic: must come BEFORE widget declaration
    if "reset_form" in st.session_state and st.session_state.reset_form:
        st.session_state["k_customer_name"] = ""
        st.session_state["k_street"] = ""
        st.session_state["k_city"] = ""
        st.session_state["k_state"] = ""
        st.session_state["k_zip_code"] = ""
        st.session_state["k_rating"] = ""
        st.session_state["k_feedback"] = ""
        st.session_state["k_engagement_type"] = "Pick one"
        st.session_state["k_activity_date"] = date.today()
        st.session_state.reset_form = False

    contractors = get_contractor_company(conn, st.query_params["username"])

    # Create label list for dropdown
    contractor_labels = [c["label"] for c in contractors]
    selected_label = st.selectbox("Contractor Company:", contractor_labels)
    # Retrieve ID of selected contractor
    selected_contractor = next((c for c in contractors if c["label"] == selected_label), None)
    #Debuggingif selected_contractor:    
                    #st.info(f"Selected Contractor ID: {selected_contractor['contractor_id']}")



    # Form fields
    with st.form("engagement_form"):

        col_name, col_ignore = st.columns([1,1])
        with col_name:
            customer_name = st.text_input("Customer Name:", key="k_customer_name")
        with col_ignore:
            st.write("")

        col_0, col_1 = st.columns([1,2])
        with col_0:
            engagement_type = st.selectbox("Job done:", ["Pick one", "Electrical", "Painting", "Plumbing", "Power Wash", "Handyman", "Misc"], key="k_engagement_type")
        with col_1:
            activity_date = st.date_input("Performed/Finished on:", key="k_activity_date")

        col4, col1, col2, col3 = st.columns([2, 1, 1, 1])
        with col4:
            street = st.text_input("Street:", key="k_street")
        with col1:
            city = st.text_input("City:", key="k_city")
        with col2:
            state = st.selectbox("State:", options=[
                "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
                "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
                "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
                "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
                "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
            ], key="k_state")
        with col3:
            zip_code = st.text_input("ZIP:", key="k_zip_code")

        # Inside your form
        col_rating, col_feedback = st.columns([1, 3])
        with col_rating:
            rating = st.selectbox("Star rating:", ["⭐⭐⭐⭐⭐","⭐⭐⭐⭐","⭐⭐⭐","⭐⭐","⭐"], key="k_rating")
            star_rating = len(rating)
            #star_rating = st_star_rating(label="Customer Rating", maxValue=5, defaultValue=3, key="rating")

        with col_feedback:
            feedback = st.text_area("Additional feedback (from last activity):", key="k_feedback", height=100)

        # Validation: Prevent future dates
        if activity_date > date.today():
            st.error("⚠️ Activity date cannot be in the future.")

        submitted = st.form_submit_button("Submit")

        if submitted:
            if not (customer_name and street and city and zip_code):
                st.warning("Please fill out all required fields.")
            else:
                insert_sql = """
                    INSERT INTO TEST.PUBLIC.engagements (
                        contractor_id, customer_name, street, city, state, zip_code, 
                        engagement_type, activity_date, rating, feedback
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cur.execute(insert_sql, (
                    selected_contractor['contractor_id'], customer_name, street, city, state, zip_code,
                    engagement_type, activity_date.isoformat(), star_rating, feedback
                ))
                conn.commit()
                st.success("Feedback saved!")
                time.sleep(1)
                st.session_state.reset_form = True
                st.rerun()

 
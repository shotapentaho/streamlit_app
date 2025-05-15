#Import necessary libraries
import streamlit as st
import snowflake.connector
import pandas as pd
from datetime import date
import time
import numpy as np

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


# -Query contractor companies ---
def get_contractor_company(valid_user):
    
    conn = get_connection()
    cur = conn.cursor()
    query = """
    SELECT distinct contractor_id, contractor_name as name
    FROM test.public.contractors 
    WHERE contractor_name IN ( select full_name from test.public.users where username = %s )
    """
    cur.execute(query, (valid_user,))
    #st.print(f"Query: {query} with {valid_user}")
    rows = cur.fetchall()
    cur.close()
    return [{"label": name, "contractor_id": cid} for cid, name in rows]

# -Query engagement types  ---
def get_all_contract_activity_types():
    
    conn = get_connection()
    cur = conn.cursor()

    query = """
            SELECT activity_id, activity_name as engagement_type 
            FROM test.public.contract_activity_type
            ORDER BY activity_name
            """
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    return [{"label": engagement_type, "activity_id": aid} for aid, engagement_type in rows]

# -- User feedbacks ---
def display_user_feedbacks(username):
    
    conn = get_connection()
    cur = conn.cursor()

    # Retrieve and display existing data
    query = """SELECT eng.ENGAGEMENT_ID, cont.contractor_name, eng.customer_name, eng.street, eng.city, eng.state, eng.zip_code as zip, eng.engagement_type, eng.activity_date,
            eng.rating,eng.feedback
            FROM TEST.PUBLIC.engagements as eng INNER JOIN TEST.PUBLIC.contractors cont ON cont.contractor_id = eng.contractor_id
                INNER JOIN TEST.PUBLIC.users u ON u.full_name = cont.contractor_name
                AND u.username = %s
            ORDER BY cont.contractor_name, eng.activity_date DESC;
        """
    cur.execute(query, (username,))
    df = cur.fetch_pandas_all()
    cur.close()
    return df

def update_feedback_rows(original_df, edited_df):
    conn = get_connection()
    cur = conn.cursor()

    # Iterate row by row
    for idx in range(len(original_df)):
        original_row = original_df.iloc[idx]
        edited_row = edited_df.iloc[idx]

        if not original_row.equals(edited_row):
            st.info(f"Updating row {idx + 1}...")

            # Use identifying columns (e.g., contractor_name, activity_date) to locate the row
            update_sql = """
                UPDATE TEST.PUBLIC.engagements
                SET customer_name = %s,
                    street = %s,
                    city = %s,
                    state = %s,
                    zip_code = %s,
                    rating = %s,
                    feedback = %s,
                    activity_date = %s
                WHERE ENGAGEMENT_ID = %s  
            """
            
            params = tuple(value.item() if isinstance(value, np.generic) else value for value in [
                edited_row["CUSTOMER_NAME"],
                edited_row["STREET"],
                edited_row["CITY"],
                edited_row["STATE"],
                edited_row["ZIP"],
                edited_row["RATING"],
                edited_row["FEEDBACK"],
                edited_row["ACTIVITY_DATE"],
                int(edited_row["ENGAGEMENT_ID"])
            ])  # Convert to tuple
            cur.execute(update_sql, params)

    conn.commit()
    cur.close()



def render():
    st.header("Feedback form..")
    conn = get_connection()
    cur = conn.cursor()
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
        #st.session_state["k_engagement_type"] = "Pick one"
        st.session_state["k_activity_date"] = date.today()
        st.session_state.reset_form = False

    contractors = get_contractor_company(st.query_params["username"])

    # Create contractors list for dropdown
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
            all_activity_types = get_all_contract_activity_types()
            # Create activity_labels list for dropdown
            activity_labels = [c["label"] for c in all_activity_types]
            engagement_type = st.selectbox("Job Done:", activity_labels)
        with col_1:
            activity_date = st.date_input("Performed/Finished on:", key="k_activity_date")

        col4, col1, col2, col3 = st.columns([2, 1, 1, 1])
        with col4:
            street = st.text_input("Street:", key="k_street")
        with col1:
            city = st.text_input("City:", key="k_city")
        with col2:
            state = st.selectbox("State:", options=["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
                "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
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
                    INSERT INTO TEST.PUBLIC.engagements (engagement_id,
                        contractor_id, customer_name, street, city, state, zip_code, 
                        engagement_type, activity_date, rating, feedback
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cur.execute(insert_sql, (ENGAGEMENT_ID_SEQ.NEXTVAL
                    selected_contractor['contractor_id'], customer_name, street, city, state, zip_code,
                    engagement_type, activity_date.isoformat(), star_rating, feedback
                ))
                conn.commit()
                st.success("Feedback saved!")
                time.sleep(1)
                st.session_state.reset_form = True
                st.rerun()

    st.header(f" {st.query_params["username"]} your feedbacks below..you may edit and save")
    original_df = display_user_feedbacks(st.query_params["username"])
    edited_df = st.data_editor( original_df,
                                column_config={
                                    "customer_name": st.column_config.TextColumn("customer_name"),
                                    "street": st.column_config.TextColumn("street"),
                                    "city": st.column_config.TextColumn("city"),
                                    "state": st.column_config.TextColumn("state"),
                                    "zip": st.column_config.TextColumn("zip"),    
                                    "rating": st.column_config.SelectboxColumn("rating", options=["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"]),
                                    "feedback": st.column_config.TextColumn("feedback"),
                                    "activity_date": st.column_config.DateColumn("activity_date")                                },
                                disabled=["ENGAGEMENT_ID", "CONTRACTOR_NAME", "ENGAGEMENT_TYPE"],  # Make these read-only
                                use_container_width=True
                             )
    #st.write("✅ All Data ", edited_df)

    # Identify changed rows
    changed_rows = edited_df.compare(original_df)
    if not changed_rows.empty:
        st.warning("Changes detected!")
        if st.button("💾 Save Changes"):
            update_feedback_rows(original_df, edited_df)
            st.success("Changes saved!")
            st.rerun()

 
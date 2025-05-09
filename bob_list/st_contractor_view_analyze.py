import streamlit as st
import snowflake.connector
import pandas as pd
from datetime import date
import openai import OpenAI


def render():
    st.header("Analyze, search, download ..")
    #st.write("Inside View Analyze Tab")
    hide_menu_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
    st.markdown(hide_menu_style, unsafe_allow_html=True)

    # Use secrets
    #openai.api_key = st.secrets["openai"]["api_key"]
    client = OpenAI(api_key=st.secrets["openai"]["api_key"])  # Or use env var

    # Question Input (reset each time a new file is uploaded)
    question = st.text_input("💬 Ask a question to retrieve data (i.e English): ex row count? OR group by [field] etc. Note: If column name contains space, qualify with double quotes"
                             #,value=st.session_state.question
                            ,placeholder="ex: row count? OR group by [field name] etc. Note: If column name contains space, qualify with double quotes",   # 👈 Greyed out tip text
                             )
    
    # Retrieve and display existing data
    cur.execute("""SELECT cont.contractor_name, eng.customer_name, eng.street, eng.city, eng.state, eng.zip_code as zip, eng.engagement_type, eng.activity_date,
            eng.rating,eng.feedback
            FROM TEST.PUBLIC.engagements as eng INNER JOIN TEST.PUBLIC.contractors cont ON cont.contractor_id = eng.contractor_id
            ORDER BY cont.contractor_name, eng.activity_date DESC;
        """)

    df = cur.fetch_pandas_all()
    st.session_state.df = df
    # Display the dataframe preview
    st.write("✅ Data Preview", df.head())
    #st.dataframe(df.head(), use_container_width=True)

    if question:
        #st.write(f"💬 User Question: {question}")  # Log user question for debugging

        with st.spinner("💡 Generating SQL..."):
            prompt = f"""
                        Translate the following question into SQL for Snowflake.
                        Table name: data
                        Schema: {st.session_state.df.dtypes.astype(str).to_string()}
                        Question: {question}
                        Only return the SQL code.
                        """

            try:
                # Make the OpenAI API request
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0,
                )

                # Debugging: Show the raw response from OpenAI
                #st.write("OpenAI Raw Response:")
                #st.json(response)  # This will give you the full raw response in JSON format

                sql_query = response.choices[0].message.content.strip()

                # Debugging: Check if the SQL query is generated
                if not sql_query:
                    st.error("❌ OpenAI returned an empty SQL query.")
                else:
                    st.write("Generated SQL Query:")
                    st.code(sql_query, language="sql")

                # Checking if the SQL is syntactically correct before executing
                if sql_query:
                    result = cur.execute(sql_query).fetchdf()  # THIS IS THE FIX: use fetchdf() to get the results

                    # Debugging: Show the result
                    st.write("SQL Execution Result:")
                    st.dataframe(result)

                    if not result.empty:
                        st.warning("Visualize the result:")
                        #plot_result_dataframe(result)
                    else:
                        st.warning("⚠️ No data returned from SQL query.")
            except Exception as e:
                st.error(f"Error: {e}")


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
if (user_exists[0] == False):
    st.error("You must be logged in to access this page.")
    st.stop()  # Stops the app execution here if the user is not logged in.
    st.session_state.logged_in = False


conn = get_connection()
cur = conn.cursor()



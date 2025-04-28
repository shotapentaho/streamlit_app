import streamlit as st
import duckdb
import pandas as pd
import openai
import matplotlib.pyplot as plt

# Use secrets
openai.api_key = st.secrets["openai"]["api_key"]

st.set_page_config(layout="wide")
st.title(" 🔍 📄 🧠 NLP (Natural Language) based data analysis: CSV or JSON!!")

# --- Setup session_state for dataframe ---
if 'df' not in st.session_state:
    st.session_state.df = None

if 'question' not in st.session_state:
    st.session_state.question = ''  # Default empty question

def plot_result_dataframe(df):
    if df.empty:
        st.warning("No data to plot.")
        return
    
    st.subheader("📊 Auto-generated Plot")

    # Pick sensible defaults
    numeric_columns = df.select_dtypes(include=['number']).columns
    non_numeric_columns = df.select_dtypes(exclude=['number']).columns

    if len(numeric_columns) >= 1 and len(non_numeric_columns) >= 1:
        x_col = non_numeric_columns[0]
        y_col = numeric_columns[0]

        fig, ax = plt.subplots(figsize=(8, 4))
        df.plot(kind='bar', x=x_col, y=y_col, ax=ax)
        st.pyplot(fig)
    else:
        st.info("Need at least one categorical column and one numeric column to plot.")

# File uploader
uploaded_file = st.file_uploader("📁 Upload your CSV or JSON file", type=["csv", "json"])

if uploaded_file is not None:
    file_name = uploaded_file.name

    # Clear the question when a new file is uploaded
    st.session_state.question = ''  # Reset question

    if file_name.endswith('.csv'):
        try:
            st.session_state.df = pd.read_csv(uploaded_file)
            st.success("✅ CSV file loaded!")
        except Exception as e:
            st.error(f"Error loading CSV: {e}")
    elif file_name.endswith('.json'):
        try:
            st.session_state.df = pd.read_json(uploaded_file, lines=True)
            st.success("✅ JSON file loaded!")
        except Exception as e:
            st.error(f"Error loading JSON: {e}")
    else:
        st.error("❌ Unsupported file format. Please upload a CSV or JSON file.")

# --- If dataframe is ready ---
if st.session_state.df is not None:
    con = duckdb.connect()
    con.register("data", st.session_state.df)
    st.write("✅ Data Preview", st.session_state.df.head())

    # Question Input (reset each time a new file is uploaded)
    question = st.text_input("💬 Ask a question in natural language:", value=st.session_state.question)

    # Check if the question has changed or is not empty
    if question:
        st.write(f"💬 User Question: {question}")  # Log user question for debugging

        with st.spinner("💡 Generating SQL..."):
            prompt = f"""
Translate the following question into SQL for DuckDB.
Table name: data
Schema: {st.session_state.df.dtypes.astype(str).to_string()}
Question: {question}
Only return the SQL code.
"""

            # Debugging: Show the generated prompt for clarity
            st.write("Generated Prompt:")
            st.code(prompt, language="text")

            try:
                # Make the OpenAI API request
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0,
                )

                # Debugging: Show the raw response from OpenAI
                st.write("OpenAI Raw Response:")
                st.json(response)  # This will give you the full raw response in JSON format

                sql_query = response.choices[0].message.content.strip()

                # Debugging: Check if the SQL query is generated
                if not sql_query:
                    st.error("❌ OpenAI returned an empty SQL query.")
                else:
                    st.write("Generated SQL Query:")
                    st.code(sql_query, language="sql")

                # Checking if the SQL is syntactically correct before executing
                if sql_query:
                    result = con.execute(sql_query).fetchdf()  # THIS IS THE FIX: use fetchdf() to get the results

                    # Debugging: Show the result
                    st.write("SQL Execution Result:")
                    st.dataframe(result)

                    if not result.empty:
                        plot_result_dataframe(result)
                    else:
                        st.warning("⚠️ No data returned from SQL query.")
            except Exception as e:
                st.error(f"Error: {e}")

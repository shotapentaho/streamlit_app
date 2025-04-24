import streamlit as st
import duckdb
import pandas as pd
import openai

# Use secrets
openai.api_key = st.secrets["openai"]["api_key"]

st.set_page_config(layout="wide")
st.title("🔍 CSV analysis with Natural Language!")

uploaded_file = st.file_uploader("📁 Upload your CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    con = duckdb.connect()
    con.register("data", df)

    st.write("✅ Data Preview", df.head())

    question = st.text_input("💬 Ask a question in natural language:")

    if question:
        with st.spinner("💡 Generating SQL..."):
            prompt = f"""
Translate the following question into SQL for DuckDB.
Table name: data
Schema: {df.dtypes.astype(str).to_string()}
Question: {question}
Only return the SQL code.
"""
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0,
                )
                sql_query = response.choices[0].message.content.strip()
                st.code(sql_query, language="sql")

                result = con.execute(sql_query).df()
                st.dataframe(result)

            except Exception as e:
                st.error(f"Error: {e}")

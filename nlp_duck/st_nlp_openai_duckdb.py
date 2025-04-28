import streamlit as st
import duckdb
import pandas as pd
import openai
import matplotlib.pyplot as plt

# Use secrets
openai.api_key = st.secrets["openai"]["api_key"]

st.set_page_config(layout="wide")
st.title(" 🔍 📄 🧠 NLP (Natural Language) based CSV data analysis!!")

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

#uploaded_file = st.file_uploader("📁 Upload your CSV file", type=["csv"])
uploaded_file = st.file_uploader("📁 Upload your CSV or JSON file", type=["csv", "json"])


if uploaded_file is not None:
    file_name = uploaded_file.name

    if file_name.endswith('.csv'):
        try:
            df = pd.read_csv(uploaded_file)
            st.success("✅ CSV file loaded!")
            con = duckdb.connect()
            con.register("data", df)
            st.write("✅ Data Preview", df.head())
        except Exception as e:
            st.error(f"Error loading CSV: {e}")
    elif file_name.endswith('.json'):
        try:
            df = pd.read_json(uploaded_file)
            st.success("✅ JSON file loaded!")
            con = duckdb.connect()
            con.register("data", df)
            st.write("✅ Data Preview", df.head())
        except Exception as e:
            st.error(f"Error loading JSON: {e}")
    #df = pd.read_csv(uploaded_file)

    

    

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
                plot_result_dataframe(result)

            except Exception as e:
                st.error(f"Error: {e}")





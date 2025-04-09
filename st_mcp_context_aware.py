import streamlit as st
import duckdb
from datetime import datetime

# DB Setup
con = duckdb.connect("context.duckdb")
con.execute("""
    CREATE TABLE IF NOT EXISTS context_history (
        user TEXT,
        timestamp TIMESTAMP,
        input TEXT,
        response TEXT
    )
""")

# UI
st.title("?? MCP Context-Aware Streamlit App")

user = st.text_input("Your name")
user_input = st.text_area("What's on your mind?")

if st.button("Submit"):
    # Simulate a model response
    response = f"Hello {user}, I see you're thinking about: {user_input}"
    
    # Save context
    con.execute("INSERT INTO context_history VALUES (?, ?, ?, ?)",
                (user, datetime.now(), user_input, response))
    
    # Display
    st.success(response)

# Show past
if st.checkbox("Show My History"):
    df = con.execute("SELECT * FROM context_history WHERE user = ?", (user,)).fetchdf()
    st.dataframe(df)

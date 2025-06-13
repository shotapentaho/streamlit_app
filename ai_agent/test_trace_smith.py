import os
import streamlit as st

# Set environment variables BEFORE any langsmith/langchain imports!
os.environ["LANGCHAIN_API_KEY"] = st.secrets["langsmith"]["api_key"]
os.environ["LANGCHAIN_PROJECT"] = st.secrets["langsmith"]["project_name"]

# For debugging: show the project name being used
st.write("LangSmith Project:", os.environ.get("LANGCHAIN_PROJECT"))

from langsmith import traceable

@traceable
def add(a, b):
    return a + b

if st.button("Send Trace!"):
    result = add(1, 2)
    st.write("Result:", result)

import streamlit as st
import requests
import json
import openai

st.set_page_config(layout="wide")
st.title("🧠 MCP Client")

openai.api_key = st.secrets["openai"]["api_key"]

prompt = st.text_area("Enter your prompt:")

if st.button("Send to MCP Server"):
    with st.spinner("Waiting for response..."):
        try:
            response = requests.post("http://localhost:5000/mcp", json={"prompt": prompt})
            if response.status_code == 200:
                result = response.json()
                st.success("Response from model:")
                st.write(result["response"])
            else:
                st.error(f"Server error: {response.text}")
        except Exception as e:
            st.error(f"Connection failed: {e}")

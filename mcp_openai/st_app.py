import streamlit as st
import requests
import json
import openai

st.set_page_config(layout="wide")
st.title("🧠 MCP Client")

prompt = st.text_area("Enter your prompt:")

if st.button("Send to MCP Server"):
    with st.spinner("Waiting for response..."):
        try:
            # Replace with your EC2/GCP public IP or domain and port 5000
            response = requests.post("https://mcp-openai.streamlit.app:5000/mcp", json={"prompt": prompt}, timeout=30)
            st.write("Response status code:", response.status_code)
            if response.status_code == 200:
                result = response.json()
                st.success("Response from model:")
                st.write(result["response"])
            else:
                st.error(f"Server error: {response.text}")
        except Exception as e:
            st.error(f"Connection failed: {e}")
